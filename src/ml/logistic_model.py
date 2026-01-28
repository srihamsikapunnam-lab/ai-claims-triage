"""
Logistic Regression model implementation.
"""
import numpy as np
from sklearn.linear_model import LogisticRegression
from .base_model import BaseModel

class LogisticModel(BaseModel):
    """Logistic Regression baseline model."""
    
    def __init__(self, random_state: int = 42):
        """
        Initialize Logistic Regression model.
        
        Args:
            random_state: Random seed for reproducibility
        """
        self.model = LogisticRegression(
            class_weight='balanced',
            random_state=random_state,
            max_iter=1000,
            n_jobs=-1
        )
        self.is_trained = False
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray):
        """Train the logistic regression model."""
        self.model.fit(X_train, y_train)
        self.is_trained = True
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict probabilities for the positive class."""
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        return self.model.predict_proba(X)[:, 1]
    
    def get_name(self) -> str:
        """Get model name."""
        return "LogisticRegression"
