import sqlite3
import json
from typing import Dict, Any

def init_database():
    conn = sqlite3.connect('claims.db')
    cursor = conn.cursor()
    
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

def save_claim_to_db(claim_data: Dict[str, Any], prediction_result: Dict[str, Any]):
    conn = sqlite3.connect('claims.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO claims_raw 
            (claim_id, patient_age, diagnosis, admission_date, discharge_date, claimed_amount, raw_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            claim_data.get('claim_id'),
            claim_data.get('patient_age'),
            claim_data.get('diagnosis'),
            claim_data.get('admission_date'),
            claim_data.get('discharge_date'),
            claim_data.get('claimed_amount'),
            json.dumps(claim_data)
        ))
        
        cursor.execute('''
            INSERT OR REPLACE INTO claims_results 
            (claim_id, prediction, probability, risk_score, risk_category, explanation, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            prediction_result.get('claim_id'),
            prediction_result.get('prediction'),
            prediction_result.get('probability'),
            prediction_result.get('risk_score'),
            prediction_result.get('risk_category'),
            json.dumps(prediction_result.get('explanation', [])),
            prediction_result.get('status')
        ))
        
        conn.commit()
        print(f"Claim {claim_data.get('claim_id')} saved to database")
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()