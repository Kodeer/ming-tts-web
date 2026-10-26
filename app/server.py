"""Flask web server exposing Ming-3.0-tts to end users.

Endpoints
---------
GET  /                       -> web UI (index.html)
GET  /api/options           -> static option lists for the UI
GET  /api/status            -> model load state + GPU info
POST /api/synthesize        -> run TTS, returns JSON with audio URL
GET  /api/audio/<file>      -> stream a generated WAV
POST /api/upload_prompt     -> upload a reference (voice-clone) WAV
GET  /api/download/<file>   -> force-download a generated WAV
"""

from __future__ import annotations

import os
import re
import secrets
import time
import uuid

from flask import (
    Flask, request, jsonify, send_file, send_from_directory,
    Response, abort,
)
from werkzeug.utils import secure_filename

from app import config
from app.tts_wrapper import TTSWrapper

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
MODELS_DIR = os.path.join(BASE_DIR, "models")

for d in (UPLOAD_DIR, OUTPUT_DIR, MODELS_DIR):
    os.makedirs(d, exist_ok=True)

MODEL_PATH = os.environ.get("MING_MODEL_PATH", os.path.join(MODELS_DIR, "Ming-3.0-tts-0.5b"))
DEVICE = os.environ.get("MING_DEVICE", "cuda:0")
# FST text normalization needs pynini, which has no Windows wheel. Off by
# default; set MING_TEXT_NORMALIZATION=1 to enable if pynini is installed.
TEXT_NORMALIZATION = os.environ.get("MING_TEXT_NORMALIZATION", "0") == "1"

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="")
wrapper = TTSWrapper(MODEL_PATH, device=DEVICE, text_normalization=TEXT_NORMALIZATION)

ALLOWED_AUDIO = {".wav", ".mp3", ".flac", ".ogg", ".m4a"}
SAFE_RE = re.compile(r"[^A-Za-z0-9._-]")


def _safe(name: str) -> str:
    name = secure_filename(name)
    name = SAFE_RE.sub("_", name)
    return name or "file"


def _gpu_info() -> dict:
    info = {"cuda_available": False}
    try:
        import torch
        if torch.cuda.is_available():
            info["cuda_available"] = True
            info["device"] = DEVICE
            info["name"] = torch.cuda.get_device_name(0)
            info["memory_allocated_mb"] = round(torch.cuda.memory_allocated(0) / 1e6, 1)
            info["memory_reserved_mb"] = round(torch.cuda.memory_reserved(0) / 1e6, 1)
    except Exception as e:  # pragma: no cover
        info["error"] = str(e)
    return info


