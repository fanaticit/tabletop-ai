#!/usr/bin/env python3
"""
Test script for Tabletop Rules API endpoints
Run this after the server is started to verify everything works.
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"

def test_endpoint(method, endpoint, data=None, headers=None, description=""):
    """Test an API endpoint and return the result."""
    url = f"{API_BASE}{endpoint}"
    
    print(f"\n🔍 Testing: {description or endpoint}")
    print(f"   {method.upper()} {endpoint}")
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            response = requests.request(method, url, json=data, headers=headers)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code < 400:
            print("   ✅ SUCCESS")
            try:
                result = response.json()
                if len(str(result)) < 200:
                    print(f"   Response: {json.dumps(result, indent=2)}")
                else:
                    print(f"   Response: {str(result)[:100]}...")
                return True, result
            except:
                print(f"   Response: {response.text[:100]}...")
                return True, response.text
        else:
            print("   ❌ FAILED")
            try:
                error = response.json()
                print(f"   Error: {error}")
            except:
                print(f"   Error: {response.text}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print("   ❌ FAILED - Cannot connect to server")
        print("   Make sure the server is running: uvicorn main:app --reload")
        return False, None
    except Exception as e:
        print(f"   ❌ FAILED - {e}")
        return False, None

def main():
    """Run all API tests."""
    print("🧪 Tabletop Rules API Endpoint Tests")
    print("=" * 50)
    print("Make sure the server is running on http://localhost:8000")
    print("Start with: uvicorn main:app --reload")
    print()
    
    # Track test results
    passed = 0
    total = 0
    
    # Test basic endpoints
    tests = [
        ("GET", "/", None, None, "Root endpoint"),
        ("GET", "/health", None, None, "Health check"),
        ("GET", "/test", None, None, "Test endpoint"),
    ]
    
    for method, endpoint, data, headers, desc in tests:
        total += 1
        success, _ = test_endpoint(method, endpoint, data, headers, desc)
        if success:
            passed += 1
    
    # Test authentication
    print("\n" + "="*30 + " AUTHENTICATION TESTS " + "="*30)
    
    # Test admin login
    total += 1
    admin_token = None
    success, result = test_endpoint(
        "POST", "/token", 
        None,  # Form data, not JSON
        {"Content-Type": "application/x-www-form-urlencoded"},
        "Admin login (token endpoint)"
    )
    
    if success:
        passed += 1
        if result and 'access_token' in result:
            admin_token = result['access_token']
            print(f"   🔑 Admin token obtained: {admin_token[:20]}...")
    else:
        # Try with form data manually
        try:
            response = requests.post(
                f"{API_BASE}/token",
                data={"username": "admin", "password": "secret"},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            if response.status_code == 200:
                result = response.json()
                admin_token = result['access_token']
                print(f"   ✅ Admin token obtained: {admin_token[:20]}...")
                passed += 1
        except:
            pass
    
    # Test user registration
    total += 1
    test_user = {
        "username": f"testuser_{int(time.time())}",
        "email": f"test_{int(time.time())}@example.com",
        "password": "password123"
    }
    
    success, result = test_endpoint(
        "POST", "/api/auth/register",
        test_user, None,
        "User registration"
    )
    if success:
        passed += 1
    
    # Test user login
    if success:
        total += 1
        login_data = {
            "username": test_user["username"],
            "password": test_user["password"]
        }
        success, result = test_endpoint(
            "POST", "/api/auth/login",
            login_data, None,
            "User login"
        )
        if success:
            passed += 1
    
    # Test games endpoints
    print("\n" + "="*30 + " GAMES ENDPOINTS " + "="*30)
    
    games_tests = [
        ("GET", "/api/games/", None, None, "List games"),
    ]
    
    for method, endpoint, data, headers, desc in games_tests:
        total += 1
        success, _ = test_endpoint(method, endpoint, data, headers, desc)
        if success:
            passed += 1
    
    # Test admin endpoints (if we have admin token)
    if admin_token:
        print("\n" + "="*30 + " ADMIN ENDPOINTS " + "="*30)
        
        auth_headers = {"Authorization": f"Bearer {admin_token}"}
        
        admin_tests = [
            ("GET", "/api/admin/test", None, auth_headers, "Admin auth test"),
            ("GET", "/api/admin/games/registered", None, auth_headers, "List registered games (admin)"),
        ]
        
        for method, endpoint, data, headers, desc in admin_tests:
            total += 1
            success, _ = test_endpoint(method, endpoint, data, headers, desc)
            if success:
                passed += 1
    
    # Test chat endpoints
    print("\n" + "="*30 + " CHAT ENDPOINTS " + "="*30)
    
    chat_tests = [
        ("GET", "/api/chat/search/chess?q=pawn", None, None, "Keyword search"),
    ]
    
    for method, endpoint, data, headers, desc in chat_tests:
        total += 1
        success, _ = test_endpoint(method, endpoint, data, headers, desc)
        if success:
            passed += 1
    
    # Final results
    print("\n" + "="*70)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your API is working correctly.")
        print("\n📚 Next steps:")
        print("1. Visit http://localhost:8000/docs for interactive API documentation")
        print("2. Upload some game rules using the admin endpoints")
        print("3. Test the frontend application")
    else:
        print("⚠️  Some tests failed. Check the server logs for more details.")
        print(f"   Success rate: {(passed/total)*100:.1f}%")
    
    print("\n🔗 Useful URLs:")
    print("- API Docs: http://localhost:8000/docs")
    print("- Health Check: http://localhost:8000/health")
    print("- Admin Panel: Upload files via /docs admin endpoints")

if __name__ == "__main__":
    main()