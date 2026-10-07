<div align="center">

# Django Base Template

Plantilla robusta y opinada para iniciar proyectos Django modernos con: modelo de usuario por email, panel de administración (usuarios conectados, roles y permisos, errores, correos), recuperación de contraseña por correo, logging con rotación y alertas, stack visual rápido (Tailwind + DaisyUI vía CDN), utilidades de auditoría, exportaciones y pruebas (Pytest + Playwright listo para configurar). Incluye carpeta preparada para integrar un frontend (Vue/Vite u otro) y dependencias para generación de PDFs / reportes.

</div>

## � Tabla de Contenidos
1. Visión General
2. Stack Tecnológico
3. Estructura del Proyecto
4. Características Destacadas
5. Modelo de Usuario Personalizado
6. Middlewares Incluidos
7. Frontend (Tailwind + DaisyUI + Integración futura Vue/Vite)
8. Configuración y Puesta en Marcha
9. Migraciones: Estrategia Inicial
10. Variables de Entorno / Seguridad
11. Testing (Pytest & Playwright)
12. Exportaciones y PDFs
13. Cambio de Base de Datos a PostgreSQL
14. Comandos Útiles
15. Panel de Administración (`/system/`)
16. Correos y Recuperación de Contraseña
17. Roadmap Sugerido / Próximos Pasos
18. Licencia

---

## 1. Visión General
El objetivo es ofrecer una base limpia pero completa para acelerar la construcción de aplicaciones Django enfocadas en APIs + panel administrativo y fácil acoplamiento de un frontend SPA. Se privilegia una curva de arranque baja y extensibilidad futura.

## 2. Stack Tecnológico
- Backend: Django 5.2 LTS (soporte hasta abril 2028)
- Administración: Grappelli (UI mejorada sobre admin nativo)
- Autenticación: Usuario personalizado + backend por email
- Estilos: TailwindCSS (CDN dev) + DaisyUI (componentes) + Line Awesome Icons
- Datos y Utilidades: django-crum, django-simple-history, django-import-export, openpyxl, Faker
- API / Seguridad: Django REST Framework (listo para usar), django-filter, SimpleJWT (tokens) *(aún no cableado en views)*
- Logs / Auditoría: `LOGGING` con archivos rotativos + errores en BD con alertas por correo (ver `README_LOGGING.md`), BaseModel (soft delete / auditoría)
- Base de datos: PostgreSQL con psycopg 3
- Testing: pytest, pytest-django, Playwright (UI / PDF e2e futuro)
- PDFs / Reportes: WeasyPrint, reportlab

Revisa `app/requeriments.txt` para la lista completa (nombre original mantenido intencionalmente: `requeriments.txt`).

## 3. Estructura del Proyecto (extracto)
```
app/
	requeriments.txt
	src/
			manage.py
			config/                 # settings, urls, wsgi/asgi
			accounts/               # usuario personalizado + vistas básicas
				models/CustomUserModel.py
				managers/CustomUserManager.py
				urls.py               # rutas login/logout/profile
				templates/            # base.html y derivados
			system/                 # panel /system/: conectados, roles/permisos, errores, correos
			common/                 # piezas reutilizables (BaseModel, middlewares, EmailService, logging)
			templates/              # 403, 404 y 500
			logs/                   # archivos de log
			static/                 # assets estáticos (dev)
			media/                  # subida de imágenes (perfil)
			tests/                  # carpeta tests pytest
	frontend/                   # espacio futuro para Vue/Vite u otro SPA
```

## 4. Características Destacadas
- Autenticación por email (sin `username`).
- `BaseModel` con auditoría (created/updated + usuario) y soft delete.
- Historial de cambios vía `django-simple-history` (si el modelo lo hereda cuando se añada).
- Panel de administración en `/system/`: usuarios conectados (con cierre forzado de sesión), roles y permisos por app, registro de errores y de correos.
- Envío de correos HTML con plantillas (`common/EmailService.py`) y registro de cada envío.
- Recuperación de contraseña por correo con enlace de un solo uso que vence en 10 minutos.
- Logging centralizado: archivos rotativos, `request_id` por petición, errores agrupados en BD y aviso a `ADMINS`.
- Configuración abierta de CORS para acelerar desarrollo (cerrar en prod).
- Tailwind + DaisyUI vía CDN para prototipado instantáneo (con guía para pasar a build local).
- Tests base (Pytest) y dependencias Playwright para pruebas E2E.
- Preparado para JWT (solo falta wiring en views/serializers DRF).
- Generación de PDF y exportaciones (WeasyPrint, reportlab, import-export, openpyxl).

