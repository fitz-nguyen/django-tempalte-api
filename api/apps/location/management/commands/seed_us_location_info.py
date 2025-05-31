import json

from django.core.management.base import BaseCommand
from django.db import connection

from apps.location.choices import MAPPER_STATE_ABBR_SHORT_TO_LONG
from apps.location.models import USLocationInfo


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Load JSON file
        data_create = []
        with open("apps/location/management/commands/us_location_info.json", "r") as file:
            data = json.load(file)

        # Insert data into the database
        for item in data:
            data_create.append(
                USLocationInfo(
                    state=MAPPER_STATE_ABBR_SHORT_TO_LONG.get(item["state"]),
                    state_abbr=item["state"],
                    city=item["city"],
                    county=item["county"],
                    zipcode=item["zipcode"],
                    zipcode_type=item["zipcode_type"],
                )
            )
        USLocationInfo.objects.bulk_create(data_create)
