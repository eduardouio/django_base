import pytest
from django.contrib.auth.models import Group, Permission
from django.test import Client
from django.urls import reverse

from accounts.models import CustomUserModel
from system.services.PermissionCatalog import get_catalog
from system.services.RoleService import sync_roles

SYSTEM_URLS = [
    ('system:dashboard', []),
    ('system:error_list', []),
    ('system:email_list', []),
    ('system:connected_users', []),
    ('system:session_history', []),
    ('system:role_list', []),
    ('system:user_permissions_list', []),
]


def perm(codename):
    return Permission.objects.get(codename=codename)


@pytest.fixture
def superuser(db):
    return CustomUserModel.objects.create_superuser(
        email='super@example.com', password='Clave-Segura-2026'
    )


@pytest.fixture
def basic_user(db):
    return CustomUserModel.objects.create_user(
        email='basic@example.com', password='Clave-Segura-2026',
        profile_type='REPORTS'
    )


def client_for(user):
    client = Client()
    client.force_login(user)
    return client


@pytest.mark.django_db
class TestAccess:

    @pytest.mark.parametrize('name,args', SYSTEM_URLS)
    def test_anonymous_redirected_to_login(self, client, name, args):
        response = client.get(reverse(name, args=args))
        assert response.status_code == 302
        assert reverse('accounts:login') in response.url

    @pytest.mark.parametrize('name,args', SYSTEM_URLS)
    def test_user_without_permission_gets_403(self, basic_user, name, args):
        response = client_for(basic_user).get(reverse(name, args=args))
        assert response.status_code == 403

    @pytest.mark.parametrize('name,args', SYSTEM_URLS)
    def test_superuser_can_access(self, superuser, name, args):
        response = client_for(superuser).get(reverse(name, args=args))
        assert response.status_code == 200

    def test_role_permission_grants_access(self, basic_user):
        group = Group.objects.get(name='Reportes')
        group.permissions.add(perm('view_dashboard'))
        response = client_for(basic_user).get(reverse('system:dashboard'))
        assert response.status_code == 200
        # Sin view_errorlog sigue sin acceso a errores
        response = client_for(basic_user).get(reverse('system:error_list'))
        assert response.status_code == 403


@pytest.mark.django_db
class TestRoles:

    def test_profile_group_follows_profile_type(self, basic_user):
        assert list(basic_user.groups.values_list('name', flat=True)) == \
            ['Reportes']
        extra = Group.objects.create(name='Auditores')
        basic_user.groups.add(extra)

        basic_user.profile_type = 'MANAGER'
        basic_user.save()
        assert set(basic_user.groups.values_list('name', flat=True)) == \
            {'Administrador', 'Auditores'}

    def test_sync_roles_is_idempotent(self, db):
        sync_roles()
        assert sync_roles() == []
        assert Group.objects.filter(name='Técnico').exists()

    def test_catalog_lists_project_apps_without_historical(self, db):
        catalog = get_catalog()
        labels = [app['label'] for app in catalog]
        assert {'accounts', 'system', 'auth'} <= set(labels)
        assert 'sessions' not in labels
        names = [m['name'] for app in catalog for m in app['models']]
        assert not any(name.lower().startswith('historical') for name in names)

    def test_save_role_matrix_keeps_permissions_outside_catalog(self, superuser):
        group = Group.objects.create(name='Soporte')
        outside = Permission.objects.get(codename='view_session')  # app sessions
        group.permissions.add(outside, perm('view_errorlog'))

        response = client_for(superuser).post(
            reverse('system:role_permissions', args=[group.pk]),
            {'name': 'Soporte TI', 'permissions': [
                perm('view_dashboard').pk, perm('view_usersession').pk
            ]}
        )
        assert response.status_code == 302
        group.refresh_from_db()
        assert group.name == 'Soporte TI'
        assert set(group.permissions.values_list('codename', flat=True)) == \
            {'view_session', 'view_dashboard', 'view_usersession'}

    def test_profile_role_cannot_be_deleted(self, superuser, basic_user):
        group = Group.objects.get(name='Reportes')
        client_for(superuser).post(reverse('system:role_delete', args=[group.pk]))
        assert Group.objects.filter(pk=group.pk).exists()

    def test_create_and_delete_role(self, superuser):
        client = client_for(superuser)
        client.post(reverse('system:role_list'), {'name': 'Temporal'})
        group = Group.objects.get(name='Temporal')
        client.post(reverse('system:role_delete', args=[group.pk]))
        assert not Group.objects.filter(name='Temporal').exists()


@pytest.mark.django_db
class TestUserPermissions:

    def test_save_groups_and_direct_permissions(self, superuser, basic_user):
        extra = Group.objects.create(name='Auditores')
        response = client_for(superuser).post(
            reverse('system:user_permissions', args=[basic_user.pk]),
            {'groups': [extra.pk], 'permissions': [perm('view_emaillog').pk]}
        )
        assert response.status_code == 302
        assert set(basic_user.groups.values_list('name', flat=True)) == \
            {'Reportes', 'Auditores'}
        assert basic_user.has_perm('system.view_emaillog')

    def test_profile_group_cannot_be_removed_from_screen(self, superuser,
                                                         basic_user):
        client_for(superuser).post(
            reverse('system:user_permissions', args=[basic_user.pk]), {}
        )
        assert list(basic_user.groups.values_list('name', flat=True)) == \
            ['Reportes']

    def test_non_superuser_cannot_edit_superuser(self, superuser, basic_user):
        basic_user.user_permissions.add(perm('manage_permissions'))
        response = client_for(basic_user).post(
            reverse('system:user_permissions', args=[superuser.pk]), {}
        )
        assert response.status_code == 403

    def test_inherited_permissions_shown_disabled(self, superuser, basic_user):
        Group.objects.get(name='Reportes').permissions.add(perm('view_errorlog'))
        response = client_for(superuser).get(
            reverse('system:user_permissions', args=[basic_user.pk])
        )
        assert perm('view_errorlog').pk in response.context['inherited']
        assert f'value="{perm("view_errorlog").pk}"'.encode() not in \
            response.content


@pytest.mark.django_db
def test_detail_pages_render(superuser):
    from common.LoggerApp import log_exception
    from system.models import ErrorLog

    try:
        1 / 0
    except ZeroDivisionError:
        log_exception(None, '/z', 'Test', 'boom')
    client = client_for(superuser)
    error = ErrorLog.objects.get()
    response = client.get(reverse('system:error_detail', args=[error.pk]))
    assert response.status_code == 200
    assert b'ZeroDivisionError' in response.content

    group = Group.objects.get(name='Reportes')
    response = client.get(reverse('system:role_permissions', args=[group.pk]))
    assert response.status_code == 200
    assert b'Cuentas de usuario' in response.content
    assert b'name="permissions"' in response.content

    response = client.post(reverse('system:error_resolve', args=[error.pk]),
                           {'next': 'https://evil.example.com/'})
    assert response.url == reverse('system:error_list')
    error.refresh_from_db()
    assert error.is_resolved and error.resolved_by == superuser
