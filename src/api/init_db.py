import sqlite3
conn = sqlite3.connect("claims.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS claims_raw (
    claim_id TEXT PRIMARY KEY,
    raw_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
c.execute("""
CREATE TABLE IF NOT EXISTS claims_results (
    claim_id TEXT PRIMARY KEY,
    prediction TEXT,
    probability REAL,
    risk_score REAL,
    explanation TEXT,
    status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()
conn.close()
print("DB initialized successfully!")
