"""
Django settings for base project.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

from pathlib import Path

from config import secrets

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = getattr(
    secrets,
    'SECRET_KEY',
    'django-insecure-dmiffk3lw9ht7&cvk#ix)y4b88xvy3c%0ci%@npnn&isex2*b$'
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = secrets.DEBUG

ALLOWED_HOSTS = getattr(secrets, 'ALLOWED_HOSTS', ['*'])


# Application definition

INSTALLED_APPS = [
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'corsheaders',
    'simple_history',
    'rest_framework',
    'django_filters',
    'import_export',
    'accounts',
    'system',
]

MIDDLEWARE = [
    'common.LoggingMiddleware.LoggingMiddleware',  # request_id + log por petición
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'crum.CurrentRequestUserMiddleware',  # usuario actual para BaseModel
    'simple_history.middleware.HistoryRequestMiddleware',
    'common.UserActivityMiddleware.UserActivityMiddleware',  # usuarios conectados
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


CORS_ORIGIN_ALLOW_ALL = True

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = secrets.DEFAULT_DB


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Recuperación de contraseña: el enlace enviado por correo vence en 10 minutos
PASSWORD_RESET_TIMEOUT = 600
# Máximo de solicitudes de recuperación por correo/IP dentro de la ventana
PASSWORD_RESET_MAX_ATTEMPTS = 3

# Email
EMAIL_BACKEND = secrets.EMAIL_BACKEND
EMAIL_HOST = secrets.EMAIL_HOST
EMAIL_PORT = secrets.EMAIL_PORT
EMAIL_USE_TLS = secrets.EMAIL_USE_TLS
EMAIL_USE_SSL = getattr(secrets, 'EMAIL_USE_SSL', False)
EMAIL_HOST_USER = secrets.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = secrets.MAIL_PASS
EMAIL_TIMEOUT = getattr(secrets, 'EMAIL_TIMEOUT', 20)
DEFAULT_FROM_EMAIL = getattr(
    secrets, 'DEFAULT_FROM_EMAIL', secrets.EMAIL_HOST_USER
)
SERVER_EMAIL = DEFAULT_FROM_EMAIL
# Lista de tuplas (nombre, correo) que reciben las alertas de errores
ADMINS = getattr(secrets, 'ADMINS', [])
# False envía los correos async_send=True de forma síncrona (pruebas)
EMAIL_ASYNC = getattr(secrets, 'EMAIL_ASYNC', True)
# Envía correo de bienvenida al crear usuarios desde el admin
SEND_WELCOME_EMAIL = getattr(secrets, 'SEND_WELCOME_EMAIL', True)
# URL pública del sistema (ej: https://app.midominio.com) para los enlaces de
# los correos. En producción defínala siempre: si falta se usa el Host del
# request, que un atacante puede manipular (envenenamiento del enlace de reset).
SITE_URL = getattr(secrets, 'SITE_URL', None)
SITE_NAME = getattr(secrets, 'SITE_NAME', 'Base Sistema')


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'es-EC'
TIME_ZONE = 'America/Guayaquil'
USE_I18N = False
USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Modelo de usuario Peronalizado
AUTH_USER_MODEL = 'accounts.CustomUserModel'
AUTHENTICATION_BACKENDS = [
    'common.EmailBackEndAuth.EmailBackEndAuth'
]

# URLs de autenticación
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/home/'
LOGOUT_REDIRECT_URL = '/'

# Usuarios conectados
# Minutos sin actividad para dejar de considerar a un usuario "en línea"
ONLINE_THRESHOLD_MINUTES = 5
# Segundos mínimos entre escrituras de last_activity por sesión
USER_ACTIVITY_UPDATE_SECONDS = 60


# Logging
# https://docs.djangoproject.com/en/5.2/topics/logging/
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)
# Respuestas más lentas que esto (ms) se registran como WARNING
LOG_SLOW_REQUEST_MS = 2000
# Rutas que no se registran en el log de peticiones
LOG_IGNORED_PATHS = ('/static/', '/media/', '/favicon.ico')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'request_id': {
            '()': 'common.logging.filters.RequestIdFilter',
        },
    },
    'formatters': {
        'verbose': {
            'format': '%(asctime)s | %(levelname)s | %(request_id)s | %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'filters': ['request_id'],
            'level': 'DEBUG' if DEBUG else 'WARNING',
        },
        'app_file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': LOG_DIR / 'app.log',
            'when': 'midnight',
            'backupCount': 30,
            'encoding': 'utf-8',
            'formatter': 'verbose',
            'filters': ['request_id'],
            'level': 'INFO',
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'errors.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 10,
            'encoding': 'utf-8',
            'formatter': 'verbose',
            'filters': ['request_id'],
            'level': 'ERROR',
        },
        'database': {
            'class': 'common.logging.DatabaseLogHandler.DatabaseLogHandler',
            'filters': ['request_id'],
            'level': 'ERROR',
        },
    },
    'loggers': {
        'app_logger': {
            'handlers': ['console', 'app_file', 'error_file', 'database'],
            'level': 'INFO',
            # root no tiene handlers; propagar permite que pytest (caplog) lo capture
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console', 'error_file', 'database'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console', 'app_file', 'error_file', 'database'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
