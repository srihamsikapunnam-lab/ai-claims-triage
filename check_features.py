import joblib

def check_feature_details():
    print("🔍 Checking feature details...")
    
    # Load the API-ready model (simpler structure)
    model_data = joblib.load("models/fraud_model_api_ready.joblib")
    
    print("📊 MODEL DETAILS:")
    print(f"Model type: {type(model_data['model'])}")
    print(f"Number of features: {len(model_data['feature_names'])}")
    print(f"Feature names: {model_data['feature_names']}")
    print(f"Encoders available: {list(model_data['encoders'].keys())}")
    
    # Check the core model too
    print("\n" + "="*50)
    core_data = joblib.load("models/fraud_detection_core_model.joblib")
    print("📊 CORE MODEL DETAILS:")
    print(f"Feature names: {core_data['feature_names']}")
    if 'model_performance' in core_data:
        print(f"Model performance: {core_data['model_performance']}")

if __name__ == "__main__":
    check_feature_details()