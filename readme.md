<div align="center">

# Django Base Template

Plantilla robusta y opinada para iniciar proyectos Django modernos con: modelo de usuario por email, middlewares útiles (licenciamiento y logging), stack visual rápido (Tailwind + DaisyUI vía CDN), utilidades de auditoría, exportaciones y pruebas (Pytest + Playwright listo para configurar). Incluye carpeta preparada para integrar un frontend (Vue/Vite u otro) y dependencias para generación de PDFs / reportes.

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
15. Roadmap Sugerido / Próximos Pasos
16. Licencia

---

## 1. Visión General
El objetivo es ofrecer una base limpia pero completa para acelerar la construcción de aplicaciones Django enfocadas en APIs + panel administrativo y fácil acoplamiento de un frontend SPA. Se privilegia una curva de arranque baja y extensibilidad futura.

## 2. Stack Tecnológico
- Backend: Django 5.1
- Administración: Grappelli (UI mejorada sobre admin nativo)
- Autenticación: Usuario personalizado + backend por email
- Estilos: TailwindCSS (CDN dev) + DaisyUI (componentes) + Line Awesome Icons
- Datos y Utilidades: django-crum, django-simple-history, django-import-export, openpyxl, Faker
- API / Seguridad: Django REST Framework (listo para usar), django-filter, SimpleJWT (tokens) *(aún no cableado en views)*
- Logs / Auditoría: Middlewares propios + BaseModel (soft delete / auditoría)
- Testing: pytest, pytest-django, Playwright (UI / PDF e2e futuro)
- PDFs / Reportes: WeasyPrint, reportlab

Revisa `app/backend/requeriments.txt` para la lista completa (nombre original mantenido intencionalmente: `requeriments.txt`).

## 3. Estructura del Proyecto (extracto)
```
app/
	backend/
		requeriments.txt
		src/
			manage.py
			config/                 # settings, urls, wsgi/asgi
			accounts/               # usuario personalizado + vistas básicas
				models/CustomUserModel.py
				managers/CustomUserManager.py
				urls.py               # rutas login/logout/profile
				templates/            # base.html y derivados
			common/                 # piezas reutilizables (BaseModel, middlewares, auth backend)
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
- Middlewares: validación de licencia y logging centralizado.
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
- `common.LicenseValidationMiddleware.LicenseValidationMiddleware`: ganchos para validar licencia / token (esqueleto que puedes completar).
- `common.LoggingMiddleware.LoggingMiddleware`: genera logs automáticos de requests / respuestas clave (ver carpeta `logs/`).

Recomendaciones producción:
- Ajustar rotación de logs (logrotate o Python logging handlers adecuados).
- Mover paths a variables de entorno.

## 7. Frontend (Tailwind + DaisyUI + Integración SPA)
La plantilla base `accounts/templates/base/base.html` incluye:
- CDN Tailwind, DaisyUI y Line Awesome.
- Estructura semántica (header/navbar + bloques de template).

Para pasar a build local (opcional):
1. Instala Node en raíz o en `frontend/`.
2. Añade `tailwind.config.js` y procesa con PostCSS (evita cargar todo el CDN en producción).
3. Purga clases con `content` apuntando a templates Django.

Integración con Vue/Vite (sugerido):
- Construir assets a `app/backend/src/static/frontend/` y referenciar en `base.html`.
- Usar `fetch`/DRF endpoints (cuando agregues viewsets/serializers).

## 8. Configuración y Puesta en Marcha
Requisitos previos:
- Python 3.12+
- (Opcional) PostgreSQL si migrarás de SQLite.

Instalación rápida:
```bash
cd app/backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requeriments.txt

python src/manage.py makemigrations accounts  # si aún no existen
python src/manage.py migrate
python src/manage.py createsuperuser --email admin@example.com
python src/manage.py runserver
```

Admin (agrega las URLs de Grappelli si las defines en `config/urls.py`).

Rutas de cuenta (namespace `accounts`):
```
/accounts/login/             name=login
/accounts/logout/            name=logout
/accounts/profile/           name=profile
/accounts/profile/edit/      name=profile_edit
/accounts/profile/change-password/  name=change_password
```

## 9. Migraciones: Estrategia Inicial
Las migraciones están ignoradas (excepto `__init__.py`) para permitir remodelar rápido.
Flujo recomendado en fase inicial:
1. Define tus modelos.
2. Borra `db.sqlite3` si necesitas reiniciar.
3. Genera migraciones y migra.
4. Cuando el esquema se estabilice, deja de ignorar migraciones y súbelas al repo.

Precaución: Nunca borres migraciones en entornos ya desplegados.

## 10. Variables de Entorno / Seguridad
`SECRET_KEY` y `DEBUG` están hardcodeados para desarrollo.
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
- Rotación y cifrado de logs sensibles.

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
app/backend/src/tests/e2e/
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
```

Script auxiliar disponible: `app/backend/delete_migrations.sh` (si lo adaptas) para limpieza temprana (no usar en producción).

## 15. Roadmap Sugerido / Próximos Pasos
- Añadir serializers y viewsets DRF (usuarios, perfiles, healthcheck).
- Implementar endpoints JWT (SimpleJWT) y refresh tokens.
- Reemplazar Tailwind CDN por build PostCSS + purge en producción.
- Añadir pipeline CI (lint + pytest + playwright headless opcional).
- Implementar `LOGGING` dictConfig centralizado y rotación.
- Añadir permisos basados en roles (Groups / django-guardian si aplica).
- Documentar API (drf-spectacular o drf-yasg).

## 16. Licencia
Define la licencia (MIT / Apache 2.0 / privativa). Añade un archivo `LICENSE` acorde.

---

¿Quieres que agregue ejemplos DRF, configuración JWT o build Tailwind local? Pídelo y lo integramos.
