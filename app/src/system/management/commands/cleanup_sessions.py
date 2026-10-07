from django.core.management import call_command
from django.core.management.base import BaseCommand

from system.models import UserSession


class Command(BaseCommand):
    help = ('Elimina sesiones de Django expiradas y marca como expiradas las '
            'sesiones del panel de usuarios conectados. Programar en cron.')

    def handle(self, *args, **options):
        call_command('clearsessions')
        closed = UserSession.close_expired()
        self.stdout.write(self.style.SUCCESS(
            f'{closed} sesiones marcadas como expiradas'
        ))
