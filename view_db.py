import sqlite3
from pathlib import Path

DB = Path(__file__).parent / "instance" / "generations.db"

if not DB.exists():
    raise SystemExit(f"DB not found: {DB}")

conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
print("Tables:", [r[0] for r in cur.fetchall()])

cur.execute("SELECT COUNT(*) FROM generation_history;")
print("Rows:", cur.fetchone()[0])

cur.execute(
    "SELECT id, category, created_at, substr(generated_text,1,80) FROM generation_history ORDER BY id DESC LIMIT 5;"
)
print("\nLast 5:")
for r in cur.fetchall():
    print(r[0], r[1], r[2], r[3] + ("…" if len(r[3]) == 80 else ""))

conn.close()
