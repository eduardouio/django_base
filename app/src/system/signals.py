from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save
from django.dispatch import receiver

from system.models import UserSession
from system.services.RoleService import sync_user_profile_group


@receiver(user_logged_in, dispatch_uid='system_session_start')
def register_session_start(sender, request, user, **kwargs):
    if request is not None and hasattr(request, 'session'):
        UserSession.start(request, user)


@receiver(user_logged_out, dispatch_uid='system_session_end')
def register_session_end(sender, request, user, **kwargs):
    if request is not None and hasattr(request, 'session'):
        session_key = request.session.session_key
        if session_key:
            UserSession.end(session_key, UserSession.LOGOUT)


@receiver(post_save, sender=get_user_model(),
          dispatch_uid='system_sync_profile_group')
def sync_profile_group(sender, instance, raw=False, update_fields=None,
                       **kwargs):
    # El login solo actualiza last_login: no hace falta sincronizar
    if raw or (update_fields and set(update_fields) == {'last_login'}):
        return
    sync_user_profile_group(instance)
