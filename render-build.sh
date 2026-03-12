#!/usr/bin/env bash
set -euo pipefail

ZIP_NAME="gen.zip"

echo "==> Extract $ZIP_NAME to ./appsrc"
rm -rf appsrc
mkdir -p appsrc

python - <<PY
import zipfile
zf = zipfile.ZipFile("$ZIP_NAME")
zf.extractall("appsrc")
print("Extracted:", len(zf.namelist()), "files")
PY

echo "==> Find requirements.txt inside zip"
REQ=$(python - <<'PY'
import os
candidates = []
for root, dirs, files in os.walk("appsrc"):
    if "requirements.txt" in files:
        candidates.append(os.path.join(root, "requirements.txt"))
candidates.sort(key=len)
print(candidates[0] if candidates else "")
PY
)

if [ -z "$REQ" ]; then
  echo "ERROR: requirements.txt not found inside zip"
  exit 1
fi

BACKEND_DIR=$(dirname "$REQ")
PROJECT_DIR=$(dirname "$BACKEND_DIR")
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo "==> Backend directory: $BACKEND_DIR"
echo "==> Frontend directory: $FRONTEND_DIR"

echo "==> Prepare frontend"
mkdir -p "$FRONTEND_DIR"

if [ -f "frontend_override/index.html" ]; then
  cp "frontend_override/index.html" "$FRONTEND_DIR/index.html"
  echo "==> Frontend ready: $FRONTEND_DIR/index.html"
else
  echo "WARNING: frontend_override/index.html not found"
fi

echo "==> Install deps + gunicorn"
python -m pip install --upgrade pip
python -m pip install -r "$REQ" gunicorn

echo "==> Create wsgi.py"
python - <<PY
from pathlib import Path

backend = Path(r"$BACKEND_DIR").resolve()
frontend = Path(r"$FRONTEND_DIR").resolve()
wsgi = backend / "wsgi.py"

wsgi.write_text(f'''
from pathlib import Path
from flask import send_from_directory

try:
    from app import create_app
    app = create_app()
except Exception:
    from app import app

FRONTEND_DIR = Path(r"{frontend}").resolve()

@app.get("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")
''')

print("Created", wsgi)
print("Frontend dir:", frontend)
PY

echo "==> Build done"
