# Start API + Web dev servers
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root

if (Test-Path .\.venv\Scripts\Activate.ps1) {
    .\.venv\Scripts\Activate.ps1
}

Start-Process powershell -ArgumentList "-NoExit", "-File", "$root\scripts\start-api.ps1"
Start-Sleep -Seconds 2
Set-Location "$root\web"
npm run dev
