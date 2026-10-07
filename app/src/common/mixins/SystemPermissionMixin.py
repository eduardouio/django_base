from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


class SystemPermissionMixin(LoginRequiredMixin, PermissionRequiredMixin):
    """
    Exige sesión iniciada y el permiso indicado en `permission_required`.
    Anónimos van al login; usuarios sin permiso reciben 403.
    Los superusuarios tienen todos los permisos.

    Uso:
        class MiVista(SystemPermissionMixin, ListView):
            permission_required = 'mi_app.view_mimodelo'
    """
    login_url = 'accounts:login'
