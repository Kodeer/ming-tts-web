# Contributing

Thanks for your interest in improving this project. This is a small, personal
project, so the process is intentionally lightweight.

## Getting started

1. Clone the repo **with its submodule**:
   ```bash
   git clone --recurse-submodules https://github.com/Kodeer/ming-tts-web.git
   cd ming-tts-web
   git submodule update --init --recursive
   ```
2. Create the Python environment and install dependencies:
   ```bash
   setup.bat
   download_model.bat   # fetches the ~3 GB Ming-3.0-tts-0.5b weights
   ```
3. Run it locally:
   ```bash
   run.bat
   ```
   The web UI is served at `http://localhost:7860`.

## Guidelines

- Keep `models/`, `venv/`, `outputs/`, and `uploads/` out of version control
  (already covered by `.gitignore`).
- The `Ming-3.0-tts` engine lives in a **submodule** — do not commit its files
  directly into this repo.
- Run the app and confirm synthesis still works on GPU before opening a PR.
- Open an issue or a pull request describing the change. Since this repo is
  private, please coordinate with the owner (`Kodeer`) before large changes.

## Reporting issues

Include: OS, Python version, GPU/driver, the exact text or audio sample used,
and the server log output.
