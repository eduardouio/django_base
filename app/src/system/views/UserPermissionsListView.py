from django.contrib.auth import get_user_model
from django.db.models import Q
from django.views.generic import ListView

from common.mixins.SystemPermissionMixin import SystemPermissionMixin


class UserPermissionsListView(SystemPermissionMixin, ListView):
    """Buscador de usuarios para editar sus roles y permisos."""
    template_name = 'pages/system/user_permissions_list.html'
    permission_required = 'system.manage_permissions'
    context_object_name = 'users'
    paginate_by = 25

    def get_queryset(self):
        queryset = get_user_model().objects.prefetch_related('groups') \
            .order_by('email')
        search = self.request.GET.get('q', '').strip()
        if search:
            queryset = queryset.filter(
                Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.copy()
        query.pop('page', None)
        context.update({
            'title': 'Permisos por usuario',
            'filters': self.request.GET,
            'querystring': query.urlencode(),
        })
        return context
