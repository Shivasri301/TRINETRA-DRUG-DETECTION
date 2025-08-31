#!/usr/bin/env python3
"""
Test the complete authentication flow
"""

import requests
import time
from database import db

def test_authentication_flow():
    base_url = "http://127.0.0.1:5001"
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    print("🧪 Testing Authentication Flow")
    print("=" * 50)
    
    # 1. Test index redirect to login
    print("1️⃣ Testing index redirect...")
    response = session.get(f"{base_url}/")
    print(f"   Status: {response.status_code}")
    print(f"   Final URL: {response.url}")
    
    # 2. Test login page
    print("\n2️⃣ Testing login page...")
    response = session.get(f"{base_url}/login")
    print(f"   Status: {response.status_code}")
    print(f"   Contains login form: {'<form' in response.text}")
    
    # 3. Test login with user credentials
    print("\n3️⃣ Testing login with testuser credentials...")
    
    # First get the user from database to verify
    user = db.get_user_by_username("testuser")
    if not user:
        print("   ❌ User testuser not found!")
        return
    
    print(f"   User telegram_linked status: {user.get('telegram_linked', False)}")
    
    # Attempt login
    login_data = {
        "username": "testuser",
        "password": "testpass"
    }
    
    response = session.post(f"{base_url}/login", data=login_data)
    print(f"   Login status: {response.status_code}")
    print(f"   Final URL: {response.url}")
    
    if "login" in response.url and response.status_code == 200:
        print("   ❌ Login failed - staying on login page")
        return
    elif "link_telegram" in response.url:
        print("   ✅ Login successful, redirected to Telegram authentication!")
    elif "dashboard" in response.url:
        print("   ✅ Login successful, accessed dashboard directly!")
    
    # 4. Test dashboard access (should redirect to link_telegram if not authenticated)
    print("\n4️⃣ Testing dashboard access...")
    response = session.get(f"{base_url}/dashboard")
    print(f"   Status: {response.status_code}")
    print(f"   Final URL: {response.url}")
    
    if "link_telegram" in response.url:
        print("   ✅ Correctly redirected to Telegram authentication!")
    elif "dashboard" in response.url:
        print("   ⚠️ Allowed access to dashboard without Telegram auth")
    
    # 5. Test logout
    print("\n5️⃣ Testing logout...")
    response = session.get(f"{base_url}/logout")
    print(f"   Status: {response.status_code}")
    print(f"   Final URL: {response.url}")
    
    # 6. Verify user status after logout
    print("\n6️⃣ Verifying user status after logout...")
    user_after = db.get_user_by_username("testuser")
    print(f"   telegram_linked after logout: {user_after.get('telegram_linked', False)}")
    
    # 7. Test dashboard access after logout (should redirect to login)
    print("\n7️⃣ Testing dashboard access after logout...")
    response = session.get(f"{base_url}/dashboard")
    print(f"   Status: {response.status_code}")
    print(f"   Final URL: {response.url}")
    
    if "login" in response.url:
        print("   ✅ Correctly redirected to login!")
    else:
        print("   ❌ Should have redirected to login")

if __name__ == "__main__":
    test_authentication_flow()
