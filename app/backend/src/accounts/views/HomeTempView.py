from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from common.LoggerApp import log_info


class HomeTempView(LoginRequiredMixin, TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        log_info(
            user=self.request.user,
            url=self.request.path,
            file_name="HomeTempView",
            message=f"Acceso a página principal por: {self.request.user.email}",
            request=self.request
        )
        
        context = super().get_context_data(**kwargs)
        context['title'] = "Bienvenido a Base Sistema"
        return context