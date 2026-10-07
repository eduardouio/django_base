from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from system.services.RoleService import sync_roles, sync_user_profile_group


class Command(BaseCommand):
    help = 'Crea los roles (grupos) de perfil y asigna cada usuario al de su profile_type'

    def handle(self, *args, **options):
        created = sync_roles()
        for name in created:
            self.stdout.write(self.style.SUCCESS(f'Rol creado: {name}'))

        users = get_user_model().objects.all()
        for user in users:
            sync_user_profile_group(user)
        self.stdout.write(self.style.SUCCESS(
            f'Roles sincronizados ({len(created)} nuevos, '
            f'{users.count()} usuarios asignados)'
        ))
