"""Aviso por correo a settings.ADMINS cuando aparece un error nuevo o reabierto."""

from django.conf import settings
from django.urls import reverse

from common.utils.request import get_site_url


def get_admin_emails():
    emails = []
    for admin in getattr(settings, 'ADMINS', []):
        emails.append(admin[1] if isinstance(admin, (tuple, list)) else admin)
    return emails


def notify_admins(error):
    recipients = get_admin_emails()
    if not recipients:
        return None

    from common.EmailService import EmailService

    detail_url = get_site_url() + reverse(
        'system:error_detail', args=[error.pk]
    )
    status = 'Reabierto' if error.occurrences > 1 else 'Nuevo'
    return EmailService.send(
        to=recipients,
        subject=f'[{settings.SITE_NAME}] {status} error: '
                f'{error.exception_type or error.level} en {error.url or error.logger_name}'[:250],
        template='error_alert',
        context={'error': error, 'detail_url': detail_url, 'status': status},
        async_send=True,
    )
