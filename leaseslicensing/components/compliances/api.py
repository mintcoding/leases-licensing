import traceback
import os
import datetime
import base64
import geojson
from six.moves.urllib.parse import urlparse
from wsgiref.util import FileWrapper
from copy import deepcopy
from django.db.models import Q, Min
from django.db import transaction
from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from rest_framework import viewsets, serializers, status, generics, views
from rest_framework.decorators import action as detail_route, renderer_classes
from rest_framework.decorators import action as list_route
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
    IsAdminUser,
    BasePermission,
)
from rest_framework.pagination import PageNumberPagination
from datetime import datetime, timedelta
from collections import OrderedDict
from django.core.cache import cache
from ledger_api_client.ledger_models import EmailUserRO as EmailUser, Address
from ledger_api_client.country_models import Country
from datetime import datetime, timedelta, date
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from leaseslicensing.components.compliances.models import (
    Compliance,
    ComplianceAmendmentRequest,
    ComplianceAmendmentReason,
)
from leaseslicensing.components.main.models import ApplicationType
from leaseslicensing.components.compliances.serializers import (
    ComplianceSerializer,
    InternalComplianceSerializer,
    SaveComplianceSerializer,
    ComplianceActionSerializer,
    ComplianceCommsSerializer,
    ComplianceAmendmentRequestSerializer,
    CompAmendmentRequestDisplaySerializer,
)
from leaseslicensing.helpers import is_customer, is_internal
from rest_framework_datatables.pagination import DatatablesPageNumberPagination
from leaseslicensing.components.proposals.api import (
    ProposalFilterBackend,
    ProposalRenderer,
)


class GetComplianceStatusesDict(views.APIView):
    renderer_classes = [
        JSONRenderer,
    ]

    def get(self, request, format=None):
        data = [
            {"code": i[0], "description": i[1]}
            for i in Compliance.CUSTOMER_STATUS_CHOICES
        ]
        return Response(data)


class CompliancePaginatedViewSet(viewsets.ModelViewSet):
    filter_backends = (ProposalFilterBackend,)
    pagination_class = DatatablesPageNumberPagination
    renderer_classes = (ProposalRenderer,)
    page_size = 10
    queryset = Compliance.objects.none()
    serializer_class = ComplianceSerializer

    def get_queryset(self):
        if is_internal(self.request):
            # return Compliance.objects.all()
            return Compliance.objects.all().exclude(processing_status="discarded")
        elif is_customer(self.request):
            # TODO: fix EmailUserRO issue here
            # user_orgs = [org.id for org in self.request.user.leaseslicensing_organisations.all()]
            # queryset =  Compliance.objects.filter( Q(proposal__org_applicant_id__in = user_orgs) | Q(proposal__submitter = self.request.user) ).exclude(processing_status='discarded')
            queryset = Compliance.objects.filter(
                Q(proposal__submitter=self.request.user.id)
            ).exclude(processing_status="discarded")
            return queryset
        return Compliance.objects.none()

    @list_route(
        methods=[
            "GET",
        ],
        detail=False,
    )
    def list_external(self, request, *args, **kwargs):
        """
        User is accessing /external/ page
        """
        qs = self.get_queryset()
        qs = self.filter_queryset(qs)

        self.paginator.page_size = qs.count()
        result_page = self.paginator.paginate_queryset(qs, request)
        # serializer = ListComplianceSerializer(result_page, context={'request': request}, many=True)
        serializer = ComplianceSerializer(
            result_page, context={"request": request}, many=True
        )
        result = self.paginator.get_paginated_response(serializer.data)
        print("result")
        print(result.__dict__)
        return result

    @list_route(
        methods=[
            "GET",
        ],
        detail=False,
    )
    def compliances_external(self, request, *args, **kwargs):
        """
        Paginated serializer for datatables - used by the external dashboard

        To test:
            http://localhost:8000/api/compliance_paginated/compliances_external/?format=datatables&draw=1&length=2
        """

        qs = self.get_queryset().exclude(processing_status="future")
        # qs = ProposalFilterBackend().filter_queryset(self.request, qs, self)
        qs = self.filter_queryset(qs)
        # qs = qs.order_by('lodgement_number', '-issue_date').distinct('lodgement_number')

        # on the internal organisations dashboard, filter the Proposal/Approval/Compliance datatables by applicant/organisation
        applicant_id = request.GET.get("org_id")
        if applicant_id:
            qs = qs.filter(proposal__org_applicant_id=applicant_id)
        submitter_id = request.GET.get("submitter_id", None)
        if submitter_id:
            qs = qs.filter(proposal__submitter_id=submitter_id)
        self.paginator.page_size = qs.count()
        result_page = self.paginator.paginate_queryset(qs, request)
        serializer = ComplianceSerializer(
            result_page, context={"request": request}, many=True
        )
        return self.paginator.get_paginated_response(serializer.data)


