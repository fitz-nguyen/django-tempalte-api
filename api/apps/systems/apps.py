from django.apps import AppConfig


class SystemsConfig(AppConfig):
    name = "apps.systems"

    def ready(self):
        from apps.systems import receivers  # noqa
