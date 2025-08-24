from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
import requests
from accounts.models import License
from common.LoggerApp import log_info, log_warning, log_error


class LoginTempView(LoginView):
    template_name = 'pages/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.get_redirect_url() or reverse_lazy('home')

    def validate_license_with_external_service(self, license_obj):
        """
        Valida la licencia contra el servicio externo.

        Args:
            license_obj: Objeto License a validar

        Returns:
            bool: True si la licencia es válida, False en caso contrario
        """
        if not license_obj.url_server or not license_obj.license_key:
            log_warning(
                user=None,
                url="N/A",
                file_name="LoginTempView",
                message=(
                    f"Licencia {license_obj.id} sin URL de servidor o clave"
                ),
                request=getattr(self, 'request', None)
            )
            return False

        try:
            # Construir la URL completa con parámetro query
            base_url = license_obj.url_server.rstrip('/')
            validation_url = f"{base_url}{license_obj.license_key}"

            # Hacer la petición al servicio externo
            response = requests.get(validation_url, timeout=15)

            # Validar respuesta según el código PHP proporcionado
            if response.status_code == 200 and response.text.strip() == "1":
                log_info(
                    user=getattr(self.request, 'user', None),
                    url=getattr(self.request, 'path', 'N/A'),
                    file_name="LoginTempView",
                    message=(
                        f"Licencia {license_obj.license_key} validada "
                        f"exitosamente"
                    ),
                    request=getattr(self, 'request', None)
                )
                return True
            elif response.status_code == 404 and response.text.strip() == "0":
                log_warning(
                    user=getattr(self.request, 'user', None),
                    url=getattr(self.request, 'path', 'N/A'),
                    file_name="LoginTempView",
                    message=(
                        f"Licencia {license_obj.license_key} no encontrada "
                        f" {validation_url} "
                        f"en servicio externo"
                    ),
                    request=getattr(self, 'request', None)
                )
                return False
            else:
                log_error(
                    user=getattr(self.request, 'user', None),
                    url=getattr(self.request, 'path', 'N/A'),
                    file_name="LoginTempView",
                    message=(
                        f"Respuesta inesperada del servicio: "
                        f"{response.status_code} - {response.text}"
                    ),
                    request=getattr(self, 'request', None)
                )
                return False

        except requests.exceptions.Timeout:
            log_error(
                user=getattr(self.request, 'user', None),
                url=getattr(self.request, 'path', 'N/A'),
                file_name="LoginTempView",
                message=(
                    f"Timeout al validar licencia {license_obj.license_key}"
                ),
                request=getattr(self, 'request', None)
            )
            return False
        except requests.exceptions.RequestException as e:
            log_error(
                user=getattr(self.request, 'user', None),
                url=getattr(self.request, 'path', 'N/A'),
                file_name="LoginTempView",
                message=(
                    f"Error al validar licencia {license_obj.license_key}: "
                    f"{str(e)}"
                ),
                request=getattr(self, 'request', None)
            )
            return False
        except Exception as e:
            log_error(
                user=getattr(self.request, 'user', None),
                url=getattr(self.request, 'path', 'N/A'),
                file_name="LoginTempView",
                message=(
                    f"Error inesperado al validar licencia "
                    f"{license_obj.license_key}: {str(e)}"
                ),
                request=getattr(self, 'request', None)
            )
            return False

    def validate_user_licenses(self, user):
        """
        Valida todas las licencias activas del usuario.

        Args:
            user: Usuario autenticado

        Returns:
            bool: True si tiene al menos una licencia válida,
                  False en caso contrario
        """
        # Obtener licencias activas y no expiradas del usuario
        active_licenses = License.objects.filter(
            user=user,
            is_active=True,
            is_deleted=False
        ).exclude(expires_on__lt=timezone.now())

        if not active_licenses.exists():
            log_warning(
                user=user,
                url=getattr(self.request, 'path', 'N/A'),
                file_name="LoginTempView",
                message=f"Usuario {user.email} no tiene licencias activas",
                request=getattr(self, 'request', None)
            )
            return False

        # Validar cada licencia contra el servicio externo
        valid_licenses = []
        for license_obj in active_licenses:
            if self.validate_license_with_external_service(license_obj):
                valid_licenses.append(license_obj)

        if valid_licenses:
            log_info(
                user=user,
                url=getattr(self.request, 'path', 'N/A'),
                file_name="LoginTempView",
                message=(
                    f"Usuario {user.email} tiene {len(valid_licenses)} "
                    f"licencia(s) válida(s)"
                ),
                request=getattr(self, 'request', None)
            )
            return True
        else:
            log_warning(
                user=user,
                url=getattr(self.request, 'path', 'N/A'),
                file_name="LoginTempView",
                message=(
                    f"Usuario {user.email} no tiene licencias válidas "
                    f"en el servicio externo"
                ),
                request=getattr(self, 'request', None)
            )
            return False

    def form_valid(self, form):
        """
        Valida el formulario de login y las licencias del usuario.

        Ajusta la duración de la sesión según el checkbox 'remember'.
        Si el usuario marca 'remember', la sesión dura 2 semanas;
        de lo contrario expira al cerrar el navegador (0 => cookie de sesión).
        """
        # Obtener el usuario antes de procesar el login
        user = form.get_user()

        log_info(
            user=user,
            url=self.request.path,
            file_name="LoginTempView",
            message=f"Intento de login para usuario: {user.email}",
            request=self.request
        )

        # Validar licencias del usuario
        if not self.validate_user_licenses(user):
            log_warning(
                user=user,
                url=self.request.path,
                file_name="LoginTempView",
                message=(
                    f"Login fallido para {user.email}: Sin licencias válidas"
                ),
                request=self.request
            )
            messages.error(
                self.request,
                'No tienes licencias válidas activas. '
                'Contacta al administrador.'
            )
            return self.form_invalid(form)

        # Si las licencias son válidas, proceder con el login normal
        remember = self.request.POST.get('remember')
        response = super().form_valid(form)

        if remember:
            self.request.session.set_expiry(1209600)  # 14 días
            session_type = "persistente (14 días)"
        else:
            self.request.session.set_expiry(0)  # Hasta cerrar navegador
            session_type = "temporal (hasta cerrar navegador)"

        log_info(
            user=user,
            url=self.request.path,
            file_name="LoginTempView",
            message=(
                f"Login exitoso para {user.email} - Sesión: {session_type}"
            ),
            request=self.request
        )

        messages.success(
            self.request,
            'Inicio de sesión exitoso. Licencias validadas.'
        )
        return response
