"""
Middleware para logging automático de peticiones HTTP.

- Asigna un request_id a cada petición (header X-Request-ID) que aparece en
  todas las líneas de log y en la página de error 500.
- Registra una línea por petición: método, ruta, status, tiempo, usuario e IP.
- Respuestas 4xx/5xx y lentas se registran como WARNING.

Las excepciones no controladas las registra el logger `django.request` con su
traceback completo y el handler de base de datos las guarda en system.ErrorLog.
"""

import re
import time

from django.conf import settings

from common.LoggerApp import log_info, log_warning
from common.logging.context import (
    new_request_id, reset_request, set_request
)
from common.utils.request import get_client_ip

# Solo se acepta un X-Request-ID entrante (ej: de un proxy) si es seguro de loguear
VALID_REQUEST_ID = re.compile(r'^[A-Za-z0-9._-]{1,64}$')


class LoggingMiddleware:
    """
    Middleware que registra automáticamente todas las peticiones HTTP.
    Debe ir primero en MIDDLEWARE para medir la petición completa.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.ignored_paths = tuple(getattr(settings, 'LOG_IGNORED_PATHS', ()))
        self.slow_ms = getattr(settings, 'LOG_SLOW_REQUEST_MS', 2000)

    def __call__(self, request):
        incoming = request.headers.get('X-Request-ID', '')
        request.request_id = (
            incoming if VALID_REQUEST_ID.match(incoming) else new_request_id()
        )
        tokens = set_request(request, request.request_id)
        start_time = time.monotonic()
        try:
            response = self.get_response(request)
            response['X-Request-ID'] = request.request_id
            if not request.path.startswith(self.ignored_paths):
                elapsed = round((time.monotonic() - start_time) * 1000, 2)
                self._log_response(request, response, elapsed)
            return response
        finally:
            reset_request(tokens)

    def _log_response(self, request, response, elapsed):
        user = getattr(request, 'user', None)
        message = (
            f"{request.method} {response.status_code} - {elapsed}ms - "
            f"IP: {get_client_ip(request)}"
        )
        kwargs = {
            'user': user if user is not None and user.is_authenticated else None,
            'url': request.get_full_path(),
            'file_name': 'LoggingMiddleware',
        }

        if response.status_code >= 400:
            log_warning(message=message, **kwargs)
        elif elapsed > self.slow_ms:
            log_warning(message=f"Respuesta lenta: {message}", **kwargs)
        else:
            log_info(message=message, **kwargs)
