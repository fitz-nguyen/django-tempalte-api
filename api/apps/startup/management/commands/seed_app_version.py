from django.core.management.base import BaseCommand

from apps.startup.models import AppVersion, Message


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print("================START ADD APP VERSION=================")
        AppVersion.objects.create(minimal_version="1.0.0", current_version="1.0.0")
        Message.objects.create(title="Update alert", message="You need to update app before use.")
        print("================DONE=================")
