#!/usr/bin/env python3
"""
Production start script for Telegram Drug Monitor
Includes health checks and proper error handling
"""

import os
import sys
import subprocess
from database import db

def check_environment():
    """Check if environment is properly configured"""
    print("🔍 Checking environment configuration...")
    
    # Check .env file
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Run 'python setup.py' to create environment configuration")
        return False
    
    # Check required environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['MONGODB_URI', 'SECRET_KEY', 'DATABASE_NAME']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ Environment configuration is valid")
    return True

def check_database_connection():
    """Test database connection"""
    print("🗄️ Testing database connection...")
    
    try:
        # Simple database test
        db.users.find_one()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_dependencies():
    """Check if all required packages are installed"""
    print("📦 Checking dependencies...")
    
    required_packages = [
        'flask', 'pymongo', 'telethon', 'transformers', 
        'torch', 'bcrypt', 'python-dotenv', 'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Run 'python setup.py' to install dependencies")
        return False
    
    print("✅ All dependencies are installed")
    return True

def start_application():
    """Start the Flask application"""
    print("🚀 Starting Telegram Drug Monitor...")
    print("=" * 50)
    
    try:
        # Import and run the app
        from app import app
        
        print("🌐 Web server starting...")
        print("📱 Access at: http://localhost:5000")
        print("🔐 For law enforcement and authorized personnel only")
        print("⏹️  Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Run in production mode
        app.run(
            debug=False,  # Production mode
            host='0.0.0.0',  # Accept connections from any IP
            port=5000,
            threaded=True
        )
        
    except KeyboardInterrupt:
        print("\n👋 Server shutdown initiated by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

def main():
    """Main function with comprehensive checks"""
    print("🚨 TELEGRAM DRUG MONITOR - PRODUCTION START")
    print("=" * 60)
    print("🎯 AI-Powered Drug Detection for Law Enforcement")
    print("=" * 60)
    
    # Run all checks
    checks = [
        ("Environment", check_environment),
        ("Dependencies", check_dependencies),
        ("Database", check_database_connection)
    ]
    
    for check_name, check_func in checks:
        if not check_func():
            print(f"\n❌ {check_name} check failed!")
            print("Please fix the issues above before starting the application.")
            sys.exit(1)
    
    print("\n🎉 All checks passed! Starting application...")
    print("\n⚖️  LEGAL NOTICE:")
    print("This software is for law enforcement and authorized security professionals only.")
    print("Ensure compliance with local privacy and surveillance laws.")
    
    # Start the application
    start_application()

if __name__ == "__main__":
    main()
