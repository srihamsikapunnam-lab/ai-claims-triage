import sqlite3
from pathlib import Path
p = Path(__file__).resolve().parent.parent / 'claims.db'
print('DB:', p)
conn = sqlite3.connect(str(p))
cur = conn.cursor()
cur.execute('SELECT id, user_id, claimed_amount, created_at FROM claims')
rows = cur.fetchall()
for r in rows:
    print(r)
conn.close()
