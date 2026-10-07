from django import forms
from django.contrib.auth.forms import SetPasswordForm

from accounts.forms.ChangePasswordForm import ChangePasswordForm


class SetNewPasswordForm(SetPasswordForm):
    """Nueva contraseña desde el enlace de recuperación (mensajes en español)."""

    new_password1 = forms.CharField(
        label='Nueva Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Ingrese su nueva contraseña',
            'autocomplete': 'new-password',
        }),
        help_text='La contraseña debe tener al menos 8 caracteres.',
        error_messages={'required': 'Este campo es obligatorio.'}
    )

    new_password2 = forms.CharField(
        label='Confirmar Nueva Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Confirme su nueva contraseña',
            'autocomplete': 'new-password',
        }),
        error_messages={'required': 'Este campo es obligatorio.'}
    )

    # Mismas reglas de validación que el cambio de contraseña del perfil
    clean_new_password1 = ChangePasswordForm.clean_new_password1
    clean_new_password2 = ChangePasswordForm.clean_new_password2