class ComplianceViewSet(viewsets.ModelViewSet):
    serializer_class = ComplianceSerializer
    # queryset = Compliance.objects.all()
    queryset = Compliance.objects.none()

    def get_queryset(self):
        if is_internal(self.request):
            return Compliance.objects.all().exclude(processing_status="discarded")
        elif is_customer(self.request):
            # TODO: fix EmailUserRO issue here
            # user_orgs = [org.id for org in self.request.user.leaseslicensing_organisations.all()]
            # queryset =  Compliance.objects.filter( Q(proposal__org_applicant_id__in = user_orgs) | Q(proposal__submitter = self.request.user) ).exclude(processing_status='discarded')
            queryset = Compliance.objects.filter(
                Q(proposal__submitter=self.request.user.id)
            ).exclude(processing_status="discarded")
            return queryset
        return Compliance.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # Filter by org
        org_id = request.GET.get("org_id", None)
        if org_id:
            queryset = queryset.filter(proposal__org_applicant_id=org_id)
        submitter_id = request.GET.get("submitter_id", None)
        if submitter_id:
            qs = qs.filter(proposal__submitter_id=submitter_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @list_route(
        methods=[
            "GET",
        ],
        detail=False,
    )
    def filter_list(self, request, *args, **kwargs):
        """Used by the external dashboard filters"""
        region_qs = (
            self.get_queryset()
            .filter(proposal__region__isnull=False)
            .values_list("proposal__region__name", flat=True)
            .distinct()
        )
        activity_qs = (
            self.get_queryset()
            .filter(proposal__activity__isnull=False)
            .values_list("proposal__activity", flat=True)
            .distinct()
        )
        application_types = ApplicationType.objects.all().values_list("name", flat=True)
        data = dict(
            regions=region_qs,
            activities=activity_qs,
            application_types=application_types,
        )
        return Response(data)

    @detail_route(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def internal_compliance(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = InternalComplianceSerializer(
            instance, context={"request": request}
        )
        return Response(serializer.data)

    @detail_route(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @renderer_classes((JSONRenderer,))
    def submit(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                data = {
                    "text": request.data.get("detail"),
                    "num_participants": request.data.get("num_participants"),
                }

                serializer = SaveComplianceSerializer(instance, data=data)
                serializer.is_valid(raise_exception=True)
                instance = serializer.save()

                # if request.data.has_key('num_participants'):
                if "num_participants" in request.data:
                    if request.FILES:
                        # if num_adults is present instance.submit is executed after payment in das_payment/views.py
                        for f in request.FILES:
                            document = instance.documents.create(
                                name=str(request.FILES[f])
                            )
                            document._file = request.FILES[f]
                            document.save()
                else:
                    instance.submit(request)

                serializer = self.get_serializer(instance)
                # Save the files
                """for f in request.FILES:
                    document = instance.documents.create()
                    document.name = str(request.FILES[f])
                    document._file = request.FILES[f]
                    document.save()
                # End Save Documents"""
                return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            if hasattr(e, "message"):
                raise serializers.ValidationError(e.message)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def assign_request_user(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.assign_to(request.user.id, request)
            serializer = InternalComplianceSerializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(
        methods=[
            "POST",
        ],
        detail=True,
    )
    def delete_document(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            doc = request.data.get("document")
            instance.delete_document(request, doc)
            serializer = ComplianceSerializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            if hasattr(e, "message"):
                raise serializers.ValidationError(e.message)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(
        methods=[
            "POST",
        ],
        detail=True,
    )
    def assign_to(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            user_id = request.data.get("user_id", None)
            #user = None
            if not user_id:
                raise serializers.ValiationError("A user id is required")
            #try:
            #    user = EmailUser.objects.get(id=user_id)
            #except EmailUser.DoesNotExist:
            #    raise serializers.ValidationError(
            #        "A user with the id passed in does not exist"
            #    )
            instance.assign_to(user_id, request)
            serializer = InternalComplianceSerializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def unassign(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.unassign(request)
            serializer = InternalComplianceSerializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def accept(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.accept(request)
            serializer = InternalComplianceSerializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def amendment_request(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.amendment_requests
            qs = qs.filter(status="requested")
            serializer = CompAmendmentRequestDisplaySerializer(qs, many=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def action_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.action_logs.all()
            serializer = ComplianceActionSerializer(qs, many=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(
        methods=[
            "GET",
        ],
        detail=True,
    )
    def comms_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.comms_logs.all()
            serializer = ComplianceCommsSerializer(qs, many=True)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))

    @detail_route(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @renderer_classes((JSONRenderer,))
    def add_comms_log(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                mutable = request.data._mutable
                request.data._mutable = True
                request.data["compliance"] = "{}".format(instance.id)
                request.data["staff"] = "{}".format(request.user.id)
                request.data._mutable = mutable
                serializer = ComplianceCommsSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                comms = serializer.save()
                # Save the files
                for f in request.FILES:
                    document = comms.documents.create()
                    document.name = str(request.FILES[f])
                    document._file = request.FILES[f]
                    document.save()
                # End Save Documents

                return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


class ComplianceAmendmentRequestViewSet(viewsets.ModelViewSet):
    queryset = ComplianceAmendmentRequest.objects.all()
    serializer_class = ComplianceAmendmentRequestSerializer

    def create(self, request, *args, **kwargs):
        try:
            request_data = deepcopy(request.data)
            request_data.update({"officer": request.user.id})
            serializer = self.get_serializer(data=request_data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            instance.generate_amendment(request)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
                # raise serializers.ValidationError(repr(e[0].encode('utf-8')))
                if hasattr(e, "message"):
                    raise serializers.ValidationError(e.message)
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e))


class ComplianceAmendmentReasonChoicesView(views.APIView):

    renderer_classes = [
        JSONRenderer,
    ]

    def get(self, request, format=None):
        choices_list = []
        # choices = ComplianceAmendmentRequest.REASON_CHOICES
        choices = ComplianceAmendmentReason.objects.all()
        if choices:
            for c in choices:
                choices_list.append({"key": c.id, "value": c.reason})
        return Response(choices_list)
