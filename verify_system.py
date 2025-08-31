#!/usr/bin/env python3
"""
Complete system verification for Telegram Drug Monitor
Checks all components are working correctly
"""

import os
import sys
from dotenv import load_dotenv

def check_environment():
    """Check environment configuration"""
    print("🔧 Checking environment configuration...")
    
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        return False
    
    load_dotenv()
    
    required_vars = ['MONGODB_URI', 'SECRET_KEY', 'DATABASE_NAME']
    for var in required_vars:
        if not os.getenv(var):
            print(f"❌ Missing environment variable: {var}")
            return False
    
    print("✅ Environment configuration OK")
    return True

def check_database():
    """Check database connection"""
    print("🗄️  Checking database connection...")
    
    try:
        from database import db
        # Try to connect
        user = db.get_user_by_username("test_user_not_exists")
        print("✅ Database connection OK")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_nlp_model():
    """Check NLP model loading"""
    print("🤖 Checking NLP model...")
    
    try:
        from telegram_monitor import monitor
        print("✅ NLP model loaded successfully")
        return True
    except Exception as e:
        print(f"❌ NLP model loading failed: {e}")
        return False

def check_telegram_client():
    """Check Telegram client can be imported"""
    print("📱 Checking Telegram client...")
    
    try:
        from telethon import TelegramClient
        print("✅ Telegram client OK")
        return True
    except Exception as e:
        print(f"❌ Telegram client import failed: {e}")
        return False

def check_flask_app():
    """Check Flask application"""
    print("🌐 Checking Flask application...")
    
    try:
        from app import app
        print("✅ Flask application OK")
        return True
    except Exception as e:
        print(f"❌ Flask application failed: {e}")
        return False

def main():
    """Run complete system verification"""
    print("🚨 Telegram Drug Monitor - System Verification")
    print("=" * 60)
    
    checks = [
        check_environment,
        check_database,
        check_nlp_model,
        check_telegram_client,
        check_flask_app
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        try:
            if check():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Check failed with error: {e}")
            print()
    
    print("=" * 60)
    print(f"📊 VERIFICATION RESULTS: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 ALL SYSTEMS GO! Your Telegram Drug Monitor is ready!")
        print("\n🚀 To start the application:")
        print("   python app.py")
        print("\n📱 Then open: http://localhost:5000")
        print("\n📋 Next steps:")
        print("   1. Register an account with your Telegram API credentials")
        print("   2. Link your Telegram account with phone verification")
        print("   3. Add Telegram channels to monitor")
        print("   4. Start detecting drug-related activities!")
        return True
    else:
        print("⚠️  Some checks failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
