$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
Write-Host 'Starting Battle Arena Command Center (read-only local dashboard)...' -ForegroundColor Cyan
Write-Host 'Open http://127.0.0.1:8765 in your browser.' -ForegroundColor Green
Write-Host 'This dashboard does not make Arena API calls or spend credits.' -ForegroundColor Yellow
python .\dashboard_server.py
