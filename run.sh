#!/usr/bin/env bash
# Mac / Linux one-click launcher. Double-click in Finder/Files, or run from terminal.
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 is not installed."
    echo
    echo "On macOS: open Terminal and run:  brew install python"
    echo "          (Or download from https://www.python.org/downloads/)"
    echo "On Linux: run:  sudo apt install python3 python3-pip"
    exit 1
fi

python3 "$DIR/run.py" "$@"
