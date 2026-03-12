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

echo "==> Prepare frontend"
if [ -f "frontend_override/index.html" ]; then
  FRONT_INDEX=$(python - <<'PY'
import os
candidates = []
for root, dirs, files in os.walk("appsrc"):
    if root.endswith("frontend") and "index.html" in files:
        candidates.append(os.path.join(root, "index.html"))
candidates.sort(key=len)
print(candidates[0] if candidates else "")
PY
)

  if [ -n "$FRONT_INDEX" ]; then
    cp "frontend_override/index.html" "$FRONT_INDEX"
    echo "==> Frontend overridden: $FRONT_INDEX"
  else
    mkdir -p appsrc/gen/project/frontend
    cp "frontend_override/index.html" appsrc/gen/project/frontend/index.html
    echo "==> Frontend created: appsrc/gen/project/frontend/index.html"
  fi
else
  echo "WARNING: frontend_override/index.html not found"
fi

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
  echo "Open the zip on your PC and make sure backend/requirements.txt exists."
  exit 1
fi

BACKEND_DIR=$(dirname "$REQ")
echo "==> Backend directory: $BACKEND_DIR"

echo "==> Install deps + gunicorn"
python -m pip install --upgrade pip
python -m pip install -r "$REQ" gunicorn

echo "==> Create wsgi.py (entrypoint for gunicorn) + serve frontend on /"
python - <<PY
from pathlib import Path

backend = Path("$BACKEND_DIR").resolve()

frontend_candidates = [
    backend.parent / "frontend",
    backend.parent.parent / "frontend",
    backend.parent.parent.parent / "frontend",
]

frontend = None
for c in frontend_candidates:
    if (c / "index.html").exists():
        frontend = c
        break

if frontend is None:
    frontend = backend

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
