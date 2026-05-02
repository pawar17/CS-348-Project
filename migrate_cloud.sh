#!/usr/bin/env bash
# Migrate via Cloud SQL Auth Proxy. Needs DB_PASSWORD; arg: INSTANCE_CONNECTION_NAME
set -euo pipefail

INSTANCE="${1:?Usage: bash migrate_cloud.sh PROJECT_ID:REGION:INSTANCE_NAME}"

if [[ -z "${DB_PASSWORD:-}" ]]; then
  echo "ERROR: DB_PASSWORD is not set."
  echo "  export DB_PASSWORD=\"<your-cloud-sql-password>\""
  exit 1
fi

PROXY_PORT=5433

echo "==> Starting Cloud SQL Auth Proxy on 127.0.0.1:${PROXY_PORT}..."
cloud-sql-proxy --port="${PROXY_PORT}" "${INSTANCE}" &
PROXY_PID=$!

sleep 3

DB_NAME="${DB_NAME:-cs348db}"
DB_USER="${DB_USER:-cs348user}"

echo "==> Applying migrations..."
DB_HOST=127.0.0.1 DB_PORT="${PROXY_PORT}" \
  DB_NAME="${DB_NAME}" DB_USER="${DB_USER}" \
  python manage.py migrate

echo "==> Creating admin superuser (skipped if already exists)..."
DB_HOST=127.0.0.1 DB_PORT="${PROXY_PORT}" \
  DB_NAME="${DB_NAME}" DB_USER="${DB_USER}" \
  python manage.py bootstrap_superuser

echo "==> Seeding demo data..."
DB_HOST=127.0.0.1 DB_PORT="${PROXY_PORT}" \
  DB_NAME="${DB_NAME}" DB_USER="${DB_USER}" \
  python manage.py seed_demo

echo "==> Stopping proxy..."
kill "${PROXY_PID}"

echo ""
echo "==> Done! The database is ready."
