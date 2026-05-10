#!/usr/bin/env python3
"""
Test script for login endpoint
Run with: python test_login.py
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_login(email, password):
    """Test login with provided credentials"""
    print(f"\n{'='*60}")
    print(f"Testing Login")
    print(f"{'='*60}")
    print(f"Email: {email}")
    print(f"Password: {'*' * len(password)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/users/login/",
            json={
                "email": email,
                "password": password
            },
            timeout=5
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ LOGIN SUCCESSFUL!")
            print(f"   Access Token: {data.get('access_token')[:30]}...")
            print(f"   Token Type: {data.get('token_type')}")
            print(f"   Expires In: {data.get('expires_in')} seconds")
            return True
        
        elif response.status_code == 401:
            print(f"\n❌ INVALID CREDENTIALS")
            print(f"   Make sure email and password are correct")
            return False
        
        elif response.status_code == 404:
            print(f"\n❌ USER NOT FOUND")
            print(f"   The email '{email}' does not exist in the database")
            print(f"   Try registering a new account first")
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
    # Test with actual user from database
    # CHANGE THESE VALUES TO TEST!
    test_email = "abc@test.com"      # Change to existing user email
    test_password = "password123"    # Change to that user's password
    
    print(f"\n🧪 Testing FastAPI Login Endpoint")
    print(f"📍 Server: {BASE_URL}")
    
    success = test_login(test_email, test_password)
    
    if not success:
        print(f"\n💡 TIPS:")
        print(f"   1. Check if the server is running (look for 'Uvicorn running on' message)")
        print(f"   2. Verify the email exists in the Django database")
        print(f"   3. Make sure you're using the correct password")
        print(f"   4. Check the server logs for detailed error messages")
    
    sys.exit(0 if success else 1)
