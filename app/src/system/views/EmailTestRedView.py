from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone
from django.views import View

from common.EmailService import EmailService
from common.mixins.SystemPermissionMixin import SystemPermissionMixin


class EmailTestRedView(SystemPermissionMixin, View):
    """Envía un correo de prueba al usuario actual para validar el SMTP."""
    permission_required = 'system.send_test_email'
    http_method_names = ['post']

    def post(self, request):
        email_log = EmailService.send(
            to=request.user.email,
            subject=f'Correo de prueba - {settings.SITE_NAME}',
            template='test_email',
            context={'user': request.user, 'sent_at': timezone.now()},
            user=request.user,
        )
        if email_log.status == email_log.SENT:
            messages.success(
                request, f'Correo de prueba enviado a {request.user.email}.'
            )
        else:
            messages.error(
                request, f'No se pudo enviar el correo: {email_log.error}'
            )
        return redirect('system:email_list')
