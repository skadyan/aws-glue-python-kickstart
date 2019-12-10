import json

import boto3
from moto import mock_secretsmanager

from osiris.base import environments
from osiris.base.environments import env


def test_check_app_version():
    from osiris.__version__ import version
    assert version


def test_app_env_name_is_set():
    app_env = environments.get_app_env_name()
    assert app_env


def test_section():
    kwargs = env.get_section("sys.vault.impl_kwargs")
    assert len(kwargs) != 0


@mock_secretsmanager
def test_secret_vault_integration():
    secret_name = "connector/sample/webapiservice/keys2"

    # Setup
    conn = boto3.client('secretsmanager', region_name=env.get_property('sys.vault.impl_kwargs.region_name'))

    secret_name = "test/secret/example"
    conn.create_secret(Name=secret_name, SecretString=json.dumps({
        "api_key": "testapikey"
    }))
    secret = env.get_property(f"vault.{secret_name}")
    assert secret["api_key"] == "testapikey"
