@echo off

echo "Building...."

if not exist setup.py goto :on_error_incorrect_cwd

if "%VIRTUAL_ENV%"=="" (
    echo Python Virtual environment not activated. Activating...
    venv\Scripts\activate
)

echo Installing python third-party requirements
pip install -r requirements-dev.txt
if not %ERRORLEVEL%==0 goto :onerror_pip_install_failed

echo Running code style checks"
flake8
if not %ERRORLEVEL%==0 goto :onerror_flake8_failed

echo Running unit tests"
pytest
if not %ERRORLEVEL%==0 goto :onerror_unit_test_failed


echo Building dist (.whl) artifact"
python setup.py bdist_wheel
if not %ERRORLEVEL%==0 goto :onerror_bdist_failed
goto :success

:on_error_incorrect_cwd
echo setup.py is missing directory. Check your current working directory path
set error_level=10
goto :on_error


:onerror_pip_install_failed
echo Pip install failed
set error_level=11
goto :on_error

:onerror_flake8_failed
echo Code style (flake8) checks failed
set error_level=12
goto :on_error

:on_unit_test_failed
echo there are unit test case failure.
set error_level=15
goto :on_error

:onerror_bdist_failed
echo Build bdist failed
set error_level=20
goto :on_error

:on_error
if "%error_level%"=="" set error_level=%ERRORLEVEL%
echo "Exiting with error level: %error_level%"

@exit /b %error_level%

:success
if %errorlevel%==0 echo "Build Successful"


