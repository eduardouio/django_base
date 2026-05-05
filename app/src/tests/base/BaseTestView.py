import pytest
from django.test import Client
from django.urls import reverse
from accounts.models import CustomUserModel


@pytest.mark.django_db
class BaseTestView():

    @pytest.fixture
    def client_logged(self):
        user, created = CustomUserModel.objects.get_or_create(
            email='eduardouio7@gmail.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
                # Agrega aquí otros campos obligatorios si es necesario
            }
        )
        client = Client()
        client.force_login(user)
        return client

    @pytest.fixture
    def client_not_logged(self):
        return Client()

    def test_client_logged(self, client_logged, url):
        response = client_logged.get(url)
        assert response.status_code == 200

    def test_client_not_logged(self, client_not_logged, url):
        response = client_not_logged.get(url)
        url_reponse = reverse('accounts:login') + '?next=' + url
        assert response.status_code == 302
        assert response.url == url_reponse
