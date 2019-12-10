import sys

from osiris.aws.glue.utils import GlueArgumentParser


def init_shell_job(*options):
    parser = GlueArgumentParser()
    parser.add_user_arguments(*options)

    sys_args = parser.parse_args(sys.argv[1:])

    from osiris.base.environments import env, ArgParserNamespacePropertySource
    env.add_source(ArgParserNamespacePropertySource(sys_args))

    return env
