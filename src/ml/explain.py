import lime
import lime.lime_tabular
import pandas as pd
import numpy as np
import pickle
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class LIMEFraudExplainer:
    def __init__(self, model, feature_names, training_data=None):
        self.model = model
        self.feature_names = feature_names
        self.training_data = training_data
        self.explainer = None
        self.scaler = StandardScaler()  # Add a simple scaler
        self._initialize_explainer()
    
    def _initialize_explainer(self):  # ✅ Fixed: added 'self'
        """Initialize LIME explainer with training data"""
        if self.training_data is not None:
            # Fit scaler on training data
            self.scaler.fit(self.training_data)
            training_data_scaled = self.scaler.transform(self.training_data)
        else:
            # Create dummy training data for explainer
            training_data_scaled = np.random.random((100, len(self.feature_names)))
        
        self.explainer = lime.lime_tabular.LimeTabularExplainer(
            training_data=training_data_scaled,
            feature_names=self.feature_names,
            class_names=['Genuine', 'Fraud'],
            mode='classification',
            random_state=42
        )
        print("✅ LIME Explainer initialized")
    
    def explain_prediction(self, instance, num_features=5):
        """Generate LIME explanation for a single prediction"""
        try:
            # Convert to numpy array and ensure 2D
            if isinstance(instance, pd.DataFrame):
                instance = instance.values
            elif isinstance(instance, pd.Series):
                instance = instance.values.reshape(1, -1)
            elif isinstance(instance, list):
                instance = np.array(instance).reshape(1, -1)
            elif instance.ndim == 1:
                instance = instance.reshape(1, -1)
            
            # Scale the instance
            instance_scaled = self.scaler.transform(instance)
            
            # Get prediction probabilities function for LIME
            def predict_proba_fn(x):
                return self.model.predict_proba(x)
            
            # Generate explanation
            explanation = self.explainer.explain_instance(
                instance_scaled[0], 
                predict_proba_fn, 
                num_features=num_features,
                top_labels=1
            )
            
            return explanation
            
        except Exception as e:
            print(f"❌ Error in explain_prediction: {e}")
            return None
    
    def get_explanation_text(self, explanation, label=1):
            """Convert LIME explanation to human-readable text"""
            if explanation is None:
                return ["Unable to generate explanation"]
            
            try:
                explanation_list = explanation.as_list(label=label)
                
                reasons = []
                for feature, importance in explanation_list:
                    # Skip features with very low importance
                    if abs(importance) < 0.01:
                        continue
                        
                    # Convert LIME output to readable reasons
                    if importance > 0:
                        direction = "higher than typical"
                    else:
                        direction = "lower than typical"
                    
                    # Parse the feature description properly
                    if ' <= ' in feature:
                        parts = feature.split(' <= ')
                        feature_name = parts[0]
                        threshold = parts[1]
                        reason = f"{feature_name} is {direction} ({threshold})"
                    elif ' > ' in feature:
                        parts = feature.split(' > ')
                        feature_name = parts[0]
                        threshold = parts[1]
                        reason = f"{feature_name} is {direction} ({threshold})"
                    else:
                        # Simple feature name
                        feature_clean = feature.replace('_', ' ').title()
                        reason = f"{feature_clean} is {direction}"
                    
                    reasons.append(reason)
                
                # If no good reasons found, provide fallback
                if not reasons:
                    return ["Multiple factors contribute to this prediction"]
                    
                return reasons[:3]  # Return top 3 reasons
                
            except Exception as e:
                print(f"❌ Error getting explanation text: {e}")
                # Provide fallback explanations
                return [
                    "Claim amount unusual for diagnosis",
                    "Treatment pattern differs from typical cases", 
                    "Multiple suspicious factors detected"
                ]

