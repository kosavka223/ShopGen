#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-10000}"
WEB_CONCURRENCY="${WEB_CONCURRENCY:-1}"

echo "==> Starting app"
echo "==> PORT=$PORT"
echo "==> WEB_CONCURRENCY=$WEB_CONCURRENCY"
echo "==> Files in root:"
ls -la

echo "==> Python version:"
python --version

echo "==> Testing import app/create_app before gunicorn"
python - <<'PY'
import traceback

try:
    print("Importing create_app from app.py ...")
    from app import create_app
    print("create_app imported OK")

    app = create_app()
    print("create_app() executed OK")
    print("Flask app object:", app)
except Exception:
    print("=== PYTHON STARTUP ERROR ===")
    traceback.print_exc()
    raise
PY

echo "==> Starting gunicorn"
exec python -m gunicorn \
  --bind "0.0.0.0:${PORT}" \
  --workers "${WEB_CONCURRENCY}" \
  --timeout 120 \
  --log-level debug \
  --access-logfile - \
  --error-logfile - \
  --capture-output \
  --preload \
  wsgi:app
