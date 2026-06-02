#!/usr/bin/env bash
# MedScribe install script. Run once on the dev box.
# Target: Ubuntu / Debian-based Linux with an NVIDIA GPU (5090 ideal).

set -euo pipefail

cd "$(dirname "$0")"

echo "=== 1/5  System packages ==="
if ! command -v ffmpeg >/dev/null; then
    sudo apt-get update
    sudo apt-get install -y ffmpeg python3-venv python3-pip curl
fi

echo "=== 2/5  Python virtualenv ==="
if [ ! -d .venv ]; then
    python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "=== 3/5  Ollama (local LLM runtime) ==="
if ! command -v ollama >/dev/null; then
    curl -fsSL https://ollama.com/install.sh | sh
fi

echo "=== 4/5  Pulling the SOAP-generation model (Qwen 2.5 32B, ~18 GB) ==="
# qwen2.5:32b runs comfortably in 32 GB VRAM at Q4. If you want a smaller
# / faster model for first tests, swap to qwen2.5:14b (~9 GB) here AND in
# server/soap.py.
ollama pull qwen2.5:32b-instruct-q4_K_M

echo "=== 5/5  Done ==="
echo
echo "Start the server with:   ./run.sh"
echo "Then open:               http://localhost:8080"
