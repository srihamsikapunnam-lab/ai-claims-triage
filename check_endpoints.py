import requests

BASE_URL = "http://localhost:8000"

def check_endpoints():
    print("🔍 Checking what endpoints are available...")
    print("=" * 50)
    
    endpoints = [
        "/batch/status",
        "/batch/predict",
    ]
    
    for endpoint in endpoints:
        try:
            if "predict" in endpoint:
                # Try POST request
                response = requests.post(f"{BASE_URL}{endpoint}", json=[], timeout=2)
                method = "POST"
            else:
                # Try GET request  
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=2)
                method = "GET"
            
            print(f"✅ {method} {endpoint}: Status {response.status_code}")
            
        except Exception as e:
            print(f"❌ {endpoint}: ERROR - {e}")

if __name__ == "__main__":
    check_endpoints()