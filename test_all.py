print("=== STARTING TESTS ===\n")

# Test 1: Basic imports
print("1. Testing basic package imports...")
try:
    import numpy as np
    print("   ✅ numpy")
except:
    print("   ❌ numpy")

try:
    import sklearn
    print("   ✅ scikit-learn")
except:
    print("   ❌ scikit-learn")

try:
    import xgboost
    print("   ✅ xgboost")
except:
    print("   ❌ xgboost")

try:
    import lightgbm
    print("   ✅ lightgbm")
except:
    print("   ❌ lightgbm")

# Test 2: Our model imports
print("\n2. Testing our model imports...")
try:
    # Add src/ml to path
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'ml'))
    
    from base_model import BaseModel
    print("   ✅ BaseModel imported")
    
    from logistic_model import LogisticModel
    print("   ✅ LogisticModel imported")
    
    from random_forest_model import RandomForestModel
    print("   ✅ RandomForestModel imported")
    
    from xgboost_model import XGBoostModel
    print("   ✅ XGBoostModel imported")
    
    from lightgbm_model import LightGBMModel
    print("   ✅ LightGBMModel imported")
    
    print("\n   ✅ ALL MODEL IMPORTS SUCCESSFUL!")
    
except ImportError as e:
    print(f"   ❌ Import Error: {e}")
except Exception as e:
    print(f"   ❌ Unexpected Error: {e}")

# Test 3: Create dummy data and test one model
print("\n3. Quick training test...")
try:
    # Create small dummy dataset
    np.random.seed(42)
    X = np.random.randn(50, 5)  # 50 samples, 5 features
    y = np.random.randint(0, 2, 50)  # Binary labels
    
    print(f"   Created dummy data: X shape={X.shape}, y shape={y.shape}")
    
    # Test Logistic Regression (simplest)
    model = LogisticModel()
    model.train(X, y)
    
    # Make predictions
    X_test = np.random.randn(10, 5)
    y_pred = model.predict_proba(X_test)
    
    print(f"   ✅ LogisticRegression trained successfully")
    print(f"   ✅ Predictions shape: {y_pred.shape}")
    print(f"   ✅ Model name: {model.get_name()}")
    
except Exception as e:
    print(f"   ❌ Training test failed: {e}")

print("\n=== TESTS COMPLETE ===")
print("\nNext: Run 'python src\\ml\\train_all_models.py' to test the full pipeline")
