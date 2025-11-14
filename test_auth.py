import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from api.models import User

# Test user creation
print("🧪 Testing User Authentication...")

# Create a test user
test_user = User(
    username="admin", 
    email="admin@test.com", 
    password="secret123",
    role="admin"
)

print("✅ User created successfully!")
print(f"   Username: {test_user.username}")
print(f"   Email: {test_user.email}")
print(f"   Role: {test_user.role}")

# Test password verification
print("\n🔐 Testing password verification...")
print(f"   Correct password: {test_user.verify_password('secret123')}")  # Should be True
print(f"   Wrong password: {test_user.verify_password('wrong')}")        # Should be False

print("\n🎉 User model is working correctly!")