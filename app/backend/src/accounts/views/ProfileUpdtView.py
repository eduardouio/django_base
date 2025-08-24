from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from accounts.forms.CustomUserForm import CustomUserForm
from common.LoggerApp import log_info, log_warning, log_error

User = get_user_model()


class ProfileUpdtView(LoginRequiredMixin, UpdateView):
    """Vista para actualizar el perfil del usuario"""
    model = User
    form_class = CustomUserForm
    template_name = 'forms/profile_update.html'
    login_url = 'accounts:login'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        """Retorna el usuario actual"""
        return self.request.user

    def get_context_data(self, **kwargs):
        log_info(
            user=self.request.user,
            url=self.request.path,
            file_name="ProfileUpdtView",
            message=(
                f"Acceso a formulario de edición de perfil "
                f"por: {self.request.user.email}"
            ),
            request=self.request
        )
        
        context = super().get_context_data(**kwargs)
        context['title'] = "Editar Perfil"
        context['subtitle'] = "Actualiza tu información personal"
        return context

    def form_valid(self, form):
        """Ejecutado cuando el formulario es válido"""
        log_info(
            user=self.request.user,
            url=self.request.path,
            file_name="ProfileUpdtView",
            message=f"Perfil actualizado exitosamente por: {self.request.user.email}",
            request=self.request
        )
        
        messages.success(
            self.request,
            'Tu perfil ha sido actualizado exitosamente.'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        """Ejecutado cuando el formulario tiene errores"""
        log_warning(
            user=self.request.user,
            url=self.request.path,
            file_name="ProfileUpdtView",
            message=(
                f"Errores en formulario de perfil "
                f"para: {self.request.user.email}"
            ),
            request=self.request
        )
        
        messages.error(
            self.request,
            'Por favor, corrige los errores en el formulario.'
        )
        return super().form_invalid(form)