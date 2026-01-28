import pandas as pd

df = pd.read_csv("data/processed/unified_claims_v1.csv", low_memory=False)

# Rename target column
if "is_fraud" in df.columns:
    df.rename(columns={"is_fraud": "PotentialFraud"}, inplace=True)

df.to_csv("data/processed/claims_processed.csv", index=False)

print("✅ Fixed: saved data/processed/claims_processed.csv")
