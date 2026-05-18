#!/usr/bin/env bash
# Run KDP auto-publisher (Mac / Linux).
# Usage:  bash kdp/run_kdp.sh
set -e
cd "$(dirname "$0")/.."

if [ ! -d ".venv" ]; then
  echo "[!] First-time setup hasn't been run yet."
  echo "    Run:  bash setup.sh"
  exit 1
fi

. .venv/bin/activate
python kdp/run.py
