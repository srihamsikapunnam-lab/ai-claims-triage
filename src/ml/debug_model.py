import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from sklearn.metrics import roc_auc_score

def debug_model_performance():
    print("=== MODEL PERFORMANCE DEBUG ===")
    
    # Load your original model
    model_path = Path("../../models/fraud_model_v1.pkl")
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    print(f"Model type: {type(model).__name__}")
    
    # Load unified data
    data_path = Path("../../data/processed/unified_claims_v1.csv")
    df = pd.read_csv(data_path)
    print(f"Unified data shape: {df.shape}")
    
    # Check target distribution
    if 'is_fraud' in df.columns:
        fraud_rate = df['is_fraud'].mean()
        print(f"Fraud rate in unified data: {fraud_rate:.3f}")
        print(f"Fraud distribution:\n{df['is_fraud'].value_counts()}")
    
    # Simple performance check
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if 'is_fraud' in numeric_cols:
        numeric_cols.remove('is_fraud')
    
    features = df[numeric_cols].fillna(0)
    target = df['is_fraud'] if 'is_fraud' in df.columns else None
    
    if target is not None and len(features) > 0:
        try:
            predictions = model.predict_proba(features)[:, 1]
            auc = roc_auc_score(target, predictions)
            print(f"🎯 Current model AUC on unified data: {auc:.4f}")
        except Exception as e:
            print(f"❌ Prediction failed: {e}")
    
    # Check if we're using the right model file
    print(f"\n=== MODEL FILES ===")
    models_dir = Path("../../models")
    for file in models_dir.glob("*.pkl"):
        print(f"  - {file.name}")

if __name__ == "__main__":
    debug_model_performance()