# recovery.py
import pandas as pd
import numpy as np
import joblib
import os

print("🔄 Starting efficient recovery...")

# Load data efficiently with dtype specification
dtypes = {
    'claim_id': 'str',
    'patient_age': 'int64',
    'gender': 'category',
    'hospital_id': 'int64', 
    'admission_date': 'str',
    'discharge_date': 'str',
    'diagnosis_code': 'str',
    'claimed_amount': 'float64',
    'billed_items_count': 'int64',
    'previous_claims_count': 'int64',
    'insurer_id': 'int64',
    'doc_missing_flag': 'int64',
    'is_fraud': 'int64'
}

# Load in chunks to avoid memory issues
chunk_size = 100000
chunks = []
for chunk in pd.read_csv('../data/processed/unified_clairns_v1.csv', dtype=dtypes, chunksize=chunk_size):
    chunks.append(chunk)

df = pd.concat(chunks, ignore_index=True)
print(f"✅ Data loaded: {df.shape}")

# Save checkpoint
joblib.dump(df, 'checkpoint_data.pkl')
print("💾 Checkpoint 1 saved: checkpoint_data.pkl")