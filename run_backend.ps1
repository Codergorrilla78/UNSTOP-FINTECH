Write-Host "Starting FinShield Backend..." -ForegroundColor Cyan

Set-Location "$PSScriptRoot\backend"

if (!(Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
}

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\.venv\Scripts\Activate.ps1

Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "Starting FastAPI server..." -ForegroundColor Green
Write-Host "API:  http://localhost:8000"
Write-Host "Docs: http://localhost:8000/docs"
Write-Host ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000