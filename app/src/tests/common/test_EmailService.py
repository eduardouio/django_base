import pytest
from django.core import mail

from common.EmailService import EmailService
from system.models import EmailLog


@pytest.mark.django_db
class TestEmailService:

    def test_send_html_with_text_alternative_and_log(self):
        log = EmailService.send(
            to='cliente@example.com',
            subject='Prueba',
            template='test_email',
            context={'user': None},
            cc=['copia@example.com'],
            attachments=[('nota.txt', b'hola', 'text/plain')],
        )
        assert len(mail.outbox) == 1
        message = mail.outbox[0]
        assert message.to == ['cliente@example.com']
        assert message.cc == ['copia@example.com']
        assert message.alternatives[0][1] == 'text/html'
        assert 'Correo de prueba' in message.alternatives[0][0]
        assert '<table' not in message.body  # texto plano sin HTML
        assert message.attachments[0][0] == 'nota.txt'

        log.refresh_from_db()
        assert log.status == EmailLog.SENT
        assert log.sent_at is not None
        assert log.cc == 'copia@example.com'

    def test_failure_is_logged_not_raised(self, mocker):
        mocker.patch(
            'django.core.mail.EmailMultiAlternatives.send',
            side_effect=ConnectionRefusedError('SMTP caído')
        )
        log = EmailService.send(
            to='x@example.com', subject='Falla', template='test_email',
            context={'user': None}
        )
        log.refresh_from_db()
        assert log.status == EmailLog.FAILED
        assert 'SMTP caído' in log.error

    def test_async_send_runs_in_thread_on_commit(
            self, settings, mocker, django_capture_on_commit_callbacks):
        settings.EMAIL_ASYNC = True
        thread_cls = mocker.patch('common.EmailService.threading.Thread')

        with django_capture_on_commit_callbacks(execute=True):
            log = EmailService.send(
                to='x@example.com', subject='Async', template='test_email',
                context={'user': None}, async_send=True
            )
            # Antes del commit no se lanza el hilo
            thread_cls.assert_not_called()

        thread_cls.assert_called_once()
        assert thread_cls.call_args.kwargs['args'][1] == log.pk
        thread_cls.return_value.start.assert_called_once()
        assert log.status == EmailLog.PENDING
        assert mail.outbox == []
