from django import forms
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.urls import reverse

from common.EmailService import EmailService
from common.utils.request import get_site_url


class PasswordResetEmailForm(PasswordResetForm):
    """
    Solicitud de recuperación de contraseña.

    Envía el enlace con el token mediante EmailService (queda en EmailLog).
    El enlace vence según settings.PASSWORD_RESET_TIMEOUT.
    """

    email = forms.EmailField(
        label='Correo Electrónico',
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'tu@correo.com',
            'autocomplete': 'email',
        }),
        error_messages={
            'required': 'Este campo es obligatorio.',
            'invalid': 'Ingresa un correo electrónico válido.',
        }
    )

    def send_mail(self, subject_template_name, email_template_name, context,
                  from_email, to_email, html_email_template_name=None):
        request = getattr(self, '_request', None)
        reset_path = reverse(
            'accounts:password_reset_confirm',
            kwargs={'uidb64': context['uid'], 'token': context['token']}
        )
        EmailService.send(
            to=to_email,
            subject=f'Recuperación de contraseña - {settings.SITE_NAME}',
            template='password_reset',
            context={
                'user': context['user'],
                'reset_url': get_site_url(request) + reset_path,
                'expiry_minutes': settings.PASSWORD_RESET_TIMEOUT // 60,
            },
            async_send=True,
        )

    def save(self, *args, request=None, **kwargs):
        self._request = request
        return super().save(*args, request=request, **kwargs)
