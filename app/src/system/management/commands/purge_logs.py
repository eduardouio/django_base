from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from system.models import EmailLog, ErrorLog, UserSession


class Command(BaseCommand):
    help = ('Elimina errores resueltos, correos y sesiones cerradas más '
            'antiguos que --days días (por defecto 90)')

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=90)

    def handle(self, *args, **options):
        limit = timezone.now() - timedelta(days=options['days'])
        errors, _ = ErrorLog.objects.filter(
            is_resolved=True, last_seen__lt=limit
        ).delete()
        emails, _ = EmailLog.objects.filter(created_at__lt=limit).delete()
        sessions, _ = UserSession.objects.filter(
            logout_at__isnull=False, logout_at__lt=limit
        ).delete()
        self.stdout.write(self.style.SUCCESS(
            f'Eliminados: {errors} errores resueltos, {emails} correos, '
            f'{sessions} sesiones cerradas (anteriores a {limit:%d/%m/%Y})'
        ))
