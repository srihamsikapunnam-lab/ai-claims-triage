import requests
import json

def test_app_endpoints():
    base_url = "http://localhost:5000"
    
    print("🧪 Testing App Endpoints...")
    print("=" * 50)
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Root endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
    
    # Test API info
    try:
        response = requests.get(f"{base_url}/api")
        print(f"✅ API info: {response.status_code}")
    except Exception as e:
        print(f"❌ API info failed: {e}")
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health check: {response.status_code}")
        if response.status_code == 200:
            health_data = response.json()
            print(f"   Status: {health_data.get('status')}")
            print(f"   Database: {health_data.get('database')}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test auth endpoints exist
    try:
        response = requests.get(f"{base_url}/api/auth") 
        print(f"✅ Auth base: {response.status_code}")
    except Exception as e:
        print(f"❌ Auth base failed: {e}")
    
    print("=" * 50)
    print("🎉 App setup test completed!")

if __name__ == "__main__":
    test_app_endpoints()