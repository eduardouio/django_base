from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from common.LoggerApp import log_info


class ProfileTempView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/profile.html'
    login_url = 'accounts:login'

    def get_context_data(self, **kwargs):
        log_info(
            user=self.request.user,
            url=self.request.path,
            file_name="ProfileTempView",
            message=f"Acceso a perfil por usuario: {self.request.user.email}",
            request=self.request
        )
        
        context = super().get_context_data(**kwargs)
        context['title'] = "Mi Perfil"
        context['user'] = self.request.user
        return context