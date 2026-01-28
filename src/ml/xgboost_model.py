"""
XGBoost model implementation.
"""
import numpy as np
import xgboost as xgb
from .base_model import BaseModel

class XGBoostModel(BaseModel):
    """XGBoost model - primary contender for fraud detection."""
    
    def __init__(self, random_state: int = 42):
        """
        Initialize XGBoost model.
        
        Args:
            random_state: Random seed for reproducibility
        """
        self.scale_pos_weight = None
        self.model = None
        self.random_state = random_state
        self.is_trained = False
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray):
        """Train the XGBoost model."""
        # Calculate scale_pos_weight for imbalance
        negative = (y_train == 0).sum()
        positive = (y_train == 1).sum()
        self.scale_pos_weight = negative / positive if positive > 0 else 1
        
        # Set up XGBoost parameters
        params = {
            'objective': 'binary:logistic',
            'eval_metric': 'aucpr',
            'max_depth': 6,
            'learning_rate': 0.1,
            'n_estimators': 200,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'scale_pos_weight': self.scale_pos_weight,
            'random_state': self.random_state,
            'n_jobs': -1,
            'verbosity': 0
        }
        
        self.model = xgb.XGBClassifier(**params)
        self.model.fit(X_train, y_train)
        self.is_trained = True
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict probabilities for the positive class."""
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        return self.model.predict_proba(X)[:, 1]
    
    def get_name(self) -> str:
        """Get model name."""
        return "XGBoost"
