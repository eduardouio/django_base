from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import CustomUserModel
from accounts.forms import CustomCreationForm, CustomChangeForm

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
                'first_name', 'last_name'
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
                'email', 'password1', 'password2',
                'is_staff', 'is_active'
            )
        }
        ),
    )

    list_display = (
        'email',
        'first_name',
        'last_name',
        'is_active',
        'is_confirmed_mail',
    )

    list_filter = (
        'is_active',
        'is_confirmed_mail',
    )

    search_fields = ('email', 'first_name', 'last_name')

    ordering = ('-date_joined',)

admin.site.register(CustomUserModel, CustomUserModelAdmin)