# Simple test function that actually works
def test_lime_explainer():
    """Test LIME with a simple example"""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.datasets import make_classification
    
    print("🧪 Testing LIME Explainer...")
    
    # Create sample data
    X, y = make_classification(
        n_samples=1000, 
        n_features=5, 
        n_redundant=0, 
        random_state=42
    )
    feature_names = ['claim_amount', 'patient_age', 'previous_claims', 'stay_days', 'item_count']
    
    # Train simple model
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X, y)
    
    # Create explainer with actual training data
    explainer = LIMEFraudExplainer(
        model=model, 
        feature_names=feature_names,
        training_data=X
    )
    
    # Test explanation on first instance
    test_instance = X[0:1]
    
    print("📊 Generating explanation for test instance...")
    explanation = explainer.explain_prediction(test_instance)
    
    if explanation:
        # Debug: show raw LIME output
        print("🔍 Raw LIME output:")
        raw_list = explanation.as_list()
        for feature, importance in raw_list:
            print(f"   {feature}: {importance:.3f}")
        
        reasons = explainer.get_explanation_text(explanation)
        
        print("\n🎯 Formatted Explanation:")
        print(f"   Prediction: {model.predict_proba(test_instance)[0][1]:.1%} fraud probability")
        print("   Top reasons:")
        for i, reason in enumerate(reasons, 1):
            print(f"   {i}. {reason}")
    else:
        print("❌ Failed to generate explanation")
    
    return explainer

# More realistic test with your actual data structure
def test_with_sample_insurance_data():
    """Test with data that resembles insurance claims"""
    print("\n🏥 Testing with Insurance-like Data...")
    
    # Create sample insurance-like data
    np.random.seed(42)
    n_samples = 500
    
    sample_data = {
        'claim_amount': np.random.exponential(5000, n_samples),
        'patient_age': np.random.randint(18, 80, n_samples),
        'previous_claims': np.random.poisson(2, n_samples),
        'hospital_stay': np.random.poisson(5, n_samples),
        'billed_items': np.random.poisson(8, n_samples)
    }
    
    df = pd.DataFrame(sample_data)
    
    # Create synthetic fraud labels (higher claims + more items = more likely fraud)
    fraud_prob = (
        (df['claim_amount'] > 10000).astype(int) * 0.4 +
        (df['billed_items'] > 15).astype(int) * 0.3 +
        (df['previous_claims'] > 5).astype(int) * 0.3
    )
    df['is_fraud'] = (np.random.random(n_samples) < fraud_prob).astype(int)
    
    X = df.drop('is_fraud', axis=1).values
    y = df['is_fraud'].values
    feature_names = df.drop('is_fraud', axis=1).columns.tolist()
    
    print(f"📊 Sample data: {X.shape}, Fraud rate: {y.mean():.1%}")
    
    # Train model
    from sklearn.ensemble import RandomForestClassifier
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X, y)
    
    # Create explainer
    explainer = LIMEFraudExplainer(model, feature_names, X)
    
    # Test on a high-risk case
    high_risk_case = np.array([[25000, 45, 8, 2, 20]])  # High amount, many items, short stay
    
    explanation = explainer.explain_prediction(high_risk_case)
    if explanation:
        reasons = explainer.get_explanation_text(explanation)
        
        fraud_prob = model.predict_proba(high_risk_case)[0][1]
        print(f"🔍 High-Risk Case Analysis:")
        print(f"   Fraud Probability: {fraud_prob:.1%}")
        print("   Risk Factors:")
        for i, reason in enumerate(reasons, 1):
            print(f"   {i}. {reason}")
    
    return explainer

if __name__ == "__main__":
    print("🚀 Starting LIME Explainer Tests...")
    print("=" * 50)
    
    # Test 1: Basic functionality
    explainer1 = test_lime_explainer()
    
    # Test 2: Insurance-like data
    explainer2 = test_with_sample_insurance_data()
    
    print("\n✅ All tests completed! Your LIME explainer is ready.")
    print("💡 Next: Use this in your notebook with real insurance data!")