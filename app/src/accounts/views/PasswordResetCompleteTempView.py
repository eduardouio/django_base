from django.contrib.auth.views import PasswordResetCompleteView


class PasswordResetCompleteTempView(PasswordResetCompleteView):
    template_name = 'pages/password_reset_complete.html'
