from django.contrib import admin

from apps.core.admin import SystemAdmin
from apps.devices.models import DeviceInfo, UserDevice


@admin.register(DeviceInfo)
class DeviceInfoAdmin(SystemAdmin):
    list_display = (
        "device_id",
        "platform",
        "platform_version",
    )
    search_fields = ("device_id",)


@admin.register(UserDevice)
class UserDeviceAdmin(SystemAdmin):
    list_display = (
        "user",
        "device",
        "in_use",
    )
    search_fields = (
        "user__username",
        "device__device_id",
    )
