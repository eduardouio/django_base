"""Vistas de error personalizadas (ver handler500 en config/urls.py)."""

from django.http import HttpResponseServerError
from django.template import loader

from common.logging.context import get_request_id


def server_error(request, template_name='500.html'):
    """
    Igual que la vista 500 de Django, pero muestra el request_id para que el
    usuario pueda reportarlo y se encuentre en el registro de errores.
    """
    template = loader.get_template(template_name)
    request_id = getattr(request, 'request_id', None) or get_request_id()
    return HttpResponseServerError(
        template.render({'request_id': request_id})
    )
