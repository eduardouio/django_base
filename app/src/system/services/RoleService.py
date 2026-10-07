"""
Roles del sistema: un Group de Django por cada profile_type del usuario.

El grupo del perfil se mantiene sincronizado automáticamente; el usuario
puede tener además otros grupos asignados manualmente.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


def get_profile_roles():
    """Retorna [(profile_type, nombre_del_grupo), ...] según el modelo de usuario."""
    field = get_user_model()._meta.get_field('profile_type')
    return list(field.choices)


def get_profile_group_names():
    return [name for _, name in get_profile_roles()]


def sync_roles():
    """Crea los grupos de perfil que no existan. Retorna los nombres creados."""
    created = []
    for name in get_profile_group_names():
        _, was_created = Group.objects.get_or_create(name=name)
        if was_created:
            created.append(name)
    return created


def sync_user_profile_group(user):
    """Deja al usuario en el grupo de su profile_type y fuera de los otros perfiles."""
    roles = dict(get_profile_roles())
    target_name = roles.get(user.profile_type)
    others = Group.objects.filter(
        name__in=[n for n in roles.values() if n != target_name]
    )
    user.groups.remove(*others)
    if target_name:
        group, _ = Group.objects.get_or_create(name=target_name)
        user.groups.add(group)
