from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from accounts.models import CustomUserModel, License
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
        'license_count',
    )

    list_filter = (
        'is_active',
        'is_confirmed_mail',
    )

    search_fields = ('email', 'first_name', 'last_name')

    ordering = ('-date_joined',)

    def license_count(self, obj):
        """Mostrar el número de licencias del usuario"""
        count = obj.licenses.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:accounts_license_changelist') + \
                f'?user__id__exact={obj.id}'
            return format_html('<a href="{}">{} licencia(s)</a>', url, count)
        return "Sin licencias"
    license_count.short_description = "Licencias Activas"


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = (
        'license_key_short',
        'user_email',
        'enterprise',
        'status_badge',
        'activated_on',
        'expires_on',
        'days_remaining_display',
        'url_server',
        'created_at',
        'is_active_base'
    )
    list_filter = (
        'is_active',  # del modelo License/BaseModel
        'is_deleted',
        'enterprise',
        'activated_on',
        'expires_on',
        'created_at',
        'updated_at'
    )
    search_fields = (
        'license_key',
        'user__email',
        'user__first_name',
        'user__last_name',
        'enterprise',
        'notes'
    )
    readonly_fields = (
        'created_at',
        'updated_at',
        'is_expired',
        'days_remaining',
        'id_user_created',
        'id_user_updated'
    )
    raw_id_fields = ('user',)

    fieldsets = (
        ('Información Principal', {
            'fields': ('user', 'license_key', 'enterprise')
        }),
        ('Estado de Licencia', {
            'fields': ('is_active',)
        }),
        ('Fechas', {
            'fields': ('activated_on', 'expires_on')
        }),
        ('Configuración', {
            'fields': ('url_server',)
        }),
        ('Estado Calculado', {
            'fields': ('is_expired', 'days_remaining'),
            'classes': ('collapse',)
        }),
        ('BaseModel Fields', {
            'fields': (
                'notes', 'is_deleted',
                'id_user_created', 'id_user_updated'
            ),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def license_key_short(self, obj):
        """Mostrar versión corta de la clave de licencia"""
        if len(obj.license_key) > 20:
            return f"{obj.license_key[:20]}..."
        return obj.license_key
    license_key_short.short_description = "Clave"

    def user_email(self, obj):
        """Mostrar email del usuario con enlace"""
        url = reverse('admin:accounts_customusermodel_change',
                      args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)
    user_email.short_description = "Usuario"

    def status_badge(self, obj):
        """Mostrar badge colorido del estado"""
        if obj.is_deleted:
            color = 'gray'
            text = 'Eliminada'
        elif obj.is_active and not obj.is_expired:
            color = 'green'
            text = 'Activa'
        elif obj.is_expired:
            color = 'red'
            text = 'Expirada'
        else:
            color = 'orange'
            text = 'Inactiva'

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, text
        )
    status_badge.short_description = "Estado"

    def days_remaining_display(self, obj):
        """Mostrar días restantes con color"""
        days = obj.days_remaining
        if days <= 0:
            color = 'red'
            text = 'Expirada'
        elif days <= 7:
            color = 'orange'
            text = f'{days} días'
        else:
            color = 'green'
            text = f'{days} días'

        return format_html('<span style="color: {};">{}</span>', color, text)
    days_remaining_display.short_description = "Días Restantes"

    def is_active_base(self, obj):
        """Mostrar estado del BaseModel"""
        if obj.is_active:  # BaseModel is_active
            return format_html('<span style="color: green;">✓ Activo</span>')
        else:
            return format_html('<span style="color: red;">✗ Inactivo</span>')
    is_active_base.short_description = "Estado Base"


admin.site.register(CustomUserModel, CustomUserModelAdmin)
