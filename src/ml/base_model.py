"""
Base model interface that all models must implement.
"""
from abc import ABC, abstractmethod
import numpy as np

class BaseModel(ABC):
    """Abstract base class for all ML models."""
    
    @abstractmethod
    def train(self, X_train: np.ndarray, y_train: np.ndarray):
        """
        Train the model on the given data.
        
        Args:
            X_train: Training features
            y_train: Training labels
        """
        pass
    
    @abstractmethod
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict probabilities for the positive class.
        
        Args:
            X: Features to predict on
            
        Returns:
            Array of probabilities for the positive class
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get the model name for reporting.
        
        Returns:
            Model name as string
        """
        pass
