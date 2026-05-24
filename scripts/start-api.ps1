# Start FastAPI backend for Resume Builder
Set-Location $PSScriptRoot\..

if (Test-Path .\.venv\Scripts\Activate.ps1) {
    .\.venv\Scripts\Activate.ps1
}

Write-Host "Starting API on http://127.0.0.1:8000"
uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
