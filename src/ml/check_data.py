import pandas as pd
import numpy as np
from pathlib import Path

def check_available_data():
    """Check what Kaggle datasets we have available"""
    data_path = Path(__file__).parent.parent.parent / "data" / "raw" / "extracted"
    
    print("🔍 Checking available Kaggle datasets...")
    
    # Find all CSV files
    csv_files = list(data_path.rglob("*.csv"))
    print(f"📁 Found {len(csv_files)} CSV files:")
    
    datasets_info = {}
    
    for csv_file in csv_files:
        try:
            # Quick load to check structure
            df = pd.read_csv(csv_file, nrows=5)  # Just load first 5 rows
            datasets_info[csv_file.name] = {
                'path': csv_file,
                'shape_preview': '?',  # We don't load full data yet
                'columns': df.columns.tolist(),
                'size_mb': csv_file.stat().st_size / (1024 * 1024)
            }
            print(f"   📊 {csv_file.name}")
            print(f"      Columns: {df.columns.tolist()[:5]}...")
            print(f"      Size: {csv_file.stat().st_size / (1024 * 1024):.1f} MB")
            
            # Check for fraud columns
            fraud_cols = [col for col in df.columns if any(word in col.lower() for word in 
                          ['fraud', 'suspect', 'abuse', 'investigation', 'flag'])]
            if fraud_cols:
                print(f"      🎯 FRAUD COLUMNS: {fraud_cols}")
                
        except Exception as e:
            print(f"   ❌ Error reading {csv_file.name}: {e}")
    
    return datasets_info

if __name__ == "__main__":
    datasets = check_available_data()
    
    print(f"\n🎯 Recommendation: Use one of these datasets for LIME:")
    for name, info in list(datasets.items())[:3]:  # Show top 3
        print(f"   - {name} (Fraud cols: {[col for col in info['columns'] if 'fraud' in col.lower()]})")