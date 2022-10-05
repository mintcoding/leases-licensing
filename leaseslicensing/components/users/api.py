import traceback
from django.db import transaction
from django.db.models import Q
from django.conf import settings
from django_countries import countries
from rest_framework import viewsets, serializers, status, generics, views
from rest_framework.decorators import action as detail_route, renderer_classes
from rest_framework.decorators import action as list_route
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from django.core.cache import cache
from ledger_api_client.ledger_models import (
    EmailUserRO as EmailUser,
    Address,
    EmailIdentity,
)  # EmailUserAction

from leaseslicensing.components.invoicing.models import ChargeMethod, RepetitionType
from leaseslicensing.components.invoicing.serializers import ChargeMethodSerializer, RepetitionTypeSerializer
# from leaseslicensing.components.main.utils import retrieve_department_users
from leaseslicensing.components.main.decorators import basic_exception_handler
from leaseslicensing.components.main.serializers import EmailUserSerializer
from leaseslicensing.components.users.serializers import (
    UserSerializer,
    UserFilterSerializer,
    UserAddressSerializer,
    PersonalSerializer,
    ContactSerializer,
    UserSystemSettingsSerializer,
)
from leaseslicensing.components.organisations.serializers import (
    OrganisationRequestDTSerializer,
)
from leaseslicensing.components.main.models import UserSystemSettings


#class DepartmentUserList(views.APIView):
#    renderer_classes = [
#        JSONRenderer,
#    ]
#
#    def get(self, request, format=None):
#        # data = cache.get('department_users')
#        # if not data:
#        #     retrieve_department_users()
#        #     data = cache.get('department_users')
#        data = retrieve_department_users()
#        return Response(data)


class GetChargeMethods(views.APIView):
    renderer_classes = [
        JSONRenderer,
    ]

    def get(self, request, format=None):
        charge_methods = ChargeMethod.objects.all()
        serializer = ChargeMethodSerializer(charge_methods, many=True)
        return Response(serializer.data)


class GetRepetitionTypes(views.APIView):
    renderer_classes = [
        JSONRenderer,
    ]

    def get(self, request, format=None):
        repetition_types = RepetitionType.objects.all()
        serializer = RepetitionTypeSerializer(repetition_types, many=True)
        return Response(serializer.data)


class GetCountries(views.APIView):
    renderer_classes = [
        JSONRenderer,
    ]

    def get(self, request, format=None):
        data = cache.get("country_list")
        if not data:
            country_list = []
            for country in list(countries):
                country_list.append({"name": country.name, "code": country.code})
            cache.set("country_list", country_list, settings.LOV_CACHE_TIMEOUT)
            data = cache.get("country_list")
        return Response(data)


class GetProfile(views.APIView):
    renderer_classes = [
        JSONRenderer,
    ]

    def get(self, request, format=None):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data)


from rest_framework import filters


class UserListFilterView(generics.ListAPIView):
    """https://cop-internal.dbca.wa.gov.au/api/filtered_users?search=russell"""

    queryset = EmailUser.objects.all()
    serializer_class = UserFilterSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("email", "first_name", "last_name")


