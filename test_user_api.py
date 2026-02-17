"""
Test script to verify user creation and retrieval
Run with: python test_user_api.py
"""
import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_google_login():
    """Test Google login endpoint"""
    print("\n🔐 Testing Google Login...")
    
    data = {
        "firebase_uid": "test_google_uid_123",
        "email": "test@gmail.com",
        "name": "Test User",
    }
    
    response = requests.post(f"{BASE_URL}/auth/google", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Google login successful!")
        return response.json()
    else:
        print("❌ Google login failed!")
        return None

def test_apple_login():
    """Test Apple login endpoint"""
    print("\n🍎 Testing Apple Login...")
    
    data = {
        "firebase_uid": "test_apple_uid_456",
        "email": "test@privaterelay.appleid.com",
        "name": "Apple Test User",
    }
    
    response = requests.post(f"{BASE_URL}/auth/apple", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Apple login successful!")
        return response.json()
    else:
        print("❌ Apple login failed!")
        return None

def test_duplicate_login():
    """Test logging in with same user twice (should update, not create)"""
    print("\n🔄 Testing Duplicate Login...")
    
    data = {
        "firebase_uid": "test_google_uid_123",
        "email": "test@gmail.com",
        "name": "Updated Test User",
    }
    
    response = requests.post(f"{BASE_URL}/auth/google", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ User updated successfully!")
        return response.json()
    else:
        print("❌ Update failed!")
        return None

if __name__ == "__main__":
    print("="*60)
    print("🧪 Memofarm User API Tests")
    print("="*60)
    
    try:
        # Test Google login
        google_result = test_google_login()
        
        # Test Apple login
        apple_result = test_apple_login()
        
        # Test duplicate (should update)
        duplicate_result = test_duplicate_login()
        
        print("\n" + "="*60)
        print("📊 Test Summary")
        print("="*60)
        print(f"Google Login: {'✅ PASS' if google_result else '❌ FAIL'}")
        print(f"Apple Login: {'✅ PASS' if apple_result else '❌ FAIL'}")
        print(f"Duplicate Login: {'✅ PASS' if duplicate_result else '❌ FAIL'}")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend server!")
        print("Make sure the Flask server is running on http://localhost:5000")
        print("Run: cd backend && python run.py")
