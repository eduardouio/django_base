from django.conf import settings
from django.contrib.auth.views import PasswordResetConfirmView
from django.urls import reverse, reverse_lazy
from django.utils import timezone

from accounts.forms.SetNewPasswordForm import SetNewPasswordForm
from common.EmailService import EmailService
from common.LoggerApp import log_info, log_warning
from common.utils.request import get_client_ip, get_site_url


class PasswordResetConfirmUpdtView(PasswordResetConfirmView):
    """
    Valida el token del enlace (vence en PASSWORD_RESET_TIMEOUT y se invalida
    al usarse) y permite definir la nueva contraseña.
    """
    template_name = 'pages/password_reset_confirm.html'
    form_class = SetNewPasswordForm
    success_url = reverse_lazy('accounts:password_reset_complete')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not context.get('validlink'):
            log_warning(
                user=None,
                url=self.request.path,
                file_name='PasswordResetConfirmUpdtView',
                message='Enlace de recuperación inválido o vencido',
                request=self.request
            )
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.user
        log_info(
            user=user,
            url=self.request.path,
            file_name='PasswordResetConfirmUpdtView',
            message=f'Contraseña restablecida por enlace para: {user.email}',
            request=self.request
        )
        send_password_changed_email(self.request, user)
        return response


def send_password_changed_email(request, user):
    """Avisa al usuario que su contraseña fue cambiada."""
    EmailService.send(
        to=user.email,
        subject=f'Tu contraseña fue cambiada - {settings.SITE_NAME}',
        template='password_changed',
        context={
            'user': user,
            'changed_at': timezone.now(),
            'ip': get_client_ip(request),
            'reset_request_url': get_site_url(request) + reverse(
                'accounts:password_reset'
            ),
        },
        async_send=True,
        user=user,
    )
