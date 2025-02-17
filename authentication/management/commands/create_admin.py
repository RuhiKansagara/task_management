from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Seed initial admin users data"

    def handle(self, *args, **options):
        """
        The function creates admin users with specified credentials if they do not already exist.
        """
        admin_users = [
            {
                "username": "Test Admin",
                "email": "testadmin@yopmail.com",
                "password": "Test@123",
            },
            {
                "username" : "Backend Admin",
                "email": "backendadmin@yopmail.com",
                "password": "BackendAdmin@123",
            }
        ]

        for admin_data in admin_users:
            if not User.objects.filter(email=admin_data["email"]).exists():
                user = User.objects.create_superuser(
                    username=admin_data["username"],
                    email=admin_data["email"],
                    password=admin_data["password"],
                    is_staff=True, 
                    is_superuser=True
                )
                user.save()

                self.stdout.write(
                    self.style.SUCCESS(f"Admin user {admin_data['username']} created successfully.")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"Admin user {admin_data['username']} already exists.")
                )