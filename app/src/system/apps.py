from django.apps import AppConfig


class SystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'system'
    verbose_name = 'Administración del sistema'

    def ready(self):
        from system import signals  # noqa: F401
