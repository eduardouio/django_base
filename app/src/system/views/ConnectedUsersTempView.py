from django.http import JsonResponse
from django.utils import timezone
from django.utils.timesince import timesince
from django.views import View
from django.views.generic import TemplateView

from common.mixins.SystemPermissionMixin import SystemPermissionMixin
from system.models import UserSession


def get_connected_data():
    """Sesiones abiertas (en línea primero) y totales para el panel."""
    UserSession.close_expired()
    sessions = list(
        UserSession.objects.open().select_related('user')
        .order_by('-last_activity')
    )
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    return {
        'sessions': sessions,
        'online_count': len({s.user_id for s in sessions if s.is_online}),
        'open_count': len(sessions),
        'logins_today': UserSession.objects.filter(login_at__gte=today).count(),
    }


class ConnectedUsersTempView(SystemPermissionMixin, TemplateView):
    template_name = 'pages/system/connected_users.html'
    permission_required = 'system.view_usersession'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_connected_data())
        context['title'] = 'Usuarios conectados'
        return context


class ConnectedUsersJsonView(SystemPermissionMixin, View):
    """Datos del panel para el refresco automático."""
    permission_required = 'system.view_usersession'

    def get(self, request):
        data = get_connected_data()
        current_key = request.session.session_key
        return JsonResponse({
            'online_count': data['online_count'],
            'open_count': data['open_count'],
            'logins_today': data['logins_today'],
            'sessions': [
                {
                    'id': s.pk,
                    'email': s.user.email,
                    'name': s.user.get_full_name(),
                    'profile': s.user.get_profile_type_display(),
                    'ip': s.ip or '',
                    'device': s.device,
                    'login_at': s.login_at.strftime('%d/%m/%Y %H:%M'),
                    'last_activity': timesince(s.last_activity),
                    'is_online': s.is_online,
                    'is_current': s.session_key == current_key,
                }
                for s in data['sessions']
            ],
        })
