# Stop anything on port 8000 and start the API with latest code
$conn = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($conn) {
    $conn | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
    Start-Sleep -Seconds 2
}
Set-Location $PSScriptRoot\..
Write-Host "Starting API from $(Get-Location)"
Write-Host "Check http://127.0.0.1:8000/api/health — must show resume_parser v4-explicit-build"
.\.venv\Scripts\python.exe -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
