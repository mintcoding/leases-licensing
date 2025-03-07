import traceback
import os
import datetime
import base64
import geojson
from six.moves.urllib.parse import urlparse
from wsgiref.util import FileWrapper
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

# from leaseslicensing.components.main.models import Organisation as ledger_org
from ledger_api_client.country_models import Country
from datetime import datetime, timedelta, date
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from leaseslicensing.components.proposals.models import Proposal, ApplicationType
from leaseslicensing.components.approvals.models import Approval, ApprovalDocument, ApprovalType, ApprovalSubType
from leaseslicensing.components.approvals.serializers import (
    ApprovalSerializer,
    ApprovalCancellationSerializer,
    ApprovalExtendSerializer,
    ApprovalSuspensionSerializer,
    ApprovalSurrenderSerializer,
    ApprovalUserActionSerializer,
    ApprovalLogEntrySerializer,
    ApprovalPaymentSerializer,
)
from leaseslicensing.components.organisations.models import (
    Organisation,
    OrganisationContact,
)
from leaseslicensing.helpers import is_customer, is_internal
from rest_framework_datatables.pagination import DatatablesPageNumberPagination
from leaseslicensing.components.proposals.api import (
    ProposalFilterBackend,
    ProposalRenderer,
)
from rest_framework_datatables.filters import DatatablesFilterBackend


# class GetApprovalTypeDict(views.APIView):
#    renderer_classes = [JSONRenderer, ]
#
#    def get(self, request, format=None):
#        include_codes = request.GET.get('include_codes', '')
#        include_codes = include_codes.split(',')
#        cache_title = 'approval_type_dict'
#        for code in include_codes:
#            cache_title += '_' + code
#        data = cache.get(cache_title)
#        if not data:
#            #cache.set(cache_title, Approval.approval_types_dict(include_codes), settings.LOV_CACHE_TIMEOUT)
#            cache.set(cache_title,[{'code': i[0], 'description': i[1]} for i in Approval.STATUS_CHOICES], settings.LOV_CACHE_TIMEOUT)
#            data = cache.get(cache_title)
#        return Response(data)


class GetApprovalTypesDict(views.APIView):
    renderer_classes = [
        JSONRenderer,
    ]

    def get(self, request, format=None):
        data = cache.get("approval_types_dict")
        if not data:
            approval_types_dict = [{
                "id": t.id, 
                "name": t.name, 
                "details_placeholder": t.details_placeholder,
                "approval_type_document_types":
                [
                    {
                        "id": doc_type_link.approval_type_document_type.id,
                        "name": doc_type_link.approval_type_document_type.name,
                        "mandatory": doc_type_link.mandatory,
                    }
                    #for doc_type in t.approvaltypedocumenttypes.all()
                    for doc_type_link in t.approvaltypedocumenttypeonapprovaltype_set.all()
                ]
            } for t in ApprovalType.objects.all()]
            cache.set(
                "approval_types_dict",
                approval_types_dict,
                settings.LOV_CACHE_TIMEOUT,
            )
            data = cache.get("approval_types_dict")
        return Response(data)


class GetApprovalSubTypesDict(views.APIView):
    renderer_classes = [
        JSONRenderer,
    ]

    def get(self, request, format=None):
        data = cache.get("approval_sub_types_dict")
        if not data:
            approval_sub_types_dict = [{
                "id": t.id, 
                "name": t.name
            } for t in ApprovalSubType.objects.all()]
            cache.set(
                "approval_sub_types_dict",
                approval_sub_types_dict,
                settings.LOV_CACHE_TIMEOUT,
            )
            data = cache.get("approval_sub_types_dict")
        return Response(data)



class GetApprovalStatusesDict(views.APIView):
    renderer_classes = [
        JSONRenderer,
    ]

    def get(self, request, format=None):
        data = cache.get("approval_statuses_dict")
        if not data:
            cache.set(
                "approval_statuses_dict",
                [{"code": i[0], "description": i[1]} for i in Approval.STATUS_CHOICES],
                settings.LOV_CACHE_TIMEOUT,
            )
            data = cache.get("approval_statuses_dict")
        return Response(data)


