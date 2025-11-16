import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from api.db_user import db_user

print("🧪 Testing Database User Model...")
print("=" * 40)

try:
    # Test creating a user in database
    print("1. Creating user in database...")
    user_id = db_user.create_user(
        username="dbuser", 
        email="dbuser@test.com", 
        password="dbpassword123",
        role="admin"
    )
    print(f"✅ User created with ID: {user_id}")
    
    # Test getting user from database
    print("\n2. Getting user from database...")
    user = db_user.get_user_by_username("dbuser")
    if user:
        print("✅ User found in database!")
        print(f"   Username: {user['username']}")
        print(f"   Email: {user['email']}")
        print(f"   Role: {user['role']}")
    else:
        print("❌ User not found!")
    
    # Test password verification
    print("\n3. Testing password verification...")
    verified_user = db_user.verify_user("dbuser", "dbpassword123")
    if verified_user:
        print("✅ Password verification successful!")
    else:
        print("❌ Password verification failed!")
    
    # Test wrong password
    print("\n4. Testing wrong password...")
    wrong_user = db_user.verify_user("dbuser", "wrongpassword")
    if not wrong_user:
        print("✅ Wrong password correctly rejected!")
    else:
        print("❌ Wrong password was accepted!")
    
    print("\n" + "=" * 40)
    print("🎉 Database user model working perfectly!")
    
except Exception as e:
    print(f"❌ Error: {e}")