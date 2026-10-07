from django.contrib import admin

from system.models import EmailLog, ErrorLog, UserSession


class ReadOnlyAdmin(admin.ModelAdmin):
    """Registros generados por el sistema: solo lectura en el admin."""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(ErrorLog)
class ErrorLogAdmin(ReadOnlyAdmin):
    list_display = ('exception_type', 'level', 'url', 'occurrences',
                    'last_seen', 'is_resolved')
    list_filter = ('is_resolved', 'level')
    search_fields = ('message', 'exception_type', 'url', 'request_id')


@admin.register(EmailLog)
class EmailLogAdmin(ReadOnlyAdmin):
    list_display = ('subject', 'to', 'template', 'status', 'created_at')
    list_filter = ('status', 'template')
    search_fields = ('to', 'subject')


@admin.register(UserSession)
class UserSessionAdmin(ReadOnlyAdmin):
    list_display = ('user', 'ip', 'login_at', 'last_activity', 'logout_at',
                    'ended_reason')
    list_filter = ('ended_reason',)
    search_fields = ('user__email', 'ip')
