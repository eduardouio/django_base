from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse

from accounts.models import CustomUserModel
from accounts.forms import CustomCreationForm, CustomChangeForm
from common.EmailService import EmailService
from common.utils.request import get_site_url
from system.services.RoleService import sync_user_profile_group


class CustomUserModelAdmin(UserAdmin):
    add_form = CustomCreationForm
    form = CustomChangeForm

    model = CustomUserModel

    fieldsets = (
        ('Basico', {
            'fields': (
                'email',  'password', 'is_active',
            )
        }
        ),
        ('Información Personal', {
            'fields': (
                'first_name', 'last_name', 'profile_type'
            )
        }
        ),
        ('Permisos', {
            'fields': (
                'is_staff', 'is_superuser', 'groups', 'user_permissions'
            )
        }
        ),
    )
    add_fieldsets = (
        ('Básico', {
            'classes': ('wide',),
            'fields': (
                'email', 'password1', 'password2', 'profile_type',
                'is_staff', 'is_active'
            )
        }
        ),
    )

    list_display = (
        'email',
        'first_name',
        'last_name',
        'profile_type',
        'is_active',
        'is_confirmed_mail',
    )

    list_filter = (
        'profile_type',
        'is_active',
        'is_confirmed_mail',
    )

    search_fields = ('email', 'first_name', 'last_name')

    ordering = ('-date_joined',)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # El formulario reemplaza los grupos: volver a asignar el del perfil
        sync_user_profile_group(form.instance)

    def response_add(self, request, obj, post_url_continue=None):
        if getattr(settings, 'SEND_WELCOME_EMAIL', True):
            self._send_welcome_email(request, obj)
        return super().response_add(request, obj, post_url_continue)

    def _send_welcome_email(self, request, user):
        site_url = get_site_url(request)
        EmailService.send(
            to=user.email,
            subject=f'Bienvenido a {settings.SITE_NAME}',
            template='welcome',
            context={
                'user': user,
                'login_url': site_url + reverse('accounts:login'),
                'reset_request_url': site_url + reverse(
                    'accounts:password_reset'
                ),
            },
            async_send=True,
            user=request.user,
        )


admin.site.register(CustomUserModel, CustomUserModelAdmin)
