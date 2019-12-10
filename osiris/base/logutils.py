import logging

from osiris.exceptions import IllegalArgumentException


def bootstrap():
    pass


def get_logger(name: str):
    if not name:
        raise IllegalArgumentException("'logger name' is required")
    return logging.getLogger(name)


# Fallback Configuration; Will be overridden in bootstrap
logging.basicConfig(level=logging.DEBUG)
