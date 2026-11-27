@echo off
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"
set "VENV_PY=.venv\Scripts\python.exe"

if exist "%VENV_PY%" goto install
where py >nul 2>nul
if errorlevel 1 goto create_with_python
py -3 -m venv .venv
if errorlevel 1 goto create_with_python
goto install

:create_with_python
python -m venv .venv
if errorlevel 1 goto failed

:install
"%VENV_PY%" -m pip install --disable-pip-version-check -q -r requirements.txt
if errorlevel 1 goto failed
"%VENV_PY%" run_tests.py %*
set "RUN_CODE=%ERRORLEVEL%"
goto finish

:failed
set "RUN_CODE=1"
echo Setup failed. Python 3.10+ and an internet connection are required for the first run.

:finish
if "%~1"=="" pause
exit /b %RUN_CODE%
