#!/usr/bin/env python3
"""
Test script for registration endpoint
Run with: python test_register.py
"""
import requests
import json
import sys
import time

BASE_URL = "http://localhost:8000"

def test_registration(username, email, password, confirm_password):
    """Test registration with provided data"""
    print(f"\n{'='*60}")
    print(f"Testing Registration")
    print(f"{'='*60}")
    print(f"Username: {username}")
    print(f"Email: {email}")
    print(f"Password: {'*' * len(password)}")
    print(f"Confirm Password: {'*' * len(confirm_password)}")
    
    # Validate inputs before sending
    errors = []
    if len(username) < 3:
        errors.append("Username must be at least 3 characters")
    if len(username) > 150:
        errors.append("Username must be at most 150 characters")
    if len(password) < 6:
        errors.append("Password must be at least 6 characters")
    if password != confirm_password:
        errors.append("Passwords do not match")
    if "@" not in email or "." not in email:
        errors.append("Invalid email format")
    
    if errors:
        print(f"\n⚠️  VALIDATION ERRORS (before sending request):")
        for error in errors:
            print(f"   - {error}")
        return False
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/users/register/",
            json={
                "username": username,
                "email": email,
                "password": password,
                "confirm_password": confirm_password
            },
            timeout=5
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 201:
            data = response.json()
            print(f"\n✅ REGISTRATION SUCCESSFUL!")
            print(f"   User ID: {data.get('user_id')}")
            print(f"   Username: {data.get('username')}")
            print(f"   Email: {data.get('email')}")
            print(f"\n   You can now login with these credentials:")
            print(f"   Email: {data.get('email')}")
            print(f"   Password: {'*' * len(password)}")
            return True
        
        elif response.status_code == 400:
            print(f"\n❌ VALIDATION ERROR")
            detail = response.json().get('detail', 'Unknown error')
            print(f"   {detail}")
            return False
        
        else:
            print(f"\n❌ UNEXPECTED ERROR")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ CONNECTION ERROR")
        print(f"   Could not connect to {BASE_URL}")
        print(f"   Make sure the server is running: uvicorn main:app --reload")
        return False
    
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False


if __name__ == "__main__":
    # Generate unique credentials for testing
    timestamp = int(time.time())
    
    test_username = f"testuser{timestamp}"
    test_email = f"testuser{timestamp}@example.com"
    test_password = "SecurePassword123"
    test_confirm = "SecurePassword123"
    
    print(f"\n🧪 Testing FastAPI Registration Endpoint")
    print(f"📍 Server: {BASE_URL}")
    
    success = test_registration(
        test_username,
        test_email,
        test_password,
        test_confirm
    )
    
    if success:
        print(f"\n💡 NEXT STEPS:")
        print(f"   1. Use the credentials above to login")
        print(f"   2. Or modify test_login.py with:")
        print(f"      - Email: {test_email}")
        print(f"      - Password: {test_password}")
        print(f"   3. Then run: python test_login.py")
    else:
        print(f"\n💡 TIPS:")
        print(f"   1. Check if the server is running")
        print(f"   2. Verify all required fields are provided")
        print(f"   3. Make sure passwords match")
        print(f"   4. Check the server logs for detailed error messages")
    
    sys.exit(0 if success else 1)
