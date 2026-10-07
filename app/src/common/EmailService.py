"""
Servicio reutilizable para enviar correos HTML con plantillas.

Uso:
    from common.EmailService import EmailService

    EmailService.send(
        to='cliente@correo.com',
        subject='Su factura',
        template='invoice',               # emails/invoice.html (+ .txt opcional)
        context={'invoice': invoice},
        attachments=[('factura.pdf', pdf_bytes, 'application/pdf')],
        async_send=True,                  # no bloquea la petición
    )

Cada envío queda registrado en system.EmailLog (pendiente/enviado/fallido).
Los fallos se registran como WARNING (no ERROR) para que una caída del SMTP
no genere alertas de error que a su vez intenten enviar más correos.
"""

import mimetypes
import threading
from pathlib import Path

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import close_old_connections, connection, transaction
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from common.LoggerApp import log_info, log_warning
from common.utils.request import get_site_url


def _as_list(value):
    if not value:
        return []
    if isinstance(value, str):
        return [value]
    return list(value)


class EmailService:

    @classmethod
    def send(cls, to, subject, template, context=None, attachments=None,
             cc=None, bcc=None, reply_to=None, from_email=None,
             async_send=False, user=None):
        """
        Envía un correo renderizando emails/<template>.html.

        Args:
            to: correo o lista de correos
            subject: asunto
            template: nombre de la plantilla sin extensión, dentro de emails/
            context: dict para la plantilla (se agregan site_name y site_url)
            attachments: lista de rutas de archivo o tuplas
                         (nombre, contenido, mimetype)
            cc, bcc, reply_to: correo o lista de correos
            from_email: remitente; por defecto DEFAULT_FROM_EMAIL
            async_send: True para enviar en segundo plano al confirmar la
                        transacción actual (se ignora si settings.EMAIL_ASYNC
                        es False, útil en pruebas)
            user: usuario que dispara el envío (para el registro)

        Returns:
            EmailLog: registro del envío. Con async_send=True su estado
            queda PENDING hasta que el hilo termina.
        """
        from system.models import EmailLog

        to, cc, bcc = _as_list(to), _as_list(cc), _as_list(bcc)
        message = cls.build_message(
            to, subject, template, context, attachments, cc, bcc,
            _as_list(reply_to), from_email
        )
        email_log = EmailLog.objects.create(
            to=', '.join(to),
            cc=', '.join(cc),
            bcc=', '.join(bcc),
            subject=subject[:255],
            template=template,
            triggered_by=user if user is not None and user.is_authenticated
            else None,
        )

        if async_send and getattr(settings, 'EMAIL_ASYNC', True):
            transaction.on_commit(
                lambda: threading.Thread(
                    target=cls._deliver_in_thread,
                    args=(message, email_log.pk),
                    daemon=True,
                ).start()
            )
        else:
            cls._deliver(message, email_log)
        return email_log

    @classmethod
    def build_message(cls, to, subject, template, context=None,
                      attachments=None, cc=None, bcc=None, reply_to=None,
                      from_email=None):
        context = {
            'site_name': settings.SITE_NAME,
            'site_url': get_site_url(),
            'subject': subject,
            **(context or {}),
        }
        html_body = render_to_string(f'emails/{template}.html', context)
        try:
            text_body = render_to_string(f'emails/{template}.txt', context)
        except TemplateDoesNotExist:
            text_body = strip_tags(html_body)

        message = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=from_email or settings.DEFAULT_FROM_EMAIL,
            to=to,
            cc=cc,
            bcc=bcc,
            reply_to=reply_to,
        )
        message.attach_alternative(html_body, 'text/html')

        for attachment in attachments or []:
            if isinstance(attachment, (tuple, list)):
                message.attach(*attachment)
            else:
                path = Path(attachment)
                mimetype = mimetypes.guess_type(path.name)[0]
                message.attach(path.name, path.read_bytes(), mimetype)
        return message

    @classmethod
    def _deliver(cls, message, email_log):
        try:
            message.send(fail_silently=False)
        except Exception as e:
            email_log.status = email_log.FAILED
            email_log.error = f'{type(e).__name__}: {e}'
            email_log.save(update_fields=['status', 'error'])
            log_warning(
                user=None,
                url='N/A',
                file_name='EmailService',
                message=(f"Fallo al enviar '{message.subject}' a "
                         f"{', '.join(message.to)}: {email_log.error}"),
            )
            return False

        email_log.status = email_log.SENT
        email_log.sent_at = timezone.now()
        email_log.save(update_fields=['status', 'sent_at'])
        log_info(
            user=None,
            url='N/A',
            file_name='EmailService',
            message=f"Correo '{message.subject}' enviado a "
                    f"{', '.join(message.to)}",
        )
        return True

    @classmethod
    def _deliver_in_thread(cls, message, email_log_id):
        from system.models import EmailLog

        close_old_connections()
        try:
            email_log = EmailLog.objects.get(pk=email_log_id)
            cls._deliver(message, email_log)
        finally:
            connection.close()
