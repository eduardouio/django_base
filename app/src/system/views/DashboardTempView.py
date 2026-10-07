from datetime import timedelta

from django.utils import timezone
from django.views.generic import TemplateView

from common.mixins.SystemPermissionMixin import SystemPermissionMixin
from system.models import EmailLog, ErrorLog, UserSession


class DashboardTempView(SystemPermissionMixin, TemplateView):
    template_name = 'pages/system/dashboard.html'
    permission_required = 'system.view_dashboard'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        UserSession.close_expired()
        last_24h = timezone.now() - timedelta(hours=24)
        today = timezone.now().replace(hour=0, minute=0, second=0,
                                       microsecond=0)
        context.update({
            'title': 'Administración del sistema',
            'online_count': UserSession.objects.online()
            .values('user').distinct().count(),
            'logins_today': UserSession.objects.filter(
                login_at__gte=today).count(),
            'open_errors': ErrorLog.objects.filter(is_resolved=False).count(),
            'errors_24h': ErrorLog.objects.filter(
                is_resolved=False, last_seen__gte=last_24h).count(),
            'emails_failed_24h': EmailLog.objects.filter(
                status=EmailLog.FAILED, created_at__gte=last_24h).count(),
            'emails_sent_24h': EmailLog.objects.filter(
                status=EmailLog.SENT, created_at__gte=last_24h).count(),
            'recent_errors': ErrorLog.objects.filter(
                is_resolved=False).select_related('user')[:5],
        })
        return context
