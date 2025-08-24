"""
Middleware para logging automático de peticiones HTTP.
"""

from common.LoggerApp import log_info, log_error, log_warning
import time


class LoggingMiddleware:
    """
    Middleware que registra automáticamente todas las peticiones HTTP.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Registrar inicio de petición
        start_time = time.time()

        user = request.user if hasattr(request, 'user') else None
        url = request.get_full_path()
        method = request.method

        # Log de acceso
        log_info(
            user=user,
            url=url,
            file_name="LoggingMiddleware",
            message=f"Petición {method} iniciada",
            request=request
        )

        try:
            response = self.get_response(request)

            # Calcular tiempo de respuesta
            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 2)  # en ms

            # Log de respuesta exitosa
            log_info(
                user=user,
                url=url,
                file_name="LoggingMiddleware",
                message=(f"Petición {method} completada - "
                         f"Status: {response.status_code} - "
                         f"Tiempo: {response_time}ms"),
                request=request
            )

            # Log de warning para respuestas lentas (más de 2 segundos)
            if response_time > 2000:
                log_warning(
                    user=user,
                    url=url,
                    file_name="LoggingMiddleware",
                    message=f"Respuesta lenta detectada: {response_time}ms",
                    request=request
                )

            return response

        except Exception as e:
            # Log de error en caso de excepción
            log_error(
                user=user,
                url=url,
                file_name="LoggingMiddleware",
                message=f"Error en petición {method}: {str(e)}",
                request=request
            )
            raise

    def process_exception(self, request, exception):
        """
        Procesa excepciones no capturadas.
        """
        user = request.user if hasattr(request, 'user') else None
        url = request.get_full_path()

        log_error(
            user=user,
            url=url,
            file_name="LoggingMiddleware",
            message=(f"Excepción no capturada: {type(exception).__name__}: "
                     f"{str(exception)}"),
            request=request
        )

        # Retornar None permite que Django maneje la excepción normalmente
        return None
