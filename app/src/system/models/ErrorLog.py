"""
Errores de la aplicación capturados por common.logging.DatabaseLogHandler.

No hereda de BaseModel a propósito: se escribe desde el sistema de logging y
no debe generar historial ni depender del usuario actual (crum).
"""

from django.conf import settings
from django.db import models


class ErrorLog(models.Model):
    LEVELS = (
        ('ERROR', 'Error'),
        ('CRITICAL', 'Crítico'),
    )

    fingerprint = models.CharField(
        'huella',
        max_length=40,
        unique=True,
        help_text='Hash que agrupa errores iguales (tipo + ubicación).'
    )
    level = models.CharField('nivel', max_length=10, default='ERROR')
    logger_name = models.CharField('logger', max_length=100, blank=True)
    message = models.TextField('mensaje', blank=True)
    exception_type = models.CharField(
        'tipo de excepción', max_length=200, blank=True
    )
    traceback = models.TextField('traceback', blank=True)
    location = models.CharField('ubicación', max_length=500, blank=True)
    occurrences = models.PositiveIntegerField('ocurrencias', default=1)
    first_seen = models.DateTimeField('primera vez')
    last_seen = models.DateTimeField('última vez', db_index=True)
    url = models.CharField('URL', max_length=500, blank=True)
    method = models.CharField('método', max_length=10, blank=True)
    status_code = models.PositiveSmallIntegerField(
        'código HTTP', null=True, blank=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='usuario',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    ip = models.GenericIPAddressField('IP', null=True, blank=True)
    user_agent = models.CharField('navegador', max_length=500, blank=True)
    request_id = models.CharField('request id', max_length=64, blank=True)
    request_data = models.JSONField('datos del request', default=dict)
    is_resolved = models.BooleanField('resuelto', default=False)
    resolved_at = models.DateTimeField('fecha de resolución', null=True,
                                       blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='resuelto por',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    class Meta:
        verbose_name = 'error'
        verbose_name_plural = 'errores'
        ordering = ['-last_seen']

    def __str__(self):
        return f'{self.exception_type or self.level}: {self.message[:80]}'

    @property
    def title(self):
        """Primera línea legible del error para listados."""
        text = self.message.split(' | Mensaje: ')[-1]
        return (text.splitlines() or [''])[0][:200]