class UserViewSet(viewsets.ModelViewSet):
    queryset = EmailUser.objects.all()
    serializer_class = UserSerializer

    @basic_exception_handler
    def list(self, request, *args, **kwargs):
        search_term = request.GET.get('term', '')
        queryset = self.queryset.filter(Q(first_name__icontains=search_term) | Q(last_name__icontains=search_term))[:10]
        data_transform = EmailUserSerializer(queryset, many=True)
        return Response(data_transform.data)

    @list_route(methods=['GET',], detail=False)
    @basic_exception_handler
    def get_department_users(self, request, *args, **kwargs):
        search_term = request.GET.get('term', '')
        data = EmailUser.objects.filter(is_staff=True). \
            filter(Q(first_name__icontains=search_term) | Q(last_name__icontains=search_term)). \
            values('email', 'first_name', 'last_name')[:10]
        data_transform = [{'id': person['email'], 'text': person['first_name'] + ' ' + person['last_name']} for person in data]
        return Response({"results": data_transform})

    @detail_route(methods=["POST",], detail=True,)
    @basic_exception_handler
    def update_personal(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PersonalSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        serializer = UserSerializer(instance)
        return Response(serializer.data)

    @detail_route(methods=["POST",], detail=True,)
    @basic_exception_handler
    def update_contact(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ContactSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        serializer = UserSerializer(instance)
        return Response(serializer.data)

    @detail_route(methods=["POST",], detail=True,)
    @basic_exception_handler
    def update_address(self, request, *args, **kwargs):
        instance = self.get_object()
        # residential address
        residential_serializer = UserAddressSerializer(
            data=request.data.get("residential_address")
        )
        residential_serializer.is_valid(raise_exception=True)
        residential_address, created = Address.objects.get_or_create(
            line1=residential_serializer.validated_data["line1"],
            locality=residential_serializer.validated_data["locality"],
            state=residential_serializer.validated_data["state"],
            country=residential_serializer.validated_data["country"],
            postcode=residential_serializer.validated_data["postcode"],
            user=instance,
        )
        instance.residential_address = residential_address
        # postal address
        postal_address_data = request.data.get("postal_address")
        if request.data.get("postal_same_as_residential"):
            instance.postal_same_as_residential = True
            instance.postal_address = residential_address
        elif postal_address_data:
            postal_serializer = UserAddressSerializer(data=postal_address_data)
            postal_serializer.is_valid(raise_exception=True)
            postal_address, created = Address.objects.get_or_create(
                line1=postal_serializer.validated_data["line1"],
                locality=postal_serializer.validated_data["locality"],
                state=postal_serializer.validated_data["state"],
                country=postal_serializer.validated_data["country"],
                postcode=postal_serializer.validated_data["postcode"],
                user=instance,
            )
            instance.postal_address = postal_address
            instance.postal_same_as_residential = False

        instance.save()
        serializer = UserSerializer(instance)
        return Response(serializer.data)

    @detail_route(methods=["POST",], detail=True,)
    @basic_exception_handler
    def update_system_settings(self, request, *args, **kwargs):
        instance = self.get_object()
        # serializer = UserSystemSettingsSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        user_setting, created = UserSystemSettings.objects.get_or_create(
            user=instance
        )
        serializer = UserSystemSettingsSerializer(user_setting, data=request.data)
        serializer.is_valid(raise_exception=True)
        # instance.residential_address = address
        serializer.save()
        instance = self.get_object()
        serializer = UserSerializer(instance)
        return Response(serializer.data)

    @detail_route(methods=["POST",], detail=True,)
    @basic_exception_handler
    def upload_id(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.upload_identification(request)
        with transaction.atomic():
            instance.save()
            instance.log_user_action(
                EmailUserAction.ACTION_ID_UPDATE.format(
                    "{} {} ({})".format(
                        instance.first_name, instance.last_name, instance.email
                    )
                ),
                request,
            )
        serializer = UserSerializer(instance, partial=True)
        return Response(serializer.data)

    @detail_route(methods=["GET",], detail=True,)
    @basic_exception_handler
    def pending_org_requests(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = OrganisationRequestDTSerializer(
            instance.organisationrequest_set.filter(status="with_assessor"),
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)

    @detail_route(methods=["GET",], detail=True,)
    @basic_exception_handler
    def action_log(self, request, *args, **kwargs):
        instance = self.get_object()
        qs = instance.action_logs.all()
        serializer = EmailUserActionSerializer(qs, many=True)
        return Response(serializer.data)

    @detail_route(methods=["GET",], detail=True,)
    @basic_exception_handler
    def comms_log(self, request, *args, **kwargs):
        instance = self.get_object()
        qs = instance.comms_logs.all()
        serializer = EmailUserCommsSerializer(qs, many=True)
        return Response(serializer.data)

    @detail_route(methods=["POST",], detail=True,)
    @renderer_classes((JSONRenderer,))
    @basic_exception_handler
    def add_comms_log(self, request, *args, **kwargs):
        with transaction.atomic():
            instance = self.get_object()
            mutable = request.data._mutable
            request.data._mutable = True
            request.data["emailuser"] = "{}".format(instance.id)
            request.data["staff"] = "{}".format(request.user.id)
            request.data._mutable = mutable
            serializer = EmailUserLogEntrySerializer(data=request.data)
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
