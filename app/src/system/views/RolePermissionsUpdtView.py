from django.contrib import messages
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404, redirect
from django.utils.functional import cached_property
from django.views.generic import TemplateView

from common.LoggerApp import log_info
from common.mixins.SystemPermissionMixin import SystemPermissionMixin
from system.services.PermissionCatalog import (
    ACTIONS, apply_permissions, get_catalog, parse_ids
)
from system.services.RoleService import get_profile_group_names


class RolePermissionsUpdtView(SystemPermissionMixin, TemplateView):
    """Matriz de permisos por app/modelo de un rol (grupo)."""
    template_name = 'pages/system/role_permissions.html'
    permission_required = 'system.manage_permissions'

    @cached_property
    def group(self):
        return get_object_or_404(Group, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': f'Permisos del rol {self.group.name}',
            'group': self.group,
            'is_profile_group': self.group.name in get_profile_group_names(),
            'users': self.group.user_set.order_by('email')[:50],
            'catalog': get_catalog(),
            'actions': ACTIONS,
            'selected': set(
                self.group.permissions.values_list('id', flat=True)
            ),
            'inherited': set(),
        })
        return context

    def post(self, request, pk):
        group = self.group
        name = request.POST.get('name', '').strip()[:150]
        is_profile_group = group.name in get_profile_group_names()
        if name and name != group.name and not is_profile_group:
            if Group.objects.filter(name__iexact=name).exclude(
                    pk=group.pk).exists():
                messages.error(request, f'Ya existe un rol llamado "{name}".')
                return redirect('system:role_permissions', pk=group.pk)
            group.name = name
            group.save(update_fields=['name'])

        catalog = get_catalog()
        current = set(group.permissions.values_list('id', flat=True))
        new = apply_permissions(
            current, parse_ids(request.POST.getlist('permissions')), catalog
        )
        group.permissions.set(new)

        log_info(
            user=request.user,
            url=request.path,
            file_name='RolePermissionsUpdtView',
            message=(f'Permisos del rol "{group.name}" actualizados: '
                     f'+{len(new - current)} / -{len(current - new)}'),
            request=request
        )
        messages.success(request, f'Permisos del rol "{group.name}" guardados.')
        return redirect('system:role_permissions', pk=group.pk)
