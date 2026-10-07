from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.utils.functional import cached_property
from django.views.generic import TemplateView

from common.LoggerApp import log_info
from common.mixins.SystemPermissionMixin import SystemPermissionMixin
from system.services.PermissionCatalog import (
    ACTIONS, apply_permissions, get_catalog, parse_ids
)
from system.services.RoleService import (
    get_profile_group_names, sync_user_profile_group
)


class UserPermissionsUpdtView(SystemPermissionMixin, TemplateView):
    """
    Roles adicionales y permisos directos de un usuario.
    Los permisos heredados de sus roles se muestran pero no se editan aquí.
    """
    template_name = 'pages/system/user_permissions.html'
    permission_required = 'system.manage_permissions'

    @cached_property
    def target(self):
        return get_object_or_404(get_user_model(), pk=self.kwargs['pk'])

    def _check_can_edit(self):
        if self.target.is_superuser and not self.request.user.is_superuser:
            raise PermissionDenied(
                'Solo un superusuario puede modificar a otro superusuario.'
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_groups = get_profile_group_names()
        user_groups = self.target.groups.all()
        context.update({
            'title': f'Permisos de {self.target.email}',
            'target': self.target,
            'profile_group': next(
                (g for g in user_groups if g.name in profile_groups), None
            ),
            'extra_groups': Group.objects.exclude(
                name__in=profile_groups).order_by('name'),
            'user_group_ids': {g.pk for g in user_groups},
            'catalog': get_catalog(),
            'actions': ACTIONS,
            'selected': set(
                self.target.user_permissions.values_list('id', flat=True)
            ),
            'inherited': set(
                Permission.objects.filter(group__user=self.target)
                .values_list('id', flat=True)
            ),
        })
        return context

    def post(self, request, pk):
        self._check_can_edit()
        target = self.target

        profile_groups = get_profile_group_names()
        posted_groups = Group.objects.filter(
            pk__in=parse_ids(request.POST.getlist('groups'))
        ).exclude(name__in=profile_groups)
        target.groups.set(posted_groups)
        sync_user_profile_group(target)

        catalog = get_catalog()
        current = set(target.user_permissions.values_list('id', flat=True))
        new = apply_permissions(
            current, parse_ids(request.POST.getlist('permissions')), catalog
        )
        target.user_permissions.set(new)

        log_info(
            user=request.user,
            url=request.path,
            file_name='UserPermissionsUpdtView',
            message=(f'Permisos de {target.email} actualizados. Roles: '
                     f'{", ".join(g.name for g in target.groups.all())}; '
                     f'permisos directos +{len(new - current)} / '
                     f'-{len(current - new)}'),
            request=request
        )
        messages.success(request, f'Permisos de {target.email} guardados.')
        return redirect('system:user_permissions', pk=target.pk)
