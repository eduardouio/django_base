import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.middleware.csrf import get_token
from accounts.forms.ChangePasswordForm import ChangePasswordForm
from common.LoggerApp import log_info, log_warning, log_error


@method_decorator(csrf_protect, name='dispatch')
class ChangePassUpdtView(LoginRequiredMixin, View):
    """Vista para cambio de contraseña por AJAX"""
    login_url = 'accounts:login'

    def post(self, request, *args, **kwargs):
        """Procesa el cambio de contraseña"""
        log_info(
            user=request.user,
            url=request.path,
            file_name="ChangePassUpdtView",
            message=f"Intento de cambio de contraseña para: {request.user.email}",
            request=request
        )
        
        try:
            # Crear el formulario con los datos del usuario actual
            form = ChangePasswordForm(user=request.user, data=request.POST)

            if form.is_valid():
                # Guardar la nueva contraseña
                user = form.save()

                # Mantener la sesión activa después del cambio de contraseña
                update_session_auth_hash(request, user)

                log_info(
                    user=request.user,
                    url=request.path,
                    file_name="ChangePassUpdtView",
                    message=f"Cambio de contraseña exitoso para: {user.email}",
                    request=request
                )

                return JsonResponse({
                    'success': True,
                    'message': 'Tu contraseña ha sido actualizada exitosamente.'
                })
            else:
                # Recopilar errores del formulario
                errors = {}
                for field, error_list in form.errors.items():
                    errors[field] = [str(error) for error in error_list]

                log_warning(
                    user=request.user,
                    url=request.path,
                    file_name="ChangePassUpdtView",
                    message=(
                        f"Errores en formulario de cambio de contraseña "
                        f"para: {request.user.email}"
                    ),
                    request=request
                )

                return JsonResponse({
                    'success': False,
                    'message': 'Por favor, corrige los errores en el formulario.',
                    'errors': errors
                })

        except Exception as e:
            log_error(
                user=request.user,
                url=request.path,
                file_name="ChangePassUpdtView",
                message=(
                    f"Error inesperado en cambio de contraseña "
                    f"para {request.user.email}: {str(e)}"
                ),
                request=request
            )
            
            return JsonResponse({
                'success': False,
                'message': f'Error inesperado: {str(e)}'
            })

    def get(self, request, *args, **kwargs):
        """Devuelve el formulario vacío para el modal"""
        log_info(
            user=request.user,
            url=request.path,
            file_name="ChangePassUpdtView",
            message=(
                f"Solicitud de formulario de cambio de contraseña "
                f"para: {request.user.email}"
            ),
            request=request
        )
        
        form = ChangePasswordForm(user=request.user)

        # Renderizar el formulario como HTML para AJAX
        form_html = self._render_form_html(form)

        return JsonResponse({
            'success': True,
            'form_html': form_html
        })

    def _render_form_html(self, form):
        """Genera el HTML del formulario"""
        csrf_token = get_token(self.request)

        html = f"""
        <form id="changePasswordForm" method="post">
            <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
            
            <!-- Contraseña actual -->
            <div class="form-control mb-4">
                <label for="id_old_password" class="label">
                    <span class="label-text font-medium">{form.fields['old_password'].label}</span>
                </label>
                {form['old_password']}
                <div id="old_password_errors" class="label hidden">
                    <span class="label-text-alt text-error"></span>
                </div>
            </div>

            <!-- Nueva contraseña -->
            <div class="form-control mb-4">
                <label for="id_new_password1" class="label">
                    <span class="label-text font-medium">{form.fields['new_password1'].label}</span>
                </label>
                {form['new_password1']}
                <div class="label">
                    <span class="label-text-alt">{form.fields['new_password1'].help_text or ''}</span>
                </div>
                <div id="new_password1_errors" class="label hidden">
                    <span class="label-text-alt text-error"></span>
                </div>
            </div>

            <!-- Confirmar nueva contraseña -->
            <div class="form-control mb-6">
                <label for="id_new_password2" class="label">
                    <span class="label-text font-medium">{form.fields['new_password2'].label}</span>
                </label>
                {form['new_password2']}
                <div id="new_password2_errors" class="label hidden">
                    <span class="label-text-alt text-error"></span>
                </div>
            </div>

            <!-- Botones -->
            <div class="modal-action">
                <button type="button" class="btn btn-ghost" onclick="closeChangePasswordModal()">
                    <i class="las la-times"></i> Cancelar
                </button>
                <button type="submit" class="btn btn-primary">
                    <i class="las la-key"></i> Cambiar Contraseña
                </button>
            </div>
        </form>
        """
        return html
