@echo off
REM Download the Ming-3.0-tts-0.5b checkpoint into models/Ming-3.0-tts-0.5b
REM Requires the venv from setup.bat (for huggingface_hub).

setlocal
set "ROOT=%~dp0"
set "VENV=%ROOT%venv"
set "MODEL_DIR=%ROOT%models\Ming-3.0-tts-0.5b"

if not exist "%VENV%" (
    echo [ERR] venv not found. Run setup.bat first.
    exit /b 1
)

call "%VENV%\Scripts\activate.bat"

if exist "%MODEL_DIR%\model.safetensors" (
    echo [OK] model already present at %MODEL_DIR%
    goto :done
)

call "%VENV%\Scripts\activate.bat"

echo Downloading inclusionAI/Ming-3.0-tts-0.5b ...
python - <<'PY'
from huggingface_hub import snapshot_download
import os
target = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "Ming-3.0-tts-0.5b")
os.makedirs(target, exist_ok=True)
path = snapshot_download(
    repo_id="inclusionAI/Ming-3.0-tts-0.5b",
    local_dir=target,
)
print("DOWNLOADED TO:", path)
PY

:done
echo.
echo Done. Model saved to: %MODEL_DIR%
echo Start the server with: run.bat
endlocal
