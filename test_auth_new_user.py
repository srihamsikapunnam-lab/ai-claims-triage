import requests
import json
import random

def test_new_user():
    base_url = "http://localhost:8000"
    
    # Generate random username to avoid duplicates
    random_id = random.randint(1000, 9999)
    username = f"newuser{random_id}"
    
    print("🧪 Testing NEW User Registration & Login")
    print("=" * 50)
    
    # Test registration with NEW user
    print(f"\n1. 📝 Registering NEW user: {username}...")
    reg_data = {
        "username": username,
        "password": "newpass123", 
        "email": f"{username}@example.com",
        "role": "user"
    }
    
    response = requests.post(f"{base_url}/auth/register", json=reg_data)
    
    if response.status_code == 200:
        print("✅ NEW USER REGISTRATION SUCCESS!")
        print(json.dumps(response.json(), indent=2))
    else:
        print("❌ Registration failed!")
        print(f"Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return
    
    # Test login with NEW user
    print(f"\n2. 🔑 Logging in NEW user: {username}...")
    login_data = {
        "username": username,
        "password": "newpass123"
    }
    
    response = requests.post(f"{base_url}/auth/login", json=login_data)
    
    if response.status_code == 200:
        print("✅ NEW USER LOGIN SUCCESS!")
        result = response.json()
        print(json.dumps(result, indent=2))
        
        token = result.get('token')
        if token:
            print(f"\n🎫 Your NEW token: {token}")
            
    else:
        print("❌ Login failed!")
        print(f"Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    
    print("\n" + "=" * 50)
    print("🎉 NEW user test completed!")

if __name__ == "__main__":
    test_new_user()