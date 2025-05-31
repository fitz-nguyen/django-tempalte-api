from django.contrib import admin
from django.contrib.sites.admin import SiteAdmin
from django.contrib.sites.models import Site


class StaffAdmin(admin.ModelAdmin):
    def has_view_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_module_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return True


class SystemAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        if request.user.is_systemuser:
            return True
        return False


class StaffReadOnlyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return True if request.user.is_superuser else False

    def has_change_permission(self, request, obj=None):
        return True if request.user.is_superuser else False

    def has_delete_permission(self, request, obj=None):
        return True if request.user.is_superuser else False

    def has_module_permission(self, request):
        return True


class CustomSiteAdmin(SystemAdmin, SiteAdmin):
    pass


admin.site.unregister(Site)
admin.site.register(Site, CustomSiteAdmin)
