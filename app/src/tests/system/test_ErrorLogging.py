import logging

import pytest
from django.core import mail
from django.test import Client
from django.urls import reverse

from accounts.models import CustomUserModel
from accounts.views.HomeTempView import HomeTempView
from common.LoggerApp import log_error, log_exception
from system.models import ErrorLog


@pytest.fixture
def user(db):
    return CustomUserModel.objects.create_user(
        email='err@example.com', password='Clave-Segura-2026'
    )


def raise_and_log():
    try:
        {}['falta']
    except KeyError:
        log_exception(None, '/x', 'TestFile', 'Fallo controlado')


@pytest.mark.django_db
class TestDatabaseLogHandler:

    def test_same_error_is_grouped(self, settings):
        settings.ADMINS = [('Admin', 'admin@example.com')]
        raise_and_log()
        raise_and_log()

        assert ErrorLog.objects.count() == 1
        error = ErrorLog.objects.get()
        assert error.occurrences == 2
        assert error.exception_type == 'KeyError'
        assert "KeyError: 'falta'" in error.traceback
        assert 'test_ErrorLogging.py' in error.location
        # Solo se avisa la primera vez
        assert len(mail.outbox) == 1
        assert 'admin@example.com' in mail.outbox[0].to

    def test_resolved_error_is_reopened_and_notified(self, settings):
        settings.ADMINS = ['admin@example.com']
        raise_and_log()
        ErrorLog.objects.update(is_resolved=True)
        raise_and_log()
        error = ErrorLog.objects.get()
        assert error.is_resolved is False
        assert len(mail.outbox) == 2
        assert 'Reabierto' in mail.outbox[1].subject

    def test_log_error_without_exception_points_to_caller(self):
        log_error(None, '/y', 'TestFile', 'Error sin excepción')
        error = ErrorLog.objects.get()
        assert 'test_ErrorLogging.py' in error.location
        assert error.traceback == ''

    def test_warning_is_not_stored(self):
        logging.getLogger('app_logger').warning('solo advertencia')
        assert ErrorLog.objects.count() == 0

    def test_unhandled_view_exception(self, user, mocker):
        mocker.patch.object(
            HomeTempView, 'get_context_data',
            side_effect=ZeroDivisionError('division by zero')
        )
        client = Client(raise_request_exception=False)
        client.force_login(user)
        response = client.get(reverse('home') + '?filtro=1')

        assert response.status_code == 500
        request_id = response['X-Request-ID']
        assert request_id.encode() in response.content

        error = ErrorLog.objects.get()
        assert error.exception_type == 'ZeroDivisionError'
        assert error.status_code == 500
        assert error.user == user
        assert error.method == 'GET'
        assert error.url == '/?filtro=1'
        assert error.request_id == request_id
        assert error.request_data['GET'] == {'filtro': '1'}

    def test_sensitive_post_data_is_masked(self, user, mocker):
        mocker.patch(
            'accounts.views.LoginTempView.LoginTempView.post',
            side_effect=RuntimeError('fallo en login')
        )
        client = Client(raise_request_exception=False)
        client.post(reverse('accounts:login'), {
            'username': 'a@b.com', 'password': 'super-secreta'
        })
        error = ErrorLog.objects.get()
        assert error.request_data['POST']['password'] == '***'
        assert error.request_data['POST']['username'] == 'a@b.com'


@pytest.mark.django_db
def test_request_id_header_on_every_response(client):
    response = client.get(reverse('accounts:login'))
    assert len(response['X-Request-ID']) == 12


@pytest.mark.django_db
def test_unsafe_incoming_request_id_is_replaced(client):
    response = client.get(reverse('accounts:login'),
                          HTTP_X_REQUEST_ID='abc\nFAKE | ERROR')
    assert '\n' not in response['X-Request-ID']
    assert len(response['X-Request-ID']) == 12
    response = client.get(reverse('accounts:login'),
                          HTTP_X_REQUEST_ID='proxy-id-123')
    assert response['X-Request-ID'] == 'proxy-id-123'
