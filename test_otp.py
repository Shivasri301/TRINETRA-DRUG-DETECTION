#!/usr/bin/env python3
"""
Test OTP sending and verification process
"""

import requests
import json
from database import db

def test_otp_flow():
    """Test the complete OTP flow"""
    
    base_url = "http://127.0.0.1:5001"
    session = requests.Session()
    
    print("🧪 Testing OTP Flow")
    print("=" * 50)
    
    # 1. Login first
    print("1️⃣ Logging in as testuser...")
    login_data = {
        "username": "testuser",
        "password": "testpass"
    }
    
    response = session.post(f"{base_url}/login", data=login_data)
    print(f"   Login status: {response.status_code}")
    print(f"   Final URL: {response.url}")
    
    if "link_telegram" not in response.url:
        print("   ❌ Expected redirect to link_telegram")
        return
    
    # 2. Test the authentication page
    print("\n2️⃣ Testing authentication page...")
    response = session.get(f"{base_url}/link_telegram")
    print(f"   Status: {response.status_code}")
    print(f"   Contains check button: {'checkExistingSession' in response.text}")
    print(f"   Contains phone input: {'phone_number' in response.text}")
    
    # 3. Test check existing session (should fail for testuser)
    print("\n3️⃣ Testing check existing session...")
    response = session.post(f"{base_url}/check_existing_session",
                           headers={'Content-Type': 'application/json'})
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Success: {data.get('success', False)}")
        print(f"   Message: {data.get('message', 'No message')}")
    else:
        print(f"   Error: {response.status_code}")
    
    print("\n✅ OTP flow test complete!")
    print("\n📝 Next steps:")
    print("1. Go to http://127.0.0.1:5001")
    print("2. Login with: testuser / testpass")
    print("3. You'll be redirected to Telegram authentication")
    print("4. Try 'Check for Existing Sessions' button")
    print("5. If no session found, enter your phone number and receive OTP")
    print("6. Enter the OTP code to complete authentication")

if __name__ == "__main__":
    test_otp_flow()
