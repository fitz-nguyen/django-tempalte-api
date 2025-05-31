"""
Settings for Notification App are all namespaced in the APP_USERS setting.
For example your project's `settings.py` file might look like this:

APP_USERS = {
     "THUMBNAIL_FILE_HEIGHT": 300,
    "THUMBNAIL_FILE_WIDTH": 300,
}

This module provides the `api_setting` object, that is used to access
App Notification settings, checking for user settings first, then falling
back to the defaults.
"""
from __future__ import unicode_literals

from django.test.signals import setting_changed

from apps.core.settings import APPSettings

APP_NAMESPACE = "APP_USERS"

DEFAULTS = {
    "THUMBNAIL_FILE_HEIGHT": 300,
    "THUMBNAIL_FILE_WIDTH": 300,
}


# List of settings that may be in string import notation.
IMPORT_STRINGS = ()


app_settings = APPSettings(APP_NAMESPACE, None, DEFAULTS, IMPORT_STRINGS)


def reload_app_settings(*args, **kwargs):
    setting = kwargs["setting"]
    if setting == APP_NAMESPACE:
        app_settings.reload()


setting_changed.connect(reload_app_settings)
