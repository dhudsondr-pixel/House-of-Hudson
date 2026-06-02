#!/usr/bin/env bash
# Start the MedScribe FastAPI server on port 8080.
set -euo pipefail
cd "$(dirname "$0")"
# shellcheck disable=SC1091
source .venv/bin/activate

# Make sure Ollama is running in the background.
if ! pgrep -x ollama >/dev/null; then
    echo "Starting ollama serve in the background..."
    nohup ollama serve >/tmp/ollama.log 2>&1 &
    sleep 2
fi

exec uvicorn server.main:app --host 0.0.0.0 --port 8080 --reload
