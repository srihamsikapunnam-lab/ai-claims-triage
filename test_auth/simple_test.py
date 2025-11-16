import requests
import json

BASE_URL = "http://localhost:8000"

def simple_test():
    print("🧪 SIMPLE TEST")
    
    # Test data
    payload = {
        "claims_data": [
            {"claim_id": "test1", "amount": 1000},
            {"claim_id": "test2", "amount": 2000}
        ]
    }
    
    print("Sending:", json.dumps(payload))
    
    response = requests.post(f"{BASE_URL}/batch/predict", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    simple_test()