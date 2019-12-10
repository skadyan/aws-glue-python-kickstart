import abc
import os
import re
import typing
from abc import abstractmethod
from argparse import Namespace
from functools import lru_cache
from typing import Any, Callable, List

import yaml

from osiris.base import logutils, generalutils
from osiris.base.fsutils import fs_open, fs_exists
from osiris.base.generalutils import flatten_dict
from osiris.exceptions import BadInterpolationException
from osiris.vault import NoopSecretVault

_log = logutils.get_logger(__name__)


class PropertySource(abc.ABC):
    """
    PropertySource abstract the property sources to provide the application/job wide properties
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def property_names(self) -> typing.Collection:
        pass

    @abstractmethod
    def get_property(self, p: str) -> Any:
        pass

    def __contains__(self, item):
        return item in self.property_names()

    def __repr__(self):
        return f"{self.name}"


class YamlPropertySource(PropertySource):
    def __init__(self, name: str, payload: dict = {}):
        super().__init__(name)
        self._payload = flatten_dict(payload)
        self._keys = frozenset(self._payload)

    @staticmethod
    def load_from(stream, name: str):
        """Load from File-Like streaming object (It should be in utf-8 encoding)"""
        combined_payload = {}
        for payload in yaml.safe_load_all(stream):
            combined_payload = {**combined_payload, **payload}
        return YamlPropertySource(name, combined_payload)

    def property_names(self) -> typing.Collection:
        return self._keys

    def get_property(self, p: str) -> Any:
        return self._payload.get(p)


class OSEnvironmentPropertySource(PropertySource):
    def __init__(self, name: str = "osenv"):
        super().__init__(name)
        self._env = os.environ
        self._key_prefix = f"{name}."

    def property_names(self) -> typing.Collection:
        return frozenset([f"{self._key_prefix}{n}" for n in self._env.keys()])

    def get_property(self, p: str) -> Any:
        prefix = self._key_prefix
        return self._env.get(p[len(prefix):]) if p.startswith(prefix) else None


class ArgParserNamespacePropertySource(PropertySource):
    def __init__(self, ns: Namespace, name: str = "sys_args"):
        super().__init__(name)
        self._ns = ns
        self._key_prefix = f"{name}."
        self._keys = frozenset([f"{self._key_prefix}{n}" for n in vars(ns)])

    def get_property(self, p: str) -> Any:
        prefix = self._key_prefix
        return getattr(self._ns, p[len(prefix):]) if p.startswith(prefix) else None

    def property_names(self) -> typing.Collection:
        return self._keys


class SecretVaultPropertySource(PropertySource):
    def __init__(self, name: str = "vault"):
        super().__init__(name)
        self._vault = None
        self._key_prefix = f"{name}."
        self._keys = frozenset([])  # Blank due to security
        self._init_vault()

    def _init_vault(self):
        if not self._vault:
            from osiris.vault import new_secret_vault
            secret_vault = new_secret_vault(env)
            if secret_vault:
                self._vault = secret_vault
            else:
                self._vault = NoopSecretVault()
                _log.warning("Secret Vault not enabled")

    def get_property(self, p: str) -> Any:
        prefix = self._key_prefix
        if not p.startswith(prefix):
            return None
        key_with_attr = p[len(prefix):]
        key, attr = (key_with_attr, None) if key_with_attr.find(':') == -1 else key_with_attr.rsplit(':', maxsplit=1)
        return self._vault.get_secret(key, attr)

    def property_names(self) -> typing.Collection:
        return self._keys

    def __contains__(self, item):
        return item.startswith(self._key_prefix)


class Environment:
    _KEYCRE = re.compile(r"\$\{([^}]+)\}")
    _MAX_INTERPOLATION_DEPTH = 10

    def __init__(self):
        self.sources: List[PropertySource] = []

    def add_source(self, source: PropertySource):
        """
        Add the property source assuming it has high precedence
        :param source: property source
        """
        self.sources.insert(0, source)
        _log.info(f"Property source registered: {source}")

    def get_property(self, key: str, fallback: Any = None, coerce: Callable = None) -> Any:
        return self._get_property(key, fallback, coerce)

    @lru_cache()
    def get_cached_property(self, key: str, fallback: Any = None, coerce: Callable = None) -> Any:
        return self._get_property(key, fallback, coerce)

    def _get_property(self, key: str, fallback: Any = None, coerce: Callable = None) -> Any:
        value = None
        for source in self.sources:
            if key in source:
                value = source.get_property(key)
                value = self._interpolation(key, value, 0)
                break
        if not value:
            value = fallback

        if coerce:
            value = coerce(value)

        return value

    def _interpolation(self, key: str, raw_value: str, depth: int):
        # Must be not None
        # Must be str value
        # Heuristic to test if contains ${var}
        if not (raw_value
                and isinstance(raw_value, str)
                and '$' in raw_value):
            return raw_value

        if depth > Environment._MAX_INTERPOLATION_DEPTH:
            raise BadInterpolationException(f"max interpolation depth reached. "
                                            f"Last offending key: {key} = {raw_value}")
        accumulator = []
        rest = raw_value
        while rest:
            p = rest.find("$")
            if p < 0:
                accumulator.append(rest)
                break
            if p > 0:
                accumulator.append(rest[:p])
                rest = rest[p:]
            c = rest[1:2]
            if c == "$":
                accumulator.append("$")
                rest = rest[2:]
            elif c == "{":
                m = self._KEYCRE.match(rest)
                if m is None:
                    raise BadInterpolationException(f"bad interpolation variable reference: {rest}")
                ref_var = m.group(1)
                rest = rest[m.end():]
                ref_var_value = self.get_property(ref_var)
                if not ref_var_value:
                    if not self.is_known_property(ref_var):
                        raise BadInterpolationException(f"undefined reference: '{ref_var}' for property: {key}")
                else:
                    if accumulator or rest:
                        accumulator.append(str(ref_var_value))
                    else:
                        return ref_var_value
        return "".join(accumulator)

    def is_known_property(self, p: str) -> bool:
        for source in self.sources:
            if p in source:
                return True
        return False

    def get_property_as_int(self, key: str, fallback: int) -> int:
        return self.get_property(key, fallback, int)

    def flag(self, key: str, fallback: bool = None) -> bool:
        return generalutils.flag(self.get_property(key, fallback))

    def get_section(self, section: str) -> dict:
        prefix = f"{section}."
        names = set()
        for source in self.sources:
            names.update([n for n in source.property_names() if n.startswith(prefix)])
        values = dict()
        for name in names:
            values[name[len(prefix):]] = self.get_property(name)
        return values


def get_app_env_name() -> str:
    """
    Return the environment name

    :return: environment name
    """
    return os.environ.get("APP_ENV_NAME")


def _bootstrap():
    from dotenv import load_dotenv
    load_dotenv()

    with fs_open("conf/defaults.yaml") as fp:
        env.add_source(YamlPropertySource.load_from(fp, "defaults"))

    env.add_source(OSEnvironmentPropertySource())
    env.add_source(SecretVaultPropertySource())

    env_conf_file = f"conf/env-{get_app_env_name()}.yaml"

    if fs_exists(env_conf_file):
        with fs_open(env_conf_file) as fp:
            env.add_source(YamlPropertySource.load_from(fp, env_conf_file))

    from osiris.base.logutils import bootstrap
    bootstrap()


env = Environment()

_bootstrap()