class ApprovalFilterBackend(DatatablesFilterBackend):
    """
    Custom filters
    """

    def filter_queryset(self, request, queryset, view):
        total_count = queryset.count()

        def get_choice(status, choices=Proposal.PROCESSING_STATUS_CHOICES):
            for i in choices:
                if i[1] == status:
                    return i[0]
            return None

        date_from = request.GET.get("date_from")
        date_to = request.GET.get("date_to")

        if queryset.model is Approval:
            if date_from:
                queryset = queryset.filter(start_date__gte=date_from)

            if date_to:
                queryset = queryset.filter(expiry_date__lte=date_to)

        #getter = request.query_params.get
        #fields = self.get_fields(getter)
        #ordering = self.get_ordering(getter, fields)
        fields = self.get_fields(request)
        ordering = self.get_ordering(request, view, fields)
        queryset = queryset.order_by(*ordering)
        if len(ordering):
            queryset = queryset.order_by(*ordering)

        queryset = super(ApprovalFilterBackend, self).filter_queryset(
            request, queryset, view
        )
        setattr(view, "_datatables_total_count", total_count)
        return queryset


class ApprovalPaginatedViewSet(viewsets.ModelViewSet):
    # filter_backends = (ProposalFilterBackend,)
    filter_backends = (ApprovalFilterBackend,)
    pagination_class = DatatablesPageNumberPagination
    renderer_classes = (ProposalRenderer,)
    page_size = 10
    queryset = Approval.objects.none()
    serializer_class = ApprovalSerializer

    def get_queryset(self):
        if is_internal(self.request):
            return Approval.objects.all()
        elif is_customer(self.request):
            # TODO: fix EmailUserRO issue here
            # user_orgs = [org.id for org in self.request.user.leaseslicensing_organisations.all()]
            # queryset =  Approval.objects.filter(Q(org_applicant_id__in = user_orgs) | Q(submitter = self.request.user))
            queryset = Approval.objects.filter(Q(submitter=self.request.user.id))
            return queryset
        return Approval.objects.none()

    #    def list(self, request, *args, **kwargs):
    #        response = super(ProposalPaginatedViewSet, self).list(request, args, kwargs)
    #
    #        # Add extra data to response.data
    #        #response.data['regions'] = self.get_queryset().filter(region__isnull=False).values_list('region__name', flat=True).distinct()
    #        return response

    @list_route(
        methods=[
            "GET",
        ],
        detail=False,
    )
    def approvals_external(self, request, *args, **kwargs):
        """
        Paginated serializer for datatables - used by the internal and external dashboard (filtered by the get_queryset method)

        To test:
            http://localhost:8000/api/approval_paginated/approvals_external/?format=datatables&draw=1&length=2
        """

        # qs = self.queryset().order_by('lodgement_number', '-issue_date').distinct('lodgement_number')
        # qs = ProposalFilterBackend().filter_queryset(self.request, qs, self)

        ids = (
            self.get_queryset()
            .order_by("lodgement_number", "-issue_date")
            .distinct("lodgement_number")
            .values_list("id", flat=True)
        )
        qs = Approval.objects.filter(id__in=ids)
        qs = self.filter_queryset(qs)

        # on the internal organisations dashboard, filter the Proposal/Approval/Compliance datatables by applicant/organisation
        applicant_id = request.GET.get("org_id")
        if applicant_id:
            qs = qs.filter(org_applicant_id=applicant_id)
        submitter_id = request.GET.get("submitter_id", None)
        if submitter_id:
            qs = qs.filter(submitter_id=submitter_id)

        self.paginator.page_size = qs.count()
        result_page = self.paginator.paginate_queryset(qs, request)
        serializer = ApprovalSerializer(
            result_page, context={"request": request}, many=True
        )
        return self.paginator.get_paginated_response(serializer.data)


from rest_framework import filters


