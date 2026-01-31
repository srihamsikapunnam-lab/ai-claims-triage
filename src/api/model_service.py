import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, List
import logging
from pathlib import Path

# Import xgboost before loading models (needed for unpickling)
try:
    import xgboost as xgb
except ImportError:
    print("⚠️ XGBoost not installed, model loading may fail")
    xgb = None

# ✅ FIXED IMPORT (this was the real problem)
from .analytics import analytics_service

logger = logging.getLogger(__name__)


class FraudModelService:
    def __init__(self):
        self.model = None
        self.feature_names = None
        self.encoders = None
        self.lime_explainer = None
        self.model_type = None
        self.model_info = {}
        self.load_model()

    def load_model(self):
        """Load the trained XGBoost model"""
        try:
            import xgboost  # ensure import before unpickling

            model_path = Path(__file__).parent.parent.parent / "models" / "fraud_model_api_ready.joblib"

            if not model_path.exists():
                print("❌ Model file not found")
                return

            model_data = joblib.load(model_path)

            self.model = model_data["model"]
            self.feature_names = model_data["feature_names"]
            self.encoders = model_data["encoders"]
            self.model_type = model_data.get("model_type", "Unknown")

            training_data = model_data.get("training_data")

            if training_data is not None:
                try:
                    import lime.lime_tabular
                    self.lime_explainer = lime.lime_tabular.LimeTabularExplainer(
                        training_data=training_data,
                        feature_names=self.feature_names,
                        class_names=["Legitimate", "Fraud"],
                        mode="classification",
                        random_state=42,
                    )
                except Exception as e:
                    print(f"⚠️ LIME init failed: {e}")
                    self.lime_explainer = None

            print("✅ Model loaded successfully")

        except Exception as e:
            print(f"❌ Failed to load model: {e}")

    def preprocess_input(self, claim_data: Dict[str, Any]) -> pd.DataFrame:
        processed = claim_data.copy()

        claimed_amount = processed.get("claimed_amount", 0)
        length_of_stay = processed.get("length_of_stay", 1)

        processed["claimed_per_day"] = claimed_amount / max(length_of_stay, 1)
        processed["high_amount_flag"] = int(claimed_amount > 10000)
        processed["short_stay_high_bill"] = int(length_of_stay < 3 and claimed_amount > 5000)

        # Encode categoricals
        if "gender" in self.encoders:
            val = processed.get("gender")
            processed["gender_encoded"] = (
                self.encoders["gender"].transform([val])[0]
                if val in self.encoders["gender"].classes_
                else 0
            )

        if "diagnosis" in self.encoders:
            val = processed.get("diagnosis")
            processed["diagnosis_encoded"] = (
                self.encoders["diagnosis"].transform([val])[0]
                if val in self.encoders["diagnosis"].classes_
                else 0
            )

        data = {f: [processed.get(f, 0)] for f in self.feature_names}
        return pd.DataFrame(data)[self.feature_names]

    def predict(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        if self.model is None:
            return self._dummy_prediction(claim_data)

        X = self.preprocess_input(claim_data)
        prob = self.model.predict_proba(X)[0][1]
        risk_score = int(prob * 100)

        analytics_service.record_prediction(
            "Fraud" if prob > 0.5 else "Legitimate",
            risk_score
        )

        return {
            "prediction": "Fraud" if prob > 0.5 else "Legitimate",
            "probability": round(prob, 4),
            "risk_score": risk_score,
            "risk_category": self.get_risk_category(risk_score),
            "model_version": f"{self.model_type}_Production_v2.0"
        }

    def get_risk_category(self, score: int) -> str:
        if score >= 80:
            return "Very High"
        elif score >= 60:
            return "High"
        elif score >= 40:
            return "Medium"
        elif score >= 20:
            return "Low"
        return "Very Low"

    def _dummy_prediction(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "prediction": "Fraud",
            "probability": 0.82,
            "risk_score": 82,
            "risk_category": "High",
            "model_version": "Dummy_Fallback"
        }


# Global instance
model_service = FraudModelService()
