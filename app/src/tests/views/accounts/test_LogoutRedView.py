import pytest
from django.urls import reverse
from django.test import Client
from accounts.models import CustomUserModel


@pytest.mark.django_db
class TestLogoutRedView:
    @pytest.fixture
    def user(self):
        return CustomUserModel.objects.create_user(
            email='logoutuser@example.com', password='pass12345'
        )

    def test_logout_redirects(self, user):
        client = Client()
        client.force_login(user)
        url = reverse('accounts:logout')
        resp = client.get(url)
        assert resp.status_code == 302
        assert resp.url == reverse('accounts:login')

    def test_logout_post(self, user):
        client = Client()
        client.force_login(user)
        url = reverse('accounts:logout')
        resp = client.post(url)
        assert resp.status_code == 302
        assert resp.url == reverse('accounts:login')
