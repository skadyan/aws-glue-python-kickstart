import abc
import enum
from abc import abstractmethod
from typing import Any

from osiris.base import logutils
from osiris.base.environments import Environment

log = logutils.get_logger(__name__)


class JobRunStatus(enum.Enum):
    """
    Generic exit status return by connector to indicate the success or failure state
    """
    SUCCESS = 0
    TIMEOUT = 5
    ERROR = 6


def load_job_settings(env: Environment, name: str) -> dict:
    return env.get_section(name)


class BaseJob(abc.ABC):
    def __init__(self, name: str, env: Environment, **kwargs):
        self.name = name
        self.env = env
        self.settings = load_job_settings(env, name)

    def get_setting(self, key: str, fallback: Any) -> Any:
        return self.settings.get(key, fallback)

    def run(self, **kwargs) -> JobRunStatus:
        self.log_event("START_JOB_RUN", f"Running with args: {kwargs}")
        # noinspection PyBroadException
        try:
            run_status = self.do_run(**kwargs)
        except TimeoutError as e:  # flake8: noqa
            log.exception(f"Timeout error occurred: {e}")
            run_status = JobRunStatus.TIMEOUT
        except Exception as e:  # flake8: noqa
            log.exception(f"Unhandled exception occurred: {e}")
            run_status = JobRunStatus.ERROR
        finally:
            self.log_event("END_JOB_RUN")

        return run_status

    @abstractmethod
    def do_run(self, **kwargs):
        pass

    def log_event(self, event, detail=None):
        # simplest implementation of logging events
        log.info(f"[{event}] {detail}")
