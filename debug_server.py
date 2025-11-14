import requests
import json

BASE_URL = "http://localhost:8000"

def debug_server():
    print("🔍 DEBUGGING SERVER ENDPOINTS")
    print("=" * 50)
    
    # Test different payload formats to see what works
    test_payloads = [
        ("Raw Array", [
            {"claim_id": "test1", "claim_amount": 1000}
        ]),
        ("Wrapped claims_data", {
            "claims_data": [
                {"claim_id": "test1", "claim_amount": 1000}
            ]
        }),
        ("Empty object", {}),
        ("Empty array", [])
    ]
    
    for name, payload in test_payloads:
        print(f"\nTrying: {name}")
        print(f"Payload: {json.dumps(payload)}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/batch/predict",
                json=payload,
                timeout=5
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    debug_server()