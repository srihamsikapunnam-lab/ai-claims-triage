"""
Main script to train and evaluate all models.
"""
import sys
import os
import numpy as np
import pandas as pd
import pickle
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from logistic_model import LogisticModel
    from random_forest_model import RandomForestModel
    from xgboost_model import XGBoostModel
    from lightgbm_model import LightGBMModel
    from evaluate import evaluate_model, compare_models
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all model files are in the same directory")
    sys.exit(1)

def load_processed_data(data_dir="data/processed"):
    """Load processed training and testing data."""
    data_dir = Path(data_dir)
    
    # Check for different possible file formats
    if (data_dir / "X_train.npy").exists():
        # NumPy format
        X_train = np.load(data_dir / "X_train.npy")
        X_test = np.load(data_dir / "X_test.npy")
        y_train = np.load(data_dir / "y_train.npy")
        y_test = np.load(data_dir / "y_test.npy")
    elif (data_dir / "X_train.csv").exists():
        # CSV format
        X_train = pd.read_csv(data_dir / "X_train.csv").values
        X_test = pd.read_csv(data_dir / "X_test.csv").values
        y_train = pd.read_csv(data_dir / "y_train.csv").values.ravel()
        y_test = pd.read_csv(data_dir / "y_test.csv").values.ravel()
    else:
        # Create dummy data for testing
        print("⚠️  No processed data found. Creating dummy data for testing...")
        n_samples = 1000
        n_features = 20
        
        # Create synthetic data
        np.random.seed(42)
        X_train = np.random.randn(n_samples, n_features)
        X_test = np.random.randn(200, n_features)
        
        # Create imbalanced labels (10% fraud)
        y_train = np.random.binomial(1, 0.1, n_samples)
        y_test = np.random.binomial(1, 0.1, 200)
        
        # Save dummy data
        data_dir.mkdir(exist_ok=True, parents=True)
        np.save(data_dir / "X_train.npy", X_train)
        np.save(data_dir / "X_test.npy", X_test)
        np.save(data_dir / "y_train.npy", y_train)
        np.save(data_dir / "y_test.npy", y_test)
        
        print(f"✅ Created dummy data")
    
    print(f"Data loaded:")
    print(f"  X_train shape: {X_train.shape}")
    print(f"  X_test shape: {X_test.shape}")
    
    return X_train, X_test, y_train, y_test

def main():
    """Main execution function."""
    print("="*70)
    print("FRAUD DETECTION MODEL BENCHMARKING")
    print("="*70)
    
    # 1. Load data
    print("\n[1/3] Loading processed data...")
    X_train, X_test, y_train, y_test = load_processed_data()
    
    # 2. Initialize models
    print("\n[2/3] Initializing models...")
    models = [
        LogisticModel(random_state=42),
        RandomForestModel(random_state=42),
        XGBoostModel(random_state=42),
        LightGBMModel(random_state=42)
    ]
    
    print(f"Models to train: {[m.get_name() for m in models]}")
    
    # 3. Train and evaluate models
    print("\n[3/3] Training and evaluating models...")
    results = []
    
    for i, model in enumerate(models):
        print(f"\n--- Training {model.get_name()} ({i+1}/{len(models)}) ---")
        
        try:
            # Train model
            model.train(X_train, y_train)
            print(f"  ✓ Training complete")
            
            # Evaluate model
            metrics = evaluate_model(model, X_test, y_test)
            results.append(metrics)
            
            # Print individual results
            print(f"  ROC-AUC: {metrics['roc_auc']:.4f}")
            print(f"  PR-AUC: {metrics['pr_auc']:.4f}")
            print(f"  Recall @ 95% precision: {metrics['recall_at_95%_precision']:.4f}")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            continue
    
    # 4. Compare and display results
    if results:
        print("\n" + "="*70)
        print("BENCHMARKING COMPLETE")
        print("="*70)
        
        results_df = compare_models(results)
        print("\nModel Comparison:")
        print(results_df.to_string(index=False))
        
        # Save results
        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)
        results_df.to_csv(results_dir / "model_comparison.csv", index=False)
        
        # Save best model
        best_model_name = results_df.iloc[0]['model_name']
        best_model = next(m for m in models if m.get_name() == best_model_name)
        
        models_dir = Path("models")
        models_dir.mkdir(exist_ok=True)
        
        model_file = models_dir / "best_model.pkl"
        with open(model_file, 'wb') as f:
            pickle.dump(best_model, f)
        
        print(f"\n✅ Best model ({best_model_name}) saved to: {model_file}")
        
        # Print recommendation
        print("\n" + "="*70)
        print("RECOMMENDATION:")
        print("="*70)
        print(f"Select {best_model_name} as it has the highest recall at 95% precision.")
        print("This is crucial for fraud detection where false positives are expensive.")
    else:
        print("\n❌ No models were successfully trained.")

if __name__ == "__main__":
    main()
