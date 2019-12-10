from coverage import env

from osiris.aws.secrets import AwsSecretManagerVault
from osiris.base.environments import env


def example():
    vault = AwsSecretManagerVault(region_name="us-east-2")

    secret_name = "connector/sample/webapiservice/keys"
    # Assumed we have configured it as : {"client_id":"ThisIsAnClientId","secret_key":"ThisIsAnSecretKey"}

    secret_attr_value = vault.get_secret(secret_name, "client_id")
    print(secret_attr_value)

    secret = vault.get_secret(secret_name)
    print(secret)

    prop = env.get_property(f"vault.{secret_name}")

    print(prop)


if __name__ == '__main__':
    example()
