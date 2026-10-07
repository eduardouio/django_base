"""
Sesiones de usuario para el panel de usuarios conectados.

Se crean con la señal user_logged_in, se cierran con user_logged_out y
UserActivityMiddleware actualiza last_activity.
"""

from datetime import timedelta

from django.conf import settings
from django.contrib.sessions.models import Session
from django.db import models
from django.utils import timezone

from common.utils.request import (
    get_client_ip, get_user_agent, parse_user_agent
)


class UserSessionQuerySet(models.QuerySet):

    def open(self):
        return self.filter(logout_at__isnull=True)

    def online(self):
        minutes = getattr(settings, 'ONLINE_THRESHOLD_MINUTES', 5)
        limit = timezone.now() - timedelta(minutes=minutes)
        return self.open().filter(last_activity__gte=limit)


class UserSession(models.Model):
    LOGOUT = 'LOGOUT'
    FORCED = 'FORCED'
    EXPIRED = 'EXPIRED'
    END_REASONS = (
        (LOGOUT, 'Cerró sesión'),
        (FORCED, 'Cerrada por administrador'),
        (EXPIRED, 'Expirada'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='usuario',
        on_delete=models.CASCADE,
        related_name='user_sessions'
    )
    session_key = models.CharField('sesión', max_length=40, unique=True)
    ip = models.GenericIPAddressField('IP', null=True, blank=True)
    user_agent = models.CharField('navegador', max_length=500, blank=True)
    login_at = models.DateTimeField('inicio de sesión', auto_now_add=True,
                                    db_index=True)
    last_activity = models.DateTimeField('última actividad', db_index=True)
    logout_at = models.DateTimeField('fin de sesión', null=True, blank=True)
    ended_reason = models.CharField(
        'motivo de cierre', max_length=10, choices=END_REASONS, blank=True
    )

    objects = UserSessionQuerySet.as_manager()

    class Meta:
        verbose_name = 'sesión de usuario'
        verbose_name_plural = 'sesiones de usuario'
        ordering = ['-last_activity']
        permissions = [
            ('close_usersession', 'Puede cerrar sesiones de otros usuarios'),
        ]

    def __str__(self):
        return f'{self.user} ({self.ip})'

    @property
    def device(self):
        return parse_user_agent(self.user_agent)

    @property
    def is_open(self):
        return self.logout_at is None

    @property
    def is_online(self):
        minutes = getattr(settings, 'ONLINE_THRESHOLD_MINUTES', 5)
        limit = timezone.now() - timedelta(minutes=minutes)
        return self.is_open and self.last_activity >= limit

    @classmethod
    def start(cls, request, user):
        """Registra una nueva sesión al iniciar sesión."""
        if not request.session.session_key:
            request.session.save()
        now = timezone.now()
        session, _ = cls.objects.update_or_create(
            session_key=request.session.session_key,
            defaults={
                'user': user,
                'ip': get_client_ip(request),
                'user_agent': get_user_agent(request),
                'last_activity': now,
                'logout_at': None,
                'ended_reason': '',
            }
        )
        return session

    @classmethod
    def touch(cls, request, session_key):
        """Actualiza la última actividad; crea el registro si no existe."""
        updated = cls.objects.filter(
            session_key=session_key, logout_at__isnull=True
        ).update(last_activity=timezone.now(), ip=get_client_ip(request))
        if not updated and not cls.objects.filter(
                session_key=session_key).exists():
            # Sesiones iniciadas antes de instalar el panel
            cls.start(request, request.user)

    @classmethod
    def end(cls, session_key, reason):
        return cls.objects.filter(
            session_key=session_key, logout_at__isnull=True
        ).update(logout_at=timezone.now(), ended_reason=reason)

    def force_close(self):
        """Cierra la sesión de este usuario eliminando la sesión de Django."""
        Session.objects.filter(session_key=self.session_key).delete()
        self.logout_at = timezone.now()
        self.ended_reason = self.FORCED
        self.save(update_fields=['logout_at', 'ended_reason'])

    @classmethod
    def close_expired(cls):
        """Marca como expiradas las sesiones cuya sesión de Django ya no existe."""
        alive = Session.objects.filter(
            expire_date__gt=timezone.now()
        ).values('session_key')
        return cls.objects.open().exclude(session_key__in=alive).update(
            logout_at=timezone.now(), ended_reason=cls.EXPIRED
        )
