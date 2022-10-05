from django.contrib import admin
from django.forms import ModelForm
from django.contrib.admin import site as admin_site
from django.contrib.admin.widgets import ForeignKeyRawIdWidget #RelatedFieldWidgetWrapper
from leaseslicensing.components.main.models import (
    MapLayer, MapColumn, SecurityGroup, SecurityGroupMembership,
)
from ledger_api_client.ledger_models import EmailUserRO as EmailUser


class MyForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(MyForm, self).__init__(*args, **kwargs)
        self.fields["layer_name"].help_text = (
            "Enter the layer name defined in geoserver (<a href='https://kmi.dpaw.wa.gov.au/geoserver/' target='_blank'>GeoServer</a>)<br />"
            "<div>Example:</div><span style='padding:1em;'>public:dbca_legislated_lands_and_waters</span>"
        )
        self.fields[
            "display_all_columns"
        ].help_text = "When checked, display all the attributes(columns) in the table regardless of the configurations below"
        self.fields[
            "option_for_internal"
        ].help_text = (
            "When checked, a checkbox for this layer is displayed for the internal user"
        )
        self.fields[
            "option_for_external"
        ].help_text = (
            "When checked, a checkbox for this layer is displayed for the external user"
        )


class MapColumnInline(admin.TabularInline):
    model = MapColumn
    extra = 0


@admin.register(MapLayer)
class MapLayerAdmin(admin.ModelAdmin):
    list_display = [
        "display_name",
        "layer_name",
        "option_for_internal",
        "option_for_external",
        "display_all_columns",
        "column_names",
        "transparency",
    ]
    list_filter = [
        "option_for_internal",
        "option_for_external",
        "display_all_columns",
    ]
    form = MyForm
    inlines = [
        MapColumnInline,
    ]


# Not ready for use
class SecurityGroupFormTemplate(ModelForm):

    class Meta:
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            #print(self.fields)
            self.fields['name'].disabled = True
         #   self.fields['name'].widget.can_add_related=False
          #  self.fields['name'].widget.can_change_related=False
           # self.fields['name'].widget.can_delete_related=False


# Not ready for use
class SecurityGroupMembershipFormTemplate(ModelForm):

    class Meta:
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            if self.fields['emailuser']:
                self.fields['emailuser'].widget = (
                    ForeignKeyRawIdWidget(
                        #self.fields['emailuser'].widget,
                        self.instance._meta.get_field('emailuser'),
                        admin_site,
                        )
                    )
            #if self.fields['group']:
                #print(self.fields['group'].__dict__)


# Not ready for use
def SecurityGroupTemplate(model_instance):
    class SecurityGroupMembershipInline(admin.TabularInline):
        model = SecurityGroupMembership
        extra = 0
        #raw_id_fields = ('emailuser',)
        model_instance = None
        verbose_name = "Group member"
        verbose_name_plural = "Group members"
        form = SecurityGroupMembershipFormTemplate

        def __init__(self, *args, **kwargs):
            super(SecurityGroupMembershipInline, self).__init__(*args, **kwargs)
            self.model_instance = model_instance

        #def emailuser(self, obj):
        #    print(self)
        #    print(obj)

        #def formfield_for_foreignkey(self, db_field, request, **kwargs):
        #    if self.model_instance.name == settings.GROUP_COMPLIANCE_MANAGEMENT_APPROVED_EXTERNAL_USER and db_field.name == "emailuser":
        #        print("external")
        #        print(EmailUser.objects.filter(is_staff=False).count())
        #        kwargs["queryset"] = EmailUser.objects.filter(is_staff=False)
        #    elif db_field.name == "emailuser":
        #        print("internal")
        #        print(EmailUser.objects.filter(is_staff=True).count())
        #        kwargs["queryset"] = EmailUser.objects.filter(is_staff=True)
        #    return super(ComplianceManagementSystemGroupPermissionInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

        #def formfield_for_foreignkey(self, db_field, request, **kwargs):
        #    print(db_field.name)
        #    if db_field.name == "group":
        #        print(EmailUser.objects.filter(is_staff=True).count())
        #        kwargs["queryset"] = EmailUser.objects.filter(is_staff=True)
        #    return super(SecurityGroupMembershipInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

    return SecurityGroupMembershipInline


# Not ready for use
@admin.register(SecurityGroup)
class SecurityGroupAdmin(admin.ModelAdmin):
    list_display = ('id','name',)
    #inlines = [ComplianceManagementPermissionTemplate(self)]
    #inlines = [ComplianceManagementAdminTemplate("what what")]
    #form = ComplianceManagementGroupAdminFormTemplate
    form = SecurityGroupFormTemplate

    def get_inline_instances(self, request, obj=None):
        return [
            SecurityGroupTemplate(obj)(self.model, self.admin_site),
        ]

    #def formfield_for_foreignkey(self, db_field, request, **kwargs):
     #   print(db_field.name)
        
     #   print(
      #  if db_field.name == "emailuser":
       #     kwargs["queryset"] = EmailUser.objects.filter(is_staff=True)
    #        kwargs["required"] = False
    #    if db_field.name == "region":
    #        kwargs["required"] = False
    #    return super(ComplianceManagementSystemGroupAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    #def has_change_permission(self, request, obj=None):
     #   return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        return None


