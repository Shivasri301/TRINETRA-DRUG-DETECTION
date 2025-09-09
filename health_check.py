#!/usr/bin/env python3
"""
Health check script for Trinetra
Validates all system components are working correctly
"""

import os
import sys
import requests
import time
from datetime import datetime

def check_database():
    """Test database connectivity"""
    print("🗄️ Checking database connection...")
    
    try:
        from database import db
        # Try to query the database
        result = db.users.find_one()
        print("✅ Database connection successful")
        
        # Check collections exist
        collections = db.db.list_collection_names()
        expected_collections = ['users', 'channels', 'monitoring_results', 'alerts']
        
        for collection in expected_collections:
            if collection in collections:
                count = db.db[collection].count_documents({})
                print(f"  📊 {collection}: {count} documents")
            else:
                print(f"  ⚠️ Collection '{collection}' not found (will be created on first use)")
        
        return True
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

def check_dependencies():
    """Check if all required packages are available"""
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        ('flask', 'Flask web framework'),
        ('pymongo', 'MongoDB driver'),
        ('telethon', 'Telegram API client'),
        ('transformers', 'HuggingFace NLP models'),
        ('torch', 'PyTorch ML framework'),
        ('bcrypt', 'Password hashing'),
        ('dotenv', 'Environment variables')
    ]
    
    all_available = True
    
    for package, description in required_packages:
        try:
            module = __import__(package.replace('-', '_'))
            version = getattr(module, '__version__', 'unknown')
            print(f"  ✅ {package} ({version}) - {description}")
        except ImportError:
            print(f"  ❌ {package} - {description}")
            all_available = False
    
    if all_available:
        print("✅ All dependencies are installed")
    else:
        print("❌ Some dependencies are missing")
    
    return all_available

def check_environment():
    """Check environment configuration"""
    print("\n🔧 Checking environment configuration...")
    
    # Check .env file
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        return False
    
    # Load and check environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = {
        'MONGODB_URI': 'MongoDB connection string',
        'SECRET_KEY': 'Flask secret key',
        'DATABASE_NAME': 'Database name'
    }
    
    all_set = True
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            masked_value = value[:20] + "..." if len(value) > 20 else value
            print(f"  ✅ {var}: {masked_value} - {description}")
        else:
            print(f"  ❌ {var}: Not set - {description}")
            all_set = False
    
    if all_set:
        print("✅ Environment configuration is complete")
    else:
        print("❌ Environment configuration is incomplete")
    
    return all_set

def check_ai_model():
    """Test AI model loading"""
    print("\n🤖 Checking AI model...")
    
    try:
        from transformers import pipeline
        print("  🔍 Loading BART model for drug detection...")
        
        # This will download the model if not cached
        classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        
        # Test with a simple message
        test_text = "High quality MDMA available for home delivery"
        result = classifier(test_text, candidate_labels=["drug sale", "normal"])
        
        prediction = result["labels"][0]
        confidence = result["scores"][0]
        
        print(f"  ✅ Model test successful")
        print(f"  📊 Test prediction: {prediction} ({confidence:.2f} confidence)")
        print("✅ AI model is ready")
        return True
        
    except Exception as e:
        print(f"❌ AI model check failed: {e}")
        print("  💡 This might be due to insufficient RAM or network issues")
        return False

def check_web_application():
    """Test web application startup"""
    print("\n🌐 Checking web application...")
    
    try:
        # Try importing the Flask app
        from app import app
        print("  ✅ Flask application imports successfully")
        
        # Test app configuration
        if app.secret_key and app.secret_key != 'your-secret-key-change-this':
            print("  ✅ Secret key is configured")
        else:
            print("  ⚠️ Default secret key detected - should be changed for production")
        
        print("✅ Web application is ready")
        return True
        
    except Exception as e:
        print(f"❌ Web application check failed: {e}")
        return False

def run_comprehensive_health_check():
    """Run all health checks"""
    
    print("🚨 TRINETRA - HEALTH CHECK")
    print("=" * 60)
    print(f"🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    checks = [
        ("Environment Configuration", check_environment),
        ("Package Dependencies", check_dependencies),
        ("Database Connection", check_database),
        ("AI Model Loading", check_ai_model),
        ("Web Application", check_web_application)
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        print(f"\n{'='*20} {check_name} {'='*20}")
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"❌ {check_name} failed with exception: {e}")
            results[check_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 HEALTH CHECK SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {check_name}")
    
    print(f"\n🎯 Overall Status: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 ALL CHECKS PASSED! System is ready for deployment.")
        print("\n🚀 To start the application:")
        print("   python app.py          (development)")
        print("   python start_production.py  (production)")
        return True
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\n🔧 Common solutions:")
        print("   python setup.py        (install dependencies)")
        print("   Check .env file configuration")
        print("   Verify MongoDB connection")
        return False

def main():
    """Main health check function"""
    success = run_comprehensive_health_check()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
