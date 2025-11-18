import sqlite3
from pathlib import Path
import os

# Resolve repo root (parent of scripts directory)
script_path = Path(__file__).resolve()
repo_root = script_path.parent.parent
p = repo_root / 'claims.db'
print('claims.db path:', p)
print('claims.db exists:', p.exists(), 'size:', p.stat().st_size if p.exists() else 'N/A')
if not p.exists():
    raise SystemExit(1)
conn = sqlite3.connect(str(p))
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [r[0] for r in cur.fetchall()]
print('Tables:', tables)
for t in tables:
    try:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        print(t, 'rows:', cur.fetchone()[0])
    except Exception as e:
        print('Error counting rows for', t, e)
conn.close()
