import base64
import json
from json import JSONDecodeError
from typing import Union

from botocore.exceptions import ClientError, NoCredentialsError

from osiris.aws import new_service_client
from osiris.base.logutils import get_logger
from osiris.exceptions import IllegalStateException, IllegalArgumentException
from osiris.vault import SecretVault

_log = get_logger(__name__)


def _try_parse_as_json(text: str) -> dict:
    try:
        return json.loads(text)
    except JSONDecodeError:
        return None


class AwsSecretManagerVault(SecretVault):
    """
    AwsSecretManagerVault - Secret Vault Manager Implementation based on below example:
    https://docs.aws.amazon.com/code-samples/latest/catalog/python-secretsmanager-secrets_manager.py.html
    """

    def __init__(self, region_name: str):
        self.client = new_service_client(service_name="secretsmanager", region_name=region_name)

    def get_secret(self, secret_id: str, attr: str = None) -> Union[dict, str]:
        """
        :param secret_id: required; Secret Id
        :param attr: configured attribute
        :return: str-value of attr is specified else dict-value if configured as json else str
        """
        secret = None
        try:
            response = self.client.get_secret_value(SecretId=secret_id)
        except NoCredentialsError as e:
            raise IllegalStateException(f"Check your boto3 api credentials. {e.args}") from None
        except ClientError as e:
            error_code = e.response['Error']['Code']
            _log.error(f"Could not retrieve secret for requested secret id: '{secret_id}' Error code: {error_code}")
            if error_code == "DecryptionFailureException":
                raise IllegalStateException(f"{error_code}: Check secret encryption setting in Secrets Manager") from e
            elif error_code in ("InvalidParameterException", "InvalidRequestException"):
                raise IllegalArgumentException(f"parameter is missing or invalid") from e
            elif error_code == "ResourceNotFoundException":
                raise IllegalArgumentException(f"Specified secret '{secret_id}' is not defined. {e.args}") from None
            elif error_code == "UnrecognizedClientException":
                raise IllegalStateException(f"Current security credentials seems not correct") from e
            else:
                raise IllegalStateException(f"Unhandled Exception occurred") from e
        else:
            if 'SecretString' in response:
                secret = response['SecretString']
            else:
                secret = base64.b64decode(response['SecretBinary'])

        json_secret = _try_parse_as_json(secret)

        if json_secret:
            secret = json_secret

        if attr:
            if json_secret and attr in json_secret:
                secret = json_secret[attr]
            else:
                raise IllegalArgumentException(f"Could not find {attr} in configured secret value")

        return secret
