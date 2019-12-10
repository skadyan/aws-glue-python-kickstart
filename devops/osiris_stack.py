from aws_cdk import (
    core
)


class OsirisStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.add_glue_shell_jobs()

    def add_glue_shell_jobs(self):
        pass
