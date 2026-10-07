from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View

from common.LoggerApp import log_info
from common.mixins.SystemPermissionMixin import SystemPermissionMixin
from system.models import ErrorLog


class ErrorLogResolveRedView(SystemPermissionMixin, View):
    """Marca un error como resuelto o lo reabre (POST)."""
    permission_required = 'system.change_errorlog'
    http_method_names = ['post']

    def post(self, request, pk):
        error = get_object_or_404(ErrorLog, pk=pk)
        if error.is_resolved:
            error.is_resolved = False
            error.resolved_at = None
            error.resolved_by = None
            action = 'reabierto'
        else:
            error.is_resolved = True
            error.resolved_at = timezone.now()
            error.resolved_by = request.user
            action = 'marcado como resuelto'
        error.save(update_fields=['is_resolved', 'resolved_at', 'resolved_by'])

        log_info(
            user=request.user,
            url=request.path,
            file_name='ErrorLogResolveRedView',
            message=f'Error #{error.pk} {action}',
            request=request
        )
        messages.success(request, f'Error #{error.pk} {action}.')
        next_url = request.POST.get('next', '')
        if url_has_allowed_host_and_scheme(
                next_url, allowed_hosts={request.get_host()}):
            return redirect(next_url)
        return redirect('system:error_list')
