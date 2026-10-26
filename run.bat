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

REM Fail fast with a clear message if the port is already in use.
powershell -NoProfile -Command "if (Get-NetTCPConnection -LocalPort %MING_PORT% -ErrorAction SilentlyContinue) { Write-Host '[ERR] Port %MING_PORT% is already in use. Stop the other server first.'; exit 1 }" || goto :portbusy

python -m app.server
if errorlevel 1 goto :failed
endlocal
exit /b 0

:portbusy
echo.
echo [ERR] Port %MING_PORT% is already occupied by another process.
echo       Close that process (or set MING_PORT to a free port) and try again.
pause
exit /b 1

:failed
echo.
echo [ERR] The server exited with an error (see output above).
pause
exit /b 1
