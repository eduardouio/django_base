from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class ChangePasswordForm(PasswordChangeForm):
    """Formulario personalizado para cambio de contraseña"""

    old_password = forms.CharField(
        label='Contraseña Actual',
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Ingrese su contraseña actual'
        }),
        error_messages={
            'required': 'Este campo es obligatorio.',
        }
    )

    new_password1 = forms.CharField(
        label='Nueva Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Ingrese su nueva contraseña'
        }),
        help_text='La contraseña debe tener al menos 8 caracteres.',
        error_messages={
            'required': 'Este campo es obligatorio.',
        }
    )

    new_password2 = forms.CharField(
        label='Confirmar Nueva Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Confirme su nueva contraseña'
        }),
        error_messages={
            'required': 'Este campo es obligatorio.',
        }
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar mensajes de error globales
        self.error_messages.update({
            'password_mismatch': 'Las contraseñas no coinciden.',
            'password_incorrect': 'La contraseña actual es incorrecta.',
        })

    def clean_new_password1(self):
        """Validar la nueva contraseña con mensajes en español"""
        password1 = self.cleaned_data.get('new_password1')

        if not password1:
            raise ValidationError('Este campo es obligatorio.')

        # Validaciones personalizadas en español
        if len(password1) < 8:
            raise ValidationError(
                'La contraseña debe tener al menos 8 caracteres.')

        if password1.isdigit():
            raise ValidationError(
                'La contraseña no puede ser completamente numérica.')

        if password1.lower() in ['password', 'contraseña', '12345678', 'password123']:
            raise ValidationError('La contraseña es demasiado común.')

        # Verificar que no sea similar al email del usuario
        user = getattr(self, 'user', None)
        if user and user.email:
            email_parts = user.email.lower().split('@')[0]
            if email_parts in password1.lower():
                raise ValidationError(
                    'La contraseña no puede ser similar a su información personal.')

        try:
            # Usar el validador de Django pero capturar errores para traducir
            validate_password(password1, user)
        except ValidationError as e:
            # Traducir algunos mensajes comunes de Django
            spanish_messages = []
            for message in e.messages:
                if 'too short' in message.lower():
                    spanish_messages.append(
                        'La contraseña debe tener al menos 8 caracteres.')
                elif 'too common' in message.lower():
                    spanish_messages.append(
                        'La contraseña es demasiado común.')
                elif 'entirely numeric' in message.lower():
                    spanish_messages.append(
                        'La contraseña no puede ser completamente numérica.')
                elif 'similar' in message.lower():
                    spanish_messages.append(
                        'La contraseña no puede ser similar a su información personal.')
                else:
                    spanish_messages.append(
                        'La contraseña no cumple con los requisitos de seguridad.')

            if spanish_messages:
                raise ValidationError(spanish_messages)

        return password1

    def clean_new_password2(self):
        """Validar que las contraseñas coincidan"""
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')

        if not password2:
            raise ValidationError('Este campo es obligatorio.')

        if password1 and password2 and password1 != password2:
            raise ValidationError('Las contraseñas no coinciden.')

        return password2

    def clean_old_password(self):
        """Validar contraseña actual"""
        old_password = self.cleaned_data.get('old_password')

        if not old_password:
            raise ValidationError('Este campo es obligatorio.')

        if not self.user.check_password(old_password):
            raise ValidationError('La contraseña actual es incorrecta.')

        return old_password
