#!/usr/bin/env python3
"""
Quick start script for Telegram Drug Monitor
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import flask
        import pymongo
        import telethon
        import transformers
        import bcrypt
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Run 'python setup.py' to install dependencies")
        return False

def check_environment():
    """Check environment configuration"""
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        print("Run 'python setup.py' to create environment file")
        return False
    
    print("✅ Environment configuration found")
    return True

def main():
    print("🚀 Starting Telegram Drug Monitor...")
    print("=" * 50)
    
    # Check prerequisites
    if not check_dependencies():
        sys.exit(1)
    
    if not check_environment():
        sys.exit(1)
    
    print("\n📋 Before you start:")
    print("1. Get Telegram API credentials from https://my.telegram.org")
    print("2. Register an account in the web interface")
    print("3. Link your Telegram account with phone verification")
    print("4. Add channels to monitor")
    
    print(f"\n🌐 Starting web server...")
    print(f"📱 Open your browser to: http://localhost:5000")
    print(f"⏹️  Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start Flask application
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Shutting down server...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
