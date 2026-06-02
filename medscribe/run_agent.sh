#!/usr/bin/env bash
# Start the MedScribe desktop agent (tray icon + global hotkey).
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d .venv_agent ]; then
    python3 -m venv .venv_agent
    .venv_agent/bin/pip install --upgrade pip
    .venv_agent/bin/pip install -r requirements_agent.txt
fi

# Linux: needs PortAudio. On Debian/Ubuntu: sudo apt install libportaudio2
# Linux: needs an X server for global hotkeys. On Wayland, run under XWayland
#         or use the X11 session.
exec .venv_agent/bin/python -m medscribe.agent.main "$@"