## 5. Modelo de Usuario Personalizado
Archivo: `accounts/models/CustomUserModel.py`
Puntos clave:
- Hereda de `AbstractUser` y elimina `username`.
- Campo `email` único (`USERNAME_FIELD = 'email'`).
- Campos extra: `picture`, `is_confirmed_mail`, `token`, `notes`.
- Manager: `CustomUserManager` (crea usuarios y superusuarios usando email).
- Método de conveniencia `get(cls, email)` que devuelve `None` si no existe.

Buenas prácticas:
1. Agrega cualquier campo nuevo ANTES de la migración inicial en proyectos nuevos.
2. Si ya migraste pero aún estás en fase inicial, puedes regenerar (ver sección migraciones). En producción: migraciones incrementales.

## 6. Middlewares Incluidos
Declarados en `settings.py`:
- `common.LoggingMiddleware.LoggingMiddleware` (primero de la lista): asigna un `request_id` y registra una línea por petición (ver `README_LOGGING.md`).
- `crum.CurrentRequestUserMiddleware`: expone el usuario actual para que `BaseModel` llene `id_user_created` / `id_user_updated`.
- `simple_history.middleware.HistoryRequestMiddleware`: guarda quién hizo cada cambio en el historial.
- `common.UserActivityMiddleware.UserActivityMiddleware`: actualiza la última actividad de la sesión (máximo una escritura por minuto) para el panel de usuarios conectados.

## 7. Frontend (Tailwind + DaisyUI + Integración SPA)
La plantilla base `accounts/templates/base/base.html` incluye:
- CDN Tailwind, DaisyUI y Line Awesome.
- Estructura semántica (header/navbar + bloques de template).

Para pasar a build local (opcional):
1. Instala Node en raíz o en `frontend/`.
2. Añade `tailwind.config.js` y procesa con PostCSS (evita cargar todo el CDN en producción).
3. Purga clases con `content` apuntando a templates Django.

Integración con Vue/Vite (sugerido):
- Construir assets a `app/src/static/frontend/` y referenciar en `base.html`.
- Usar `fetch`/DRF endpoints (cuando agregues viewsets/serializers).

## 8. Configuración y Puesta en Marcha
Requisitos previos:
- Python 3.12+
- (Opcional) PostgreSQL si migrarás de SQLite.

Instalación rápida:

primero corre el scrit  bash

bash app/manage_migrations.sh

crea la base en blanco

```bash
cd app
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requeriments.txt

cd src
python manage.py makemigrations accounts system  # las migraciones no se versionan
python manage.py migrate
python manage.py sowseed
python manage.py runserver
```

`sowseed` también crea los roles de perfil (`sync_roles`).

Rutas de cuenta (namespace `accounts`):
```
/login/                              name=login
/logout/                             name=logout
/profile/                            name=profile
/profile/edit/                       name=profile_edit
/profile/change-password/            name=change_password
/password-reset/                     name=password_reset
/password-reset/sent/                name=password_reset_done
/password-reset/<uidb64>/<token>/    name=password_reset_confirm
/password-reset/complete/            name=password_reset_complete
```

Panel (namespace `system`): `/system/` (ver sección 15). Admin: `/admin/`.

## 9. Migraciones: Estrategia Inicial
Las migraciones están ignoradas (excepto `__init__.py`) para permitir remodelar rápido.
Flujo recomendado en fase inicial:
1. Define tus modelos.
2. Borra `db.sqlite3` si necesitas reiniciar.
3. Genera migraciones y migra.
4. Cuando el esquema se estabilice, deja de ignorar migraciones y súbelas al repo.

Precaución: Nunca borres migraciones en entornos ya desplegados.

## 10. Variables de Entorno / Seguridad

### Crear `secrets.py` (obligatorio)

El archivo `app/src/config/secrets.py` contiene credenciales sensibles y **nunca se versiona** (está en `.gitignore`). Debes crearlo manualmente antes de levantar el proyecto.

Ruta: `app/src/config/secrets.py`

