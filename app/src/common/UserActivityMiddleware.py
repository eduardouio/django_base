"""
Middleware que mantiene actualizada la última actividad de cada sesión
(system.UserSession) para el panel de usuarios conectados.

Para no escribir en la base de datos en cada petición, solo actualiza si
pasaron USER_ACTIVITY_UPDATE_SECONDS desde la última actualización.
"""

import time

from django.conf import settings

SESSION_ACTIVITY_KEY = '_last_activity_sync'


class UserActivityMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        self.interval = getattr(settings, 'USER_ACTIVITY_UPDATE_SECONDS', 60)

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if user is not None and user.is_authenticated:
            self._touch(request)
        return self.get_response(request)

    def _touch(self, request):
        now = time.time()
        last_sync = request.session.get(SESSION_ACTIVITY_KEY, 0)
        if now - last_sync < self.interval:
            return
        session_key = request.session.session_key
        if not session_key:
            return

        from system.models import UserSession
        UserSession.touch(request, session_key)
        request.session[SESSION_ACTIVITY_KEY] = now
