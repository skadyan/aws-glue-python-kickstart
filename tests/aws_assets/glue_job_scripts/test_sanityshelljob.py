from tests.aws_assets.glue_job_scripts import load_shell_job_script


def test_run_it():
    with load_shell_job_script('sanity_shell_job', "--python_version", "no") as job:
        data = job.run_it()
    assert len(data) > 1