```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Email ──────────────────────────────────────────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.tudominio.com'
EMAIL_PORT = 465
EMAIL_USE_SSL = True       # puerto 465 = SSL
EMAIL_USE_TLS = False      # puerto 587 = TLS (EMAIL_USE_TLS=True, EMAIL_USE_SSL=False)
EMAIL_HOST_USER = 'notificaciones@tudominio.com'
MAIL_PASS = 'tu_password_de_correo'
DEFAULT_FROM_EMAIL = 'Mi Sistema <notificaciones@tudominio.com>'  # opcional

# ── Sistema (opcionales, con valores por defecto) ──────────────────────────
SECRET_KEY = 'genera-una-clave-larga-y-aleatoria'   # obligatorio en producción
ALLOWED_HOSTS = ['app.tudominio.com']
SITE_NAME = 'Mi Sistema'
SITE_URL = 'https://app.tudominio.com'  # enlaces de los correos (obligatorio en producción)
ADMINS = [('Soporte', 'soporte@tudominio.com')]  # reciben alertas de errores
SEND_WELCOME_EMAIL = True               # correo al crear usuarios desde el admin

# ── Datos semilla (sowseed) ────────────────────────────────────────────────
DOMMAIN = 'tudominio.com'
GENERIC_PASSWORD = 'clave-inicial-de-los-usuarios-semilla'

# ── Bases de datos ─────────────────────────────────────────────────────────
DATABASES = {
    'TEST': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'test_db',
        'USER': 'postgres',
        'PASSWORD': 'tu_password',
        'HOST': 'localhost',
        'PORT': '5432',
    },
    'PRODUCTION': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'prod_db',
        'USER': 'postgres',
        'PASSWORD': 'tu_password_prod',
        'HOST': 'localhost',
        'PORT': '5432',
    },
    'DEVELOPMENT': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'dev_db',
        'USER': 'tu_usuario',
        'PASSWORD': 'tu_password_dev',
        'HOST': 'localhost',
        'PORT': '5432',
    },
}

# Selecciona cuál DB es la activa (usa la clave de DATABASES de arriba)
DEFAULT_DB = {
    'default': {
        **DATABASES['DEVELOPMENT'],
        'CONN_MAX_AGE': 60,
    }
}

DEBUG = True  # False en producción
```

> Para crear las bases de datos en PostgreSQL:
> ```sql
> CREATE DATABASE dev_db OWNER tu_usuario;
> GRANT ALL PRIVILEGES ON DATABASE dev_db TO tu_usuario;
> ```

`SECRET_KEY` se lee de `secrets.py` (si falta se usa una clave insegura de desarrollo). Genera una con:
`python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"`
Sugerencia `.env` (no versionarlo):
```env
DJANGO_SECRET_KEY=changeme
DJANGO_DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```
Y en `settings.py` (extensión futura):
```python
import os
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-inseguro')
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')
```

Checklist endurecimiento producción:
- Configurar `CSRF_TRUSTED_ORIGINS`.
- Cerrar CORS (`CORS_ORIGIN_ALLOW_ALL = False` + lista blanca).
- Activar `USE_TZ = True` y almacenar en UTC.
- HTTPS (SECURE_* settings, HSTS) detrás de reverse proxy.
- Definir `SITE_URL` (evita que el Host de la petición se use en los enlaces de recuperación).
- `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_SSL_REDIRECT` y HSTS (`python manage.py check --deploy`).

## 11. Testing (Pytest & Playwright)
Pytest ya configurado (`pytest.ini`). Ejecutar:
```bash
pytest -q
```

Playwright: dependencia instalada, inicializa navegadores (si usas Node) con:
```bash
npx playwright install
```
Estructura sugerida para tests E2E (crear si decides usarlos):
```
app/src/tests/e2e/
	test_login_flow.py
```
Ejemplo mínimo (pseudo):
```python
from playwright.sync_api import sync_playwright

def test_home_title():
		with sync_playwright() as p:
				browser = p.chromium.launch()
				page = browser.new_page()
				page.goto('http://127.0.0.1:8000/')
				assert 'Bienvenido' in page.text_content('h1')
				browser.close()
```

## 12. Exportaciones y PDFs
Disponibles bibliotecas para:
- Exportar datos (django-import-export, openpyxl)
- Generar PDF (WeasyPrint, reportlab)

Pendiente: añadir ejemplos de views / servicios PDF (puede agregarse bajo petición).

## 13. Cambio a PostgreSQL
Reemplaza bloque `DATABASES` en `settings.py`:
```python
DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql',
		'NAME': 'mi_db',
		'USER': 'mi_usuario',
		'PASSWORD': 'mi_password',
		'HOST': 'localhost',
		'PORT': '5432',
	}
}
```
Luego:
```bash
python src/manage.py migrate
```

