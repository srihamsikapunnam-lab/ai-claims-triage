import lime
import lime.lime_tabular
import pandas as pd
import numpy as np
import pickle
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class LimeExplainer:
    def __init__(self, model_path="../../models/fraud_model_v1.pkl", 
                 preprocessor_path="../../models/model_artifacts/preprocessor.pkl"):
        self.model_path = Path(model_path)
        self.preprocessor_path = Path(preprocessor_path)
        self.model = None
        self.preprocessor_data = None
        self.explainer = None
        self.feature_names = []
        
    def load_model_and_preprocessor(self):
        """Load the trained model and preprocessor"""
        with open(self.model_path, 'rb') as f:
            self.model = pickle.load(f)
        
        with open(self.preprocessor_path, 'rb') as f:
            self.preprocessor_data = pickle.load(f)
            self.feature_names = self.preprocessor_data.get('feature_names', [])
        
        logger.info("Model and preprocessor loaded successfully")
        
    def create_lime_explainer(self, X_train, feature_names=None, mode='classification'):
        """Create LIME explainer for tabular data"""
        if feature_names is None:
            feature_names = self.feature_names
            
        self.explainer = lime.lime_tabular.LimeTabularExplainer(
            training_data=X_train.values,
            feature_names=feature_names,
            mode=mode,
            random_state=42
        )
        logger.info("LIME explainer created")
        
    def explain_instance(self, instance, num_features=5):
        """Explain a single prediction instance"""
        if self.explainer is None:
            raise ValueError("LIME explainer not created. Call create_lime_explainer first.")
            
        # Get explanation
        exp = self.explainer.explain_instance(
            data_row=instance.values[0],
            predict_fn=self.model.predict_proba,
            num_features=num_features
        )
        
        return exp
    
    def generate_explanation_text(self, explanation, top_features=3):
        """Generate human-readable 3-line explanation from LIME"""
        explanations = []
        
        # Get top features from LIME explanation
        lime_list = explanation.as_list()
        
        for i in range(min(top_features, len(lime_list))):
            feature, impact = lime_list[i]
            
            # Parse feature name and create explanation
            if 'claimed_amount' in feature:
                explanations.append(f"Claimed amount significantly {'increases' if impact > 0 else 'decreases'} fraud risk")
            elif 'length_of_stay' in feature:
                explanations.append(f"Length of stay {'increases' if impact > 0 else 'decreases'} fraud risk")
            elif 'patient_age' in feature:
                explanations.append(f"Patient age {'increases' if impact > 0 else 'decreases'} fraud risk")
            else:
                # Generic explanation
                direction = "increases" if impact > 0 else "decreases"
                explanations.append(f"{feature} {direction} fraud risk")
                
        return explanations
    
    def get_global_feature_importance(self, X_sample, num_samples=1000):
        """Estimate global feature importance using LIME on multiple instances"""
        if self.explainer is None:
            raise ValueError("LIME explainer not created")
            
        feature_impacts = {feature: 0 for feature in self.feature_names}
        
        # Sample instances for global importance
        sample_indices = np.random.choice(len(X_sample), min(num_samples, len(X_sample)), replace=False)
        
        for idx in sample_indices:
            instance = X_sample.iloc[[idx]]
            exp = self.explain_instance(instance, num_features=len(self.feature_names))
            
            # Aggregate feature impacts
            for feature, impact in exp.as_list():
                for feat_name in self.feature_names:
                    if feat_name in feature:
                        feature_impacts[feat_name] += abs(impact)
                        break
        
        # Normalize and create DataFrame
        importance_df = pd.DataFrame({
            'feature': list(feature_impacts.keys()),
            'importance': list(feature_impacts.values())
        }).sort_values('importance', ascending=False)
        
        return importance_df

def test_lime_explanations():
    """Test LIME explanation system"""
    logging.basicConfig(level=logging.INFO)
    
    # Load sample data
    from data.data_loader import DataLoader
    from data.data_unifier import DataUnifier
    from data.preprocessor import ClaimPreprocessor
    
    print("=== TESTING LIME EXPLANATIONS ===")
    
    # Load a small sample of data
    loader = DataLoader()
    datasets = loader.load_kaggle_datasets()
    unifier = DataUnifier()
    unified_df = unifier.unify_datasets(datasets)
    
    preprocessor = ClaimPreprocessor()
    features, processed_df = preprocessor.preprocess_data(unified_df.head(1000))
    target = processed_df['is_fraud']
    
    # Initialize LIME explainer
    explainer = LimeExplainer()
    explainer.load_model_and_preprocessor()
    explainer.create_lime_explainer(features.head(100), explainer.feature_names)
    
    # Explain a specific prediction
    test_instance = features.iloc[[0]]  # First claim
    lime_explanation = explainer.explain_instance(test_instance)
    
    explanation_text = explainer.generate_explanation_text(lime_explanation)
    
    print("\n=== LIME EXPLANATION FOR SAMPLE CLAIM ===")
    for i, explanation in enumerate(explanation_text, 1):
        print(f"{i}. {explanation}")
    
    # Get global feature importance
    global_importance = explainer.get_global_feature_importance(features.head(50))
    
    print("\n=== GLOBAL FEATURE IMPORTANCE (LIME) ===")
    for i, row in global_importance.head(10).iterrows():
        print(f"{i+1:2d}. {row['feature']:25} {row['importance']:.4f}")
    
    print("\n✅ LIME explanations generated successfully!")

if __name__ == "__main__":
    test_lime_explanations()
    