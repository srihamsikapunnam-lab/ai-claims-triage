import sys
import os

# Add the src directory to the Python path so we can import our module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from policy_management import PolicyManager

def test_policy_management():
    """Test the complete policy management system."""
    print("=== Testing Policy Management System ===\n")
    
    # Create manager instance
    manager = PolicyManager()
    
    # Clear any existing policies
    manager.clear_policies()
    
    # Test 1: Add policies
    print("1. Adding sample policies...")
    manager.add_policy("Sharing credit card information is prohibited", "privacy")
    manager.add_policy("Medical diagnosis without license is forbidden", "medical")
    manager.add_policy("Hate speech is not allowed", "content")
    manager.add_policy("Commercial promotion requires disclosure", "commercial")
    print("   Sample policies added successfully!\n")
    
    # Test 2: Test evaluation
    print("2. Testing policy evaluation...")
    test_cases = [
        ("I want to share my credit card number", "privacy"),
        ("I can diagnose your illness", "medical"),
        ("This product is amazing buy now", "commercial"),
        ("Hello how are you", "content")  # Should not violate
    ]
    
    for user_input, category in test_cases:
        result = manager.evaluate(user_input, category)
        print(f"   Input: '{user_input}'")
        print(f"   Category: {category}")
        print(f"   Violations: {result['violation_count']}")
        print(f"   Details: {result}\n")
    
    # Test 3: Test analysis across all categories
    print("3. Testing comprehensive analysis...")
    analysis = manager.analyze("I can diagnose illness and share credit card info")
    print(f"   Overall violations: {analysis['overall_violations']}")
    print(f"   Categories checked: {analysis['categories_checked']}\n")
    
    # Test 4: Export policies
    print("4. Testing export functionality...")
    manager.export_policies("test_policies.json")
    print("   Policies exported to test_policies.json\n")
    
    # Test 5: Import policies
    print("5. Testing import functionality...")
    manager.import_policies("test_policies.json")
    print("   Policies imported successfully!\n")
    
    # Test 6: List all policies
    print("6. Current policies in system:")
    policies = manager.list_policies()
    for i, policy in enumerate(policies, 1):
        print(f"   {i}. {policy}")
    
    print("\n=== All tests completed successfully! ===")

if __name__ == "__main__":
    test_policy_management()