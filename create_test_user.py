#!/usr/bin/env python3
"""
Create a test user for authentication testing
"""

from database import db

def create_test_user():
    """Create a test user with known credentials"""
    
    print("👤 Creating Test User")
    print("=" * 50)
    
    # Use test credentials
    username = "testuser"
    password = "testpass"
    api_id = 12345  # Example API ID
    api_hash = "abcdef123456"  # Example API hash
    
    print(f"Creating user: {username}")
    print(f"Password: {password}")
    
    # Remove existing test user if exists
    existing = db.get_user_by_username(username)
    if existing:
        print(f"⚠️ User {username} already exists, removing first...")
        db.users.delete_one({"username": username})
    
    # Create new test user
    success, message = db.create_user(username, password, api_id, api_hash)
    
    if success:
        print(f"✅ Test user created successfully!")
        print(f"📝 User ID: {message}")
        
        # Verify the user can login
        success, user = db.verify_user(username, password)
        print(f"🔑 Login test: {'✅ SUCCESS' if success else '❌ FAILED'}")
        
        if success:
            print(f"📊 telegram_linked: {user.get('telegram_linked', False)}")
            print(f"📱 phone_number: {user.get('phone_number', 'None')}")
    else:
        print(f"❌ Failed to create test user: {message}")

if __name__ == "__main__":
    create_test_user()
