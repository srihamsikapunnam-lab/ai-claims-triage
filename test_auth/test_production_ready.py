import requests
import json
import time

def test_production_ready():
    # Test data with EXACT features needed by the model
    test_claims = [
        {
            "patient_age": 45,
            "claimed_amount": 15000,
            "length_of_stay": 2,
            "gender": "Male",
            "diagnosis": "Fracture"
        },
        {
            "patient_age": 35,
            "claimed_amount": 5000,
            "length_of_stay": 5,
            "gender": "Female", 
            "diagnosis": "Infection"
        },
        {
            "patient_age": 28,
            "claimed_amount": 25000,
            "length_of_stay": 1,
            "gender": "Male",
            "diagnosis": "Appendicitis"
        }
    ]
    
    url = "http://localhost:5000/predict"
    
    for i, claim_data in enumerate(test_claims, 1):
        print(f"\n🧪 Testing Claim {i}:")
        print(f"📥 Sending: {claim_data}")
        
        try:
            response = requests.post(url, json=claim_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ REAL MODEL PREDICTION SUCCESSFUL!")
                print(f"   Model: {result.get('model_version', 'Unknown')}")
                print(f"   Prediction: {result['prediction']}")
                print(f"   Probability: {result['probability']}")
                print(f"   Risk Score: {result['risk_score']}")
                print(f"   Category: {result['risk_category']}")
                print(f"   Status: {result['status']}")
                print("   Explanations:")
                for exp in result['explanation']:
                    print(f"     - {exp}")
            else:
                print(f"❌ Prediction failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
        
        time.sleep(1)

if __name__ == "__main__":
    test_production_ready()