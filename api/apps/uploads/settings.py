"""
Settings for Uploads App are all namespaced in the APP_UPLOADS setting.
For example your project's `settings.py` file might look like this:

APP_UPLOADS = {
    'TIME_TO_DELETE_UPLOAD_FILE': 24,
}

This module provides the `api_setting` object, that is used to access
App Uploads settings, checking for user settings first, then falling
back to the defaults.
"""
from __future__ import unicode_literals

from apps.core.settings import APPSettings
from django.test.signals import setting_changed

APP_NAMESPACE = "APP_UPLOADS"

DEFAULTS = {
    "TIME_TO_DELETE_UPLOAD_FILE": 24,
    "THUMBNAIL_FILE_HEIGHT": 300,
    "THUMBNAIL_FILE_WIDTH": 300,
    "UPLOAD_CLASS": "app.uploads.services.storage.aws.AWSStorage",
}


# List of settings that may be in string import notation.
IMPORT_STRINGS = ("UPLOAD_CLASS",)


app_settings = APPSettings(APP_NAMESPACE, None, DEFAULTS, IMPORT_STRINGS)


def reload_app_settings(*args, **kwargs):
    setting = kwargs["setting"]
    if setting == APP_NAMESPACE:
        app_settings.reload()


setting_changed.connect(reload_app_settings)
