import pytest
from django.urls import reverse
from django.test import Client
from accounts.models import CustomUserModel


@pytest.mark.django_db
class TestLoginTempView:
    @pytest.fixture
    def user(self):
        return CustomUserModel.objects.create_user(
            email='loginuser@example.com', password='pass12345'
        )

    def test_get_login_page_anonymous(self):
        client = Client()
        url = reverse('accounts:login')
        resp = client.get(url)
        assert resp.status_code == 200

    def test_redirect_if_authenticated(self, user):
        client = Client()
        client.force_login(user)
        # LoginView con redirect_authenticated_user=True debe redirigir
        url = reverse('accounts:login')
        resp = client.get(url)
        assert resp.status_code in (302, 301)
        # Debe terminar en home
        home_url = reverse('home')
        assert home_url in resp.url
