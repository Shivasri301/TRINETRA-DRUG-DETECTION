#!/usr/bin/env python3
"""
Test script to reset user authentication status and clean up session files
"""

import os
import glob
from database import db

def reset_user_auth(username):
    """Reset user's Telegram authentication status"""
    
    print(f"🔄 Resetting authentication for user: {username}")
    
    # Get user first to check if exists
    user = db.get_user_by_username(username)
    if not user:
        print(f"❌ User {username} not found")
        return False
    
    print(f"📊 Current user status: telegram_linked = {user.get('telegram_linked', False)}")
    
    # Reset database status
    result = db.users.update_one(
        {"username": username},
        {"$set": {"telegram_linked": False, "phone_number": None}}
    )
    
    print(f"📝 Database update: {result.modified_count} documents modified")
    
    # Clean up session files
    current_dir = os.getcwd()
    session_patterns = [
        f"temp_{username}.session",
        f"auth_{username}.session", 
        f"monitor_session_{username}.session",
        f"real_session_{username}.session",
        "authenticated_session.session"
    ]
    
    files_removed = 0
    for pattern in session_patterns:
        # Check in current directory
        full_path = os.path.join(current_dir, pattern)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
                print(f"🗑️ Removed: {full_path}")
                files_removed += 1
            except Exception as e:
                print(f"❌ Failed to remove {full_path}: {e}")
        
        # Also check with glob
        for session_file in glob.glob(pattern):
            try:
                os.remove(session_file)
                print(f"🗑️ Removed: {session_file}")
                files_removed += 1
            except Exception as e:
                print(f"❌ Failed to remove {session_file}: {e}")
    
    print(f"✅ Authentication reset complete! Removed {files_removed} session files")
    
    # Verify the reset
    user_after = db.get_user_by_username(username)
    print(f"📊 Final user status: telegram_linked = {user_after.get('telegram_linked', False)}")
    
    return True

def list_all_users():
    """List all users in the database"""
    print("👥 All users in database:")
    users = list(db.users.find({}, {"username": 1, "telegram_linked": 1, "phone_number": 1}))
    for user in users:
        print(f"  - {user['username']}: telegram_linked = {user.get('telegram_linked', False)}, phone = {user.get('phone_number', 'None')}")
    return users

if __name__ == "__main__":
    print("🔧 Authentication Reset Tool")
    print("=" * 50)
    
    # List all users first
    users = list_all_users()
    
    if not users:
        print("❌ No users found in database")
        exit(1)
    
    print("\n" + "=" * 50)
    username = input("Enter username to reset (or 'all' to reset all users): ").strip()
    
    if username.lower() == 'all':
        for user in users:
            reset_user_auth(user['username'])
            print()
    elif username:
        reset_user_auth(username)
    else:
        print("❌ No username provided")