class ApprovalPaymentFilterViewSet(generics.ListAPIView):
    """https://cop-internal.dbca.wa.gov.au/api/filtered_organisations?search=Org1"""

    queryset = Approval.objects.none()
    serializer_class = ApprovalPaymentSerializer
    filter_backends = (filters.SearchFilter,)
    # search_fields = ('applicant', 'applicant_id',)
    search_fields = ("id",)

    def get_queryset(self):
        """
        Return All approvals associated with user (proxy_applicant and org_applicant)
        """
        # return Approval.objects.filter(proxy_applicant=self.request.user)
        user = self.request.user

        # get all orgs associated with user
        user_org_ids = OrganisationContact.objects.filter(email=user.email).values_list(
            "organisation_id", flat=True
        )

        now = datetime.now().date()
        approval_qs = Approval.objects.filter(
            Q(proxy_applicant=user)
            | Q(org_applicant_id__in=user_org_ids)
            | Q(submitter_id=user)
        )
        approval_qs = approval_qs.exclude(
            current_proposal__application_type__name="E Class"
        )
        approval_qs = approval_qs.exclude(expiry_date__lt=now)
        approval_qs = approval_qs.exclude(
            replaced_by__isnull=False
        )  # get lastest licence, ignore the amended
        return approval_qs

    @list_route(
        methods=[
            "GET",
        ],
        detail=False,
    )
    def _list(self, request, *args, **kwargs):
        data = []
        for approval in self.get_queryset():
            data.append(
                dict(
                    lodgement_number=approval.lodgement_number,
                    current_proposal=approval.current_proposal_id,
                )
            )
        return Response(data)
        # return Response(self.get_queryset().values_list('lodgement_number','current_proposal_id'))


