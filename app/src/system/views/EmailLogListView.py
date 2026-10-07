from django.db.models import Q
from django.views.generic import ListView

from common.mixins.SystemPermissionMixin import SystemPermissionMixin
from system.models import EmailLog


class EmailLogListView(SystemPermissionMixin, ListView):
    model = EmailLog
    template_name = 'pages/system/email_list.html'
    permission_required = 'system.view_emaillog'
    paginate_by = 25

    def get_queryset(self):
        queryset = EmailLog.objects.select_related('triggered_by')
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        search = self.request.GET.get('q', '').strip()
        if search:
            queryset = queryset.filter(
                Q(to__icontains=search) | Q(subject__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.copy()
        query.pop('page', None)
        context.update({
            'title': 'Correos enviados',
            'statuses': EmailLog.STATUSES,
            'filters': self.request.GET,
            'querystring': query.urlencode(),
        })
        return context
