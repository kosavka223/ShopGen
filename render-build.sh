#!/usr/bin/env bash
set -euo pipefail

BACKEND_DIR="gen/project/backend"

echo "==> Check backend dir: $BACKEND_DIR"
if [ ! -d "$BACKEND_DIR" ]; then
  echo "ERROR: $BACKEND_DIR not found"
  find . -maxdepth 4 -type f | sort || true
  exit 1
fi

if [ ! -f "$BACKEND_DIR/requirements.txt" ]; then
  echo "ERROR: requirements.txt not found in $BACKEND_DIR"
  exit 1
fi

echo "==> Install dependencies"
python -m pip install --upgrade pip
python -m pip install -r "$BACKEND_DIR/requirements.txt" gunicorn

echo "==> Create wsgi.py"
cat > "$BACKEND_DIR/wsgi.py" <<'PY'
from app import create_app
app = create_app()
PY

echo "==> Build done"
