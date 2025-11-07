import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import LabelEncoder

def fix_feature_mismatch():
    print("=== FIXING FEATURE MISMATCH ===")
    
    # Load unified data
    data_path = Path("../../data/processed/unified_claims_v1.csv")
    df = pd.read_csv(data_path, low_memory=False)
    print(f"Unified data shape: {df.shape}")
    
    # Check current columns and dtypes
    print("Current columns and dtypes:")
    for col in df.columns:
        print(f"  - {col}: {df[col].dtype}")
    
    # Load model to see expected features
    model_path = Path("../../models/fraud_model_v1.pkl")
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    print(f"Model type: {type(model).__name__}")
    
    # Get expected features from model (if available)
    if hasattr(model, 'feature_names_in_'):
        expected_features = model.feature_names_in_.tolist()
        print(f"Model expects: {expected_features}")
    else:
        # Manual list based on error message
        expected_features = [
            'patient_age', 'gender', 'hospital_id', 'diagnosis_code', 
            'claimed_amount', 'billed_items_count', 'previous_claims_count', 
            'insurer_id', 'doc_missing_flag', 'length_of_stay', 
            'claimed_per_day', 'amount_per_item'
        ]
        print(f"Model expects (manual): {expected_features}")
    
    # Check which features are missing
    missing_features = [f for f in expected_features if f not in df.columns]
    print(f"Missing features: {missing_features}")
    
    # FIX: Convert string columns to numeric first
    numeric_columns = ['claimed_amount', 'billed_items_count', 'previous_claims_count']
    for col in numeric_columns:
        if col in df.columns:
            # Handle string formatting (commas, spaces, currency symbols)
            if df[col].dtype == 'object':
                print(f"Converting {col} from string to numeric...")
                df[col] = df[col].astype(str).str.replace(',', '').str.replace(' ', '').str.replace('$', '')
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Convert other numeric columns
    if 'patient_age' in df.columns and df['patient_age'].dtype == 'object':
        df['patient_age'] = pd.to_numeric(df['patient_age'], errors='coerce').fillna(0)
    
    # FIX: Convert categorical columns to numeric
    categorical_columns = ['gender', 'diagnosis_code', 'hospital_id', 'insurer_id']
    label_encoders = {}
    
    for col in categorical_columns:
        if col in df.columns and df[col].dtype == 'object':
            print(f"Encoding categorical column: {col}")
            # Fill NaN values first
            df[col] = df[col].fillna('unknown')
            # Use LabelEncoder to convert to numeric
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            label_encoders[col] = le
            print(f"  - Unique values encoded: {len(le.classes_)}")
    
    # Create missing features with proper numeric handling
    for feature in missing_features:
        if feature == 'length_of_stay':
            # Calculate from dates if available
            if 'admission_date' in df.columns and 'discharge_date' in df.columns:
                print("Calculating length_of_stay from dates...")
                df['admission_date'] = pd.to_datetime(df['admission_date'], errors='coerce')
                df['discharge_date'] = pd.to_datetime(df['discharge_date'], errors='coerce')
                df['length_of_stay'] = (df['discharge_date'] - df['admission_date']).dt.days.fillna(1)
                # Clip negative values
                df['length_of_stay'] = df['length_of_stay'].clip(lower=1)
            else:
                df['length_of_stay'] = 1  # Default 1 day stay
                
        elif feature == 'claimed_per_day':
            # Ensure numeric types
            claimed_amt = pd.to_numeric(df.get('claimed_amount', 1000), errors='coerce').fillna(1000)
            stay_days = pd.to_numeric(df.get('length_of_stay', 1), errors='coerce').fillna(1)
            df['claimed_per_day'] = claimed_amt / stay_days
            
        elif feature == 'amount_per_item':
            # Ensure numeric types
            claimed_amt = pd.to_numeric(df.get('claimed_amount', 1000), errors='coerce').fillna(1000)
            items_count = pd.to_numeric(df.get('billed_items_count', 1), errors='coerce').fillna(1)
            df['amount_per_item'] = claimed_amt / items_count
            
        else:
            df[feature] = 0  # Default value for other features
    
    # Select only the expected features in correct order
    final_features = [f for f in expected_features if f in df.columns]
    features_df = df[final_features].fillna(0)
    
    # Ensure ALL columns are numeric
    print("\nFinal feature dtypes:")
    for col in features_df.columns:
        if features_df[col].dtype == 'object':
            print(f"  - Converting {col} to numeric...")
            features_df[col] = pd.to_numeric(features_df[col], errors='coerce').fillna(0)
        print(f"  - {col}: {features_df[col].dtype}")
    
    print(f"Final features shape: {features_df.shape}")
    print(f"Final features: {features_df.columns.tolist()}")
    
    # Test prediction
    if 'is_fraud' in df.columns:
        target = df['is_fraud']
        try:
            print("Testing model prediction...")
            predictions = model.predict_proba(features_df)[:, 1]
            auc = roc_auc_score(target, predictions)
            print(f"🎯 FIXED! Model AUC: {auc:.4f}")
            
            # Save the fixed features dataset
            fixed_data_path = Path("../../data/processed/unified_claims_fixed_features.csv")
            features_df['is_fraud'] = target
            features_df.to_csv(fixed_data_path, index=False)
            print(f"💾 Fixed dataset saved to: {fixed_data_path}")
            
        except Exception as e:
            print(f"❌ Prediction failed: {e}")
            print("Trying alternative prediction method...")
            try:
                # Try with DMatrix for XGBoost
                import xgboost as xgb
                dmatrix = xgb.DMatrix(features_df, label=target)
                predictions = model.predict(dmatrix)
                auc = roc_auc_score(target, predictions)
                print(f"🎯 FIXED (DMatrix)! Model AUC: {auc:.4f}")
            except Exception as e2:
                print(f"❌ DMatrix also failed: {e2}")
    
    return features_df

if __name__ == "__main__":
    fixed_features = fix_feature_mismatch()