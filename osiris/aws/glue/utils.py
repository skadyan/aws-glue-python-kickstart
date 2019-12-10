from argparse import ArgumentParser

from osiris.aws.glue import Job
from osiris.base.logutils import get_logger

_log = get_logger(__name__)


class GlueArgumentError(Exception):
    def __init__(self, msg: str):
        self.msg = msg


class GlueArgumentParser(ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Below are based on the
        # https://github.com/awslabs/aws-glue-libs/blob/9a7611c854a3972f0bd94a2ce27e539b877d5542/awsglue/utils.py#L64

        self.add_argument(Job.job_bookmark_options()[0], choices=Job.job_bookmark_options()[1:], required=False)
        self.add_argument(Job.continuation_options()[0], choices=Job.continuation_options()[1:], required=False)

        for option in Job.job_bookmark_range_options():
            self.add_argument(option, required=False)

        for option in Job.id_params()[1:]:  # Notice JOB_NAME is not reserved parameter
            # TODO are these Mandatory or always present by glue runtime?
            self.add_argument(option, required=False)

        self.add_argument(Job.encryption_type_options()[0], choices=Job.encryption_type_options()[1:])
        self.add_argument('--TempDir', required=False)  # TODO is this Mandatory or always present by glue runtime
        self.add_argument(Job.script_location()[0], required=False)
        self.add_argument(Job.extra_py_files()[0], required=False)
        self.add_argument(Job.job_language()[0], required=False)

    def add_user_arguments(self, *options):
        for option in options:
            required = True
            if option[-1] == "?":
                option = option[:-1]
                required = False
            self.add_argument(f"--{option}", required=required)

    def error(self, msg):
        raise GlueArgumentError(msg)
