from contextlib import contextmanager

from botocore.exceptions import ClientError
from botocore.response import StreamingBody

from osiris.aws import new_service_client

_s3_client = new_service_client("s3")


@contextmanager
def open_s3(bucket: str, key: str) -> StreamingBody:
    """
    This method must be called with context manager
    :param bucket: s3 bucket
    :param key: file key
    :return: content stream as file-like object
    """
    body: StreamingBody = _s3_client.get_object(Bucket=bucket, Key=key)['Body']
    try:
        yield body
    finally:
        body.close()


def exists_s3(bucket: str, key: str) -> bool:
    """
    This method test if the specified key exists in bucket
    :param bucket:
    :param key:
    :return: true if key exists
    """
    try:
        _s3_client.head_object(Bucket=bucket, Key=key)
        exists = True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            exists = False
        else:
            raise
    return exists