class ApprovalViewSet(viewsets.ModelViewSet):
    # queryset = Approval.objects.all()
    queryset = Approval.objects.none()
    serializer_class = ApprovalSerializer

    def get_queryset(self):
        if is_internal(self.request):
            return Approval.objects.all()
        elif is_customer(self.request):
            user_orgs = [
                org.id for org in self.request.user.leaseslicensing_organisations.all()
            ]
            queryset = Approval.objects.filter(
                Q(org_applicant_id__in=user_orgs) | Q(submitter=self.request.user)
            )
            return queryset
        return Approval.objects.none()

    def list(self, request, *args, **kwargs):
        # queryset = self.get_queryset()
        queryset = (
            self.get_queryset()
            .order_by("lodgement_number", "-issue_date")
            .distinct("lodgement_number")
        )
        # Filter by org
        org_id = request.GET.get("org_id", None)
        if org_id:
            queryset = queryset.filter(org_applicant_id=org_id)
        submitter_id = request.GET.get("submitter_id", None)
        if submitter_id:
            qs = qs.filter(submitter_id=submitter_id)
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
        # region_qs =  self.get_queryset().filter(current_proposal__region__isnull=False).values_list('current_proposal__region__name', flat=True).distinct()
        # activity_qs =  self.get_queryset().filter(current_proposal__activity__isnull=False).values_list('current_proposal__activity', flat=True).distinct()
        application_types = ApplicationType.objects.all().values_list("name", flat=True)
        data = dict(
            approval_status_choices=[i[1] for i in Approval.STATUS_CHOICES],
            application_types=application_types,
        )
        return Response(data)

    @detail_route(methods=["POST"], detail=True)
    @renderer_classes((JSONRenderer,))
    def process_document(self, request, *args, **kwargs):
        instance = self.get_object()
        action = request.POST.get("action")
        section = request.POST.get("input_name")
        if action == "list" and "input_name" in request.POST:
            pass

        elif action == "delete" and "document_id" in request.POST:
            document_id = request.POST.get("document_id")
            document = instance.qaofficer_documents.get(id=document_id)

            document.visible = False
            document.save()
            instance.save(
                version_comment="Licence ({}): {}".format(section, document.name)
            )  # to allow revision to be added to reversion history

        elif (
            action == "save"
            and "input_name" in request.POST
            and "filename" in request.POST
        ):
            proposal_id = request.POST.get("proposal_id")
            filename = request.POST.get("filename")
            _file = request.POST.get("_file")
            if not _file:
                _file = request.FILES.get("_file")

            document = instance.qaofficer_documents.get_or_create(
                input_name=section, name=filename
            )[0]
            path = default_storage.save(
                "{}/proposals/{}/approvals/{}".format(
                    settings.MEDIA_APP_DIR, proposal_id, filename
                ),
                ContentFile(_file.read()),
            )

            document._file = path
            document.save()
            instance.save(
                version_comment="Licence ({}): {}".format(section, filename)
            )  # to allow revision to be added to reversion history
            # instance.current_proposal.save(version_comment='File Added: {}'.format(filename)) # to allow revision to be added to reversion history

        return Response(
            [
                dict(
                    input_name=d.input_name,
                    name=d.name,
                    file=d._file.url,
                    id=d.id,
                    can_delete=d.can_delete,
                )
                for d in instance.qaofficer_documents.filter(
                    input_name=section, visible=True
                )
                if d._file
            ]
        )

    @detail_route(
        methods=[
            "POST",
        ],
        detail=True,
    )
    @renderer_classes((JSONRenderer,))
    def add_eclass_licence(self, request, *args, **kwargs):
        def raiser(exception):
            raise serializers.ValidationError(exception)

        try:
            with transaction.atomic():
                # keys = request.data.keys()
                # file_keys = [key for key in keys if 'file-upload' in i]
                org_applicant = None
                proxy_applicant = None

                _file = (
                    request.data.get("file-upload-0")
                    if request.data.get("file-upload-0")
                    else raiser("Licence File is required")
                )
                try:
                    if request.data.get("applicant_type") == "org":
                        org_applicant = Organisation.objects.get(
                            organisation_id=request.data.get("holder-selected")
                        )
                        # org_applicant = ledger_org.objects.get(id=request.data.get('holder-selected'))
                    else:
                        proxy_applicant = EmailUser.objects.get(
                            id=request.data.get("holder-selected")
                        )
                except:
                    raise serializers.ValidationError("Licence holder is required")

                start_date = (
                    datetime.strptime(request.data.get("start_date"), "%d/%m/%Y")
                    if request.data.get("start_date")
                    else raiser("Start Date is required")
                )
                issue_date = (
                    datetime.strptime(request.data.get("issue_date"), "%d/%m/%Y")
                    if request.data.get("issue_date")
                    else raiser("Issue Date is required")
                )
                expiry_date = (
                    datetime.strptime(request.data.get("expiry_date"), "%d/%m/%Y")
                    if request.data.get("expiry_date")
                    else raiser("Expiry Date is required")
                )

                (
                    application_type,
                    app_type_created,
                ) = ApplicationType.objects.get_or_create(
                    name="E Class",
                    defaults={
                        "visible": False,
                        "max_renewals": 1,
                        "max_renewal_period": 5,
                    },
                )

                (
                    proposal,
                    proposal_created,
                ) = Proposal.objects.get_or_create(  # Dummy 'E Class' proposal
                    id=0,
                    defaults={
                        "application_type": application_type,
                        "submitter": request.user,
                        "schema": [],
                    },
                )

                approval = Approval.objects.create(
                    issue_date=issue_date,
                    expiry_date=expiry_date,
                    start_date=start_date,
                    org_applicant=org_applicant,
                    proxy_applicant=proxy_applicant,
                    current_proposal=proposal,
                )

                doc = ApprovalDocument.objects.create(approval=approval, _file=_file)
                approval.licence_document = doc
                approval.save()

                return Response({"approval": approval.lodgement_number})

        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
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
    def approval_extend(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = ApprovalExtendSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance.approval_extend(request, serializer.validated_data)
            serializer = ApprovalSerializer(instance, context={"request": request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
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
    def approval_cancellation(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = ApprovalCancellationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance.approval_cancellation(request, serializer.validated_data)
            serializer = ApprovalSerializer(instance, context={"request": request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
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
    def approval_suspension(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = ApprovalSuspensionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance.approval_suspension(request, serializer.validated_data)
            serializer = ApprovalSerializer(instance, context={"request": request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
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
    def approval_reinstate(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.reinstate_approval(request)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
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
    def approval_surrender(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = ApprovalSurrenderSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance.approval_surrender(request, serializer.validated_data)
            serializer = ApprovalSerializer(instance, context={"request": request})
            return Response(serializer.data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            if hasattr(e, "error_dict"):
                raise serializers.ValidationError(repr(e.error_dict))
            else:
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
    def action_log(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            qs = instance.action_logs.all()
            serializer = ApprovalUserActionSerializer(qs, many=True)
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
            serializer = ApprovalLogEntrySerializer(qs, many=True)
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
                request.data["approval"] = "{}".format(instance.id)
                request.data["staff"] = "{}".format(request.user.id)
                request.data._mutable = mutable
                serializer = ApprovalLogEntrySerializer(data=request.data)
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
