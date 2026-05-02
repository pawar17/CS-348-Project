# Requires: DB_PASSWORD, CLOUD_SQL_CONNECTION_NAME; cloud-sql-proxy.exe optional path.
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$INSTANCE = if ($env:CLOUD_SQL_CONNECTION_NAME) { $env:CLOUD_SQL_CONNECTION_NAME } else { "YOUR_PROJECT_ID:REGION:INSTANCE" }
$PROXY_PORT = if ($env:CLOUD_SQL_PROXY_PORT) { $env:CLOUD_SQL_PROXY_PORT } else { "5433" }
$DB_NAME = if ($env:DB_NAME) { $env:DB_NAME } else { "your_database_name" }
$DB_USER = if ($env:DB_USER) { $env:DB_USER } else { "your_database_user" }

if (-not $env:DB_PASSWORD) {
    Write-Error "DB_PASSWORD is not set. Example:`n  `$env:DB_PASSWORD=`"<your-cloud-sql-password>`""
    exit 1
}

if ($INSTANCE -eq "YOUR_PROJECT_ID:REGION:INSTANCE") {
    Write-Error "Set CLOUD_SQL_CONNECTION_NAME before running. Example:`n  `$env:CLOUD_SQL_CONNECTION_NAME=`"my-project:us-central1:my-instance`""
    exit 1
}

$PYTHON = $null
foreach ($p in @("C:\Python312\python.exe", ".\venv\Scripts\python.exe")) {
    if (Test-Path $p) { $PYTHON = $p; break }
}
if (-not $PYTHON) { $PYTHON = "python" }
Write-Host "==> Using Python: $PYTHON"

$PROXY = $null
foreach ($p in @(".\cloud-sql-proxy.exe", "cloud-sql-proxy")) {
    if (Get-Command $p -ErrorAction SilentlyContinue) { $PROXY = $p; break }
}
if (-not $PROXY) {
    Write-Error "cloud-sql-proxy.exe not found. Download it to the project root from:`n  https://cloud.google.com/sql/docs/postgres/sql-proxy#install"
    exit 1
}

Write-Host "==> Starting Cloud SQL Auth Proxy on 127.0.0.1:$PROXY_PORT ..."
$proxy = Start-Process -FilePath $PROXY `
    -ArgumentList "--port=$PROXY_PORT", $INSTANCE `
    -PassThru -NoNewWindow
Start-Sleep -Seconds 3

$env:DB_HOST     = "127.0.0.1"
$env:DB_PORT     = $PROXY_PORT
$env:DB_NAME     = $DB_NAME
$env:DB_USER     = $DB_USER

try {
    Write-Host "==> Applying migrations..."
    & $PYTHON manage.py migrate
    if ($LASTEXITCODE -ne 0) { throw "migrate failed" }

    Write-Host "==> Creating admin superuser (skipped if exists)..."
    & $PYTHON manage.py bootstrap_superuser
    if ($LASTEXITCODE -ne 0) { throw "bootstrap_superuser failed" }

    Write-Host "==> Seeding demo data..."
    & $PYTHON manage.py seed_demo
    if ($LASTEXITCODE -ne 0) { throw "seed_demo failed" }

    Write-Host ""
    Write-Host "==> Done!  Database is ready."
} finally {
    Write-Host "==> Stopping proxy..."
    Stop-Process -Id $proxy.Id -ErrorAction SilentlyContinue
    Remove-Item Env:\DB_HOST, Env:\DB_PORT, Env:\DB_NAME, Env:\DB_USER, Env:\DB_PASSWORD -ErrorAction SilentlyContinue
}
