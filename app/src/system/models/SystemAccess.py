"""
Modelo sin tabla que solo define permisos generales del panel de
administración (no asociados a un modelo concreto).
"""

from django.db import models


class SystemAccess(models.Model):

    class Meta:
        managed = False
        default_permissions = ()
        verbose_name = 'acceso al sistema'
        verbose_name_plural = 'accesos al sistema'
        permissions = [
            ('view_dashboard', 'Puede ver el panel de administración'),
            ('manage_permissions', 'Puede administrar roles y permisos'),
        ]
