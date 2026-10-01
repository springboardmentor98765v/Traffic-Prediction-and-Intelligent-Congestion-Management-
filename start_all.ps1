$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot

& (Join-Path $projectRoot 'start_backend.ps1')
& (Join-Path $projectRoot 'start_frontend.ps1')

$health = Invoke-RestMethod -Uri 'http://127.0.0.1:8001/health' -TimeoutSec 5
$page = Invoke-WebRequest -Uri 'http://127.0.0.1:5500/dashboard.html' -TimeoutSec 5 -UseBasicParsing
Write-Output "Backend health: $($health.status) ($($health.traffic_records) traffic records; model $($health.model_version))"
Write-Output "Swagger: http://127.0.0.1:8001/docs"
Write-Output "Frontend: http://127.0.0.1:5500/dashboard.html (HTTP $($page.StatusCode))"