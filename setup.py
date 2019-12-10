import glob
import logging
import os
import shutil
import subprocess
from pathlib import Path

from distutils.log import WARN
from setuptools import find_packages, setup, Command

logging.basicConfig(level="WARN")

COPY_LIB_DIR = False


def read_install_requirements():
    with open("requirements.txt", encoding="utf-8") as fp:
        requirements = [dep for dep in [line.strip() for line in fp.readlines()] if dep and dep[0] not in ('#', '-')]
    return requirements


class BuildException(Exception):
    def __init__(self, msg):
        super().__init__(msg)
        self.msg = msg


class Clean(Command):
    CLEAN_FILES = './build ./dist ./*.pyc ./*.tgz ./*.egg-info'.split(' ')
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        for path_spec in self.CLEAN_FILES:
            abs_paths = glob.glob(path_spec)
            for path in [str(p) for p in abs_paths]:
                self.announce(f"removing {os.path.relpath(path)}", level=WARN)
                shutil.rmtree(path)


class CopyAppFiles(Command):
    description = "Copy application configuration and job_script files for deployment"
    user_options = []
    app_file_dirs = [
        "conf",
        "aws_assets",
    ]

    @staticmethod
    def copy_dir(src, dst):
        dst.mkdir(parents=True, exist_ok=True)
        for item in os.listdir(src):
            s = src / item
            d = dst / item
            if s.is_dir():
                CopyAppFiles.copy_dir(s, d)
            else:
                shutil.copy2(str(s), str(d))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        target = Path("dist")
        dirs = map(lambda e: Path(e), self.app_file_dirs)
        for file_dir in dirs:
            CopyAppFiles.copy_dir(file_dir, target / file_dir)


class GluePackageBuild(Command):
    description = "Python Build Package for Glue jobs"
    requirements_txt = "requirements.txt"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):

        os.makedirs("target", exist_ok=True)
        self.run_command("flake8")  # code style
        self.run_command("pytest")  # Unit tests
        self.run_command("bdist_wheel")  # .whl dist file
        self.run_command("copy_app_files")  # Zip app files

        target = "dist/lib"
        cmd = f"pip wheel -r {GluePackageBuild.requirements_txt} -w {target}"
        exit_code, output = subprocess.getstatusoutput(cmd)

        if exit_code != 0:
            raise BuildException(f"build failed: {output}")

        provided_dependencies = []
        with open("requirements-glue.txt") as glue_req_txt:
            from pkg_resources import parse_requirements
            for line in glue_req_txt.readlines():
                line: str = line.strip()
                if line == "" or line.startswith("#") or line.startswith("-r"):
                    continue
                provided_dependencies.append(list(parse_requirements(line))[0].name)

        for whl in os.listdir(target):
            whl_name = whl[0: whl.index('-')]
            if whl_name in provided_dependencies:
                self.announce(f"Review your requirements.txt if this dependency is specified explicitly: {whl}", WARN)
                os.unlink(f"{target}/{whl}")
        if not COPY_LIB_DIR:
            shutil.rmtree(target)
        self.announce(f"Code artifacts are in: {Path(target).parent.resolve()}", WARN)


# See setup.cfg for additional keywords
setup(
    name="osiris",
    author="Sandeep Kadyan",
    packages=find_packages(include=("osiris*",)),
    python_requires=">=3.6",
    cmdclass={
        "clean": Clean,
        "copy_app_files": CopyAppFiles,
        "package": GluePackageBuild
    },
    install_requires=read_install_requirements()
)
