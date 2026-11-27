@echo off
call "%~dp0run_tests.cmd" --phone-demo
if errorlevel 1 pause
