"""
Comando de Django para probar la validación de licencias.
python manage.py test_license_validation <user_email>
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import License
from accounts.views.LoginTempView import LoginTempView

User = get_user_model()


class Command(BaseCommand):
    help = 'Prueba la validación de licencias para un usuario específico'

    def add_arguments(self, parser):
        parser.add_argument(
            'email',
            type=str,
            help='Email del usuario a probar'
        )

    def handle(self, *args, **options):
        email = options['email']
        
        try:
            user = User.objects.get(email=email)
            self.stdout.write(
                self.style.SUCCESS(f'Usuario encontrado: {user.email}')
            )
            
            # Instanciar la vista para usar sus métodos
            login_view = LoginTempView()
            
            # Probar validación de licencias
            result = login_view.validate_user_licenses(user)
            
            if result:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Usuario {user.email} tiene licencias válidas'
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Usuario {user.email} NO tiene licencias válidas'
                    )
                )
                
            # Mostrar detalles de licencias
            licenses = License.objects.filter(
                user=user,
                is_active=True,
                is_deleted=False
            )
            
            self.stdout.write('\nLicencias del usuario:')
            for license_obj in licenses:
                self.stdout.write(f'  - {license_obj.license_key}')
                self.stdout.write(f'    URL: {license_obj.url_server}')
                self.stdout.write(f'    Activa: {license_obj.is_active}')
                self.stdout.write(f'    Expirada: {license_obj.is_expired}')
                self.stdout.write(
                    f'    Días restantes: {license_obj.days_remaining}'
                )
                
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Usuario con email {email} no encontrado')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            )
