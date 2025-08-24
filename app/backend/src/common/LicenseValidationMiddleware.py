"""
Middleware para validación periódica de licencias de usuarios autenticados.
Realiza validaciones automáticas según intervalos configurables por rol.
"""

from django.contrib.auth import logout
from django.contrib import messages
from django.utils import timezone
from django.shortcuts import redirect
from django.urls import reverse
from accounts.views.LoginTempView import LoginTempView
from common.LoggerApp import log_info, log_warning, log_error


class LicenseValidationMiddleware:
    """
    Middleware que valida licencias de usuarios autenticados periódicamente.

    Características:
    - Validación automática basada en intervalos configurables
    - Diferentes intervalos según el rol/tipo de usuario
    - Integración con el sistema de logging existente
    - Cierre automático de sesión en caso de licencia inválida
    """

    # Intervalo de validación único para todos los usuarios
    VALIDATION_INTERVAL = 1800  # 30 minutos

    # URLs que se excluyen de la validación (para evitar loops infinitos)
    EXCLUDED_URLS = [
        '/accounts/login/',
        '/accounts/logout/',
        '/admin/login/',
        '/admin/logout/',
        '/static/',
        '/media/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response
        # Instanciar LoginTempView para reutilizar métodos de validación
        self.login_view = LoginTempView()

    def __call__(self, request):
        # Solo validar para usuarios autenticados
        if request.user.is_authenticated:
            validation_result = self._check_license_validation_schedule(
                request
            )

            # Si la validación falló, redirigir al login
            if validation_result is False:
                return self._handle_invalid_license(request)

        response = self.get_response(request)
        return response

    def _check_license_validation_schedule(self, request):
        """
        Verifica si es necesario validar las licencias del usuario
        y ejecuta la validación si corresponde.

        Args:
            request: HttpRequest object

        Returns:
            bool: True si las licencias son válidas o no requiere validación,
                  False si las licencias son inválidas
        """
        # Excluir URLs específicas
        if self._should_exclude_url(request.path):
            return True

        # Determinar el intervalo de validación (siempre 30 minutos)
        validation_interval = self.VALIDATION_INTERVAL

        # Verificar si es tiempo de validar
        if not self._is_validation_time(request, validation_interval):
            # Verificar que tengamos confirmación previa de licencia válida
            return request.session.get('license_valid', True)

        # Ejecutar validación de licencias
        log_info(
            user=request.user,
            url=request.path,
            file_name="LicenseValidationMiddleware",
            message="Iniciando validación periódica de licencias",
            request=request
        )

        try:
            is_valid = self.login_view.validate_user_licenses(request.user)

            # Actualizar estado en sesión
            current_time = timezone.now().timestamp()
            request.session['last_license_check'] = current_time
            request.session['license_valid'] = is_valid

            if is_valid:
                log_info(
                    user=request.user,
                    url=request.path,
                    file_name="LicenseValidationMiddleware",
                    message="Validación periódica exitosa",
                    request=request
                )
            else:
                log_warning(
                    user=request.user,
                    url=request.path,
                    file_name="LicenseValidationMiddleware",
                    message="Validación periódica falló - licencias inválidas",
                    request=request
                )

            return is_valid

        except Exception as e:
            log_error(
                user=request.user,
                url=request.path,
                file_name="LicenseValidationMiddleware",
                message=f"Error en validación periódica: {str(e)}",
                request=request
            )
            # En caso de error, mantener sesión activa pero marcar
            # para re-validación
            request.session['license_valid'] = True
            next_check = (timezone.now().timestamp() -
                          (validation_interval - 60))
            request.session['last_license_check'] = next_check
            return True

    def _should_exclude_url(self, path):
        """
        Determina si una URL debe ser excluida de la validación.

        Args:
            path: Ruta de la URL

        Returns:
            bool: True si debe excluirse, False en caso contrario
        """
        excluded_check = any(path.startswith(excluded)
                             for excluded in self.EXCLUDED_URLS)
        return excluded_check

    def _is_validation_time(self, request, interval):
        """
        Verifica si es momento de realizar una validación.

        Args:
            request: HttpRequest object
            interval: Intervalo en segundos

        Returns:
            bool: True si debe validar, False en caso contrario
        """
        last_check = request.session.get('last_license_check')

        # Si no hay registro de validación previa, validar
        if last_check is None:
            return True

        current_time = timezone.now().timestamp()
        time_since_last_check = current_time - last_check

        return time_since_last_check >= interval

    def _handle_invalid_license(self, request):
        """
        Maneja el caso cuando las licencias del usuario son inválidas.

        Args:
            request: HttpRequest object

        Returns:
            HttpResponse: Respuesta de redirección
        """
        log_warning(
            user=request.user,
            url=request.path,
            file_name="LicenseValidationMiddleware",
            message=(f"Cerrando sesión por licencia inválida - "
                     f"Usuario: {request.user.email}"),
            request=request
        )

        # Cerrar sesión del usuario
        logout(request)

        # Agregar mensaje de error
        messages.error(
            request,
            ('Tu licencia ha expirado o es inválida. '
             'Por favor, contacta al administrador.')
        )

        # Redirigir al login
        return redirect(reverse('accounts:login'))

    def get_validation_status(self, request):
        """
        Método auxiliar para obtener el estado de validación actual.
        Útil para debugging o monitoreo.

        Args:
            request: HttpRequest object

        Returns:
            dict: Estado de validación con detalles
        """
        if not request.user.is_authenticated:
            return {'authenticated': False}

        last_check = request.session.get('last_license_check')
        license_valid = request.session.get('license_valid', False)
        current_time = timezone.now().timestamp()

        status = {
            'authenticated': True,
            'license_valid': license_valid,
            'last_check': last_check,
            'last_check_ago': ((current_time - last_check)
                               if last_check else None),
            'validation_interval': self.VALIDATION_INTERVAL,
            'next_validation_in': None
        }

        if last_check:
            time_since_check = current_time - last_check
            next_validation = max(0,
                                  self.VALIDATION_INTERVAL - time_since_check)
            status['next_validation_in'] = next_validation

        return status
