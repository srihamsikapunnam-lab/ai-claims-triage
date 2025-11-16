import joblib
import os

def examine_working_models():
    print("🔍 Examining working model files...")
    
    # Test the working models
    working_models = [
        "models/fraud_model_api_ready.joblib",
        "models/fraud_detection_core_model.joblib"
    ]
    
    for model_path in working_models:
        print(f"\n" + "="*50)
        print(f"📂 Loading: {model_path}")
        
        try:
            model_data = joblib.load(model_path)
            print(f"✅ Loaded successfully!")
            print(f"📊 Data type: {type(model_data)}")
            
            if isinstance(model_data, dict):
                print("🔍 Dictionary contents:")
                for key, value in model_data.items():
                    if hasattr(value, 'predict_proba'):
                        print(f"  ✅ {key}: Model with predict_proba")
                    elif hasattr(value, 'predict'):
                        print(f"  ✅ {key}: Model with predict")
                    else:
                        print(f"  📝 {key}: {type(value)}")
                        
                # Show all keys
                print(f"  🗝️  All keys: {list(model_data.keys())}")
                
            else:
                print(f"❓ Unexpected data type: {type(model_data)}")
                
        except Exception as e:
            print(f"❌ Failed: {str(e)}")

if __name__ == "__main__":
    examine_working_models()