"""
Modelo de Licencias para usuarios.
Permite gestionar licencias con fechas de vencimiento y activaciones.
"""

from django.db import models
from common.BaseModel import BaseModel
from accounts.models import CustomUserModel
from django.utils import timezone

ROLE_CHOICES = (
    ('ADMINISTRATIVO', 'ADMINISTRATIVO'),
    ('TECNICO', 'TECNICO'),
)


class License(BaseModel):
    """Licencias asignadas a usuarios"""

    id = models.AutoField(
        primary_key=True
    )
    license_key = models.CharField(
        'clave de licencia',
        max_length=250,
        unique=True
    )
    activated_on = models.DateTimeField(
        'activada el',
        null=True,
        blank=True
    )
    expires_on = models.DateTimeField(
        'expira el',
        null=True,
        blank=True
    )
    enterprise = models.CharField(
        'Empresa',
        max_length=50,
        default='KOSMOFLOWERS'
    )
    is_active = models.BooleanField(
        'Activo?',
        default=False
    )
    url_server = models.URLField(
        'URL del servidor',
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        CustomUserModel,
        on_delete=models.CASCADE,
        related_name='licenses',
        verbose_name='usuario'
    )

    class Meta:
        verbose_name = 'Licencia'
        verbose_name_plural = 'Licencias'
        ordering = ['-created_at']

    def __str__(self):
        return 'Licencia de {}'.format(self.user.email)

    @property
    def is_expired(self):
        """Verificar si la licencia ha expirado"""
        if not self.expires_on:
            return False
        return timezone.now() > self.expires_on

    @property
    def days_remaining(self):
        """Calcular días restantes de la licencia"""
        if not self.expires_on or self.is_expired:
            return 0
        remaining = self.expires_on - timezone.now()
        return remaining.days

    def activate(self):
        """Activar la licencia"""
        self.is_active = True
        if not self.activated_on:
            self.activated_on = timezone.now()
        self.save()

    def deactivate(self):
        """Desactivar la licencia"""
        self.is_active = False
        self.save()
