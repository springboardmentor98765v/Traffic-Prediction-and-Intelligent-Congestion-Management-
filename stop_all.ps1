$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$backendRoot = Join-Path $projectRoot 'team-reference\backend'
$frontendRoot = Join-Path $projectRoot 'frontend'

function Stop-TrafficVisionListener([int]$Port, [string]$ExpectedPattern, [string]$ExpectedPath) {
    $listeners = @(Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
    foreach ($listener in $listeners) {
        $process = Get-CimInstance Win32_Process -Filter "ProcessId = $($listener.OwningProcess)"
        $verified = $process.CommandLine -match $ExpectedPattern
        if ($ExpectedPath) {
            $verified = $verified -and $process.CommandLine -like "*$ExpectedPath*"
        }
        if ($Port -eq 8001 -and $verified) {
            try {
                $health = Invoke-RestMethod -Uri 'http://127.0.0.1:8001/health' -TimeoutSec 3
                $verified = $health.service -eq 'TrafficVision AI Engine' -and $health.status -eq 'healthy' -and $health.model_version -eq 'ml-v2'
            } catch {
                $verified = $false
            }
        }
        if (-not $verified) {
            Write-Warning "Leaving PID $($listener.OwningProcess) on port $Port untouched; it does not match this project's $ExpectedPattern process."
            continue
        }
        Stop-Process -Id $listener.OwningProcess -Force
        Write-Output "Stopped verified TrafficVision process PID $($listener.OwningProcess) on port $Port."
    }
}

Stop-TrafficVisionListener -Port 5500 -ExpectedPattern 'http\.server\s+5500' -ExpectedPath $frontendRoot
Stop-TrafficVisionListener -Port 8001 -ExpectedPattern 'uvicorn.*api\.main:app.*--port\s+8001' -ExpectedPath $null