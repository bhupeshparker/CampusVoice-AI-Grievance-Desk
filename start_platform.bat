@echo off
title CampusVoice - Speak. Detect. Resolve.
echo =====================================================================
echo  CampusVoice - AI Campus Incident Intelligence Platform
echo =====================================================================
echo.

cd /d "%~dp0"

if not exist ".venv" (
    echo [*] Creating Python virtual environment (.venv)...
    python -m venv .venv
    if errorlevel 1 (
        echo [!] Error: Python 3.10+ is required. Please install Python.
        pause
        exit /b 1
    )
    echo [*] Installing required packages...
    call .venv\Scripts\activate
    pip install -r backend\requirements.txt
) else (
    call .venv\Scripts\activate
)

echo.
echo [*] Starting CampusVoice Incident Intelligence Platform on http://127.0.0.1:8000 ...
echo [*] Student Voice Concierge:  http://127.0.0.1:8000
echo [*] Admin Command Center:    http://127.0.0.1:8000/dashboard.html
echo.

start http://127.0.0.1:8000

python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
pause
