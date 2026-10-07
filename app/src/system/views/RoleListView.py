from django.contrib import messages
from django.contrib.auth.models import Group
from django.db.models import Count
from django.shortcuts import redirect
from django.views.generic import ListView

from common.LoggerApp import log_info
from common.mixins.SystemPermissionMixin import SystemPermissionMixin
from system.services.RoleService import get_profile_group_names


class RoleListView(SystemPermissionMixin, ListView):
    """Listado de roles (grupos) y creación de nuevos roles."""
    template_name = 'pages/system/role_list.html'
    permission_required = 'system.manage_permissions'
    context_object_name = 'roles'

    def get_queryset(self):
        return Group.objects.annotate(
            users_count=Count('user', distinct=True),
            permissions_count=Count('permissions', distinct=True),
        ).order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Roles y permisos'
        context['profile_groups'] = get_profile_group_names()
        return context

    def post(self, request):
        name = request.POST.get('name', '').strip()[:150]
        if not name:
            messages.error(request, 'Ingresa un nombre para el rol.')
        elif Group.objects.filter(name__iexact=name).exists():
            messages.error(request, f'Ya existe un rol llamado "{name}".')
        else:
            group = Group.objects.create(name=name)
            log_info(
                user=request.user,
                url=request.path,
                file_name='RoleListView',
                message=f'Rol creado: {name}',
                request=request
            )
            messages.success(request, f'Rol "{name}" creado.')
            return redirect('system:role_permissions', pk=group.pk)
        return redirect('system:role_list')
