from django.core.management.base import BaseCommand
from faker import Faker

from apps.users.models import User


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("user_number", type=int, help="Generate number of fake users.")

    def handle(self, *args, **options):
        if options["user_number"]:
            if int(options["user_number"] <= 0):
                self.stdout.write(self.style.NOTICE("User number must be from 1."))
                return

            fake = Faker()

            for index in range(int(options["user_number"])):
                User.objects.create_user(
                    username=fake.profile(fields=["username"])["username"],
                    email=fake.email(),
                    password=fake.password(),
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    bio=fake.text(),
                    display_name=fake.name(),
                    phone=fake.phone_number(),
                    is_demo_account=False,
                )
