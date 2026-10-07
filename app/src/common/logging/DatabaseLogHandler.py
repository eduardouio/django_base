"""
Handler de logging que guarda los errores (ERROR+) en el modelo system.ErrorLog.

- Agrupa errores repetidos por "fingerprint" (tipo de excepción + ubicación),
  sumando ocurrencias en lugar de crear un registro por cada vez.
- Si un error resuelto vuelve a ocurrir, se reabre.
- En errores nuevos o reabiertos notifica por correo a settings.ADMINS.
- Nunca lanza excepciones: si la BD no está disponible el error queda solo
  en los archivos de log.
"""

import hashlib
import logging
import traceback
from contextvars import ContextVar

from common.logging.context import get_current_request

_emitting = ContextVar('db_log_handler_emitting', default=False)


class DatabaseLogHandler(logging.Handler):

    def emit(self, record):
        # Evita recursión si guardar el error produce otro log de error
        if _emitting.get():
            return
        token = _emitting.set(True)
        try:
            self._save(record)
        except Exception:
            # No usar logging aquí: provocaría recursión
            pass
        finally:
            _emitting.reset(token)

    def _save(self, record):
        from django.apps import apps
        if not apps.ready:
            return

        from django.db import transaction
        from django.utils import timezone
        from system.models import ErrorLog
        from common.utils.request import (
            get_client_ip, get_user_agent, sanitize_data
        )

        exception_type = ''
        trace = ''
        location = f'{record.pathname}:{record.lineno}'
        if record.exc_info and record.exc_info[0]:
            exc_type, exc_value, exc_tb = record.exc_info
            exception_type = exc_type.__name__
            trace = ''.join(
                traceback.format_exception(exc_type, exc_value, exc_tb)
            )
            frames = traceback.extract_tb(exc_tb)
            if frames:
                location = f'{frames[-1].filename}:{frames[-1].lineno}'

        fingerprint = hashlib.sha1(
            f'{record.name}|{record.levelno}|{exception_type}|{location}'
            .encode()
        ).hexdigest()

        request = getattr(record, 'request', None) or get_current_request()
        # django.request adjunta el request; otros loggers podrían no hacerlo
        if request is not None and not hasattr(request, 'META'):
            request = None

        user = None
        url = method = ip = user_agent = ''
        request_data = {}
        if request is not None:
            req_user = getattr(request, 'user', None)
            if req_user is not None and req_user.is_authenticated:
                user = req_user
            url = request.get_full_path()[:500]
            method = request.method or ''
            ip = get_client_ip(request)
            user_agent = get_user_agent(request)
            request_data = {
                'GET': sanitize_data(request.GET),
                'POST': sanitize_data(request.POST)
                if method == 'POST' else {},
            }

        status_code = getattr(record, 'status_code', None)
        message = record.getMessage()[:5000]
        now = timezone.now()

        with transaction.atomic():
            error = (
                ErrorLog.objects.select_for_update()
                .filter(fingerprint=fingerprint).first()
            )
            notify = False
            if error is None:
                error = ErrorLog(fingerprint=fingerprint, first_seen=now)
                notify = True
            else:
                error.occurrences += 1
                if error.is_resolved:
                    error.is_resolved = False
                    error.resolved_at = None
                    error.resolved_by = None
                    notify = True

            error.level = record.levelname
            error.logger_name = record.name
            error.message = message
            error.exception_type = exception_type
            error.traceback = trace
            error.location = location[:500]
            error.last_seen = now
            error.url = url
            error.method = method
            error.status_code = status_code
            error.user = user
            error.ip = ip
            error.user_agent = user_agent
            error.request_id = getattr(record, 'request_id', '-')
            error.request_data = request_data
            error.save()

        if notify:
            from system.services.ErrorNotifier import notify_admins
            notify_admins(error)
