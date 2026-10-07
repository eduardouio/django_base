from django.views.generic import DetailView

from common.mixins.SystemPermissionMixin import SystemPermissionMixin
from system.models import ErrorLog


class ErrorLogDetailView(SystemPermissionMixin, DetailView):
    model = ErrorLog
    template_name = 'pages/system/error_detail.html'
    permission_required = 'system.view_errorlog'
    context_object_name = 'error'

    def get_queryset(self):
        return ErrorLog.objects.select_related('user', 'resolved_by')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Detalle del error'
        return context
