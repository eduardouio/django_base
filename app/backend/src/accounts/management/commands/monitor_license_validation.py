"""
Comando de Django para monitorear el estado de validación de licencias.
Útil para debugging y verificación del middleware.

Uso:
python manage.py monitor_license_validation <user_email>
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.utils import timezone
from common.LicenseValidationMiddleware import LicenseValidationMiddleware

User = get_user_model()


class Command(BaseCommand):
    help = 'Monitorea el estado de validación de licencias de un usuario'

    def add_arguments(self, parser):
        parser.add_argument(
            'email',
            type=str,
            help='Email del usuario a monitorear'
        )
        parser.add_argument(
            '--simulate-request',
            action='store_true',
            help='Simular una petición para activar el middleware'
        )

    def handle(self, *args, **options):
        email = options['email']
        simulate_request = options.get('simulate_request', False)

        try:
            user = User.objects.get(email=email)
            self.stdout.write(
                self.style.SUCCESS(f'Usuario encontrado: {user.email}')
            )

            if simulate_request:
                self._simulate_request_with_middleware(user)
            else:
                self._show_validation_status(user)

        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Usuario con email {email} no encontrado')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            )

    def _simulate_request_with_middleware(self, user):
        """
        Simula una petición HTTP para probar el middleware de validación.
        """
        self.stdout.write('\n🔄 Simulando petición con middleware...')

        # Crear una petición simulada
        factory = RequestFactory()
        request = factory.get('/accounts/profile/')
        request.user = user

        # Simular sesión
        from django.contrib.sessions.backends.db import SessionStore
        session = SessionStore()
        session.create()
        request.session = session

        # Instanciar el middleware
        def dummy_get_response(request):
            return None

        middleware = LicenseValidationMiddleware(dummy_get_response)

        # Ejecutar verificación
        validation_result = middleware._check_license_validation_schedule(
            request
        )

        self.stdout.write(f'Resultado de validación: {validation_result}')

        # Mostrar estado de la sesión
        status = middleware.get_validation_status(request)
        self._display_status(status)

    def _show_validation_status(self, user):
        """
        Muestra el estado de validación sin ejecutar el middleware.
        """
        self.stdout.write('\n📊 Estado de validación de licencias:')

        # Verificar licencias directamente
        from accounts.models import License
        licenses = License.objects.filter(
            user=user,
            is_active=True,
            is_deleted=False
        ).exclude(expires_on__lt=timezone.now())

        self.stdout.write(f'Licencias activas encontradas: {licenses.count()}')

        for license_obj in licenses:
            self.stdout.write(f'  - {license_obj.license_key}')
            self.stdout.write(f'    URL: {license_obj.url_server}')
            self.stdout.write(f'    Activa: {license_obj.is_active}')
            self.stdout.write(f'    Expirada: {license_obj.is_expired}')
            self.stdout.write(
                f'    Días restantes: {license_obj.days_remaining}'
            )

    def _display_status(self, status):
        """
        Muestra el estado de validación de manera formateada.
        """
        self.stdout.write('\n📋 Estado detallado de validación:')

        for key, value in status.items():
            if key == 'authenticated':
                icon = '✅' if value else '❌'
                self.stdout.write(f'  {icon} Autenticado: {value}')
            elif key == 'license_valid':
                icon = '✅' if value else '❌'
                self.stdout.write(f'  {icon} Licencia válida: {value}')
            elif key == 'last_check':
                if value:
                    last_check_time = timezone.datetime.fromtimestamp(value)
                    self.stdout.write(
                        f'  🕐 Última verificación: {last_check_time}'
                    )
                else:
                    self.stdout.write('  🕐 Última verificación: Nunca')
            elif key == 'last_check_ago':
                if value is not None:
                    self.stdout.write(
                        f'  ⏱️  Hace: {int(value)} segundos'
                    )
            elif key == 'validation_interval':
                self.stdout.write(
                    f'  ⏰ Intervalo de validación: {value} segundos '
                    f'({value/60:.1f} minutos)'
                )
            elif key == 'next_validation_in':
                if value is not None:
                    self.stdout.write(
                        f'  ⏳ Próxima validación en: {int(value)} segundos '
                        f'({value/60:.1f} minutos)'
                    )

        # Configuración del middleware
        middleware = LicenseValidationMiddleware(None)
        self.stdout.write('\n⚙️  Configuración del middleware:')
        self.stdout.write('  • Intervalo de validación único:')
        interval = middleware.VALIDATION_INTERVAL
        self.stdout.write(
            f'    - Todos los usuarios: {interval}s ({interval/60:.1f} min)'
        )

        excluded_count = len(middleware.EXCLUDED_URLS)
        self.stdout.write(f'  • URLs excluidas: {excluded_count}')
        for url in middleware.EXCLUDED_URLS:
            self.stdout.write(f'    - {url}')
