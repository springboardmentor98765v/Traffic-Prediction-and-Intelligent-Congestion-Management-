$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$backendRoot = Join-Path $projectRoot 'team-reference\backend'
$python = Join-Path $backendRoot '.venv\Scripts\python.exe'
$model = Join-Path $projectRoot 'team-reference\aiml\models\source_ml_v2.joblib'
$port = 8001
$healthUrl = "http://127.0.0.1:$port/health"

if (-not (Test-Path $python)) {
    throw "Backend virtual environment not found: $python"
}
if (-not (Test-Path $model)) {
    throw "Active source-trained model not found: $model. Restore the model artifact before starting."
}
$sklearnVersion = & $python -c "import sklearn; print(sklearn.__version__)"
if ($LASTEXITCODE -ne 0 -or $sklearnVersion.Trim() -ne '1.9.1') {
    throw "The active model requires scikit-learn 1.9.1; found '$sklearnVersion'. Install backend requirements before starting."
}

$listener = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($listener) {
    try {
        $health = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 3
        if ($health.service -eq 'TrafficVision AI Engine' -and $health.status -eq 'healthy') {
            Write-Output "TrafficVision backend is already healthy on port $port."
            Write-Output "Health: $($healthUrl) ($($health.traffic_records) records; model $($health.model_version))"
            return
        }
    } catch {
    }

    $process = Get-CimInstance Win32_Process -Filter "ProcessId = $($listener.OwningProcess)"
    $ownedProcess = $process.ExecutablePath -ieq $python -and $process.CommandLine -match 'uvicorn' -and $process.CommandLine -match 'api\.main:app'
    if (-not $ownedProcess) {
        throw "Port $port is occupied by PID $($listener.OwningProcess), which is not a verified TrafficVision backend. No process was stopped."
    }

    Stop-Process -Id $listener.OwningProcess -Force
    for ($attempt = 0; $attempt -lt 20 -and (Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue); $attempt++) {
        Start-Sleep -Milliseconds 250
    }
}

$runtimeDir = Join-Path $projectRoot '.trafficvision'
New-Item -ItemType Directory -Path $runtimeDir -Force | Out-Null
$stdout = Join-Path $runtimeDir 'backend.log'
$stderr = Join-Path $runtimeDir 'backend-error.log'
$process = Start-Process -FilePath $python -ArgumentList @('-m', 'uvicorn', 'api.main:app', '--host', '127.0.0.1', '--port', "$port") -WorkingDirectory $backendRoot -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru -WindowStyle Hidden

$health = $null
for ($attempt = 0; $attempt -lt 60; $attempt++) {
    try {
        $health = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 2
        break
    } catch {
        if ($process.HasExited) {
            throw "Backend exited during startup. See $stderr"
        }
        Start-Sleep -Milliseconds 500
    }
}

if (-not $health -or $health.status -ne 'healthy' -or $health.service -ne 'TrafficVision AI Engine') {
    throw "Backend did not become healthy. See $stdout and $stderr"
}

Write-Output "Backend PID $($process.Id) is healthy."
Write-Output "API: http://127.0.0.1:$port"
Write-Output "Swagger: http://127.0.0.1:$port/docs"
Write-Output "Health: $healthUrl ($($health.traffic_records) records; model $($health.model_version))"