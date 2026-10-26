@echo off
REM Setup script for the Ming-3.0-tts web project (Windows).
REM Creates a Python 3.10 virtual environment and installs dependencies.

setlocal
set "ROOT=%~dp0"
set "VENV=%ROOT%venv"

where py >nul 2>&1 || (echo [ERR] Python launcher 'py' not found. Install Python 3.10. & exit /b 1)

if not exist "%VENV%" (
    echo [1/3] Creating virtual environment (Python 3.10)...
    py -3.10 -m venv "%VENV%"
) else (
    echo [1/3] venv already exists, skipping creation.
)

echo [2/3] Upgrading pip...
call "%VENV%\Scripts\activate.bat"
python -m pip install --upgrade pip

echo [3/3] Installing dependencies...
pip install -r "%ROOT%requirements.txt"

echo.
echo Setup complete. Next steps:
echo   1. Download the model:  download_model.bat
echo   2. Start the server:    run.bat
echo.
endlocal
