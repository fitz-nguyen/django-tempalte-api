from django.contrib import admin

from apps.core.admin import SystemAdmin
from apps.startup.models import AppVersion, Message


@admin.register(AppVersion)
class AppVersionAdmin(admin.ModelAdmin):
    list_display = (
        "minimal_version",
        "current_version",
        "platform",
        "created",
        "modified",
    )
    search_fields = (
        "minimal_version",
        "current_version",
    )


@admin.register(Message)
class MessageAdmin(SystemAdmin):
    list_display = (
        "id",
        "title",
        "message",
        "icon",
        "background",
        "created",
        "modified",
    )
    search_fields = (
        "title",
        "message",
    )
