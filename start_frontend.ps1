$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$backendRoot = Join-Path $projectRoot 'team-reference\backend'
$python = Join-Path $backendRoot '.venv\Scripts\python.exe'
$frontendRoot = Join-Path $projectRoot 'frontend'
$port = 5500
$pageUrl = "http://127.0.0.1:$port/dashboard.html"

if (-not (Test-Path $python)) {
    throw "Backend virtual environment not found: $python"
}
if (-not (Test-Path (Join-Path $frontendRoot 'dashboard.html'))) {
    throw "Frontend dashboard not found under $frontendRoot"
}

$listener = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($listener) {
    $process = Get-CimInstance Win32_Process -Filter "ProcessId = $($listener.OwningProcess)"
    $ownedProcess = $process.CommandLine -match 'http\.server\s+5500' -and $process.CommandLine -like "*$frontendRoot*"
    if (-not $ownedProcess) {
        throw "Port $port is occupied by PID $($listener.OwningProcess), which is not the TrafficVision frontend server. No process was stopped."
    }
    try {
        $page = Invoke-WebRequest -Uri $pageUrl -TimeoutSec 3 -UseBasicParsing
        if ($page.StatusCode -eq 200) {
            Write-Output "TrafficVision frontend is already running: $pageUrl"
            return
        }
    } catch {
        throw "TrafficVision frontend process owns port $port but did not serve the dashboard. Inspect PID $($listener.OwningProcess); it was not stopped."
    }
}

$runtimeDir = Join-Path $projectRoot '.trafficvision'
New-Item -ItemType Directory -Path $runtimeDir -Force | Out-Null
$stdout = Join-Path $runtimeDir 'frontend.log'
$stderr = Join-Path $runtimeDir 'frontend-error.log'
$quotedFrontend = '"' + $frontendRoot + '"'
$process = Start-Process -FilePath $python -ArgumentList @('-m', 'http.server', "$port", '--bind', '127.0.0.1', '--directory', $quotedFrontend) -WorkingDirectory $projectRoot -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru -WindowStyle Hidden

$page = $null
for ($attempt = 0; $attempt -lt 40; $attempt++) {
    try {
        $page = Invoke-WebRequest -Uri $pageUrl -TimeoutSec 2 -UseBasicParsing
        break
    } catch {
        if ($process.HasExited) {
            throw "Frontend server exited during startup. See $stderr"
        }
        Start-Sleep -Milliseconds 250
    }
}

if (-not $page -or $page.StatusCode -ne 200) {
    throw "Frontend did not become available. See $stdout and $stderr"
}

Write-Output "Frontend PID $($process.Id) is serving $frontendRoot."
Write-Output "Frontend: $pageUrl"