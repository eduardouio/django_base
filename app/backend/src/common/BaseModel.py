"""
 Modelo base para todos los modelos de la aplicación, todos los modelos
    deben heredar de este modelo.

    Attributes:
        created_at (DateTime): Fecha de creación del registro.
        updated_at (DateTime): Fecha de actualización del registro.
        deleted_at (DateTime): Fecha de eliminación del registro.
        historical (HistoricalRecords): Registros históricos del modelo.
        is_active (Boolean): Estado del registro.
        is_deleted (Boolean): Estado de eliminación del registro.

    Methods:
        save: Guarda el registro en la base de datos, 
              incluye el usuario creador y actualizador.
        get_user: Obtiene el usuario creador o actualizador del registro.

"""


from django.db import models
from simple_history.models import HistoricalRecords
from django.core.exceptions import ObjectDoesNotExist

# django-crum
from crum import get_current_user

# Modelo de usuario Peronalizado
from accounts.models.CustomUserModel import CustomUserModel


class BaseModel(models.Model):

    notes = models.TextField(
        'notas',
        blank=True,
        default=None,
        null=True,
        help_text='Notas del registro.'
    )

    created_at = models.DateTimeField(
        'fecha de creación',
        auto_now_add=True,
        help_text='Fecha de creación del registro.'
    )
    updated_at = models.DateTimeField(
        'fecha de actualización',
        auto_now=True,
        help_text='Fecha de ultima actualización del registro.'
    )
    is_active = models.BooleanField(
        'activo',
        default=True,
        help_text='Estado del registro.'
    )
    is_deleted = models.BooleanField(
        'eliminado',
        default=False,
        help_text='Estado de eliminación del registro.'
    )
    id_user_created = models.PositiveIntegerField(
        'usuario creador',
        default=0,
        blank=True,
        null=True,
        help_text='Identificador del usuario creador del registro 0 es anonimo.'
    )

    id_user_updated = models.PositiveIntegerField(
        'usuario actualizador',
        default=0,
        blank=True,
        null=True,
        help_text='Identificador del usuario actualizador del registro.'
    )

    history = HistoricalRecords(inherit=True)

    def save(self, *args, **kwargs):
        user = get_current_user()

        if user is None:
            return super().save(*args, **kwargs)

        if not self.pk:
            self.id_user_created = user.pk

        self.id_user_updated = user.pk
        return super().save(*args, **kwargs)

    def get_create_user(self):
        '''Retorna el usuario creador del registro.'''
        try:
            return CustomUserModel.objects.get(pk=self.id_user_created)
        except ObjectDoesNotExist:
            return None

    def get_update_user(self):
        '''Retorna el usuario ultimo en actualizar el registro '''
        try:
            return CustomUserModel.objects.get(pk=self.id_user_updated)
        except ObjectDoesNotExist:
            return None

    @classmethod
    def get_by_id(cls, id):
        '''Obtiene un registro por ID, omite los eliminados e inactivos.

        Args:
            id: ID del registro a buscar

        Returns:
            Instancia del modelo o False si no existe
        '''
        try:
            return cls.objects.get(pk=id, is_active=True, is_deleted=False)
        except ObjectDoesNotExist:
            return False

    @classmethod
    def get_all(cls):
        '''Obtiene todos los registros activos y no eliminados.

        Returns:
            QuerySet con todos los registros activos
        '''
        return cls.objects.filter(is_active=True, is_deleted=False)

    @classmethod
    def get_by_field(cls, field_name, value):
        '''Obtiene registros filtrados por un campo específico.

        Args:
            field_name: Nombre del campo por el que filtrar
            value: Valor a buscar

        Returns:
            QuerySet con los registros que coinciden
        '''
        filter_kwargs = {
            field_name: value,
            'is_active': True,
            'is_deleted': False
        }
        return cls.objects.filter(**filter_kwargs)

    @classmethod
    def get_deleted(cls):
        '''Obtiene todos los registros marcados como eliminados.

        Returns:
            QuerySet con los registros eliminados
        '''
        return cls.objects.filter(is_deleted=True)

    @classmethod
    def get_not_active(cls):
        '''Obtiene todos los registros marcados como inactivos.

        Returns:
            QuerySet con los registros inactivos
        '''
        return cls.objects.filter(is_active=False)

    def disable(self):
        '''Marca el registro como inactivo.

        Returns:
            bool: True si se guardó correctamente
        '''
        self.is_active = False
        self.save()
        return True

    def enable(self):
        '''Marca el registro como activo.

        Returns:
            bool: True si se guardó correctamente
        '''
        self.is_active = True
        self.save()
        return True

    def delete(self, *args, **kwargs):
        '''Marca el registro como eliminado (soft delete).

        Returns:
            bool: True si se guardó correctamente
        '''
        self.is_deleted = True
        self.save()
        return True

    def recover(self):
        '''Marca el registro como no eliminado (recupera el registro).

        Returns:
            bool: True si se guardó correctamente
        '''
        self.is_deleted = False
        self.save()
        return True

    class Meta:
        abstract = True
        get_latest_by = 'created_at'
        ordering = ['-created_at']
