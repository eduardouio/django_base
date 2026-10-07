from datetime import datetime

from django.views.generic import ListView

from common.mixins.SystemPermissionMixin import SystemPermissionMixin
from system.models import UserSession


class SessionHistoryListView(SystemPermissionMixin, ListView):
    model = UserSession
    template_name = 'pages/system/session_history.html'
    permission_required = 'system.view_usersession'
    paginate_by = 30

    def get_queryset(self):
        queryset = UserSession.objects.select_related('user').order_by(
            '-login_at'
        )
        search = self.request.GET.get('q', '').strip()
        if search:
            queryset = queryset.filter(user__email__icontains=search)
        for param, lookup in (('date_from', 'login_at__date__gte'),
                              ('date_to', 'login_at__date__lte')):
            try:
                value = datetime.strptime(
                    self.request.GET.get(param, ''), '%Y-%m-%d'
                )
                queryset = queryset.filter(**{lookup: value.date()})
            except ValueError:
                pass
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.copy()
        query.pop('page', None)
        context.update({
            'title': 'Historial de accesos',
            'filters': self.request.GET,
            'querystring': query.urlencode(),
        })
        return context
