from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from common.LoggerApp import log_info, log_warning, log_error


class LoginTempView(LoginView):
    template_name = 'pages/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.get_redirect_url() or reverse_lazy('home')

    def form_valid(self, form):
        """
        Valida el formulario de login y ajusta la duración de la sesión 
        según el checkbox 'remember'.
        Si el usuario marca 'remember', la sesión dura 2 semanas;
        de lo contrario expira al cerrar el navegador (0 => cookie de sesión).
        """
        # Obtener el usuario antes de procesar el login
        user = form.get_user()

        log_info(
            user=user,
            url=self.request.path,
            file_name="LoginTempView",
            message=f"Intento de login para usuario: {user.email}",
            request=self.request
        )

        remember = self.request.POST.get('remember')
        response = super().form_valid(form)

        if remember:
            self.request.session.set_expiry(1209600)  # 14 días
            session_type = "persistente (14 días)"
        else:
            self.request.session.set_expiry(0)  # Hasta cerrar navegador
            session_type = "temporal (hasta cerrar navegador)"

        log_info(
            user=user,
            url=self.request.path,
            file_name="LoginTempView",
            message=(
                f"Login exitoso para {user.email} - Sesión: {session_type}"
            ),
            request=self.request
        )

        messages.success(
            self.request,
            'Inicio de sesión exitoso.'
        )
        return response

