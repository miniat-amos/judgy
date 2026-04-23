from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decouple import config

User = get_user_model()

class Command(BaseCommand):
    help = "Creates initial superuser if it does not exist"

    def handle(self, *args, **options):
        email = config('SUPER_USER_EMAIL')

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "first_name": config('SUPER_USER_FIRST_NAME'),
                "last_name": config('SUPER_USER_LAST_NAME'),
                "is_staff": True,
                "is_superuser": True,
                "is_verified": True
            }
        )

        if created:
            password = config('SUPER_USER_PASSWORD')
            user.set_password(password)
            user.save()

            self.stdout.write(self.style.SUCCESS(f"Superuser created: {email}"))

        else:
            self.stdout.write(self.style.WARNING(f"Superuser already exists: {email}"))