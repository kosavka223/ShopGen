#!/usr/bin/env bash
set -euo pipefail

echo "==> Install dependencies"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt gunicorn

echo "==> Create wsgi.py"

cat > wsgi.py <<'PY'
from pathlib import Path
from flask import send_from_directory, jsonify
from app import create_app

app = create_app()

FRONTEND_DIR = Path("frontend_override").resolve()

@app.get("/healthz")
def healthz():
    return jsonify({"ok": True})

@app.route("/", defaults={"path": "index.html"})
@app.route("/<path:path>")
def serve_frontend(path):
    file_path = FRONTEND_DIR / path
    if file_path.exists():
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, "index.html")
PY

echo "==> Build done"
