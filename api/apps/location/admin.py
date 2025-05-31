from django.contrib import admin

from apps.location.models import USLocationInfo


@admin.register(USLocationInfo)
class USLocationInfoAdmin(admin.ModelAdmin):
    list_display = (
        "state",
        "state_abbr",
        "city",
        "county",
        "zipcode",
    )
    readonly_fields = ("created", "modified")
    search_fields = (
        "state",
        "zipcode",
        "city",
        "county",
    )
    fieldsets = (
        (None, {"fields": ("state", "state_abbr", "city", "county", "zipcode", "zipcode_type")}),
        (
            "System Fields",
            {
                "fields": ("created", "modified"),
                "classes": ("collapse",),
            },
        ),
    )
