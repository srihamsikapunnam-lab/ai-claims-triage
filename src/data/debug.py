import pandas as pd
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from data.data_loader import DataLoader
from data.data_unifier import DataUnifier

def run_diagnostic():
    print("=== DATA DIAGNOSTIC ===")
    
    # Load data
    loader = DataLoader()
    datasets = loader.load_kaggle_datasets()
    
    print(f"\nLoaded {len(datasets)} datasets")
    
    for name, df in datasets.items():
        print(f"\n--- {name} ---")
        print(f"Shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        
        # Check for amount columns
        amount_cols = [col for col in df.columns if 'amount' in col.lower() or 'billed' in col.lower()]
        if amount_cols:
            print(f"Amount columns: {amount_cols}")
            for amt_col in amount_cols:
                sample_values = df[amt_col].head(3).tolist()
                print(f"  {amt_col} sample: {sample_values} (dtype: {df[amt_col].dtype})")
        
        # Check for fraud columns
        fraud_cols = [col for col in df.columns if 'fraud' in col.lower()]
        if fraud_cols:
            print(f"Fraud columns: {fraud_cols}")
            for fraud_col in fraud_cols:
                unique_vals = df[fraud_col].unique()[:5]
                print(f"  {fraud_col} unique: {unique_vals}")

if __name__ == "__main__":
    run_diagnostic()