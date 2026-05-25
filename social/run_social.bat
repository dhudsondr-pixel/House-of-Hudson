@echo off
setlocal
cd /d "%~dp0.."
if not exist ".venv" (
    echo [!] First-time setup hasn't been run yet. Run:  setup.bat
    pause
    exit /b 1
)
call .venv\Scripts\activate.bat
python social\run.py
pause