## 14. Comandos Útiles
```bash
# Crear nueva app
python src/manage.py startapp inventario

# Migraciones
python src/manage.py makemigrations
python src/manage.py migrate

# Superusuario
python src/manage.py createsuperuser --email admin@example.com

# Shell enriquecido
python src/manage.py shell_plus

# Ejecutar tests
pytest -q

# Roles de perfil (grupos) y asignación de usuarios
python src/manage.py sync_roles

# Mantenimiento (programar en cron)
python src/manage.py cleanup_sessions          # sesiones expiradas
python src/manage.py purge_logs --days 90      # errores resueltos, correos y sesiones viejas
```

Script auxiliar: `app/manage_migrations.sh` para crear/eliminar la base de datos y las migraciones en fase inicial (no usar en producción).

## 15. Panel de Administración (`/system/`)
Visible en la barra superior ("Administración") para quien tenga `system.view_dashboard`.

| Sección | URL | Permiso |
|---|---|---|
| Resumen | `/system/` | `system.view_dashboard` |
| Usuarios conectados (refresco cada 30 s) | `/system/sessions/` | `system.view_usersession` |
| Cerrar sesión de otro usuario | botón en la lista | `system.close_usersession` |
| Historial de accesos | `/system/sessions/history/` | `system.view_usersession` |
| Roles y permisos | `/system/roles/` | `system.manage_permissions` |
| Permisos por usuario | `/system/users/` | `system.manage_permissions` |
| Registro de errores | `/system/errors/` | `system.view_errorlog` / `change_errorlog` |
| Correos enviados + correo de prueba | `/system/emails/` | `system.view_emaillog` / `send_test_email` |

**Roles**: cada `profile_type` (Administrador, Empresa, Consultor, Técnico, Reportes) es un grupo de Django y el usuario queda en el de su perfil automáticamente. Se pueden crear roles adicionales y asignar permisos directos por usuario. La matriz muestra todas las apps del proyecto (las nuevas aparecen solas) con ver/crear/editar/eliminar por modelo.

Usar los permisos en tus apps:
```python
from common.mixins.SystemPermissionMixin import SystemPermissionMixin

class FacturaListView(SystemPermissionMixin, ListView):
    permission_required = 'ventas.view_factura'
```
```django
{% if perms.ventas.add_factura %}<a href="...">Nueva factura</a>{% endif %}
```

**Usuarios conectados**: un usuario está "en línea" si tuvo actividad en los últimos `ONLINE_THRESHOLD_MINUTES` (5). Se muestra IP, navegador/SO, inicio de sesión y última actividad.

## 16. Correos y Recuperación de Contraseña
```python
from common.EmailService import EmailService

EmailService.send(
    to='cliente@correo.com',
    subject='Su factura',
    template='invoice',            # templates/emails/invoice.html (+ invoice.txt opcional)
    context={'invoice': invoice},
    attachments=[('factura.pdf', pdf_bytes, 'application/pdf')],
    async_send=True,               # en segundo plano, al confirmar la transacción
)
```
Las plantillas extienden `emails/base_email.html`. Cada envío queda en `system.EmailLog`.

Correos del sistema incluidos: recuperación de contraseña, aviso de contraseña cambiada, bienvenida al crear usuario en el admin (`SEND_WELCOME_EMAIL`) y alertas de errores a `ADMINS`.

**Recuperación de contraseña** (`/password-reset/`): el enlace lleva un token firmado que vence a los 10 minutos (`PASSWORD_RESET_TIMEOUT = 600`) y deja de servir al usarse. La respuesta es la misma exista o no el correo, y hay un límite de 3 solicitudes por correo/IP cada 10 minutos (`PASSWORD_RESET_MAX_ATTEMPTS`). El límite usa la caché de Django (en memoria por proceso); con varios workers de gunicorn configura una caché compartida (Redis o base de datos).

## 17. Roadmap Sugerido / Próximos Pasos
- Añadir serializers y viewsets DRF (usuarios, perfiles, healthcheck).
- Implementar endpoints JWT (SimpleJWT) y refresh tokens.
- Reemplazar Tailwind CDN por build PostCSS + purge en producción.
- Añadir pipeline CI (lint + pytest + playwright headless opcional).
- Cola de tareas (Celery / django-q) si el volumen de correos lo requiere.
- Documentar API (drf-spectacular o drf-yasg).

## 18. Licencia
Define la licencia (MIT / Apache 2.0 / privativa). Añade un archivo `LICENSE` acorde.

---

¿Quieres que agregue ejemplos DRF, configuración JWT o build Tailwind local? Pídelo y lo integramos.
