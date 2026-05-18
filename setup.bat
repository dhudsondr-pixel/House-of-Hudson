@echo off
REM One-time setup for House of Hudson (Windows).
REM Usage:  double-click this file, OR run from terminal: setup.bat
setlocal

cd /d "%~dp0"

echo === House of Hudson setup ===

where python >nul 2>nul
if errorlevel 1 (
    echo [!] Python is not installed. Install from https://www.python.org/downloads/
    echo     IMPORTANT: check "Add Python to PATH" during install.
    pause
    exit /b 1
)
echo [ok] Python found

where ffmpeg >nul 2>nul
if errorlevel 1 (
    echo [!] ffmpeg is not installed.
    echo     Easiest install: open PowerShell as admin and run:  winget install ffmpeg
    echo     Or download from: https://www.gyan.dev/ffmpeg/builds/
    pause
    exit /b 1
)
echo [ok] ffmpeg found

if not exist ".venv" (
    python -m venv .venv
    echo [ok] Created virtual environment
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
echo [ok] Installed Python dependencies

if not exist ".env" (
    copy /Y .env.example .env >nul
    echo.
    echo [!] Created .env from template.
    echo     EDIT .env now and paste in your API keys:
    echo       - ANTHROPIC_API_KEY   (from https://console.anthropic.com/)
    echo       - PEXELS_API_KEY      (free, from https://www.pexels.com/api/)
    echo.
)

echo.
echo === Setup complete ===
echo Next: open .env in Notepad, paste your API keys, then run:  run.bat
pause
