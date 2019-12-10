import abc
from abc import abstractmethod
from typing import Union

from osiris.base.generalutils import instantiate


class SecretVault(abc.ABC):

    @abstractmethod
    def get_secret(self, key: str, attr: str = None, **kwargs) -> Union[dict, str]:
        pass


class NoopSecretVault(SecretVault):

    def get_secret(self, key: str, attr: str = None, **kwargs) -> Union[dict, str]:
        return None


def new_secret_vault(env) -> SecretVault:
    instance = None
    if env.flag("sys.vault.enabled"):
        impl = env.get_property("sys.vault.impl")
        impl_kwargs = env.get_section("sys.vault.impl_kwargs")
        instance = instantiate(impl, impl_kwargs)
    return instance