@app.route("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


@app.route("/api/options")
def api_options():
    return jsonify({
        "tasks": config.TASKS,
        "languages": config.LANGUAGES,
        "emotions": config.EMOTIONS,
        "speed": config.SPEED_VALUES,
        "pitch": config.PITCH_VALUES,
        "volume": config.VOLUME_VALUES,
        "dialects": config.DIALECT_VALUES,
        "paralinguistic_tags": config.PARALINGUISTIC_TAGS,
        "builtin_voices": config.BUILTIN_VOICES,
        "defaults": config.DEFAULTS,
    })


@app.route("/api/status")
def api_status():
    return jsonify({
        "loaded": wrapper.is_loaded,
        "model_path": MODEL_PATH,
        "device": DEVICE,
        "sample_rate": wrapper.sample_rate if wrapper.is_loaded else None,
        "gpu": _gpu_info(),
    })


@app.route("/api/upload_prompt", methods=["POST"])
def api_upload_prompt():
    if "file" not in request.files:
        return jsonify({"error": "no file field"}), 400
    f = request.files["file"]
    if not f.filename:
        return jsonify({"error": "empty filename"}), 400
    ext = os.path.splitext(f.filename)[1].lower()
    if ext not in ALLOWED_AUDIO:
        return jsonify({"error": f"unsupported audio type: {ext}"}), 400
    token = secrets.token_hex(8)
    name = f"{token}_{_safe(f.filename)}"
    path = os.path.join(UPLOAD_DIR, name)
    f.save(path)
    return jsonify({"upload_id": name, "path": path, "filename": f.filename})


@app.route("/api/synthesize", methods=["POST"])
def api_synthesize():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "text is required"}), 400

    task = (data.get("task") or "TTS").upper()
    valid_tasks = {t["value"] for t in config.TASKS}
    if task not in valid_tasks:
        return jsonify({"error": f"unknown task: {task}"}), 400

    # Resolve prompt audio: either an uploaded id or a raw uploaded file path.
    prompt_wav_path = data.get("prompt_wav_path") or None
    if not prompt_wav_path and data.get("upload_id"):
        cand = os.path.join(UPLOAD_DIR, data["upload_id"])
        if os.path.exists(cand):
            prompt_wav_path = cand

    # use_spk_emb is meaningless without a reference clip; MingTTS rejects it.
    # Drop it (and fall back to the default voice) when no prompt is present.
    use_spk_emb = bool(data.get("use_spk_emb", False))
    if use_spk_emb and not prompt_wav_path:
        use_spk_emb = False

    params = {
        "task": task,
        "text": text,
        "language_id": data.get("language_id"),
        "instruction": data.get("instruction"),
        "prompt_wav_path": prompt_wav_path,
        "prompt_text": data.get("prompt_text"),
        "use_spk_emb": use_spk_emb,
        "use_zero_spk_emb": data.get("use_zero_spk_emb", False),
        "ip": data.get("ip"),
        "emotion": data.get("emotion"),
        "speed": data.get("speed"),
        "pitch": data.get("pitch"),
        "volume": data.get("volume"),
        "dialect": data.get("dialect"),
        "style": data.get("style"),
        "cfg": data.get("cfg", config.DEFAULTS["cfg"]),
        "sigma": data.get("sigma", config.DEFAULTS["sigma"]),
        "temperature": data.get("temperature", config.DEFAULTS["temperature"]),
        "max_length": data.get("max_length", config.DEFAULTS["max_length"]),
        "max_decode_steps": data.get("max_decode_steps", config.DEFAULTS["max_decode_steps"]),
        "no_trim_silence": data.get("no_trim_silence", False),
        "raw_text": data.get("raw_text", False),
    }

    try:
        import torchaudio
        waveform = wrapper.synthesize(params)
    except Exception as e:  # surface model errors to the UI
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"synthesis failed: {e}"}), 500

    out_name = f"{uuid.uuid4().hex}.wav"
    out_path = os.path.join(OUTPUT_DIR, out_name)
    torchaudio.save(out_path, waveform, sample_rate=wrapper.sample_rate)

    duration = float(waveform.shape[-1]) / wrapper.sample_rate
    return jsonify({
        "audio_url": f"/api/audio/{out_name}",
        "download_url": f"/api/download/{out_name}",
        "filename": out_name,
        "sample_rate": wrapper.sample_rate,
        "duration_seconds": round(duration, 3),
    })


@app.route("/api/audio/<filename>")
def api_audio(filename):
    path = os.path.join(OUTPUT_DIR, _safe(filename))
    if not os.path.exists(path):
        abort(404)
    return send_file(path, mimetype="audio/wav", conditional=True)


@app.route("/api/download/<filename>")
def api_download(filename):
    path = os.path.join(OUTPUT_DIR, _safe(filename))
    if not os.path.exists(path):
        abort(404)
    return send_file(path, mimetype="audio/wav", as_attachment=True,
                     download_name=filename)


if __name__ == "__main__":
    port = int(os.environ.get("MING_PORT", "7860"))
    print(f"[server] Ming-3.0-tts web UI on http://localhost:{port}")
    print(f"[server] model path: {MODEL_PATH}  device: {DEVICE}")
    app.run(host="0.0.0.0", port=port, threaded=True)
