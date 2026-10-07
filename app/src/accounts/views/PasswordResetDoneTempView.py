from django.conf import settings
from django.contrib.auth.views import PasswordResetDoneView


class PasswordResetDoneTempView(PasswordResetDoneView):
    template_name = 'pages/password_reset_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['expiry_minutes'] = settings.PASSWORD_RESET_TIMEOUT // 60
        return context
