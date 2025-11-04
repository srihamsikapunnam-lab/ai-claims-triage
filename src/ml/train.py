import pandas as pd
import numpy as np
import logging
from pathlib import Path
import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import xgboost as xgb
import lightgbm as lgb

# Import our custom modules
import sys
sys.path.append(str(Path(__file__).parent.parent))
from data.data_loader import DataLoader
from data.data_unifier import DataUnifier, save_unified_data
from data.preprocessor import ClaimPreprocessor

logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self):
        self.models = {}
        self.best_model = None
        self.preprocessor = ClaimPreprocessor()
        
    def load_and_preprocess_data(self):
        """Load and preprocess data using our data loader"""
        logger.info("Loading and preprocessing data...")
        
        # Load data
        loader = DataLoader()
        datasets = loader.load_kaggle_datasets()
        
        if not datasets:
            raise Exception("No datasets loaded. Please check your data files.")
        
        # Unify datasets
        unifier = DataUnifier()
        unified_df = unifier.unify_datasets(datasets)
        
        if unified_df is None:
            raise Exception("Failed to unify datasets")
        
        # Save unified data
        output_path = Path("../../data/processed/unified_claims_v1.csv")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        save_unified_data(unified_df, output_path)
        
        # Preprocess data
        features, processed_df = self.preprocessor.preprocess_data(unified_df)
        
        # Prepare target variable
        if 'is_fraud' not in processed_df.columns:
            raise Exception("Target column 'is_fraud' not found in data")
        
        target = processed_df['is_fraud']
        
        logger.info(f"Data loaded: {features.shape}, target: {target.shape}")
        logger.info(f"Fraud rate: {target.mean():.3f}")
        
        return features, target, processed_df
    
    def train_baseline_models(self, X_train, X_test, y_train, y_test):
        """Train baseline models"""
        logger.info("Training baseline models...")
        
        # Logistic Regression
        lr_model = LogisticRegression(random_state=42, max_iter=1000)
        lr_model.fit(X_train, y_train)
        self.models['logistic_regression'] = lr_model
        
        # Random Forest
        rf_model = RandomForestClassifier(random_state=42, n_estimators=100)
        rf_model.fit(X_train, y_train)
        self.models['random_forest'] = rf_model
        
        # Evaluate models
        results = {}
        for name, model in self.models.items():
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1]
            
            results[name] = {
                'model': model,
                'predictions': y_pred,
                'probabilities': y_pred_proba,
                'auc': roc_auc_score(y_test, y_pred_proba)
            }
            
            logger.info(f"{name} AUC: {results[name]['auc']:.3f}")
        
        return results
    
    def train_advanced_models(self, X_train, X_test, y_train, y_test):
        """Train advanced models (XGBoost, LightGBM)"""
        logger.info("Training advanced models...")
        
        # XGBoost
        xgb_model = xgb.XGBClassifier(
            random_state=42,
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1
        )
        xgb_model.fit(X_train, y_train)
        self.models['xgboost'] = xgb_model
        
        # LightGBM
        lgb_model = lgb.LGBMClassifier(
            random_state=42,
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1
        )
        lgb_model.fit(X_train, y_train)
        self.models['lightgbm'] = lgb_model
        
        # Evaluate
        results = {}
        for name, model in self.models.items():
            if name in ['xgboost', 'lightgbm']:
                y_pred_proba = model.predict_proba(X_test)[:, 1]
                results[name] = {
                    'model': model,
                    'auc': roc_auc_score(y_test, y_pred_proba)
                }
                logger.info(f"{name} AUC: {results[name]['auc']:.3f}")
        
        return results
    
    def select_best_model(self, results):
        """Select the best performing model"""
        best_auc = 0
        best_model_name = None
        
        for name, result in results.items():
            if result['auc'] > best_auc:
                best_auc = result['auc']
                best_model_name = name
        
        if best_model_name:
            self.best_model = self.models[best_model_name]
            logger.info(f"Best model: {best_model_name} with AUC: {best_auc:.3f}")
        
        return best_model_name, best_auc
    
    def save_models(self, output_dir="../../models"):
        """Save trained models and preprocessor"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save best model
        if self.best_model:
            model_path = output_path / "fraud_model_v1.pkl"
            with open(model_path, 'wb') as f:
                pickle.dump(self.best_model, f)
            logger.info(f"Best model saved to {model_path}")
        
        # Save preprocessor
        preprocessor_path = output_path / "model_artifacts" / "preprocessor.pkl"
        preprocessor_path.parent.mkdir(parents=True, exist_ok=True)
        self.preprocessor.save_preprocessor(preprocessor_path)

def main():
    """Main training function"""
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Initialize trainer
        trainer = ModelTrainer()
        
        # Load and preprocess data
        features, target, processed_df = trainer.load_and_preprocess_data()
        
        # Split data
        X_train, X_test, y_train, y_test = trainer.preprocessor.get_train_test_split(
            features, target
        )
        
        # Train baseline models
        baseline_results = trainer.train_baseline_models(X_train, X_test, y_train, y_test)
        
        # Train advanced models
        advanced_results = trainer.train_advanced_models(X_train, X_test, y_train, y_test)
        
        # Combine results
        all_results = {**baseline_results, **advanced_results}
        
        # Select best model
        best_name, best_auc = trainer.select_best_model(all_results)
        
        # Save models
        trainer.save_models()
        
        logger.info(f"Training completed. Best model: {best_name} with AUC: {best_auc:.3f}")
        
    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise

if __name__ == "__main__":
    main()