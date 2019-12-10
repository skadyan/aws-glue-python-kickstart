import json
import sys
import os
import pkg_resources

#
# Below line define the expected shell command line arguments which can be defined in Glue Job Definition.
# To make the argument optional, suffix the name with '?' character.
# in order to access the command line argument you could use
#
# >>>   env.get_property('sys_args.python_version')
#

from osiris.base.jobutils import init_shell_job

env = init_shell_job(
    'python_version?',
    'environ?',
    'cmd_args?'
)


class PythonEnvironmentInfo(dict):
    def __init__(self):
        self['platform'] = sys.platform
        self['dependencies'] = []

        if env.get_property('sys_args.python_version', True):
            self['version_info'] = sys.version

        if env.flag('sys_args.environ', True):
            self['environ'] = dict(os.environ)

        if env.flag('sys_args.cmd_args', True):
            self['args'] = sys.argv

    def add_dependency(self, dependency):
        self['dependencies'].append(dependency)


def run_it():
    info = PythonEnvironmentInfo()
    for ws in pkg_resources.working_set:
        info.add_dependency(str(ws.as_requirement()))
    return info


if __name__ == '__main__':
    print(json.dumps(run_it(), indent=4))
