from django.core.management.base import BaseCommand
from accounts.models import CustomUserModel
from config import secrets

class Command(BaseCommand):
    help = 'Seeds the database with initial users'

    def handle(self, *args, **kwargs):
        domain = secrets.DOMMAIN
        password = secrets.GENERIC_PASSWORD

        # Generic users based on profile types
        profiles = ['MANAGER', 'ENTERPRISE', 'CONSULTOR', 'TECHNICAL', 'REPORTS']
        for profile in profiles:
            email = f"{profile.lower()}@{domain}"
            user, created = CustomUserModel.objects.get_or_create(email=email, defaults={'profile_type': profile})
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully created user {email}'))
            else:
                self.stdout.write(self.style.WARNING(f'User {email} already exists'))

        # Specific users
        specific_users = [
            {'email': f'owner@{domain}', 'profile': 'MANAGER'},
            {'email': f'consultant@{domain}', 'profile': 'CONSULTOR'}
        ]

        for user_data in specific_users:
            email = user_data['email']
            profile = user_data['profile']
            user, created = CustomUserModel.objects.get_or_create(email=email, defaults={'profile_type': profile})
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully created user {email}'))
            else:
                self.stdout.write(self.style.WARNING(f'User {email} already exists'))
