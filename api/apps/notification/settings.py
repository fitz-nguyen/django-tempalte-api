"""
Settings for Notification App are all namespaced in the APP_NOTIFICATION setting.
For example your project's `settings.py` file might look like this:

APP_NOTIFICATION = {
    'DEFAULT_PUSHER_CLASS': 'app.notification.pushers.FakePusher',
}

This module provides the `api_setting` object, that is used to access
App Notification settings, checking for user settings first, then falling
back to the defaults.
"""
from __future__ import unicode_literals

from django.test.signals import setting_changed

from apps.core.settings import APPSettings

APP_NAMESPACE = "APP_NOTIFICATION"

DEFAULTS = {
    "DEFAULT_PUSHER_CLASS": "app.notification.pushers.FakePusher",
}


# List of settings that may be in string import notation.
IMPORT_STRINGS = ("DEFAULT_PUSHER_CLASS",)


app_settings = APPSettings(APP_NAMESPACE, None, DEFAULTS, IMPORT_STRINGS)


def reload_app_settings(*args, **kwargs):
    setting = kwargs["setting"]
    if setting == APP_NAMESPACE:
        app_settings.reload()


setting_changed.connect(reload_app_settings)
