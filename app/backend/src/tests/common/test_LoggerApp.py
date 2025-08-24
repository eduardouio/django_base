import uuid
import re
import logging
from pathlib import Path

import pytest
from django.conf import settings
from django.test import RequestFactory

from common.LoggerApp import (
    log_info, log_warning, log_error,
    log_debug, log_critical, log_view_access
)


LOG_FILE = Path(settings.BASE_DIR) / 'logs' / 'app_log.log'


@pytest.mark.django_db
class TestLoggerApp:

    def _read_log(self):
        if LOG_FILE.exists():
            return LOG_FILE.read_text(encoding='utf-8').splitlines()
        return []

    def test_log_info_writes_line(self):
        unique = f"TEST_INFO_{uuid.uuid4()}"
        log_info(
            user='tester@example.com', url='/x', file_name='TestFile',
            message=unique
        )
        lines = self._read_log()
        assert any(unique in line for line in lines)
        target = next(line for line in lines if unique in line)
        assert 'Usuario: tester@example.com' in target
        assert 'Archivo: TestFile' in target
        assert 'Mensaje: ' in target

    def test_warning_and_error(self):
        warn_msg = f"TEST_WARN_{uuid.uuid4()}"
        err_msg = f"TEST_ERR_{uuid.uuid4()}"
        log_warning(user=None, url='/warn', file_name='WarnFile',
                    message=warn_msg)
        log_error(user=None, url='/err', file_name='ErrFile',
                  message=err_msg)
        lines = self._read_log()
        assert any(warn_msg in line for line in lines)
        assert any(err_msg in line for line in lines)

    def test_debug_and_critical(self):
        crit_msg = f"TEST_CRIT_{uuid.uuid4()}"
        dbg_msg = f"TEST_DBG_{uuid.uuid4()}"
        log_debug(user='u', url='/d', file_name='DbgFile', message=dbg_msg)
        log_critical(user='u', url='/c', file_name='CritFile',
                     message=crit_msg)
        lines = self._read_log()
        assert any(crit_msg in line for line in lines)

    def test_log_view_access_success(self, caplog):
        rf = RequestFactory()
        request = rf.get('/demo')

        @log_view_access
        def demo_view(request):  # noqa: F811
            return 'ok'

        # El decorador puede preservar el nombre original o usar 'wrapper'
        with caplog.at_level(logging.INFO, logger='app_logger'):
            result = demo_view(request)
        assert result == 'ok'
        assert re.search(r"Acceso a vista: (demo_view|wrapper)", caplog.text)

    def test_log_view_access_error(self, caplog):
        rf = RequestFactory()
        request = rf.get('/boom')

        @log_view_access
        def boom_view(request):  # noqa: F811
            raise RuntimeError('Boom!')

        with caplog.at_level(logging.ERROR, logger='app_logger'):
            with pytest.raises(RuntimeError):
                boom_view(request)
        assert re.search(r"Error en vista boom_view: Boom!", caplog.text)
