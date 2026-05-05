import pytest
from django.urls import reverse
from django.test import Client
from accounts.models import CustomUserModel


@pytest.mark.django_db
class TestProfileTempView:
    @pytest.fixture
    def user(self):
        return CustomUserModel.objects.create_user(
            email='profile@example.com', password='pass12345', first_name='A'
        )

    def test_profile_requires_login(self):
        client = Client()
        url = reverse('accounts:profile')
        resp = client.get(url)
        assert resp.status_code == 302
        assert reverse('accounts:login') in resp.url

    def test_profile_context(self, user):
        client = Client()
        client.force_login(user)
        url = reverse('accounts:profile')
        resp = client.get(url)
        assert resp.status_code == 200
        assert resp.context['title'] == 'Mi Perfil'
        assert resp.context['user'] == user
