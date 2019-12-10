import os

from osiris.aws.glue import Job
from osiris.aws.s3 import open_s3, exists_s3
from osiris.base.logutils import get_logger

_log = get_logger(__name__)

s3_bucket, app_home = Job.s3_bucket_and_app_home()


def fs_open(path: str):
    if s3_bucket:
        full_path = f"{app_home}/{path}"
        _log.info(f"Opening path 's3://{s3_bucket}/{full_path}' as input stream")
        fs = open_s3(s3_bucket, full_path)
    else:
        _log.info(f"Opening path '{path}' as input stream")
        fs = open(path)

    return fs


def fs_exists(path: str) -> bool:
    if s3_bucket:
        full_path = f"{app_home}/{path}"
        exist = exists_s3(s3_bucket, full_path)
    else:
        exist = os.path.exists(path)
    return exist
