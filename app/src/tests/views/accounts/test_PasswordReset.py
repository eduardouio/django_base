import re
from datetime import datetime, timedelta

import pytest
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core import mail
from django.urls import reverse

from accounts.models import CustomUserModel
from system.models import EmailLog

OLD_PASSWORD = 'Clave-Anterior-2026'
NEW_PASSWORD = 'Nueva-Clave-Segura-77'


@pytest.fixture
def user(db):
    user = CustomUserModel.objects.create_user(
        email='reset@example.com', password=OLD_PASSWORD
    )
    return user


def request_reset_link(client, email='reset@example.com'):
    response = client.post(reverse('accounts:password_reset'), {'email': email})
    assert response.status_code == 302
    assert response.url == reverse('accounts:password_reset_done')
    if not mail.outbox:
        return None
    match = re.search(r'http://testserver(/password-reset/[^/\s]+/[^/\s]+/)',
                      mail.outbox[-1].body)
    return match.group(1)


def set_new_password(client, link):
    # Django redirige el token a una URL "set-password" guardada en sesión
    response = client.get(link)
    assert response.status_code == 302
    return client.post(response.url, {
        'new_password1': NEW_PASSWORD,
        'new_password2': NEW_PASSWORD,
    })


@pytest.mark.django_db
class TestPasswordReset:

    def test_login_has_forgot_password_link(self, client):
        response = client.get(reverse('accounts:login'))
        assert reverse('accounts:password_reset').encode() in response.content

    def test_full_flow(self, client, user):
        link = request_reset_link(client)
        assert link is not None
        message = mail.outbox[0]
        assert message.to == ['reset@example.com']
        assert '10 minutos' in message.body
        assert EmailLog.objects.filter(
            template='password_reset', status=EmailLog.SENT).exists()

        response = set_new_password(client, link)
        assert response.status_code == 302
        assert response.url == reverse('accounts:password_reset_complete')

        user.refresh_from_db()
        assert user.check_password(NEW_PASSWORD)
        # Aviso de contraseña cambiada
        assert mail.outbox[-1].subject.startswith('Tu contraseña fue cambiada')

    def test_link_is_single_use(self, client, user):
        link = request_reset_link(client)
        set_new_password(client, link)

        response = client.get(link, follow=True)
        assert response.context['validlink'] is False
        assert 'Enlace no válido' in response.content.decode()

    def test_link_expires_after_10_minutes(self, client, user, mocker):
        link = request_reset_link(client)
        mocker.patch.object(
            PasswordResetTokenGenerator, '_now',
            return_value=datetime.now() + timedelta(minutes=11)
        )
        response = client.get(link, follow=True)
        assert response.context['validlink'] is False
        user.refresh_from_db()
        assert user.check_password(OLD_PASSWORD)

    def test_link_valid_before_10_minutes(self, client, user, mocker):
        link = request_reset_link(client)
        mocker.patch.object(
            PasswordResetTokenGenerator, '_now',
            return_value=datetime.now() + timedelta(minutes=9)
        )
        response = client.get(link, follow=True)
        assert response.context['validlink'] is True

    def test_unknown_email_same_response_and_no_mail(self, client, user):
        link = request_reset_link(client, email='nadie@example.com')
        assert link is None
        assert mail.outbox == []

    def test_rate_limit(self, client, user, settings):
        settings.PASSWORD_RESET_MAX_ATTEMPTS = 2
        url = reverse('accounts:password_reset')
        for _ in range(2):
            assert client.post(url, {'email': user.email}).status_code == 302
        response = client.post(url, {'email': user.email})
        assert response.status_code == 200
        assert 'demasiadas solicitudes' in response.content.decode()
        assert len(mail.outbox) == 2

    def test_weak_password_rejected(self, client, user):
        link = request_reset_link(client)
        response = client.get(link)
        response = client.post(response.url, {
            'new_password1': '12345678', 'new_password2': '12345678'
        })
        assert response.status_code == 200
        assert 'completamente numérica' in response.content.decode()
