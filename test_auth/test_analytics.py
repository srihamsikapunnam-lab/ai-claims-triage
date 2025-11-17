import requests
import time

def test_analytics():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Week 4 Analytics Endpoints")
    print("=" * 50)
    
    # Make a few predictions first to generate data
    test_claims = [
        {"patient_age": 45, "claimed_amount": 15000, "length_of_stay": 2, "gender": "Male", "diagnosis": "Fracture"},
        {"patient_age": 35, "claimed_amount": 5000, "length_of_stay": 5, "gender": "Female", "diagnosis": "Infection"},
    ]
    
    for i, claim in enumerate(test_claims, 1):
        print(f"Making prediction {i}...")
        response = requests.post(f"{base_url}/predict", json=claim)
        if response.status_code == 200:
            print(f"✅ Prediction {i} successful")
        time.sleep(1)
    
    # Test analytics endpoints
    endpoints = [
        "/analytics/",
        "/analytics/health", 
        "/analytics/predictions/summary"
    ]
    
    for endpoint in endpoints:
        print(f"\n📊 Testing {endpoint}")
        try:
            response = requests.get(f"{base_url}{endpoint}")
            if response.status_code == 200:
                print("✅ SUCCESS!")
                print(f"Response: {response.json()}")
            else:
                print(f"❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"💥 Error: {e}")

if __name__ == "__main__":
    test_analytics()