#!/usr/bin/env bash
# Run the video generator (Mac / Linux).
# Usage:  bash run.sh
set -e
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  echo "[!] First-time setup hasn't been run yet."
  echo "    Run:  bash setup.sh"
  exit 1
fi

. .venv/bin/activate
python run.py
