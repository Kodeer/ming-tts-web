@echo off
REM Start the Ming-3.0-tts web server.
REM Set MING_MODEL_PATH / MING_DEVICE / MING_PORT to override defaults.

setlocal
set "ROOT=%~dp0"
set "VENV=%ROOT%venv"

if not exist "%VENV%" (
    echo [ERR] venv not found. Run setup.bat first.
    exit /b 1
)

if "%MING_MODEL_PATH%"=="" set "MING_MODEL_PATH=%ROOT%models\Ming-3.0-tts-0.5b"
if "%MING_DEVICE%"=="" set "MING_DEVICE=cuda:0"
if "%MING_PORT%"=="" set "MING_PORT=7860"

call "%VENV%\Scripts\activate.bat"
echo Starting Ming-3.0-tts web UI on http://localhost:%MING_PORT%
echo Model: %MING_MODEL_PATH%   Device: %MING_DEVICE%
python -m app.server
endlocal
