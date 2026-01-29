#!/usr/bin/env python3
"""
Automated Backend Tests for Chatbot API
Tests all endpoints on localhost:8001
"""

import requests
import json
from typing import Dict, Tuple
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8001"
HEADERS = {"Content-Type": "application/json"}

# Test Results
results = []

def log_test(test_id: str, name: str, passed: bool, details: str = ""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} | {test_id}: {name}")
    if details:
        print(f"       {details}")
    results.append({
        "id": test_id,
        "name": name,
        "passed": passed,
        "details": details
    })

def test_server_health() -> bool:
    """Test 1: Server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        passed = response.status_code == 200
        details = f"Status: {response.status_code}"
        log_test("BACKEND-002", "Health Check Endpoint", passed, details)
        return passed
    except Exception as e:
        log_test("BACKEND-002", "Health Check Endpoint", False, f"Error: {str(e)}")
        return False

def test_root_endpoint() -> bool:
    """Test 2: Root endpoint returns API info"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=2)
        passed = response.status_code == 200 and "service" in response.json()
        details = f"Status: {response.status_code}"
        log_test("BACKEND-003", "Root Endpoint", passed, details)
        return passed
    except Exception as e:
        log_test("BACKEND-003", "Root Endpoint", False, f"Error: {str(e)}")
        return False

def test_greeting():
    """Test 3: Greeting response"""
    test_cases = [
        ("hello", "Hello! I can help with claims processing."),
        ("hi", "Hello! I can help with claims processing."),
        ("greetings", "Hello! I can help with claims processing."),
    ]
    
    for message, expected_reply in test_cases:
        try:
            payload = {"message": message}
            response = requests.post(f"{BASE_URL}/chat", json=payload, headers=HEADERS, timeout=2)
            data = response.json()
            
            # Check if response contains expected text
            reply = data.get("reply", "")
            passed = response.status_code == 200 and expected_reply in reply
            
            details = f"Message: '{message}' → '{reply}'"
            log_test(f"BACKEND-004", f"Greeting - '{message}'", passed, details)
        except Exception as e:
            log_test(f"BACKEND-004", f"Greeting - '{message}'", False, f"Error: {str(e)}")

def test_claim_status():
    """Test 4: Claim status response"""
    test_cases = [
        ("status", "Check your dashboard"),
        ("claim status", "Check your dashboard"),
        ("where is my claim", "Check your dashboard"),
    ]
    
    for message, expected_reply in test_cases:
        try:
            payload = {"message": message}
            response = requests.post(f"{BASE_URL}/chat", json=payload, headers=HEADERS, timeout=2)
            data = response.json()
            
            reply = data.get("reply", "")
            passed = response.status_code == 200 and expected_reply in reply
            
            details = f"Message: '{message}' → Contains: '{expected_reply}'"
            log_test(f"BACKEND-005", f"Claim Status - '{message}'", passed, details)
        except Exception as e:
            log_test(f"BACKEND-005", f"Claim Status - '{message}'", False, f"Error: {str(e)}")

def test_fraud_detection():
    """Test 5: Fraud detection response"""
    test_cases = [
        ("fraud", "Our AI system detects"),
        ("suspicious", "Our AI system detects"),
        ("fraud detection", "Our AI system detects"),
    ]
    
    for message, expected_reply in test_cases:
        try:
            payload = {"message": message}
            response = requests.post(f"{BASE_URL}/chat", json=payload, headers=HEADERS, timeout=2)
            data = response.json()
            
            reply = data.get("reply", "")
            passed = response.status_code == 200 and expected_reply in reply
            
            details = f"Message: '{message}' → Contains: '{expected_reply}'"
            log_test(f"BACKEND-006", f"Fraud Detection - '{message}'", passed, details)
        except Exception as e:
            log_test(f"BACKEND-006", f"Fraud Detection - '{message}'", False, f"Error: {str(e)}")

