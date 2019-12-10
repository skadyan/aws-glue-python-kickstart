import json

import boto3
import httpretty


def assume_secret_is_defined_with(secret_name: str, payload: dict):
    conn = boto3.client('secretsmanager')
    conn.create_secret(Name=secret_name, SecretString=json.dumps(payload))


def assume_http_service_will_return_json(url, http_method: str, body: dict, **headers: dict):
    httpretty.register_uri(httpretty.POST, url, json.dumps(body), content_type="application/json", **headers)
