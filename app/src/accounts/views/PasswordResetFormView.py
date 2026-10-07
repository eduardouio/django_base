from django.conf import settings
from django.contrib.auth.views import PasswordResetView
from django.core.cache import cache
from django.urls import reverse_lazy

from accounts.forms.PasswordResetEmailForm import PasswordResetEmailForm
from common.LoggerApp import log_info, log_warning
from common.utils.request import get_client_ip


class PasswordResetFormView(PasswordResetView):
    """
    Solicitud de recuperación de contraseña por correo.

    Siempre redirige a la misma página de confirmación exista o no el correo,
    para no revelar qué cuentas están registradas. Limita las solicitudes por
    correo e IP dentro de la ventana de validez del enlace.
    """
    template_name = 'pages/password_reset_form.html'
    form_class = PasswordResetEmailForm
    success_url = reverse_lazy('accounts:password_reset_done')

    def form_valid(self, form):
        email = form.cleaned_data['email'].lower()
        ip = get_client_ip(self.request)

        if self._is_rate_limited(email, ip):
            log_warning(
                user=email,
                url=self.request.path,
                file_name='PasswordResetFormView',
                message=f'Límite de solicitudes de recuperación excedido (IP {ip})',
                request=self.request
            )
            form.add_error(
                None,
                'Has realizado demasiadas solicitudes. Espera unos minutos e '
                'inténtalo de nuevo.'
            )
            return self.form_invalid(form)

        log_info(
            user=email,
            url=self.request.path,
            file_name='PasswordResetFormView',
            message=f'Solicitud de recuperación de contraseña (IP {ip})',
            request=self.request
        )
        return super().form_valid(form)

    def _is_rate_limited(self, email, ip):
        limit = getattr(settings, 'PASSWORD_RESET_MAX_ATTEMPTS', 3)
        window = settings.PASSWORD_RESET_TIMEOUT
        limited = False
        for key in (f'pwreset:email:{email}', f'pwreset:ip:{ip}'):
            cache.add(key, 0, timeout=window)
            try:
                attempts = cache.incr(key)
            except ValueError:
                cache.set(key, 1, timeout=window)
                attempts = 1
            if attempts > limit:
                limited = True
        return limited
