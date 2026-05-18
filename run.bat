@echo off
REM Run the video generator (Windows).
setlocal
cd /d "%~dp0"

if not exist ".venv" (
    echo [!] First-time setup hasn't been run yet.
    echo     Run:  setup.bat
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
python run.py
pause
