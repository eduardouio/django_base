from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views import View
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from common.LoggerApp import log_info


class LogoutRedView(LoginRequiredMixin, View):
    """Cierra la sesión del usuario y redirige a la página de login.

    Acciones:
    - Elimina la sesión actual
    - (Opcional) Limpia datos adicionales (extensible)
    - Muestra un mensaje flash de confirmación
    """

    redirect_url = reverse_lazy('accounts:login')

    def post(self, request, *args, **kwargs):
        """Logout vía POST (más seguro para CSRF)."""
        return self._do_logout(request)

    def get(self, request, *args, **kwargs):
        """Logout vía GET (puede deshabilitarse si se requiere solo POST)."""
        return self._do_logout(request)

    def _do_logout(self, request):
        if request.user.is_authenticated:
            log_info(
                user=request.user,
                url=request.path,
                file_name="LoguoutRedView",
                message=f"Logout exitoso para usuario: {request.user.email}",
                request=request
            )
            logout(request)
            messages.success(request, 'Sesión cerrada correctamente.')
        return redirect(self.redirect_url)
