import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Create an admin user if missing. Set DJANGO_SUPERUSER_PASSWORD in the "
        "environment (avoids interactive password prompts that often mismatch in PowerShell)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            default=os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin"),
        )
        parser.add_argument(
            "--email",
            default=os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@localhost"),
        )

    def handle(self, *args, **options):
        User = get_user_model()
        username = options["username"]
        email = options["email"]
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        if not password:
            self.stderr.write(
                "Set DJANGO_SUPERUSER_PASSWORD first, e.g. in PowerShell:\n"
                '  $env:DJANGO_SUPERUSER_PASSWORD="YourPassword"\n'
                "  python manage.py bootstrap_superuser\n"
            )
            return
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"User '{username}' already exists."))
            return
        User.objects.create_superuser(username, email, password)
        self.stdout.write(
            self.style.SUCCESS(
                f"Created superuser '{username}'. Sign in at /admin/ with that password."
            )
        )
