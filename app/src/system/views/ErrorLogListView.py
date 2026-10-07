from datetime import datetime

from django.db.models import Q
from django.views.generic import ListView

from common.mixins.SystemPermissionMixin import SystemPermissionMixin
from system.models import ErrorLog


class ErrorLogListView(SystemPermissionMixin, ListView):
    model = ErrorLog
    template_name = 'pages/system/error_list.html'
    permission_required = 'system.view_errorlog'
    paginate_by = 25

    def get_queryset(self):
        params = self.request.GET
        queryset = ErrorLog.objects.select_related('user')

        status = params.get('status', 'open')
        if status == 'open':
            queryset = queryset.filter(is_resolved=False)
        elif status == 'resolved':
            queryset = queryset.filter(is_resolved=True)

        if params.get('level'):
            queryset = queryset.filter(level=params['level'])

        for param, lookup in (('date_from', 'last_seen__date__gte'),
                              ('date_to', 'last_seen__date__lte')):
            try:
                value = datetime.strptime(params.get(param, ''), '%Y-%m-%d')
                queryset = queryset.filter(**{lookup: value.date()})
            except ValueError:
                pass

        search = params.get('q', '').strip()
        if search:
            queryset = queryset.filter(
                Q(message__icontains=search)
                | Q(exception_type__icontains=search)
                | Q(url__icontains=search)
                | Q(request_id__iexact=search)
                | Q(user__email__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.copy()
        query.pop('page', None)
        context.update({
            'title': 'Registro de errores',
            'filters': self.request.GET,
            'status': self.request.GET.get('status', 'open'),
            'levels': ErrorLog.LEVELS,
            'querystring': query.urlencode(),
        })
        return context
