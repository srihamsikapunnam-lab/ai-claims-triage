import joblib
import pandas as pd
from typing import Dict, Any, List

class FraudModelService:
    def __init__(self):
        self.model = None
        print("✅ Model service initialized - using dummy predictions for now")
    
    def predict(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "prediction": "Fraud",
            "probability": 0.82,
            "risk_score": 0.82,
            "risk_category": "High",
            "explanation": [
                "Claimed amount higher than typical for diagnosis",
                "Length of stay unusually short", 
                "Hospital has higher than average previous claims"
            ],
            "status": "Under Review"
        }

model_service = FraudModelService()