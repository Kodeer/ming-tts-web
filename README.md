# Ming-3.0-tts Web UI

A self-hosted web application that wraps the open-source
[Ming-3.0-tts](https://github.com/inclusionAI/Ming-3.0-tts) TTS model family
and exposes every synthesis feature through a browser interface. Inference runs
on your **local NVIDIA GPU** (CUDA).

The project uses the **0.5b dense** variant — it fits comfortably on a single
consumer GPU (e.g. RTX 4060 8 GB) and supports the full task set: zero-shot
voice cloning, multilingual, emotion/dialect/attribute control, free-form
instructions, voice design, and built-in premium voices.

## Features

- **Text input** — type text or upload a `.txt`/`.md` file.
- **All TTS tasks** — TTS, Multilingual, Basic (speed/pitch/volume), Emotion,
  Dialect (Cantonese / Sichuan), Free-form, Voice Design, Built-in voice (IP).
- **Voice cloning** — upload a reference audio clip + its transcript and enable
  speaker embedding to clone that voice.
- **Full control surface** — language, emotion, speed/pitch/volume, dialect,
  voice-design style, free-form instruction, built-in voice, inline
  paralinguistic tags (`[Laughter]`, `[Sigh]`, …), and advanced knobs
  (cfg / sigma / temperature / max_length).
- **Audio output** — stream the result in the browser and **download** it as a
  WAV file.
- **GPU** — the model is loaded once onto `cuda:0` with bfloat16; `flash-attn`
  is optional (falls back to PyTorch SDPA, which works on Windows).

## Project layout

```
Ming-3.0-tts/        # cloned upstream repo (ming_tts.py, modeling_*, frontend/, …)
app/
  config.py          # option lists / vocabulary for tasks & controls
  tts_wrapper.py     # loads MingTTS on GPU, maps request -> synthesize()
  server.py          # Flask REST API + static file serving
static/
  index.html         # web UI
  style.css
  app.js
models/              # downloaded checkpoint (Ming-3.0-tts-0.5b)
uploads/             # user-uploaded reference clips
outputs/             # generated WAV files
requirements.txt
setup.bat            # create venv + install deps
download_model.bat   # fetch the 0.5b checkpoint
run.bat              # launch the web server
```

## Setup (Windows)

1. **Install Python 3.10** (the repo pins `torch==2.6.0`, which has no wheels
   for 3.13). The Windows Store / python.org 3.10 build works.
2. **Create the environment and install dependencies:**
   ```
   setup.bat
   ```
3. **Download the model** (≈ a few GB):
   ```
   download_model.bat
   ```
   In mainland China, `modelscope download` is usually faster — see the upstream
   README.
4. **Start the server:**
   ```
   run.bat
   ```
5. Open <http://localhost:7860> in your browser.

### Environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `MING_MODEL_PATH` | `models/Ming-3.0-tts-0.5b` | Checkpoint directory or Hub repo id |
| `MING_DEVICE` | `cuda:0` | Torch device for the model |
| `MING_PORT` | `7860` | Web server port |

## Using the web UI

1. **Text** — type or load the text to speak.
2. **Task & language** — pick a task; for Multilingual, choose the target
   language (required).
3. **Dynamic controls** — the panel shows the controls valid for the chosen
   task (emotion, speed/pitch/volume, dialect, style, instruction, or built-in
   voice).
4. **Voice cloning** — upload a short reference clip, enter its exact
   transcript, and keep *"Use speaker embedding"* checked. This is required for
   TTS / Multilingual / Emotion / Dialect / Basic.
5. **Paralinguistic tags** — click any tag to insert it inline into the text
   (e.g. `[Laughter]`).
6. **Speak** — generates audio, plays it, and enables **Download WAV**.

### Quick presets

The right panel has one-click presets: *Zero-shot clone*, *Voice design*,
*Free-form*, *Built-in voice*, *Emotion*, *Multilingual*.

## REST API

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/options` | Static option lists for the UI |
| `GET` | `/api/status` | Model load state + GPU info |
| `POST` | `/api/upload_prompt` | Upload a reference (voice-clone) audio file |
| `POST` | `/api/synthesize` | Run TTS; returns JSON with audio URL |
| `GET` | `/api/audio/<file>` | Stream a generated WAV |
| `GET` | `/api/download/<file>` | Force-download a generated WAV |

### Example `curl` request

```bash
curl -X POST http://localhost:7860/api/synthesize \
  -H "Content-Type: application/json" \
  -d '{"task":"TTS","text":"Hello from Ming TTS.","language_id":"en",
       "prompt_text":"reference transcript here","use_spk_emb":true,
       "upload_id":"<id from /api/upload_prompt>"}'
```

## Notes & limitations

- The 0.5b model is used because the `tiny` MoE variant (7.9B) needs far more
  VRAM and a separate dependency stack (`requirements-tiny.txt`). To switch,
  download `inclusionAI/Ming-3.0-tts-tiny` and adapt `app/tts_wrapper.py` to use
  `ming_tiny.MingTinyTTS`.
- Text normalization (`pynini`) is optional; the app works without it.
- Voice cloning and built-in voices are for research/creative use only — label
  synthetic speech as synthetic and do not impersonate real people without
  consent (see the upstream usage disclaimer).

## License

Code here is provided under the MIT license, matching the upstream
Ming-3.0-tts project.
