"""
Settings for Notification App are all namespaced in the APP_NOTIFICATION setting.
For example your project's `settings.py` file might look like this:

APP_NOTIFICATION = {
    'DEFAULT_PUSHER_CLASS':  'app.notification.pusher.FakePusher',
}

This module provides the `app_setting` object, that is used to access
App settings, checking for user settings first, then falling
back to the defaults.
"""
from __future__ import unicode_literals

import importlib
from typing import Set

import six
from django.conf import settings


def perform_import(val, setting_name):
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.
    """
    if val is None:
        return None
    elif isinstance(val, six.string_types):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    return val


def import_from_string(val, setting_name):
    """
    Attempt to import a class from a string representation.
    """
    try:
        parts = val.split(".")
        module_path, class_name = ".".join(parts[:-1]), parts[-1]
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except ImportError as e:
        msg = "Could not import '%s' for setting '%s': %s: %s." % (
            val,
            setting_name,
            e.__class__.__name__,
            e,
        )
        raise ImportError(msg)


class APPSettings(object):
    """
    A settings object, that allows API settings to be accessed as properties.
    For example:

        from app.notification.settings import app_settings
        print(app_settings.DEFAULT_PUSHER_CLASS)

    Any setting with string import paths will be automatically resolved
    and return the class, rather than the string literal.
    """

    def __init__(
        self,
        app_namespace: str,
        user_settings=None,
        defaults=None,
        import_strings=None,
    ):
        self._app_namespace = app_namespace
        if user_settings:
            self._user_settings = user_settings
        self.defaults = defaults or {}
        self.import_strings = import_strings or {}
        self._cached_attrs = set()  # type: Set[str]

    @property
    def user_settings(self):
        if not hasattr(self, "_user_settings"):
            self._user_settings = getattr(settings, self._app_namespace, {})
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid API setting: '%s'" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Coerce import strings into classes
        if attr in self.import_strings:
            val = perform_import(val, attr)

        # Cache the result
        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    def reload(self):
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        if hasattr(self, "_user_settings"):
            delattr(self, "_user_settings")
