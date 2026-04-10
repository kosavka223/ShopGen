#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-10000}"
WEB_CONCURRENCY="${WEB_CONCURRENCY:-2}"

BACKEND_DIR=$(python - <<'PY'
import os

candidates = []
for root, dirs, files in os.walk("appsrc"):
    if "wsgi.py" in files:
        candidates.append(root)

candidates.sort(key=len)
print(candidates[0] if candidates else "")
PY
)

if [ -z "$BACKEND_DIR" ]; then
  echo "ERROR: backend with wsgi.py not found. Build step probably failed."
  find appsrc -maxdepth 5 -type f | sort || true
  exit 1
fi

echo "==> Starting gunicorn from: $BACKEND_DIR"
exec python -m gunicorn \
  --chdir "$BACKEND_DIR" \
  --bind "0.0.0.0:${PORT}" \
  --workers "${WEB_CONCURRENCY}" \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  wsgi:app
