@echo off

REM Build the full command to execute
set "full_command=python manage.py %*"

REM Execute the full command
%full_command%

exit /b 0
