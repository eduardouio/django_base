"""Registro de cada correo enviado desde common.EmailService."""

from django.conf import settings
from django.db import models


class EmailLog(models.Model):
    PENDING = 'PENDING'
    SENT = 'SENT'
    FAILED = 'FAILED'
    STATUSES = (
        (PENDING, 'Pendiente'),
        (SENT, 'Enviado'),
        (FAILED, 'Fallido'),
    )

    to = models.TextField('para', help_text='Destinatarios separados por coma.')
    cc = models.TextField('cc', blank=True)
    bcc = models.TextField('cco', blank=True)
    subject = models.CharField('asunto', max_length=255)
    template = models.CharField('plantilla', max_length=100, blank=True)
    status = models.CharField(
        'estado', max_length=10, choices=STATUSES, default=PENDING,
        db_index=True
    )
    error = models.TextField('error', blank=True)
    created_at = models.DateTimeField('creado', auto_now_add=True,
                                      db_index=True)
    sent_at = models.DateTimeField('enviado', null=True, blank=True)
    triggered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='enviado por',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    class Meta:
        verbose_name = 'correo enviado'
        verbose_name_plural = 'correos enviados'
        ordering = ['-created_at']
        permissions = [
            ('send_test_email', 'Puede enviar correos de prueba'),
        ]

    def __str__(self):
        return f'{self.subject} → {self.to}'
