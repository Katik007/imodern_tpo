@echo off
call "%~dp0run_tests.cmd" --headed
if errorlevel 1 pause
