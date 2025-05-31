#
from apps.systems.models import (
    HirePredictionConfig,
    HomeSizeConfig,
    NotInterestedReasonConfig,
    PageConfig,
    RoofMaterialConfig,
    SaleStatusConfig,
    StormDamageConfig,
    SystemConfig,
)
from apps.systems.utils import SystemConfigCache
from django import forms
from django.contrib import admin
from django.contrib.admin.models import DELETION, LogEntry
from django.shortcuts import redirect
from django.urls import NoReverseMatch, reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django_celery_results.admin import GroupResultAdmin, TaskResultAdmin
from django_celery_results.models import GroupResult, TaskResult
from rest_framework.authtoken.models import Token

from apps.core.admin import SystemAdmin
from apps.core.redis import get_redis
from apps.users import choices


# Base admin class to clear cache on model changes
class SystemConfigBaseAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        result = super().save_model(request, obj, form, change)
        # Clear both caches
        SystemConfigCache().delete_cache()
        return result

    def delete_model(self, request, obj):
        result = super().delete_model(request, obj)
        # Clear both caches
        SystemConfigCache().delete_cache()
        return result

    def delete_queryset(self, request, queryset):
        result = super().delete_queryset(request, queryset)
        # Clear both caches
        SystemConfigCache().delete_cache()
        return result


