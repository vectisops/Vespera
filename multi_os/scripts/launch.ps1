# Vespera multi-OS launcher for Windows (PowerShell)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Test-Path ".venv")) {
    Write-Host "Creating venv…"
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
} else {
    .\.venv\Scripts\Activate.ps1
}

Write-Host "Launching Vespera Control Center (http://127.0.0.1:7860)…"
python -m vespera.ui
