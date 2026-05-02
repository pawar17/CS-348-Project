# Needs DJANGO_SECRET_KEY and DB_PASSWORD in the environment before running.
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not $env:DJANGO_SECRET_KEY) {
    Write-Error "DJANGO_SECRET_KEY is not set. Example:`n  `$env:DJANGO_SECRET_KEY=`"a-long-random-string-50-chars-or-more`""
    exit 1
}

if (-not $env:DB_PASSWORD) {
    Write-Error "DB_PASSWORD is not set. Example:`n  `$env:DB_PASSWORD=`"<your-cloud-sql-password>`""
    exit 1
}

$python = ".\venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    $python = "C:\Python312\python.exe"
    if (-not (Test-Path $python)) {
        $python = "python"
    }
}

Write-Host "==> Checking psycopg..."
& $python -c "import psycopg" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "==> Installing psycopg into $python ..."
    & $python -m pip install "psycopg[binary]" --quiet
}

Write-Host "==> Collecting static files..."
& $python manage.py collectstatic --noinput

Write-Host "==> Deploying to App Engine..."
gcloud app deploy app.yaml --set-env-vars="DJANGO_SECRET_KEY=$($env:DJANGO_SECRET_KEY),DB_PASSWORD=$($env:DB_PASSWORD)" --quiet

$project = (gcloud config get-value project 2>$null).Trim()
Write-Host ""
Write-Host "==> Deployed!  https://$project.appspot.com"
Write-Host ""
Write-Host "Next step — run database migrations:"
Write-Host "  .\migrate_cloud.ps1"
