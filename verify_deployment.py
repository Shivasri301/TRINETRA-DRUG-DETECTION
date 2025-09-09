#!/usr/bin/env python3
"""
Deployment verification script for Trinetra
Quick check before deployment to ensure compatibility
"""

import sys
import subprocess
import os

def check_python_version():
    """Verify Python version compatibility"""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    print(f"  Current Python: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor == 10:
        print("  ✅ Python 3.10 detected - compatible with runtime.txt")
        return True
    else:
        print(f"  ⚠️ Python {version.major}.{version.minor} detected - may differ from runtime.txt (3.10)")
        return True  # Still proceed but warn

def check_pip_and_setuptools():
    """Verify pip and setuptools are working"""
    print("\n📦 Checking pip and setuptools...")
    
    try:
        import setuptools
        print(f"  ✅ setuptools version: {setuptools.__version__}")
    except ImportError:
        print("  ❌ setuptools not available")
        return False
    
    try:
        import pip
        print(f"  ✅ pip version: {pip.__version__}")
    except ImportError:
        print("  ❌ pip not available")
        return False
    
    # Test setuptools.build_meta specifically
    try:
        import setuptools.build_meta
        print("  ✅ setuptools.build_meta is importable")
        return True
    except ImportError as e:
        print(f"  ❌ setuptools.build_meta failed: {e}")
        return False

def check_critical_imports():
    """Test importing critical dependencies"""
    print("\n🔍 Testing critical imports...")
    
    critical_imports = [
        'flask',
        'pymongo', 
        'telethon',
        'gunicorn'
    ]
    
    success = True
    for module in critical_imports:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
            success = False
    
    return success

def main():
    """Run deployment verification"""
    print("🚀 DEPLOYMENT VERIFICATION")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Pip & Setuptools", check_pip_and_setuptools),
        ("Critical Imports", check_critical_imports)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {name} check failed: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print("🎉 ALL CHECKS PASSED! Ready for deployment.")
        return True
    else:
        print(f"❌ {total - passed} checks failed. Please fix before deployment.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
