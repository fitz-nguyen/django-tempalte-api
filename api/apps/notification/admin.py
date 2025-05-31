from django.contrib import admin
from fcm_django.admin import DeviceAdmin
from fcm_django.models import FCMDevice

from apps.core.admin import SystemAdmin
from apps.notification.models import Message


@admin.register(Message)
class MessageAdmin(SystemAdmin):
    list_display = (
        "created",
        "user",
        "verb",
        "title",
        "content",
        "status",
        "sent_date",
    )
    search_fields = (
        "user__username",
        "verb",
    )
    raw_id_fields = (
        "user",
        "actor",
    )
    ordering = ("-created",)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "user",
            )
        )


class FCMDeviceAdmin(DeviceAdmin):
    def has_module_permission(self, request):
        if request.user.is_systemuser:
            return True
        return False


admin.site.unregister(FCMDevice)
admin.site.register(FCMDevice, FCMDeviceAdmin)
