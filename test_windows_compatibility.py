#!/usr/bin/env python3
"""
Test script to verify Windows compatibility before .exe compilation
"""

import os
import sys
import traceback

def test_basic_imports():
    """Test all required imports"""
    print("🔍 Testing basic imports...")
    try:
        import requests
        print("✅ requests imported")
        
        import threading
        print("✅ threading imported")
        
        import subprocess
        print("✅ subprocess imported")
        
        import signal
        print("✅ signal imported")
        
        import logging
        print("✅ logging imported")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_flask_import():
    """Test Flask import"""
    print("\n🔍 Testing Flask import...")
    try:
        from pagos.webhook_server import app
        print("✅ Flask app imported successfully")
        return True
    except Exception as e:
        print(f"❌ Flask import error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_telegram_import():
    """Test Telegram bot import"""
    print("\n🔍 Testing Telegram import...")
    try:
        import telegram
        print("✅ telegram imported")
        
        from telegram.ext import Application
        print("✅ telegram.ext imported")
        
        return True
    except Exception as e:
        print(f"❌ Telegram import error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_file_structure():
    """Test required file structure"""
    print("\n🔍 Testing file structure...")
    required_files = [
        '.env',
        'pagos/webhook_server.py',
        'pagos/payments.py',
        'telegram_bot_listener.py',
        'sergiobets_unified.py'
    ]
    
    all_found = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - NOT FOUND")
            all_found = False
    
    return all_found

def main():
    print("🧪 SergioBets Windows Compatibility Test")
    print("=" * 50)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Flask Import", test_flask_import),
        ("Telegram Import", test_telegram_import),
        ("File Structure", test_file_structure)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Ready for .exe compilation")
    else:
        print("❌ Some tests failed. Fix issues before compilation")
    
    input("\nPresiona Enter para salir...")
    return 0 if all_passed else 1

if __name__ == "__main__":
    main()
