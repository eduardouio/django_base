"""
Contexto de la petición actual para el sistema de logs.

Usa contextvars para que funcione igual con WSGI (hilos) y ASGI (async).
"""

import uuid
from contextvars import ContextVar

_request_id = ContextVar('request_id', default='-')
_request = ContextVar('request', default=None)


def new_request_id():
    """Genera un identificador corto para correlacionar logs de una petición."""
    return uuid.uuid4().hex[:12]


def set_request(request, request_id):
    """Registra la petición actual; retorna tokens para restaurar el contexto."""
    return _request.set(request), _request_id.set(request_id)


def reset_request(tokens):
    request_token, request_id_token = tokens
    _request.reset(request_token)
    _request_id.reset(request_id_token)


def get_request_id():
    return _request_id.get()


def get_current_request():
    return _request.get()
