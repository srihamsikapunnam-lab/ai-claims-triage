import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, List
import logging
from pathlib import Path

# 🆕 WEEK 4 ANALYTICS: Import analytics service
from analytics import analytics_service

logger = logging.getLogger(__name__)

class FraudModelService:
    def __init__(self):
        self.model = None
        self.feature_names = None
        self.encoders = None
        self.model_info = {}
        self.load_model()
    
    def load_model(self):
        """Load the trained RandomForest model from the API-ready file"""
        try:
            # Use the API-ready model
            model_path = Path(__file__).parent.parent.parent / "models" / "fraud_model_api_ready.joblib"
            
            if model_path.exists():
                model_data = joblib.load(model_path)
                print("✅ API-ready RandomForest model loaded successfully!")
                
                # Extract all components
                self.model = model_data['model']
                self.feature_names = model_data['feature_names']
                self.encoders = model_data['encoders']
                
                print(f"🎯 Model type: RandomForestClassifier")
                print(f"📊 Number of features: {len(self.feature_names)}")
                print(f"📝 Features: {self.feature_names}")
                print(f"🔧 Encoders: {list(self.encoders.keys())}")
                print("✅ Real model ready for production predictions!")
                
            else:
                print("❌ Model file not found")
                
        except Exception as e:
            print(f"❌ Failed to load model: {str(e)}")
    
    def encode_categorical_features(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Encode categorical features using the saved encoders"""
        encoded_data = claim_data.copy()
        
        try:
            # Encode gender if encoder exists and gender is provided
            if 'gender' in self.encoders and 'gender' in claim_data:
                gender = claim_data['gender']
                encoder = self.encoders['gender']
                if gender in encoder.classes_:
                    encoded_data['gender_encoded'] = encoder.transform([gender])[0]
                    print(f"✅ Gender encoded: {gender} -> {encoded_data['gender_encoded']}")
                else:
                    encoded_data['gender_encoded'] = -1  # Unknown category
                    print(f"⚠️  Unknown gender: {gender}, using default")
            else:
                encoded_data['gender_encoded'] = 0
                print("⚠️  Gender not provided or encoder not found")
            
            # Encode diagnosis if encoder exists and diagnosis is provided
            if 'diagnosis' in self.encoders and 'diagnosis' in claim_data:
                diagnosis = claim_data['diagnosis']
                encoder = self.encoders['diagnosis']
                if diagnosis in encoder.classes_:
                    encoded_data['diagnosis_encoded'] = encoder.transform([diagnosis])[0]
                    print(f"✅ Diagnosis encoded: {diagnosis} -> {encoded_data['diagnosis_encoded']}")
                else:
                    encoded_data['diagnosis_encoded'] = -1  # Unknown category
                    print(f"⚠️  Unknown diagnosis: {diagnosis}, using default")
            else:
                encoded_data['diagnosis_encoded'] = 0
                print("⚠️  Diagnosis not provided or encoder not found")
                
        except Exception as e:
            print(f"⚠️ Encoding error: {str(e)}")
            # Set defaults if encoding fails
            encoded_data['gender_encoded'] = 0
            encoded_data['diagnosis_encoded'] = 0
            
        return encoded_data
    
    def calculate_derived_features(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate the derived features that the model expects"""
        derived_data = claim_data.copy()
        
        # Get claimed amount (handle both field names)
        claimed_amount = claim_data.get('claimed_amount', claim_data.get('claimed amount', 0))
        length_of_stay = claim_data.get('length_of_stay', claim_data.get('length_of_stay', 1))
        
        # Calculate claimed_per_day
        if length_of_stay > 0:
            derived_data['claimed_per_day'] = claimed_amount / length_of_stay
        else:
            derived_data['claimed_per_day'] = claimed_amount
        
        # Calculate high_amount_flag (1 if > 10000, else 0)
        derived_data['high_amount_flag'] = 1 if claimed_amount > 10000 else 0
        
        # Calculate short_stay_high_bill (1 if stay < 3 days and amount > 5000, else 0)
        derived_data['short_stay_high_bill'] = 1 if length_of_stay < 3 and claimed_amount > 5000 else 0
        
        print(f"✅ Derived features calculated:")
        print(f"   claimed_per_day: {derived_data['claimed_per_day']}")
        print(f"   high_amount_flag: {derived_data['high_amount_flag']}")
        print(f"   short_stay_high_bill: {derived_data['short_stay_high_bill']}")
        
        return derived_data
    
    def preprocess_input(self, claim_data: Dict[str, Any]) -> pd.DataFrame:
        """Convert API input to model-ready features using EXACT training features"""
        try:
            print(f"📥 Raw input: {claim_data}")
            
            # Step 1: Calculate derived features
            processed_data = self.calculate_derived_features(claim_data)
            
            # Step 2: Encode categorical features
            processed_data = self.encode_categorical_features(processed_data)
            
            # Step 3: Create final feature set in EXACT order expected by model
            final_features = {}
            
            for feature in self.feature_names:
                if feature in processed_data:
                    final_features[feature] = [processed_data[feature]]
                else:
                    # Set default values for missing features
                    defaults = {
                        'patient_age': 45,
                        'claimed_amount': 0,
                        'claimed amount': 0,
                        'length_of_stay': 1,
                        'claimed_per_day': 0,
                        'high_amount_flag': 0,
                        'short_stay_high_bill': 0,
                        'gender_encoded': 0,
                        'diagnosis_encoded': 0
                    }
                    final_features[feature] = [defaults.get(feature, 0)]
                    print(f"⚠️  Using default for: {feature}")
            
            # Create DataFrame with exact feature order
            df = pd.DataFrame(final_features)
            df = df[self.feature_names]  # CRITICAL: Ensure correct order
            
            print(f"📊 Processed data shape: {df.shape}")
            print(f"🔍 Final features: {dict(zip(df.columns, df.iloc[0].values))}")
            return df
            
        except Exception as e:
            logger.error(f"Preprocessing error: {str(e)}")
            raise
    
    def predict(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make real fraud prediction using RandomForest model"""
        
        # If model didn't load, fall back to dummy
        if self.model is None:
            print("⚠️ Using dummy prediction - model not loaded")
            return self._dummy_prediction(claim_data)
        
        try:
            print("🎯 Making real RandomForest prediction...")
            
            # Preprocess the input data
            processed_data = self.preprocess_input(claim_data)
            
            # Make prediction
            prediction_proba = self.model.predict_proba(processed_data)
            fraud_probability = float(prediction_proba[0][1])  # Probability of fraud class
            
            # Convert to risk score (0-100)
            risk_score = int(fraud_probability * 100)
            
            # 🆕 WEEK 4 ANALYTICS: Track this prediction for dashboard
            analytics_service.record_prediction(
                "Fraud" if fraud_probability > 0.5 else "Legitimate", 
                risk_score
            )
            
            # Generate explanations
            explanations = self.generate_explanations(claim_data, fraud_probability)
            
            # FIXED: Intelligent status logic based on both prediction and risk
            if fraud_probability > 0.5:  # If predicted as Fraud
                if risk_score >= 80:
                    status = "High Priority Investigation"
                elif risk_score >= 60:
                    status = "Manual Review Required"
                elif risk_score >= 40:
                    status = "Additional Verification Needed"
                else:
                    status = "Flagged for Review"
            else:  # If predicted as Legitimate
                if risk_score < 20:
                    status = "Auto-Approved"
                elif risk_score < 40:
                    status = "Fast-Track Approval"
                else:
                    status = "Standard Review"
            
            response = {
                "prediction": "Fraud" if fraud_probability > 0.5 else "Legitimate",
                "probability": round(fraud_probability, 4),
                "risk_score": risk_score,
                "risk_category": self.get_risk_category(risk_score),
                "explanation": explanations,
                "status": status,
                "model_version": "RandomForest_Production_v1.1",  # Updated version
                "features_used": self.feature_names
            }
            
            print(f"📤 Prediction result: Risk Score {risk_score}, Category: {response['risk_category']}, Status: {status}")
            return response
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            print(f"⚠️ Real model prediction failed: {str(e)}")
            return self._dummy_prediction(claim_data)
    
    def generate_explanations(self, claim_data: Dict[str, Any], fraud_prob: float) -> List[str]:
        """Generate 3-line explanation texts based on actual prediction and features"""
        explanations = []
        
        claimed_amount = claim_data.get('claimed_amount', claim_data.get('claimed amount', 0))
        length_of_stay = claim_data.get('length_of_stay', 1)
        patient_age = claim_data.get('patient_age', 45)
        
        # Explanation 1: Based on probability
        if fraud_prob > 0.8:
            explanations.append("Very high fraud probability based on historical claim patterns")
        elif fraud_prob > 0.6:
            explanations.append("High risk patterns detected in claim characteristics")
        elif fraud_prob > 0.4:
            explanations.append("Moderate risk level requiring standard review")
        else:
            explanations.append("Low risk profile based on claim analysis")
        
        # Explanation 2: Based on amount and stay
        if claimed_amount > 15000:
            explanations.append("Claim amount significantly exceeds typical range for procedure")
        elif claimed_amount > 8000:
            explanations.append("Above-average claim amount requires verification")
        
        if length_of_stay < 2 and claimed_amount > 5000:
            explanations.append("Short stay with high billing amount detected")
        else:
            explanations.append("Length of stay within expected range")
        
        # Explanation 3: Based on derived features
        if fraud_prob > 0.7:
            explanations.append("Multiple risk factors requiring investigation")
        else:
            explanations.append("Standard verification process recommended")
        
        return explanations[:3]
    
    def get_risk_category(self, risk_score: int) -> str:
        """Convert risk score to category"""
        if risk_score >= 80:
            return "Very High"
        elif risk_score >= 60:
            return "High"
        elif risk_score >= 40:
            return "Medium"
        elif risk_score >= 20:
            return "Low"
        else:
            return "Very Low"
    
    def _dummy_prediction(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback dummy prediction"""
        return {
            "prediction": "Fraud",
            "probability": 0.82,
            "risk_score": 82,
            "risk_category": "High",
            "explanation": [
                "Claimed amount higher than typical for diagnosis",
                "Length of stay unusually short", 
                "Hospital has higher than average previous claims"
            ],
            "status": "Manual Review Required",
            "model_version": "Dummy_Fallback"
        }

# Global instance
model_service = FraudModelService()