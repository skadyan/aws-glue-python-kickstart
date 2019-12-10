# *** Disclaimer: Adopted from: https://github.com/awslabs/aws-glue-libs/tree/master/awsglue/job.py
import os
from pathlib import Path

from osiris.aws import S3Url
from osiris.aws.s3 import exists_s3
from osiris.exceptions import IllegalStateException


class Job:

    @classmethod
    def continuation_options(cls):
        return ['--continuation-option', 'continuation-enabled', 'continuation-readonly', 'continuation-ignore']

    @classmethod
    def job_bookmark_options(cls):
        return ['--job-bookmark-option', 'job-bookmark-enable', 'job-bookmark-pause', 'job-bookmark-disable']

    @classmethod
    def job_bookmark_range_options(cls):
        return ['--job-bookmark-from', '--job-bookmark-to']

    @classmethod
    def id_params(cls):
        return ['--JOB_NAME', '--JOB_ID', '--JOB_RUN_ID', '--WORKFLOW_RUN_ID', '--WORKFLOW_NAME '
            , '--SECURITY_CONFIGURATION']

    @classmethod
    def encryption_type_options(cls):
        return ['--encryption-type', 'sse-s3']

    @classmethod
    def script_location(cls):
        return ['--scriptLocation']

    @classmethod
    def extra_py_files(cls):
        return ['--extra-py-files']

    @classmethod
    def job_language(cls):
        return ['--job-language']

    @classmethod
    def is_running_in_glue(cls):
        return os.environ.get('GLUE_INSTALLATION') is not None

    @classmethod
    def s3_bucket_and_app_home(cls):
        # This method assume that script is defined
        # APP_HOME/scripts/xyz-job.py
        # This method read the --scriptLocation argument
        if Job.is_running_in_glue():
            from osiris.aws.glue.utils import GlueArgumentParser

            parser = GlueArgumentParser()
            args, extras = parser.parse_known_args()
            url = S3Url(args.scriptLocation)
            app_home = Path(url.key).parent
            posix_path = None
            while app_home:
                posix_path = app_home.as_posix()
                if posix_path == ".":
                    raise IllegalStateException("Script location parent(or grandparent) "
                                                "must have conf/ directory in it's parent")
                if exists_s3(url.bucket, f"{posix_path}/conf/defaults.yaml"):
                    break
                app_home = app_home.parent

            return url.bucket, posix_path
        else:
            return None, None