@admin.register(PageConfig)
class PageCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "type", "published", "created", "modified")
    readonly_fields = ("created", "modified")
    fieldsets = (
        (None, {"fields": ("title", "type", "content", "published")}),
        (
            "System Fields",
            {
                "fields": ("created", "modified"),
                "classes": ("collapse",),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        if obj.published:
            PageConfig.objects.filter(type=obj.type).exclude(id=obj.id).update(published=False)
        return super().save_model(request, obj, form, change)


@admin.register(LogEntry)
class LogEntryAdmin(SystemAdmin):
    date_hierarchy = "action_time"
    readonly_fields = ("action_time",)
    list_filter = ("content_type",)
    search_fields = (
        "object_repr",
        "change_message",
    )
    list_display = ("__str__", "user", "object_repr", "action_flag", "change_message", "action_time", "object_link")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True

    def object_link(self, obj):
        if obj.action_flag == DELETION:
            link = obj.object_repr
        else:
            ct = obj.content_type
            try:
                link = mark_safe(
                    '<a href="%s">%s</a>'
                    % (
                        reverse("admin:%s_%s_change" % (ct.app_label, ct.model), args=[obj.object_id]),
                        escape(obj.object_repr),
                    )
                )
            except NoReverseMatch:
                link = obj.object_repr
        return link

    object_link.admin_order_field = "object_repr"  # type:ignore
    object_link.short_description = "object"  # type:ignore


class SystemConfigAdminForm(forms.ModelForm):
    export_building_permit_count_limit = forms.IntegerField(
        label="Building Permits Export Limit",
        help_text="Maximum limit: 10,000,000 building permits.",
        min_value=1,
        max_value=10000000,  # Set the maximum value to 10 million
        error_messages={"max_value": "Ensure this value is less than or equal to 10,000,000."},
    )

    customer_lead_import_limit = forms.IntegerField(
        label="Customer Lead Import Limit", help_text="Maximum number of leads a customer can import."
    )
    customer_max_lead_file_size = forms.IntegerField(
        label="Customer Max Lead File Size", help_text="Maximum file size (in bytes) for lead import by a customer."
    )
    csv_map_generation_duration = forms.IntegerField(
        label="CSV Map Generation Duration", help_text="Time duration (in seconds) for generating a lead CSV file"
    )
    reach_valid_distance = forms.IntegerField(
        label="Reach Valid Distance",
        help_text="Maximum distance (in feet) allowed for validating a reach. Set to 0 to disable validation.",
        min_value=0,
        max_value=1000000,
        error_messages={
            "min_value": "Ensure this value is greater than or equal to 0.",
            "max_value": "Ensure this value is less than or equal to 1,000,000.",
        },
    )
    visit_valid_distance = forms.IntegerField(
        label="Visit Valid Distance",
        help_text="Maximum distance (in feet) allowed for validating a visit. Set to 0 to disable validation.",
        min_value=0,
        max_value=1000000,
        error_messages={
            "min_value": "Ensure this value is greater than or equal to 0.",
            "max_value": "Ensure this value is less than or equal to 1,000,000.",
        },
    )

    import_chunk_size = forms.IntegerField(
        label="Building Permits Import Chunk Size",
        help_text="Number of records per chunk file for building permits import to optimize performance.",
        min_value=1,
        max_value=1000000,
        error_messages={"max_value": "Ensure this value is less than or equal to 1,000,000."},
    )

    class Meta:
        model = SystemConfig
        fields = "__all__"


@admin.register(SystemConfig)
class SystemConfigAdmin(SystemConfigBaseAdmin):
    form = SystemConfigAdminForm
    readonly_fields = ("created", "modified")
    fieldsets = (
        (
            "Data Import & File Config",
            {
                "fields": (
                    "export_building_permit_count_limit",
                    "import_chunk_size",
                    "customer_lead_import_limit",
                    "customer_max_lead_file_size",
                    "csv_example_file",
                )
            },
        ),
        (
            "Validation Settings",
            {
                "fields": (
                    "csv_map_generation_duration",
                    "reach_valid_distance",
                    "visit_valid_distance",
                )
            },
        ),
        (
            "App Settings",
            {
                "fields": (
                    "email_footer_url",
                    "facebook_page_url",
                    "instagram_page_url",
                    "x_page_url",
                )
            },
        ),
        (
            "System Fields",
            {
                "fields": ("created", "modified"),
                "classes": ("collapse",),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        result = super().save_model(request, obj, form, change)
        # Clear both caches
        client = get_redis(db=0)
        SystemConfigCache().delete_cache()
        cache_key = "system_config_cache"
        client.delete(cache_key)
        return result

    def changelist_view(self, request, extra_context=None):
        if SystemConfig.objects.count() == 1:
            obj = SystemConfig.objects.first()
            return redirect("admin:systems_systemconfig_change", obj.id)
        return super().changelist_view(request, extra_context=extra_context)


class HirePredictionConfigForm(forms.ModelForm):
    key = forms.CharField(label="Title")

    class Meta:
        model = HirePredictionConfig
        fields = "__all__"


@admin.register(HirePredictionConfig)
class HirePredictionConfigAdmin(SystemConfigBaseAdmin):
    form = HirePredictionConfigForm
    list_display = ("get_key", "value", "hex_color", "order", "created", "modified")
    readonly_fields = ("created", "modified")
    fieldsets = (
        (None, {"fields": ("key", "value", "hex_color", "icon_url", "order")}),
        (
            "System Fields",
            {
                "fields": ("created", "modified"),
                "classes": ("collapse",),
            },
        ),
    )
    ordering = ("order",)

    def get_key(self, obj):
        return obj.key

    get_key.short_description = "Title"


class RoofMaterialConfigForm(forms.ModelForm):
    key = forms.CharField(label="Title")

    class Meta:
        model = RoofMaterialConfig
        fields = "__all__"


@admin.register(RoofMaterialConfig)
class RoofMaterialConfigAdmin(SystemConfigBaseAdmin):
    form = RoofMaterialConfigForm
    list_display = ("get_key", "value", "order", "created", "modified")
    readonly_fields = ("created", "modified")
    fieldsets = (
        (None, {"fields": ("key", "value", "order")}),
        (
            "System Fields",
            {
                "fields": ("created", "modified"),
                "classes": ("collapse",),
            },
        ),
    )
    ordering = ("order",)

    def get_key(self, obj):
        return obj.key

    get_key.short_description = "Title"


class SaleStatusConfigForm(forms.ModelForm):
    key = forms.CharField(label="Title")

    class Meta:
        model = SaleStatusConfig
        fields = "__all__"


@admin.register(SaleStatusConfig)
class SaleStatusConfigAdmin(SystemConfigBaseAdmin):
    form = SaleStatusConfigForm
    list_display = ("get_key", "value", "hex_color", "order", "created", "modified")
    readonly_fields = ("created", "modified")
    fieldsets = (
        (None, {"fields": ("key", "value", "hex_color", "order")}),
        (
            "System Fields",
            {
                "fields": ("created", "modified"),
                "classes": ("collapse",),
            },
        ),
    )
    ordering = ("order",)

    def get_key(self, obj):
        return obj.key

    get_key.short_description = "Title"


@admin.register(NotInterestedReasonConfig)
class NotInterestedReasonConfigAdmin(SystemConfigBaseAdmin):
    list_display = ("value", "order", "created", "modified")
    readonly_fields = ("created", "modified")
    fieldsets = (
        (None, {"fields": ("value", "order")}),
        (
            "System Fields",
            {
                "fields": ("created", "modified"),
                "classes": ("collapse",),
            },
        ),
    )
    ordering = ("order",)


class StormDamageConfigForm(forms.ModelForm):
    key = forms.CharField(label="Title")

    class Meta:
        model = StormDamageConfig
        fields = "__all__"


@admin.register(StormDamageConfig)
class StormDamageConfigAdmin(SystemConfigBaseAdmin):
    form = StormDamageConfigForm
    list_display = ("get_key", "unit_value", "unit", "order", "created", "modified")
    readonly_fields = ("created", "modified")
    fieldsets = (
        (None, {"fields": ("key", "value", "unit", "unit_value", "order")}),
        (
            "System Fields",
            {
                "fields": ("created", "modified"),
                "classes": ("collapse",),
            },
        ),
    )
    ordering = ("order",)

    def get_key(self, obj):
        return obj.key

    get_key.short_description = "Title"


class HomeSizeConfigForm(forms.ModelForm):
    key = forms.CharField(label="Title")

    class Meta:
        model = HomeSizeConfig
        fields = "__all__"


@admin.register(HomeSizeConfig)
class HomeSizeConfigAdmin(SystemConfigBaseAdmin):
    form = HomeSizeConfigForm
    list_display = ("get_key", "total_sqft_from", "total_sqft_to", "description", "order", "created", "modified")
    readonly_fields = ("created", "modified")
    fieldsets = (
        (None, {"fields": ("key", "value", "total_sqft_from", "total_sqft_to", "description", "order")}),
        (
            "System Fields",
            {
                "fields": ("created", "modified"),
                "classes": ("collapse",),
            },
        ),
    )
    ordering = ("order",)

    def get_key(self, obj):
        return obj.key

    get_key.short_description = "Title"


class CustomTaskResultAdmin(SystemAdmin, TaskResultAdmin):
    list_display = (
        "task_id",
        "periodic_task_name",
        "task_name",
        "task_args",
        "date_created",
        "date_done",
        "status",
        "worker",
    )


admin.site.unregister(TaskResult)
admin.site.register(TaskResult, CustomTaskResultAdmin)


class CustomGroupResultAdmin(SystemAdmin, GroupResultAdmin):
    pass


admin.site.unregister(GroupResult)
admin.site.register(GroupResult, CustomGroupResultAdmin)
