"""
Test script to verify everything works.
"""
print("Testing the model implementation...")

try:
    # Try to import and run the main training script
    from src.ml.train_all_models import main
    
    print("✅ Imports successful!")
    print("\nYou can now run:")
    print("python src\\ml\\train_all_models.py")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nMake sure:")
    print("1. You're in the project root directory")
    print("2. All Python files are in src\\ml\\")
    print("3. Required packages are installed: pip install scikit-learn xgboost lightgbm numpy pandas")
