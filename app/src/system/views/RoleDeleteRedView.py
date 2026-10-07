from django.contrib import messages
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from common.LoggerApp import log_info
from common.mixins.SystemPermissionMixin import SystemPermissionMixin
from system.services.RoleService import get_profile_group_names


class RoleDeleteRedView(SystemPermissionMixin, View):
    """Elimina un rol (POST). Los roles de perfil no se pueden eliminar."""
    permission_required = 'system.manage_permissions'
    http_method_names = ['post']

    def post(self, request, pk):
        group = get_object_or_404(Group, pk=pk)
        if group.name in get_profile_group_names():
            messages.error(
                request,
                f'"{group.name}" es un rol de perfil y no se puede eliminar.'
            )
            return redirect('system:role_list')

        name = group.name
        group.delete()
        log_info(
            user=request.user,
            url=request.path,
            file_name='RoleDeleteRedView',
            message=f'Rol eliminado: {name}',
            request=request
        )
        messages.success(request, f'Rol "{name}" eliminado.')
        return redirect('system:role_list')
