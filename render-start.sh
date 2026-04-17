#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-10000}"
WEB_CONCURRENCY="${WEB_CONCURRENCY:-2}"

echo "==> Starting app"

exec python -m gunicorn \
  --bind "0.0.0.0:${PORT}" \
  --workers "${WEB_CONCURRENCY}" \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  wsgi:app
