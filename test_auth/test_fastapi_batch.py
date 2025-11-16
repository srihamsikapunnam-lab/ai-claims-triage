import requests
import json

BASE_URL = "http://localhost:8000"

def test_fastapi_batch():
    print("🧪 Testing FastAPI Batch Processing")
    print("=" * 45)
    
    # Test data for FastAPI
    test_data = {
        "claims_data": [
            {
                "claim_id": "fastapi_test_1",
                "policy_id": "POL123",
                "claim_amount": 1500.0,
                "incident_date": "2024-01-15",
                "claim_type": "auto",
                "customer_age": 35,
                "customer_income": 75000,
                "previous_claims": 0
            },
            {
                "claim_id": "fastapi_test_2",
                "policy_id": "POL124",
                "claim_amount": 3500.0,
                "incident_date": "2024-01-16", 
                "claim_type": "property",
                "customer_age": 42,
                "customer_income": 68000,
                "previous_claims": 2
            }
        ]
    }
    
    print("1. Testing batch status:")
    try:
        response = requests.get(f"{BASE_URL}/api/batch/status")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Status endpoint working!")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
        return
    
    print("\n2. Testing batch prediction:")
    try:
        response = requests.post(
            f"{BASE_URL}/api/batch/predict",
            json=test_data
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   🎉 SUCCESS! FastAPI Batch processing working!")
            results = response.json()
            print(f"   Processed {results['processed']} claims")
            print(json.dumps(results, indent=2))
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_fastapi_batch()