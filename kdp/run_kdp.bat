@echo off
REM Run KDP auto-publisher (Windows).
setlocal
cd /d "%~dp0.."

if not exist ".venv" (
    echo [!] First-time setup hasn't been run yet.
    echo     Run:  setup.bat
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
python kdp\run.py
pause
