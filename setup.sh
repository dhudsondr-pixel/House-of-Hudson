#!/usr/bin/env bash
# One-time setup for House of Hudson (Mac / Linux).
# Usage:  bash setup.sh
set -e

cd "$(dirname "$0")"

echo "=== House of Hudson setup ==="

# 1. Check Python.
if ! command -v python3 >/dev/null 2>&1; then
  echo "[!] Python 3 is not installed."
  echo "    macOS: install from https://www.python.org/downloads/ or 'brew install python'"
  echo "    Ubuntu: sudo apt-get install python3 python3-venv python3-pip"
  exit 1
fi
echo "[ok] Python 3 found: $(python3 --version)"

# 2. Check ffmpeg.
if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "[!] ffmpeg is not installed. Installing now..."
  if [[ "$OSTYPE" == "darwin"* ]]; then
    if command -v brew >/dev/null 2>&1; then
      brew install ffmpeg
    else
      echo "    Homebrew not found. Install from https://brew.sh then run: brew install ffmpeg"
      exit 1
    fi
  elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command -v apt-get >/dev/null 2>&1; then
      sudo apt-get update && sudo apt-get install -y ffmpeg
    else
      echo "    Please install ffmpeg manually for your distro."
      exit 1
    fi
  else
    echo "    Please install ffmpeg manually."
    exit 1
  fi
fi
echo "[ok] ffmpeg found"

# 3. Create virtualenv.
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  echo "[ok] Created virtual environment at .venv"
fi

# 4. Install Python deps.
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
echo "[ok] Installed Python dependencies"

# 5. Copy .env if missing.
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo
  echo "[!] Created .env from template."
  echo "    EDIT .env now and paste in your API keys:"
  echo "      - ANTHROPIC_API_KEY   (from https://console.anthropic.com/)"
  echo "      - PEXELS_API_KEY      (free, from https://www.pexels.com/api/)"
  echo
fi

echo
echo "=== Setup complete ==="
echo "Next: open .env, paste your API keys, then run:  bash run.sh"
