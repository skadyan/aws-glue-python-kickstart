import importlib
import sys
from contextlib import contextmanager


@contextmanager
def load_shell_job_script(script, *cmd_args):
    file_path = f"aws_assets/glue_job_scripts/shell/{script}.py"
    spec = importlib.util.spec_from_file_location(script, file_path)
    script_module = importlib.util.module_from_spec(spec)
    try:
        orig_argv = sys.argv
        sys.argv = [file_path, *cmd_args]
        spec.loader.exec_module(script_module)
        yield script_module
    finally:
        sys.argv = orig_argv
