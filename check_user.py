#!/usr/bin/env python3
"""
Check user credentials in database
"""

from database import db
import bcrypt

def check_user_credentials():
    """Check user credentials and try different passwords"""
    
    print("🔍 Checking User Credentials")
    print("=" * 50)
    
    # List all users
    users = list(db.users.find({}, {"username": 1, "telegram_linked": 1}))
    print("👥 Users in database:")
    for user in users:
        print(f"  - {user['username']}: telegram_linked = {user.get('telegram_linked', False)}")
    
    print("\n" + "=" * 50)
    username = input("Enter username to test: ").strip()
    
    user = db.get_user_by_username(username)
    if not user:
        print(f"❌ User {username} not found")
        return
    
    print(f"✅ User found: {username}")
    print(f"📊 telegram_linked: {user.get('telegram_linked', False)}")
    print(f"📱 phone_number: {user.get('phone_number', 'None')}")
    
    # Test different passwords
    test_passwords = ["123", "password", "admin", username, username.lower()]
    
    print(f"\n🔑 Testing common passwords for {username}:")
    for password in test_passwords:
        try:
            success, _ = db.verify_user(username, password)
            print(f"  - '{password}': {'✅ WORKS' if success else '❌ Failed'}")
            if success:
                break
        except Exception as e:
            print(f"  - '{password}': ❌ Error - {e}")

if __name__ == "__main__":
    check_user_credentials()
