@echo off
REM Start the MedScribe desktop agent on Windows.
REM Beta GPs run this on their consult-room workstation.

cd /d "%~dp0"

if not exist .venv_agent (
    python -m venv .venv_agent
    .venv_agent\Scripts\pip install --upgrade pip
    .venv_agent\Scripts\pip install -r requirements_agent.txt
)

.venv_agent\Scripts\python -m medscribe.agent.main %*
