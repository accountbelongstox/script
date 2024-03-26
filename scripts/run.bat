@echo off
set "python_version=39"
set "python_exe=python%python_version%"
rem Check if Python with version 3.9 exists
where %python_exe% >nul 2>nul

set "VENV_DIR=%~dp0venv"
if not exist "%VENV_DIR%" (

    if %errorlevel% neq 0 (
        echo %python_exe% not found. Please install Python %python_version% and run the script again.
        exit /b 1
    )
    %python_exe% --version
    echo venv directory does not exist. Creating...
    cd /d "%~dp0" || exit /b
    %python_exe% -m venv venv
    echo Venv-Python: %VENV_DIR%\Scripts\python.exe
)
echo Venv-Python: %VENV_DIR%\Scripts\python.exe
rem Execute main.py with the provided argument
%VENV_DIR%\Scripts\python.exe main.py %1
