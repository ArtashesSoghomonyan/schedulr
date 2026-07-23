from django.core.management import BaseCommand
from faker import Faker

from users.models import CostumerProfile, ProviderProfile, User

fake = Faker()

class Command(BaseCommand):
    help = "Seeds the database with dummy users for development/testing"

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=20)

    def handle(self, *args, **options):
        for _ in range(options["count"]):
            user_type = fake.random_element([User.UserType.COSTUMER, User.UserType.PROVIDER])
            user = User.objects.create_user(
                email=fake.unique.email(),
                username=fake.unique.user_name(),
                password="testpass123",
                user_type=user_type,
                is_verified=fake.boolean(chance_of_getting_true=80),
            )
            profile_model = (
                ProviderProfile if user_type == User.UserType.PROVIDER
                else CostumerProfile
            )
            profile_model.objects.create(user=user, **self._profile_data(user_type))
            self.stdout.write(f"  Created {user}")

        self.stdout.write(self.style.SUCCESS(f"Done. {options['count']} users created."))

    def _profile_data(self, user_type):
        if user_type == User.UserType.PROVIDER:
            return {"business_name": fake.company(), "description": fake.text(200)}
        return {"first_name": fake.first_name(), "last_name": fake.last_name()}
