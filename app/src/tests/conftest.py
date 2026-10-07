import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def sync_emails_and_clean_cache(settings):
    """Correos síncronos (los hilos no ven la transacción del test) y caché limpia."""
    settings.EMAIL_ASYNC = False
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
    settings.SITE_URL = 'http://testserver'
    cache.clear()
    yield
    cache.clear()
