@echo off
REM Windows one-click launcher. Double-click this file.
where python >nul 2>nul
if errorlevel 1 (
    echo Python is not installed.
    echo.
    echo 1. Go to https://www.python.org/downloads/
    echo 2. Click "Download Python".
    echo 3. Run the installer. IMPORTANT: check the box that says
    echo    "Add Python to PATH" before clicking Install.
    echo 4. Re-run this file after Python finishes installing.
    echo.
    pause
    exit /b 1
)
python "%~dp0run.py" %*
pause
