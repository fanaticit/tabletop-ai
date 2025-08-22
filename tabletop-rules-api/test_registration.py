# test_registration.py - Script to test the new registration endpoint

import requests
import json

# Test data
test_user = {
    "username": "testuser123",
    "email": "test@example.com", 
    "password": "password123"
}

def test_registration():
    """Test user registration endpoint."""
    try:
        response = requests.post(
            "http://localhost:8000/api/auth/register",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Registration successful!")
            return True
        else:
            print("❌ Registration failed!")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is the FastAPI server running on port 8000?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_login(username, password):
    """Test login with the registered user."""
    try:
        login_data = {
            "username": username,
            "password": password
        }
        
        response = requests.post(
            "http://localhost:8000/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nLogin Status Code: {response.status_code}")
        print(f"Login Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            return response.json().get("access_token")
        else:
            print("❌ Login failed!")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_duplicate_registration():
    """Test registering the same user again (should fail)."""
    try:
        response = requests.post(
            "http://localhost:8000/api/auth/register",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nDuplicate Registration Status Code: {response.status_code}")
        print(f"Duplicate Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 400:
            print("✅ Duplicate registration correctly rejected!")
            return True
        else:
            print("❌ Duplicate registration should have been rejected!")
            return False
            
    except Exception as e:
        print(f"❌ Duplicate test error: {e}")
        return False

if __name__ == "__main__":
    print("Testing User Registration and Login")
    print("=" * 40)
    
    # Test registration
    if test_registration():
        # Test login
        token = test_login(test_user["username"], test_user["password"])
        
        # Test duplicate registration
        test_duplicate_registration()
        
        if token:
            print(f"\n🎉 All tests passed! Token: {token[:20]}...")
        else:
            print("\n❌ Login test failed")
    else:
        print("\n❌ Registration test failed")
    
    print("\nTo clean up, you can delete the test user from MongoDB if needed.")