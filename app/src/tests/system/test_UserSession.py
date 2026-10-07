from datetime import timedelta

import pytest
from django.contrib.sessions.models import Session
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from accounts.models import CustomUserModel
from system.models import UserSession

PASSWORD = 'Clave-Segura-2026'


def make_user(email, **extra):
    return CustomUserModel.objects.create_user(
        email=email, password=PASSWORD, **extra
    )


def login(email, ua='Mozilla/5.0 (Windows NT 10.0) Chrome/120.0 Safari/537.36'):
    client = Client(HTTP_USER_AGENT=ua)
    response = client.post(reverse('accounts:login'), {
        'username': email, 'password': PASSWORD
    })
    assert response.status_code == 302
    return client


@pytest.mark.django_db
class TestUserSession:

    def test_login_creates_and_logout_closes(self):
        make_user('s1@example.com')
        client = login('s1@example.com')

        session = UserSession.objects.get()
        assert session.session_key == client.session.session_key
        assert session.is_online
        assert session.device == 'Chrome 120 · Windows'

        client.post(reverse('accounts:logout'))
        session.refresh_from_db()
        assert session.logout_at is not None
        assert session.ended_reason == UserSession.LOGOUT

    def test_activity_is_throttled(self, settings):
        settings.USER_ACTIVITY_UPDATE_SECONDS = 60
        make_user('s2@example.com')
        client = login('s2@example.com')
        old = timezone.now() - timedelta(minutes=30)
        UserSession.objects.update(last_activity=old)

        client.get(reverse('home'))  # primera petición: actualiza
        first = UserSession.objects.get().last_activity
        assert first > old

        UserSession.objects.update(last_activity=old)
        client.get(reverse('home'))  # dentro de los 60 s: no escribe
        assert UserSession.objects.get().last_activity == old

    def test_online_threshold(self, settings):
        settings.ONLINE_THRESHOLD_MINUTES = 5
        make_user('s3@example.com')
        login('s3@example.com')
        assert UserSession.objects.online().count() == 1
        UserSession.objects.update(
            last_activity=timezone.now() - timedelta(minutes=6)
        )
        assert UserSession.objects.online().count() == 0
        assert UserSession.objects.open().count() == 1

    def test_force_close_logs_user_out(self):
        make_user('admin@example.com', is_superuser=True, is_staff=True)
        make_user('victim@example.com')
        admin = login('admin@example.com')
        victim = login('victim@example.com')

        session = UserSession.objects.get(user__email='victim@example.com')
        response = admin.post(reverse('system:session_close', args=[session.pk]))
        assert response.status_code == 302

        session.refresh_from_db()
        assert session.ended_reason == UserSession.FORCED
        assert not Session.objects.filter(
            session_key=session.session_key).exists()
        response = victim.get(reverse('home'))
        assert response.status_code == 302
        assert reverse('accounts:login') in response.url

    def test_cannot_close_own_session(self):
        make_user('own@example.com', is_superuser=True)
        client = login('own@example.com')
        session = UserSession.objects.get()
        client.post(reverse('system:session_close', args=[session.pk]))
        session.refresh_from_db()
        assert session.logout_at is None

    def test_expired_sessions_are_closed(self):
        make_user('exp@example.com')
        login('exp@example.com')
        Session.objects.all().delete()
        assert UserSession.close_expired() == 1
        assert UserSession.objects.get().ended_reason == UserSession.EXPIRED

    def test_json_endpoint(self):
        make_user('json@example.com', is_superuser=True)
        client = login('json@example.com')
        data = client.get(reverse('system:connected_users_data')).json()
        assert data['online_count'] == 1
        assert data['sessions'][0]['email'] == 'json@example.com'
        assert data['sessions'][0]['is_current'] is True
