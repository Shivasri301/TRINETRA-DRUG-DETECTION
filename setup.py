#!/usr/bin/env python3
"""
Setup script for Telegram Drug Monitor
Installs dependencies and sets up the application
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        # Upgrade pip first
        subprocess.check_call(["py", "-m", "pip", "install", "--upgrade", "pip"])
        print("✅ pip upgraded successfully")
        
        # Install requirements
        subprocess.check_call(["py", "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        raise e

def setup_environment():
    """Set up environment variables"""
    if not os.path.exists('.env'):
        print("Creating .env file...")
        with open('.env', 'w') as f:
            f.write("""MONGODB_URI=mongodb+srv://adityapatel1335_db_user:1aSMNRnCgkUJLvuC@cluster0.woydxwp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
SECRET_KEY=your_secret_key_here_change_this_in_production
DATABASE_NAME=telegram_drug_monitor""")
        print(".env file created. Please update the SECRET_KEY for production use.")

def main():
    print("Setting up Telegram Drug Monitor...")
    
    try:
        install_requirements()
        setup_environment()
        
        print("\n✅ Setup completed successfully!")
        print("\nTo run the application:")
        print("python app.py")
        print("\nThen open your browser to: http://localhost:5000")
        print("\n📋 Before using the application:")
        print("1. Get your Telegram API credentials from https://my.telegram.org")
        print("2. Register an account in the application")
        print("3. Link your Telegram account")
        print("4. Start monitoring channels!")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
