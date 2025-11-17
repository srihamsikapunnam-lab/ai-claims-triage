import joblib
import os
import sys

def test_model_loading():
    print("🔍 Checking model files...")
    
    # Check if models directory exists
    if not os.path.exists("models"):
        print("❌ 'models' directory not found!")
        return
    
    # List all model files
    model_files = os.listdir("models/")
    print("📁 Available model files in 'models/' directory:")
    for file in model_files:
        file_path = os.path.join("models", file)
        file_size = os.path.getsize(file_path)
        print(f"  - {file} ({file_size} bytes)")
    
    # Try loading the specific model
    model_path = "models/fraud_model_v1.pkl"
    print(f"\n🔄 Attempting to load: {model_path}")
    
    if not os.path.exists(model_path):
        print(f"❌ Model file not found: {model_path}")
        print("💡 Available .pkl files:")
        pkl_files = [f for f in model_files if f.endswith('.pkl')]
        for pkl_file in pkl_files:
            print(f"  - {pkl_file}")
        return
    
    try:
        # Load the model
        model = joblib.load(model_path)
        print(f"✅ Model loaded successfully!")
        print(f"📊 Model type: {type(model)}")
        
        # Check model attributes
        print(f"🔧 Model attributes:")
        if hasattr(model, 'predict_proba'):
            print("  ✅ Has predict_proba method - ready for probability predictions")
        else:
            print("  ❌ No predict_proba method")
            
        if hasattr(model, 'predict'):
            print("  ✅ Has predict method")
        else:
            print("  ❌ No predict method")
            
        if hasattr(model, 'feature_names_in_'):
            print(f"  ✅ Has feature names: {list(model.feature_names_in_)}")
        elif hasattr(model, 'get_booster'):
            try:
                # For XGBoost models
                booster = model.get_booster()
                feature_names = booster.feature_names
                if feature_names:
                    print(f"  ✅ XGBoost feature names: {feature_names}")
                else:
                    print("  ℹ️  XGBoost model but no feature names saved")
            except:
                print("  ℹ️  Could not extract XGBoost feature names")
        else:
            print("  ℹ️  No feature names found in model")
            
        # Try a simple test prediction if possible
        print(f"\n🧪 Testing model with sample data...")
        try:
            # Create simple test data based on common features
            import numpy as np
            import pandas as pd
            
            # Try to determine feature count
            if hasattr(model, 'n_features_in_'):
                n_features = model.n_features_in_
                test_data = np.random.random((1, n_features))
                test_df = pd.DataFrame(test_data)
                
                if hasattr(model, 'predict_proba'):
                    proba = model.predict_proba(test_df)
                    print(f"  ✅ Test prediction successful!")
                    print(f"  📈 Probability shape: {proba.shape}")
                    print(f"  🎯 Sample probabilities: {proba[0]}")
            else:
                print("  ℹ️  Could not determine number of features for test")
                
        except Exception as e:
            print(f"  ⚠️  Test prediction failed (expected): {str(e)}")
            
    except Exception as e:
        print(f"❌ Failed to load model: {str(e)}")
        print("💡 Try loading with different model files:")
        for file in model_files:
            if file.endswith('.joblib') or file.endswith('.pkl'):
                try:
                    test_path = os.path.join("models", file)
                    test_model = joblib.load(test_path)
                    print(f"  ✅ {file} can be loaded! Type: {type(test_model)}")
                except:
                    print(f"  ❌ {file} cannot be loaded")

if __name__ == "__main__":
    test_model_loading()