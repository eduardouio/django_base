# Sistema de logs y errores

## Qué se registra y dónde

| Destino | Qué contiene | Rotación |
|---|---|---|
| `app/src/logs/app.log` | Todo desde INFO: una línea por petición + los `log_info/...` de las vistas | Diaria, 30 días |
| `app/src/logs/errors.log` | Solo ERROR/CRITICAL, **con traceback** | 10 MB × 10 archivos |
| Tabla `system.ErrorLog` | ERROR/CRITICAL agrupados, con datos del request | `purge_logs` |
| Consola | Todo si `DEBUG`, si no solo WARNING+ | — |
| Correo a `ADMINS` | Errores nuevos o reabiertos (no cada ocurrencia) | — |

La configuración está en `settings.LOGGING`. Cada línea lleva un **request_id** que
también se devuelve en el header `X-Request-ID` y se muestra en la página 500, para
que el usuario pueda reportarlo y lo encuentres en el panel.

```
2026-10-07 15:20:11 | INFO | 3f2a9c1b7d4e | Usuario: ana@x.com | URL: /home/ | Archivo: LoggingMiddleware | Mensaje: GET 200 - 35.2ms - IP: 10.0.0.4
```

## Uso en el código

```python
from common.LoggerApp import log_info, log_warning, log_error, log_exception

log_info(request.user, request.path, 'MiVista', 'Factura creada', request)

try:
    procesar()
except Exception:
    # Guarda el traceback completo (log_error solo guarda el mensaje)
    log_exception(request.user, request.path, 'MiVista', 'No se pudo procesar', request)
    raise
```

- `@log_view_access` (decorador de vistas de función) sigue disponible.
- Las excepciones **no controladas** no necesitan nada: Django las registra
  (`django.request`) y quedan en `errors.log` y en el panel automáticamente.
- También funciona el `logging` estándar: `logging.getLogger('app_logger').error(...)`.

## Panel de errores (`/system/errors/`)

- Errores iguales (mismo tipo de excepción + archivo:línea) se **agrupan** y se
  cuentan las ocurrencias en vez de crear miles de registros.
- Filtros por estado, nivel, fechas y búsqueda (mensaje, URL, usuario o request_id).
- Detalle con traceback, datos GET/POST (las claves con `password`, `token`,
  `secret`, `csrf` o `key` se guardan como `***`), usuario, IP y navegador.
- **Marcar como resuelto**: si el error vuelve a ocurrir se reabre y se avisa
  de nuevo a los administradores.

Permisos: `system.view_errorlog` para ver, `system.change_errorlog` para resolver.

## Configuración

En `config/secrets.py`:

```python
ADMINS = [('Soporte', 'soporte@midominio.com')]   # reciben las alertas
SITE_URL = 'https://app.midominio.com'            # para el enlace del correo
```

En `settings.py`:

- `LOG_SLOW_REQUEST_MS = 2000`: peticiones más lentas se registran como WARNING.
- `LOG_IGNORED_PATHS`: rutas que no se registran (`/static/`, `/media/`, favicon).

## Mantenimiento

```bash
python manage.py purge_logs --days 90   # borra errores resueltos, correos y sesiones viejas
```

Sugerencia de cron diario:

```cron
0 3 * * * cd /ruta/app/src && /ruta/venv/bin/python manage.py purge_logs --days 90
```

## Diseño

- `common/LoggingMiddleware.py`: genera el request_id (primer middleware) y escribe la línea por petición.
- `common/logging/context.py`: guarda el request actual en `contextvars` (funciona con WSGI y ASGI).
- `common/logging/filters.py`: agrega `request_id` a cada registro.
- `common/logging/DatabaseLogHandler.py`: guarda en `ErrorLog`. Nunca lanza
  excepciones y evita la recursión: si la base de datos no responde, el error
  queda solo en `errors.log`.
- Los fallos de envío de correo se registran como WARNING a propósito, para que
  una caída del SMTP no dispare alertas que intenten enviar más correos.
