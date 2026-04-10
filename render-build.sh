#!/usr/bin/env bash
set -euo pipefail

ZIP_NAME="${ZIP_NAME:-gen.zip}"
APP_ROOT="appsrc"

echo "==> Extract $ZIP_NAME to ./$APP_ROOT"
rm -rf "$APP_ROOT"
mkdir -p "$APP_ROOT"

python - <<PY
import os
import zipfile

zip_name = r"$ZIP_NAME"
if not os.path.exists(zip_name):
    raise SystemExit(f"ERROR: {zip_name} not found in repo root")

with zipfile.ZipFile(zip_name) as zf:
    zf.extractall(r"$APP_ROOT")
    print("Extracted:", len(zf.namelist()), "files")
PY

echo "==> Find backend requirements.txt"
REQ=$(python - <<'PY'
import os

candidates = []
for root, dirs, files in os.walk("appsrc"):
    if "requirements.txt" in files:
        path = os.path.join(root, "requirements.txt")
        score = (
            0 if "backend" in root.lower() else 1,
            len(path),
            path,
        )
        candidates.append((score, path))

candidates.sort()
print(candidates[0][1] if candidates else "")
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
echo "==> Project directory: $PROJECT_DIR"
echo "==> Frontend directory: $FRONTEND_DIR"

mkdir -p "$FRONTEND_DIR"

echo "==> Prepare frontend"
if [ -f "$FRONTEND_DIR/index.html" ]; then
  echo "==> Using frontend from zip: $FRONTEND_DIR/index.html"
elif [ -f "frontend_override/index.html" ]; then
  cp "frontend_override/index.html" "$FRONTEND_DIR/index.html"
  echo "==> Copied frontend_override/index.html -> $FRONTEND_DIR/index.html"
else
  echo "==> No frontend found, generating fallback index.html"
  cat > "$FRONTEND_DIR/index.html" <<'HTML'
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Render deploy OK</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 760px; margin: 40px auto; padding: 0 16px; }
    pre { background: #f6f8fa; padding: 12px; border-radius: 8px; overflow: auto; }
    button { padding: 10px 16px; border: 0; border-radius: 8px; cursor: pointer; }
  </style>
</head>
<body>
  <h1>Backend is running</h1>
  <p>Это fallback-страница, потому что frontend не был найден в zip и не был передан через frontend_override.</p>

  <button id="pingBtn">Check /ping</button>
  <pre id="out">Нажми кнопку</pre>

  <script>
    document.getElementById("pingBtn").addEventListener("click", async () => {
      const out = document.getElementById("out");
      out.textContent = "Loading...";
      try {
        const res = await fetch("/ping");
        const data = await res.json();
        out.textContent = JSON.stringify(data, null, 2);
      } catch (e) {
        out.textContent = "Request failed: " + e.message;
      }
    });
  </script>
</body>
</html>
HTML
fi

echo "==> Install dependencies"
python -m pip install --upgrade pip
python -m pip install -r "$REQ" gunicorn

echo "==> Create wsgi.py"
python - <<PY
from pathlib import Path

backend = Path(r"$BACKEND_DIR").resolve()
frontend = Path(r"$FRONTEND_DIR").resolve()
wsgi = backend / "wsgi.py"

wsgi.write_text(f'''from pathlib import Path
from flask import send_from_directory, jsonify

try:
    from app import create_app
    app = create_app()
except Exception as e:
    raise RuntimeError(f"Cannot import Flask app: {{e}}")

FRONTEND_DIR = Path(r"{frontend}").resolve()

@app.get("/healthz")
def healthz():
    return jsonify({{"ok": True}})

@app.route("/", defaults={{"path": "index.html"}})
@app.route("/<path:path>")
def serve_frontend(path):
    file_path = FRONTEND_DIR / path
    if file_path.exists() and file_path.is_file():
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, "index.html")
''')

print("Created", wsgi)
print("Frontend dir:", frontend)
PY

echo "==> Build done"
