#!/usr/bin/env bash
# Needs DJANGO_SECRET_KEY and DB_PASSWORD exported before running.
set -euo pipefail

if [[ -z "${DJANGO_SECRET_KEY:-}" ]]; then
  echo "ERROR: DJANGO_SECRET_KEY is not set."
  echo "  export DJANGO_SECRET_KEY=\"a-long-random-string-50-chars-or-more\""
  exit 1
fi

if [[ -z "${DB_PASSWORD:-}" ]]; then
  echo "ERROR: DB_PASSWORD is not set."
  echo "  export DB_PASSWORD=\"<your-cloud-sql-password>\""
  exit 1
fi

echo "==> Collecting static files..."
PYTHON="./venv/Scripts/python.exe"
if [[ ! -f "$PYTHON" ]]; then
  PYTHON="python"
fi
$PYTHON manage.py collectstatic --noinput

echo "==> Deploying to App Engine..."
gcloud app deploy app.yaml \
  --set-env-vars="DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY},DB_PASSWORD=${DB_PASSWORD}" \
  --quiet

PROJECT=$(gcloud config get-value project 2>/dev/null)
echo ""
echo "==> Deployed!  https://${PROJECT}.appspot.com"
echo ""
echo "Next step — run database migrations:"
echo "  bash migrate_cloud.sh PROJECT_ID:REGION:INSTANCE_NAME"
