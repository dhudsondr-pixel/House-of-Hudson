@echo off
setlocal
cd /d "%~dp0.."
if not exist ".venv" (
    echo [!] Setup hasn't been run yet. Run:  setup.bat
    pause
    exit /b 1
)
call .venv\Scripts\activate.bat
python stl\run.py
pause
