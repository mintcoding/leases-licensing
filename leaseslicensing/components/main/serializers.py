from rest_framework import serializers
from django.db.models import Sum, Max
from leaseslicensing.components.main.models import (
    CommunicationsLogEntry,
    RequiredDocument,
    Question,
    GlobalSettings,
    ApplicationType,
    MapLayer,
    MapColumn, TemporaryDocumentCollection,
)
from ledger_api_client.ledger_models import EmailUserRO as EmailUser, EmailUserRO
from datetime import datetime, date

# from leaseslicensing.components.proposals.serializers import ProposalTypeSerializer


class CommunicationLogEntrySerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(
        queryset=EmailUser.objects.all(), required=False
    )
    documents = serializers.SerializerMethodField()

    class Meta:
        model = CommunicationsLogEntry
        fields = (
            "id",
            "customer",
            "to",
            "fromm",
            "cc",
            "type",
            "reference",
            "subject" "text",
            "created",
            "staff",
            "proposal",
            "documents",
        )

    def get_documents(self, obj):
        return [[d.name, d._file.url] for d in obj.documents.all()]


class ApplicationTypeSerializer(serializers.ModelSerializer):
    name_display = serializers.SerializerMethodField()
    confirmation_text = serializers.SerializerMethodField()
    # regions = RegionSerializer(many=True)
    # activity_app_types = ActivitySerializer(many=True)
    # tenure_app_types = TenureSerializer(many=True)

    class Meta:
        model = ApplicationType
        # fields = ('id', 'name', 'activity_app_types', 'tenure_app_types')
        # fields = ('id', 'name', 'tenure_app_types')
        fields = "__all__"
        extra_fields = ["name_display", "confirmation_text"]

    def get_name_display(self, obj):
        return obj.name_display

    def get_confirmation_text(self, obj):
        return obj.confirmation_text


class GlobalSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalSettings
        fields = ("key", "value")


class RequiredDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequiredDocument
        fields = ("id", "park", "activity", "question")


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = (
            "id",
            "question_text",
            "answer_one",
            "answer_two",
            "answer_three",
            "answer_four",
            "correct_answer",
            "correct_answer_value",
        )


class BookingSettlementReportSerializer(serializers.Serializer):
    date = serializers.DateTimeField(input_formats=["%d/%m/%Y"])


class OracleSerializer(serializers.Serializer):
    date = serializers.DateField(input_formats=["%d/%m/%Y", "%Y-%m-%d"])
    override = serializers.BooleanField(default=False)


class MapColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = MapColumn
        fields = (
            "name",
            "option_for_internal",
            "option_for_external",
        )


class MapLayerSerializer(serializers.ModelSerializer):
    layer_full_name = serializers.SerializerMethodField()
    layer_group_name = serializers.SerializerMethodField()
    layer_name = serializers.SerializerMethodField()
    columns = MapColumnSerializer(many=True)

    class Meta:
        model = MapLayer
        fields = (
            "id",
            "display_name",
            "layer_full_name",
            "layer_group_name",
            "layer_name",
            "display_all_columns",
            "columns",
            "transparency",
        )
        read_only_fields = ("id",)

    def get_layer_full_name(self, obj):
        return obj.layer_name.strip()

    def get_layer_group_name(self, obj):
        return obj.layer_name.strip().split(":")[0]

    def get_layer_name(self, obj):
        return obj.layer_name.strip().split(":")[1]


class EmailUserROSerializerForReferral(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    telephone = serializers.CharField(source="phone_number")
    mobile_phone = serializers.CharField(source="mobile_number")

    class Meta:
        model = EmailUserRO
        fields = (
            "id",
            "name",
            "title",
            "email",
            "telephone",
            "mobile_phone",
        )

    def get_name(self, user):
        return user.get_full_name()


class EmailUserSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()
    # text = serializers.SerializerMethodField()

    class Meta:
        model = EmailUser
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "title",
            "organisation",
            "fullname",
            # "text",
        )

    def get_fullname(self, obj):
        return "{} {}".format(obj.first_name, obj.last_name)

    def get_text(self, obj):
        return self.get_fullname(obj)


class TemporaryDocumentCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemporaryDocumentCollection
        fields = ('id',)
