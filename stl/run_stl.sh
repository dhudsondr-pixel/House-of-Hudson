#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
if [ ! -d ".venv" ]; then
  echo "[!] Setup hasn't been run yet. Run:  bash setup.sh"
  exit 1
fi
. .venv/bin/activate
python stl/run.py
