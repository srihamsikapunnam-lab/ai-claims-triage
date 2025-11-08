import requests
import json

def test_final():
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
    
    base_url = "http://localhost:8000"
    
    # Test health endpoint first
    try:
        health_response = requests.get(f"{base_url}/health")
        print("🔍 Health check:", health_response.json())
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test predictions
    for i, claim_data in enumerate(test_claims, 1):
        print(f"\n" + "="*50)
        print(f"🧪 TESTING CLAIM {i}:")
        print(f"📥 Input: {claim_data}")
        
        try:
            response = requests.post(f"{base_url}/predict", json=claim_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                print("🎉 SUCCESS! REAL MODEL WORKING!")
                print(f"   Model: {result.get('model_version', 'Unknown')}")
                print(f"   Prediction: {result['prediction']}")
                print(f"   Probability: {result['probability']:.4f}")
                print(f"   Risk Score: {result['risk_score']}/100")
                print(f"   Category: {result['risk_category']}")
                print(f"   Status: {result['status']}")
                print("   Explanations:")
                for exp in result['explanation']:
                    print(f"     • {exp}")
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    print("🚀 STARTING FINAL INTEGRATION TEST")
    print("This should show REAL RandomForest predictions!")
    test_final()