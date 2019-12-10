# Development Setup

## Prerequisites Software
* Python 3.6.9 (or 3.6.x)

* Any decent text editor (e.g. Notepad++ )
* PyCharm Community Edition
* Git Client 2.22.x or better

For CDK pipelines
* Install aws-cli .See https://cdkworkshop.com/15-prerequisites/100-awscli.html
* Install nodejs with npm https://nodejs.org/
* Install aws-cdk toolkit. Make sure it is added in path
    
    > npm install -g aws-cdk

## Technology Stater Links
1. Markdown: For this readme documentation
   https://www.markdownguide.org/basic-syntax/
1. CDK
   https://cdkworkshop.com/ 
1. PyGreSQL  (use DB-API)
   http://www.pygresql.org/contents/tutorial.html#first-steps-with-the-db-api-2-0-interface

## Local Development Box Setup
1. Ensure python, git executables are in your PATH variable.
1. Checkout code using git clone into a directory, say: ROOT
    > git clone <git-repo-path>
1. Change directory to ROOT
    > cd $ROOT

1. Create Python Virtual environment. Make sure you are using virtualenv belonging to python 3.6.x
    1. Linux/macOS  : virtualenv venv
1. Open Terminal and activate your virtual environment and install external python modules via below command:
    >(Windows): venv\Scripts\activate
    
    >pip install -r requirements-dev.txt

1. Configure the project in PyCharm IDE
    1. Open python code root directory via menu 
    > File | Open... | Open File or Folder (choose **$ROOT**) 

1. Once opened, configure the Project Interpreter (Python executable)
    
    <sub>**Note:-** PyCharm may already detected venv automatically. So you may not need to perform this step.</sub>
    > File | Settings | Project: aws-glue-python-kickstart| Project Interpreter
    
    In `Settings` dialog box, click on `settings button` in front of `Project Interpreter` dropdown box <br/> 
    and select `Add..` <br/>
    In `Add Python Interpreter` dialog box choose `Existing environment` option<br/> 
    and select (windows) $ROOT/venv/Scripts/python path.<br/>
    Click `OK` to close the dialog box <br/>
    Now ensure or choose the newly added virtual environment in the drop down field (on top) <br/>
    Click `Apply` to apply change.<br/>

1. Configure the pytest as default integrated test runner.
    
    <sub>**Note:-** PyCharm may already detected pytest as default runner automatically. So you may not need to
    perform this step.</sub>
    > File | Settings | Tools | Python Integrated Tools

    Chose `py.test` in dropdown field `Default test Runner:` <br/>
    and click on `Apply` button
1. Configure default run configuration
    > Run | Edit Configurations...
    
        > File | Settings | Tools | Python Integrated Tools

    Navigate to `Templates` > `Python panel` <br/>
    For field `Working Directory` choose project root path (`$ROOT`) <br/>
    
    Navigate to `Templates` > `Python tests` > `pytest` <br/>
    For field `Working Directory` choose project root path (`$ROOT`) <br/>
    and click on `OK` button to close the `Run/Debug Configurations` dialog box.
1. For setting any OS ENVIRONMENT variable, you can create the `.env` file at root folder by copying the file 
    `.env.template`. This file is meant to host environment variable meaningful for your local environment only. So 
    never commit this.
1. Add Source directories

    > devops

# Build
1. Activate the venv, if not already done
    > cd $ROOT<br/>
    (windows) venv/Scripts/activate
1. Code Build
    > No compilation required (as of now)
1. Python Code style check (report at target/flake-reports/index.html)
    
    See `setup.cfg#flake8` section for custom PEP-8 rule configuration 
    > flake8 
    
    <sub>**Note:-** You may use `# flake8: noqa` for disabling inspection on any code line</sub> 
1. Python Unit Test (report at target/pytest-report.html)

    You can run all unit test cases from PyCharm too by right clicking on `tests` directory and `Run pytests in tests`
     option
    > pytest
1. Python Unit Test with code Coverage (target/coverage-reports/index.html)
    
    See `setup.cfg#coverage:report` section for configuration and coverage threshold 
    > pytest --cov=osiris --cov-report html --cov-report term
    
    1. Cover code under package `osiris`
    1. Generate html report and
    1. Generate terminal report
1. Generating .whl files for Glue Shell Jobs
    > python setup.py package
    
    1. Generate artifacts under dist/ directory.
1. Run CDK
    > cdk synth \[--toolkit-stack-name stackname \]
    
    > cdk deploy
    
    > cdk destroy
