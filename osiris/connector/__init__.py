import abc
import enum
from typing import Any

from osiris.base import logutils
from osiris.base.environments import env
from osiris.exceptions import IllegalArgumentException


class ConnectorException(Exception):
    pass


class ConnectorFailedException(ConnectorException):
    pass


class ConnectorExitState(enum.Enum):
    """
    Generic exit status return by connector to indicate the success or failure state
    """
    SUCCESS = 0
    TIMEOUT = 5
    ERROR = 6


log = logutils.get_logger(__name__)


def load_connector_settings(key: str) -> dict:
    log.info(f"Loading connector settings for: {key}")
    settings = env.get_section(key)
    if not settings:
        raise IllegalArgumentException(f"no settings defined for key: {key}")
    secret_name = settings.pop("secure_settings_aws_secret_name", None)
    if secret_name:
        log.info(f"....... and loading secure settings")
    secure = env.get_property(f"vault.{secret_name}")
    return {**settings, **secure}


class Connector(abc.ABC):

    def __init__(self, name: str):
        self.name = name
        self.settings = load_connector_settings(f"connector.{name}")

    def get_setting(self, name: str, fallback: Any = None) -> Any:
        return self.settings.get(name, fallback)

    def log_event(self, event, detail=None):
        # simplest implementation of logging events
        log.info(f"[{event}] {detail}")
