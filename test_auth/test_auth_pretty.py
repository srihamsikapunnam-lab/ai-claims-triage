import requests
import json

def test_auth():
    base_url = "http://localhost:8000"
    
    print("🔐 Testing Authentication System")
    print("=" * 50)
    
    # Test registration
    print("\n1. 📝 Testing USER REGISTRATION...")
    reg_data = {
        "username": "prettyuser",
        "password": "prettypass123", 
        "email": "pretty@example.com"
    }
    
    response = requests.post(f"{base_url}/auth/register", json=reg_data)
    
    if response.status_code == 200:
        print("✅ REGISTRATION SUCCESS!")
        print(json.dumps(response.json(), indent=2))
    else:
        print("❌ REGISTRATION FAILED!")
        print(f"Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    
    # Test login
    print("\n2. 🔑 Testing USER LOGIN...")
    login_data = {
        "username": "prettyuser",
        "password": "prettypass123"
    }
    
    response = requests.post(f"{base_url}/auth/login", json=login_data)
    
    if response.status_code == 200:
        print("✅ LOGIN SUCCESS!")
        result = response.json()
        print(json.dumps(result, indent=2))
        
        # Save the token for later use
        token = result.get('token')
        if token:
            print(f"\n🎫 Your token: {token}")
            
    else:
        print("❌ LOGIN FAILED!")
        print(f"Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    
    print("\n" + "=" * 50)
    print("🎉 Authentication test completed!")

if __name__ == "__main__":
    test_auth()