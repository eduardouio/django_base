"""Utilidades para obtener información del request."""

import re


def get_client_ip(request):
    """Retorna la IP del cliente respetando proxies (X-Forwarded-For)."""
    if request is None:
        return None
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def get_user_agent(request):
    if request is None:
        return ''
    return request.META.get('HTTP_USER_AGENT', '')[:500]


_BROWSERS = (
    ('Edge', r'Edg(?:e|A|iOS)?/([\d]+)'),
    ('Opera', r'(?:OPR|Opera)/([\d]+)'),
    ('Chrome', r'(?:Chrome|CriOS)/([\d]+)'),
    ('Firefox', r'(?:Firefox|FxiOS)/([\d]+)'),
    ('Safari', r'Version/([\d]+).*Safari'),
)

_SYSTEMS = (
    ('Android', r'Android'),
    ('iOS', r'iPhone|iPad|iPod'),
    ('Windows', r'Windows'),
    ('macOS', r'Mac OS X|Macintosh'),
    ('Linux', r'Linux'),
)


def parse_user_agent(user_agent):
    """Describe navegador y sistema operativo de un User-Agent, ej: 'Chrome 120 · Windows'."""
    if not user_agent:
        return 'Desconocido'
    browser = next(
        (f'{name} {m.group(1)}' for name, pattern in _BROWSERS
         if (m := re.search(pattern, user_agent))),
        'Otro navegador'
    )
    system = next(
        (name for name, pattern in _SYSTEMS if re.search(pattern, user_agent)),
        'Otro SO'
    )
    return f'{browser} · {system}'


SENSITIVE_KEYS = ('password', 'passwd', 'token', 'secret', 'csrf', 'key')


def sanitize_data(data):
    """Copia un QueryDict/dict ocultando valores sensibles (contraseñas, tokens)."""
    if not data:
        return {}
    clean = {}
    for key in data.keys():
        values = data.getlist(key) if hasattr(data, 'getlist') else [data[key]]
        if any(word in key.lower() for word in SENSITIVE_KEYS):
            clean[key] = '***'
        else:
            value = values if len(values) > 1 else values[0]
            clean[key] = str(value)[:1000]
    return clean


def get_site_url(request=None):
    """
    URL base del sistema para enlaces absolutos (correos).
    Prioridad: settings.SITE_URL > request (o el request actual) > localhost.
    """
    from django.conf import settings
    from common.logging.context import get_current_request

    if getattr(settings, 'SITE_URL', None):
        return settings.SITE_URL.rstrip('/')
    request = request or get_current_request()
    if request is not None:
        return request.build_absolute_uri('/').rstrip('/')
    return 'http://localhost:8000'
