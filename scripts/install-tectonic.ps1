# Downloads Tectonic into tools/tectonic/ for local LaTeX compile (Windows x64).
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$DestDir = Join-Path $Root "tools\tectonic"
$Version = "0.16.9"
$ZipName = "tectonic-$Version-x86_64-pc-windows-msvc.zip"
$Url = "https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%40$Version/$ZipName"
$ZipPath = Join-Path $env:TEMP $ZipName

Write-Host "Installing Tectonic $Version to $DestDir ..."
New-Item -ItemType Directory -Force -Path $DestDir | Out-Null

Invoke-WebRequest -Uri $Url -OutFile $ZipPath -UseBasicParsing
Expand-Archive -Path $ZipPath -DestinationPath $DestDir -Force
Remove-Item $ZipPath -Force

$Exe = Join-Path $DestDir "tectonic.exe"
if (-not (Test-Path $Exe)) {
    throw "tectonic.exe not found after extract"
}

& $Exe --version
Write-Host "OK: $Exe"
Write-Host "Restart the API. Optional .env: TECTONIC_PATH=$Exe"
