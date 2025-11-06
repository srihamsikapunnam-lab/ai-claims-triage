import sqlite3

def init_database():
    # Connect to SQLite database (creates if not exists)
    conn = sqlite3.connect('claims.db')
    cursor = conn.cursor()
    
    # Create claims_raw table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS claims_raw (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            claim_id TEXT UNIQUE,
            patient_age INTEGER,
            diagnosis TEXT,
            admission_date TEXT,
            discharge_date TEXT,
            claimed_amount REAL,
            raw_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create claims_results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS claims_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            claim_id TEXT UNIQUE,
            prediction TEXT,
            probability REAL,
            risk_score REAL,
            risk_category TEXT,
            explanation TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (claim_id) REFERENCES claims_raw (claim_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_database()