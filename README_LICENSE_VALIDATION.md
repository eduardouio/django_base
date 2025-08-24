# Sistema de Validación Periódica de Licencias

## 📋 Descripción

Este sistema implementa una validación periódica y automática de licencias para usuarios autenticados, proporcionando un balance óptimo entre seguridad y rendimiento.

## 🔧 Componentes Implementados

### 1. **LicenseValidationMiddleware**
- **Ubicación**: `common/LicenseValidationMiddleware.py`
- **Función**: Valida licencias automáticamente según intervalos configurables
- **Características**:
  - Validación automática basada en intervalos por rol
  - Cierre automático de sesión si las licencias son inválidas
  - Exclusión de URLs específicas (login, logout, static files)
  - Validación más frecuente para URLs críticas

### 2. **Comando de Monitoreo**
- **Ubicación**: `accounts/management/commands/monitor_license_validation.py`
- **Uso**: `python manage.py monitor_license_validation <email>`
- **Función**: Permite monitorear y debuggear el estado de validación

## ⚙️ Configuración

### Intervalo de Validación

```python
VALIDATION_INTERVAL = 1800  # 30 minutos para todos los usuarios
```

### URLs Excluidas (sin validación)
- `/accounts/login/`
- `/accounts/logout/`
- `/static/`
- `/media/`

## 🚀 Instalación

### 1. Agregar el Middleware

En `config/settings.py`, el middleware ya está configurado después de `AuthenticationMiddleware`:

```python
MIDDLEWARE = [
    # ... otros middlewares
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'common.LicenseValidationMiddleware.LicenseValidationMiddleware',  # ← YA CONFIGURADO
    'django.contrib.messages.middleware.MessageMiddleware',
    # ... resto de middlewares
]
```

### 2. URLs

El sistema funciona automáticamente con el middleware. No requiere URLs adicionales.

## 📊 Uso

### Monitoreo desde Terminal

```bash
# Ver estado de un usuario
python manage.py monitor_license_validation usuario@ejemplo.com

# Simular una petición con middleware
python manage.py monitor_license_validation usuario@ejemplo.com --simulate-request
```

### Funcionamiento Automático

El middleware funciona automáticamente una vez instalado:
- Valida licencias según los intervalos configurados
- Cierra sesión automáticamente si las licencias son inválidas
- Registra todas las validaciones en los logs

### Programáticamente

```python
from common.LicenseValidationMiddleware import LicenseValidationMiddleware

# Obtener estado de validación (solo disponible con middleware activo)
middleware = LicenseValidationMiddleware(None)
status = middleware.get_validation_status(request)

# El middleware ejecuta validación automática según intervalos configurados
```

## 🔍 Comportamiento del Sistema

### Flujo de Validación

1. **Login**: Validación completa obligatoria
2. **Sesión Activa**: Validación cada 30 minutos para todos los usuarios
3. **Licencia Inválida**: Cierre automático de sesión

### Estados de Sesión

- `last_license_check`: Timestamp de última validación
- `license_valid`: Boolean del estado de licencia
- Los estados se mantienen durante toda la sesión

### Manejo de Errores

- **Error de conexión**: Mantiene sesión activa, programa re-validación
- **Timeout**: Registra error, mantiene sesión
- **Licencia inválida**: Cierra sesión inmediatamente

## 📈 Ventajas de esta Implementación

1. **Seguridad Balanceada**: 
   - Detecta revocaciones en tiempo razonable (15-30 min)
   - No compromete el rendimiento del sistema

2. **Rendimiento Optimizado**:
   - Validación cada 30 minutos para todos los usuarios
   - Validación asíncrona y no bloqueante

3. **Simplicidad**:
   - Un solo intervalo de validación fácil de entender
   - Configuración simple y mantenible
   - Sin complejidad de roles o URLs especiales

4. **Experiencia de Usuario**:
   - Validaciones transparentes
   - Mensajes claros en caso de problema
   - Interfaz de monitoreo disponible

5. **Observabilidad**:
   - Logging completo de todas las validaciones
   - Comando de monitoreo para debugging
   - Métricas disponibles via comando de terminal

## 🎯 Casos de Uso Recomendados

- **Sistemas empresariales** con licencias por suscripción
- **Aplicaciones críticas** donde la seguridad es prioritaria
- **Entornos multi-tenant** con licencias por organización
- **Sistemas con licencias temporales** que pueden revocarse

## 🔧 Personalización

Para ajustar el intervalo según tus necesidades, modifica la constante en `LicenseValidationMiddleware.py`:

```python
# Intervalo más conservador (mayor seguridad)
VALIDATION_INTERVAL = 900  # 15 minutos

# Intervalo más relajado (mejor rendimiento)
VALIDATION_INTERVAL = 3600  # 1 hora

# Intervalo por defecto (recomendado)
VALIDATION_INTERVAL = 1800  # 30 minutos
```