def test_claim_submission():
    """Test 6: Claim submission response"""
    test_cases = [
        ("submit", "Submit claims via"),
        ("new claim", "Submit claims via"),
        ("submit claim", "Submit claims via"),
    ]
    
    for message, expected_reply in test_cases:
        try:
            payload = {"message": message}
            response = requests.post(f"{BASE_URL}/chat", json=payload, headers=HEADERS, timeout=2)
            data = response.json()
            
            reply = data.get("reply", "")
            passed = response.status_code == 200 and expected_reply in reply
            
            details = f"Message: '{message}' → Contains: '{expected_reply}'"
            log_test(f"BACKEND-007", f"Claim Submission - '{message}'", passed, details)
        except Exception as e:
            log_test(f"BACKEND-007", f"Claim Submission - '{message}'", False, f"Error: {str(e)}")

def test_default_response():
    """Test 7: Default response for unmatched queries"""
    try:
        payload = {"message": "random unrelated question about pizza"}
        response = requests.post(f"{BASE_URL}/chat", json=payload, headers=HEADERS, timeout=2)
        data = response.json()
        
        reply = data.get("reply", "")
        passed = response.status_code == 200 and "help" in reply.lower()
        
        details = f"Response: '{reply}'"
        log_test("BACKEND-008", "Default Response", passed, details)
    except Exception as e:
        log_test("BACKEND-008", "Default Response", False, f"Error: {str(e)}")

def test_empty_message():
    """Test 8: Empty message handling"""
    try:
        payload = {"message": ""}
        response = requests.post(f"{BASE_URL}/chat", json=payload, headers=HEADERS, timeout=2)
        data = response.json()
        
        # Should still return a response (backend validates at frontend level)
        passed = response.status_code == 200
        
        reply = data.get("reply", "")
        details = f"Status: {response.status_code}, Reply: '{reply}'"
        log_test("BACKEND-010", "Empty Message", passed, details)
    except Exception as e:
        log_test("BACKEND-010", "Empty Message", False, f"Error: {str(e)}")

def test_missing_field():
    """Test 9: Missing message field"""
    try:
        payload = {"model": "test"}
        response = requests.post(f"{BASE_URL}/chat", json=payload, headers=HEADERS, timeout=2)
        
        # Should return 422 (validation error)
        passed = response.status_code == 422
        
        details = f"Status: {response.status_code} (expected 422)"
        log_test("BACKEND-012", "Missing Message Field", passed, details)
    except Exception as e:
        log_test("BACKEND-012", "Missing Message Field", False, f"Error: {str(e)}")

def test_cors_headers():
    """Test 10: CORS headers"""
    try:
        response = requests.options(f"{BASE_URL}/chat", headers={
            "Origin": "http://localhost:3000"
        }, timeout=2)
        
        cors_headers = {
            "access-control-allow-origin": response.headers.get("access-control-allow-origin"),
            "access-control-allow-methods": response.headers.get("access-control-allow-methods"),
        }
        
        passed = "localhost:3000" in (cors_headers.get("access-control-allow-origin") or "")
        
        details = f"Origin header: {cors_headers['access-control-allow-origin']}"
        log_test("BACKEND-009", "CORS Headers", passed, details)
    except Exception as e:
        log_test("BACKEND-009", "CORS Headers", False, f"Error: {str(e)}")

def test_response_format():
    """Test: Response format validation"""
    try:
        payload = {"message": "hello"}
        response = requests.post(f"{BASE_URL}/chat", json=payload, headers=HEADERS, timeout=2)
        data = response.json()
        
        # Verify response has required field
        has_reply = "reply" in data
        
        details = f"Response keys: {list(data.keys())}"
        log_test("BACKEND-011", "Response Format", has_reply, details)
    except Exception as e:
        log_test("BACKEND-011", "Response Format", False, f"Error: {str(e)}")

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 CHATBOT BACKEND AUTOMATED TEST SUITE")
    print("=" * 60)
    print(f"Target: {BASE_URL}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    # Run tests
    test_server_health()
    test_root_endpoint()
    test_greeting()
    test_claim_status()
    test_fraud_detection()
    test_claim_submission()
    test_default_response()
    test_empty_message()
    test_missing_field()
    test_cors_headers()
    test_response_format()
    
    # Summary
    print()
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    
    print()
    print("Detailed Results:")
    for result in results:
        status = "✅" if result["passed"] else "❌"
        print(f"{status} {result['id']}: {result['name']}")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()
