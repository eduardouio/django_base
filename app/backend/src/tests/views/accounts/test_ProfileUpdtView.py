import pytest
from django.urls import reverse
from django.test import Client
from accounts.models import CustomUserModel


@pytest.mark.django_db
class TestProfileUpdtView:
    @pytest.fixture
    def user(self):
        return CustomUserModel.objects.create_user(
            email='editprofile@example.com',
            password='pass12345',
            first_name='Old'
        )

    def test_get_update_form(self, user):
        client = Client()
        client.force_login(user)
        url = reverse('accounts:profile_edit')
        resp = client.get(url)
        assert resp.status_code == 200
        assert 'Editar Perfil' in resp.content.decode()

    def test_post_valid_update(self, user):
        client = Client()
        client.force_login(user)
        url = reverse('accounts:profile_edit')
        resp = client.post(url, {
            'first_name': 'New',
            'last_name': 'Name',
            'email': 'editprofile@example.com',
            'notes': 'Hola'
        })
        assert resp.status_code == 302
        user.refresh_from_db()
        assert user.first_name == 'New'
        assert user.last_name == 'Name'

    def test_email_duplicate_invalid(self, user):
        other = CustomUserModel.objects.create_user(
            email='other@example.com', password='pass12345'
        )
        client = Client()
        client.force_login(user)
        url = reverse('accounts:profile_edit')
        resp = client.post(url, {
            'first_name': 'X',
            'last_name': 'Y',
            'email': other.email,
            'notes': ''
        })
        # Debe mantenerse en la página con errores
        assert resp.status_code == 200
        assert 'ya está siendo utilizado' in resp.content.decode()
