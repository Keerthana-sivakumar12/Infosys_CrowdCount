"""
API Testing Script for CrowdCount System
Tests all endpoints and authentication
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_home():
    print_section("Testing Home Endpoint")
    response = requests.get(f"{API_BASE}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_login(username, password):
    print_section(f"Testing Login - {username}")
    response = requests.post(
        f"{API_BASE}/login",
        json={"username": username, "password": password}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Login successful!")
        print(f"Role: {data['role']}")
        print(f"Token: {data['access_token'][:50]}...")
        return data['access_token']
    else:
        print(f"❌ Login failed: {response.json()}")
        return None

def test_get_count():
    print_section("Testing Get Count (Public)")
    response = requests.get(f"{API_BASE}/get_count")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total People: {data.get('total_people', 0)}")
        print(f"Zones: {json.dumps(data.get('zones', {}), indent=2)}")
    return response.status_code == 200

def test_protected_endpoint(endpoint, token, method="GET"):
    print_section(f"Testing {endpoint} (Protected)")
    headers = {"Authorization": f"Bearer {token}"}
    
    if method == "GET":
        response = requests.get(f"{API_BASE}{endpoint}", headers=headers)
    else:
        response = requests.post(f"{API_BASE}{endpoint}", headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Access granted")
        if endpoint == "/thresholds":
            print(f"Thresholds: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"❌ Access denied or error")
    
    return response.status_code == 200

def test_admin_endpoint(token):
    print_section("Testing Set Threshold (Admin Only)")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{API_BASE}/set_threshold?zone_name=TestZone&max_capacity=50",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Threshold set successfully")
        print(f"Response: {response.json()}")
    elif response.status_code == 403:
        print(f"❌ Forbidden - Admin access required")
    else:
        print(f"❌ Error: {response.json()}")
    
    return response.status_code == 200

def run_all_tests():
    print("\n" + "🚀 CrowdCount API Testing Suite".center(60))
    print("="*60)
    
    results = {
        "passed": 0,
        "failed": 0
    }
    
    # Test 1: Home endpoint
    if test_home():
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    time.sleep(0.5)
    
    # Test 2: Public endpoint
    if test_get_count():
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    time.sleep(0.5)
    
    # Test 3: Admin login
    admin_token = test_login("admin", "admin123")
    if admin_token:
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    time.sleep(0.5)
    
    # Test 4: User login
    user_token = test_login("user", "user123")
    if user_token:
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    time.sleep(0.5)
    
    # Test 5: Protected endpoint with admin token
    if admin_token and test_protected_endpoint("/thresholds", admin_token):
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    time.sleep(0.5)
    
    # Test 6: Admin-only endpoint with admin token
    if admin_token and test_admin_endpoint(admin_token):
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    time.sleep(0.5)
    
    # Test 7: Admin-only endpoint with user token (should fail)
    print_section("Testing Admin Endpoint with User Token (Should Fail)")
    if user_token:
        headers = {"Authorization": f"Bearer {user_token}"}
        response = requests.post(
            f"{API_BASE}/set_threshold?zone_name=TestZone&max_capacity=50",
            headers=headers
        )
        if response.status_code == 403:
            print("✅ Correctly denied - RBAC working!")
            results["passed"] += 1
        else:
            print("❌ Security issue - User should not have admin access!")
            results["failed"] += 1
    else:
        results["failed"] += 1
    
    # Summary
    print_section("Test Summary")
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"Total: {results['passed'] + results['failed']}")
    
    if results['failed'] == 0:
        print("\n🎉 All tests passed! System is working perfectly!")
    else:
        print(f"\n⚠️ {results['failed']} test(s) failed. Check backend logs.")
    
    print("="*60)

if __name__ == "__main__":
    try:
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API!")
        print("Make sure the backend is running: python main.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
