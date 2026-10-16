$ErrorActionPreference = "Stop"

$ProjectRoot = "C:\Users\bathu\Downloads\M4_Traffic_Monitoring_"
$BackupDir = Join-Path $ProjectRoot "backups"
$PgDump = "C:\Program Files\PostgreSQL\18\bin\pg_dump.exe"

New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null

if (-not (Test-Path $PgDump)) {
    throw "pg_dump.exe not found: $PgDump"
}

$env:PGSSLMODE = "require"

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupFile = Join-Path $BackupDir "traffic_monitoring_prod_$Timestamp.dump"
$TempFile = "$BackupFile.tmp"

try {
    & $PgDump `
        -h "dpg-db2fgtmk1f9s73a983cg-a.oregon-postgres.render.com" `
        -p "5432" `
        -U "traffic_user_m4" `
        -d "traffic_monitoring" `
        --format=custom `
        --no-owner `
        --no-privileges `
        --file="$TempFile"

    if ($LASTEXITCODE -ne 0) {
        throw "pg_dump failed with exit code $LASTEXITCODE"
    }

    if (-not (Test-Path $TempFile) -or (Get-Item $TempFile).Length -eq 0) {
        throw "Backup file is missing or empty"
    }

    $PgRestore = "C:\Program Files\PostgreSQL\18\bin\pg_restore.exe"

    & $PgRestore --list $TempFile | Out-Null

    if ($LASTEXITCODE -ne 0) {
        throw "Backup archive validation failed"
    }

    Move-Item -LiteralPath $TempFile -Destination $BackupFile

    Write-Host "BACKUP SUCCESS"
    Write-Host "Backup file: $BackupFile"
    Write-Host "Backup size: $((Get-Item $BackupFile).Length) bytes"
}
catch {
    Write-Host "BACKUP FAILED: $($_.Exception.Message)"
    Remove-Item -LiteralPath $TempFile -Force -ErrorAction SilentlyContinue
    exit 1
}