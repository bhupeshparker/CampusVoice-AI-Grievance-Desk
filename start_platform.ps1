# CampusVoice - Speak. Detect. Resolve.
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host " CampusVoice - AI Campus Incident Intelligence Platform" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

if (-not (Test-Path ".venv")) {
    Write-Host "[*] Creating virtual environment (.venv)..." -ForegroundColor Yellow
    python -m venv .venv
    & .\.venv\Scripts\Activate.ps1
    Write-Host "[*] Installing backend dependencies..." -ForegroundColor Yellow
    pip install -r backend\requirements.txt
} else {
    & .\.venv\Scripts\Activate.ps1
}

Write-Host ""
Write-Host "[*] Launching CampusVoice on http://127.0.0.1:8000 ..." -ForegroundColor Green
Write-Host "[*] Student Portal:  http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "[*] Admin Ops Desk:  http://127.0.0.1:8000/dashboard.html" -ForegroundColor Green
Write-Host ""

Start-Process "http://127.0.0.1:8000"

python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
