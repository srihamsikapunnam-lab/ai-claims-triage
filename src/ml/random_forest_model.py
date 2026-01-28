"""
Random Forest model implementation.
"""
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from .base_model import BaseModel

class RandomForestModel(BaseModel):
    """Random Forest model for non-linear baseline."""
    
    def __init__(self, random_state: int = 42):
        """
        Initialize Random Forest model.
        
        Args:
            random_state: Random seed for reproducibility
        """
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=None,
            class_weight='balanced',
            random_state=random_state,
            n_jobs=-1,
            verbose=0
        )
        self.is_trained = False
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray):
        """Train the Random Forest model."""
        self.model.fit(X_train, y_train)
        self.is_trained = True
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict probabilities for the positive class."""
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        return self.model.predict_proba(X)[:, 1]
    
    def get_name(self) -> str:
        """Get model name."""
        return "RandomForest"
