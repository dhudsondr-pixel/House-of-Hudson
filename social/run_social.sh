#!/usr/bin/env bash
# Run social content factory (Mac / Linux).
set -e
cd "$(dirname "$0")/.."
if [ ! -d ".venv" ]; then
  echo "[!] First-time setup hasn't been run yet. Run:  bash setup.sh"
  exit 1
fi
. .venv/bin/activate
python social/run.py
