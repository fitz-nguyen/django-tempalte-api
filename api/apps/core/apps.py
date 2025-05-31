from django.apps import AppConfig
from health_check.plugins import plugin_dir


class CoreConfig(AppConfig):
    name = "apps.core"

    def ready(self):
        from apps.core.health_check import CheckCeleryResult

        plugin_dir.register(CheckCeleryResult)
