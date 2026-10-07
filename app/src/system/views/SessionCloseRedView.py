from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from common.LoggerApp import log_info
from common.mixins.SystemPermissionMixin import SystemPermissionMixin
from system.models import UserSession


class SessionCloseRedView(SystemPermissionMixin, View):
    """Cierra a la fuerza la sesión de otro usuario (POST)."""
    permission_required = 'system.close_usersession'
    http_method_names = ['post']

    def post(self, request, pk):
        session = get_object_or_404(
            UserSession.objects.select_related('user'), pk=pk,
            logout_at__isnull=True
        )
        if session.session_key == request.session.session_key:
            messages.warning(
                request, 'No puedes cerrar tu propia sesión desde aquí.'
            )
            return redirect('system:connected_users')

        session.force_close()
        log_info(
            user=request.user,
            url=request.path,
            file_name='SessionCloseRedView',
            message=f'Sesión cerrada a la fuerza: {session.user.email} '
                    f'(IP {session.ip})',
            request=request
        )
        messages.success(
            request, f'Se cerró la sesión de {session.user.email}.'
        )
        return redirect('system:connected_users')
