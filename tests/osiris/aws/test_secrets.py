import json

import boto3
import pytest
from moto import mock_secretsmanager
from pytest import fail

from osiris.aws.secrets import AwsSecretManagerVault
from osiris.exceptions import IllegalArgumentException

vault = AwsSecretManagerVault(region_name="us-east-2")


@mock_secretsmanager
def test_secret_manager_vault_impl():
    secret_name = "connector/sample/webapiservice/keys2"

    # Setup
    conn = boto3.client('secretsmanager', region_name='us-east-2')
    conn.create_secret(Name=secret_name, SecretString=json.dumps({
        "api_key": "testapikey"
    }))

    # Call
    secret = vault.get_secret(secret_name)
    secret_api_key = vault.get_secret(secret_name, "api_key")
    # Assert
    assert secret["api_key"] == "testapikey"
    assert secret_api_key == "testapikey"


@mock_secretsmanager
@pytest.mark.skip("Manual test")
def test_secret_manager_vault_impl_invalid_key():
    secret_name = "connector/sample/webapiservice/keys3"
    # Nothing to setup

    # Call
    with pytest.raises(IllegalArgumentException) as info:
        vault.get_secret(secret_name)
        fail("Should not happen")
    assert "ResourceNotFoundException" in info.value.msg
