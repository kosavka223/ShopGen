#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-10000}"
WEB_CONCURRENCY="${WEB_CONCURRENCY:-2}"
BACKEND_DIR="gen/project/backend"

echo "==> Starting gunicorn from: $BACKEND_DIR"

exec python -m gunicorn \
  --chdir "$BACKEND_DIR" \
  --bind "0.0.0.0:${PORT}" \
  --workers "${WEB_CONCURRENCY}" \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  wsgi:app
