@echo off

REM Check for the "install" command (case-insensitive)
if "%~1"=="install" (
    call venv\Scripts\pip install -r requirements.txt
) else (
    REM Check for the "update" command (case-insensitive)
    if "%~1"=="update" (
        call venv\Scripts\pip freeze > requirements.txt
    ) else (
        echo Unknown command: %~1
        exit /b 1
    )
)

exit /b 0
