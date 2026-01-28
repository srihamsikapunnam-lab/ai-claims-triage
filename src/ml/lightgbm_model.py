"""
LightGBM model implementation.
"""
import numpy as np
import lightgbm as lgb
from .base_model import BaseModel

class LightGBMModel(BaseModel):
    """LightGBM model - efficient alternative to XGBoost."""
    
    def __init__(self, random_state: int = 42):
        """
        Initialize LightGBM model.
        
        Args:
            random_state: Random seed for reproducibility
        """
        self.model = None
        self.random_state = random_state
        self.is_trained = False
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray):
        """Train the LightGBM model."""
        # Set up LightGBM parameters
        params = {
            'objective': 'binary',
            'metric': 'auc',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.1,
            'feature_fraction': 0.8,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': -1,
            'random_state': self.random_state,
            'is_unbalance': True
        }
        
        self.model = lgb.LGBMClassifier(**params)
        self.model.fit(X_train, y_train)
        self.is_trained = True
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict probabilities for the positive class."""
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        return self.model.predict_proba(X)[:, 1]
    
    def get_name(self) -> str:
        """Get model name."""
        return "LightGBM"
