import logging

from common.logging.context import get_request_id


class RequestIdFilter(logging.Filter):
    """Agrega `request_id` a cada registro para poder usarlo en el formato."""

    def filter(self, record):
        if not hasattr(record, 'request_id'):
            record.request_id = get_request_id()
        return True
