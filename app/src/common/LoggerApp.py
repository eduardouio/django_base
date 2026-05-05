"""
Sistema de Logging Personalizado para la Aplicación Django.
Registra información detallada de las actividades del usuario.
"""

import logging
import os
from django.conf import settings
from pathlib import Path


class AppLogger:
    """
    Clase para manejar el sistema de logging de la aplicación.
    Registra información del usuario, fecha/hora, URL, archivo y mensaje.
    """

    def __init__(self):
        self.log_file_path = os.path.join(
            settings.BASE_DIR,
            'logs',
            'app_log.log'
        )
        self._setup_logger()

    def _setup_logger(self):
        """
        Configura el logger con el formato personalizado.
        """
        # Crear directorio de logs si no existe
        log_dir = os.path.dirname(self.log_file_path)
        Path(log_dir).mkdir(parents=True, exist_ok=True)

        # Configurar el logger
        self.logger = logging.getLogger('app_logger')
        self.logger.setLevel(logging.INFO)

        # Evitar duplicar handlers si ya existen
        if not self.logger.handlers:
            # Handler para archivo
            file_handler = logging.FileHandler(
                self.log_file_path, encoding='utf-8'
            )
            file_handler.setLevel(logging.INFO)

            # Formato personalizado
            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)

    def _format_log_message(self, user, url, file_name, message, request=None):
        """
        Formatea el mensaje de log con toda la información requerida.

        Args:
            user: Usuario (puede ser instancia de User, email string o None)
            url: URL donde ocurrió el evento
            file_name: Nombre del archivo donde se genera el log
            message: Mensaje descriptivo del evento
            request: Objeto request de Django (opcional)

        Returns:
            str: Mensaje formateado para el log
        """
        # Obtener información del usuario
        if hasattr(user, 'email'):
            user_info = user.email
        elif isinstance(user, str):
            user_info = user
        elif user is None:
            user_info = "Sistema/Anónimo"
        else:
            user_info = str(user)

        # Obtener URL desde request si no se proporciona
        if not url and request:
            url = request.get_full_path()
        elif not url:
            url = "N/A"

        # Formatear mensaje
        log_parts = [
            f"Usuario: {user_info}",
            f"URL: {url}",
            f"Archivo: {file_name}",
            f"Mensaje: {message}"
        ]

        return " | ".join(log_parts)

    def info(self, user, url, file_name, message, request=None):
        """
        Registra un mensaje de información.

        Args:
            user: Usuario que realiza la acción
            url: URL donde ocurrió el evento
            file_name: Archivo donde se genera el log (ej: 'CustomUserModel')
            message: Mensaje descriptivo
            request: Objeto request de Django (opcional)
        """
        formatted_message = self._format_log_message(
            user, url, file_name, message, request
        )
        self.logger.info(formatted_message)

    def warning(self, user, url, file_name, message, request=None):
        """
        Registra un mensaje de advertencia.
        """
        formatted_message = self._format_log_message(
            user, url, file_name, message, request
        )
        self.logger.warning(formatted_message)

    def error(self, user, url, file_name, message, request=None):
        """
        Registra un mensaje de error.
        """
        formatted_message = self._format_log_message(
            user, url, file_name, message, request
        )
        self.logger.error(formatted_message)

    def debug(self, user, url, file_name, message, request=None):
        """
        Registra un mensaje de debug.
        """
        formatted_message = self._format_log_message(
            user, url, file_name, message, request
        )
        self.logger.debug(formatted_message)

    def critical(self, user, url, file_name, message, request=None):
        """
        Registra un mensaje crítico.
        """
        formatted_message = self._format_log_message(
            user, url, file_name, message, request
        )
        self.logger.critical(formatted_message)


# Instancia global del logger
app_logger = AppLogger()


# Funciones de conveniencia para usar en toda la aplicación
def log_info(user, url, file_name, message, request=None):
    """Función de conveniencia para logging de información."""
    app_logger.info(user, url, file_name, message, request)


def log_warning(user, url, file_name, message, request=None):
    """Función de conveniencia para logging de advertencias."""
    app_logger.warning(user, url, file_name, message, request)


def log_error(user, url, file_name, message, request=None):
    """Función de conveniencia para logging de errores."""
    app_logger.error(user, url, file_name, message, request)


def log_debug(user, url, file_name, message, request=None):
    """Función de conveniencia para logging de debug."""
    app_logger.debug(user, url, file_name, message, request)


def log_critical(user, url, file_name, message, request=None):
    """Función de conveniencia para logging crítico."""
    app_logger.critical(user, url, file_name, message, request)


# Decorator para logging automático de vistas
def log_view_access(view_func):
    """
    Decorator para registrar automáticamente el acceso a vistas.

    Uso:
    @log_view_access
    def mi_vista(request):
        # código de la vista
    """
    def wrapper(request, *args, **kwargs):
        user = request.user if hasattr(request, 'user') else None
        url = (request.get_full_path()
               if hasattr(request, 'get_full_path') else 'N/A')

        log_info(
            user=user,
            url=url,
            file_name=view_func.__module__,
            message=f"Acceso a vista: {view_func.__name__}",
            request=request
        )

        try:
            response = view_func(request, *args, **kwargs)
            return response
        except Exception as e:
            log_error(
                user=user,
                url=url,
                file_name=view_func.__module__,
                message=f"Error en vista {view_func.__name__}: {str(e)}",
                request=request
            )
            raise

    return wrapper


# Clase para logging específico de modelos
class ModelLogger:
    """
    Clase específica para logging de operaciones en modelos.
    """

    @staticmethod
    def log_model_operation(user, operation, model_name, instance_id=None,
                            changes=None, request=None):
        """
        Registra operaciones en modelos (crear, actualizar, eliminar).

        Args:
            user: Usuario que realiza la operación
            operation: Tipo de operación ('create', 'update', 'delete')
            model_name: Nombre del modelo
            instance_id: ID de la instancia (opcional)
            changes: Diccionario con los cambios realizados (opcional)
            request: Objeto request (opcional)
        """
        url = request.get_full_path() if request else 'N/A'

        message_parts = [f"Operación: {operation}", f"Modelo: {model_name}"]

        if instance_id:
            message_parts.append(f"ID: {instance_id}")

        if changes:
            changes_str = ", ".join([f"{k}: {v}" for k, v in changes.items()])
            message_parts.append(f"Cambios: {changes_str}")

        message = " - ".join(message_parts)

        log_info(
            user=user,
            url=url,
            file_name=model_name,
            message=message,
            request=request
        )


# Instancia global del logger de modelos
model_logger = ModelLogger()
