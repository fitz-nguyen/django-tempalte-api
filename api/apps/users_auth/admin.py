from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group
from rest_framework.authtoken.admin import TokenAdmin
from rest_framework.authtoken.models import TokenProxy

from apps.core.admin import SystemAdmin


class CustomTokenAdmin(SystemAdmin, TokenAdmin):
    pass


class CustomGroupAdmin(SystemAdmin, GroupAdmin):
    pass


# Unregister the default TokenProxy admin
admin.site.unregister(TokenProxy)
# Register our custom admin
admin.site.register(TokenProxy, CustomTokenAdmin)

# Unregister the default Group admin
admin.site.unregister(Group)
# Register our custom Group admin
admin.site.register(Group, CustomGroupAdmin)
