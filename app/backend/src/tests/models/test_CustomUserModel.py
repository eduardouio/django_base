import pytest
from django.db import IntegrityError
from accounts.models.CustomUserModel import CustomUserModel


@pytest.mark.django_db
class TestCustomUserModel:
    def test_create_user_success(self):
        user = CustomUserModel.objects.create_user(
            email='test@example.com',
            password='testpassword123'
        )
        assert user.pk is not None
        assert user.email == 'test@example.com'
        assert user.check_password('testpassword123')
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.is_confirmed_mail is False

    def test_create_user_without_email_raises_value_error(self):
        with pytest.raises(ValueError):
            CustomUserModel.objects.create_user(email='', password='pass')

    def test_email_must_be_unique(self):
        CustomUserModel.objects.create_user(
            email='dup@example.com', password='x'
        )
        with pytest.raises(IntegrityError):
            CustomUserModel.objects.create_user(
                email='dup@example.com', password='y'
            )

    def test_create_superuser(self):
        su = CustomUserModel.objects.create_superuser(
            email='admin@example.com',
            password='adminpass'
        )
        assert su.is_staff is True
        assert su.is_superuser is True
        assert su.is_active is True

    def test_get_classmethod_found(self):
        CustomUserModel.objects.create_user(
            email='findme@example.com', password='pwd'
        )
        found = CustomUserModel.get('findme@example.com')
        assert found is not None
        assert found.email == 'findme@example.com'

    def test_get_classmethod_not_found(self):
        assert CustomUserModel.get('idontexist@example.com') is None

    def test_str_returns_email(self):
        user = CustomUserModel.objects.create_user(
            email='str@example.com', password='pwd'
        )
        assert str(user) == 'str@example.com'
