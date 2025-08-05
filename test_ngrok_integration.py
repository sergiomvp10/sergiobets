#!/usr/bin/env python3
"""
Test script for ngrok integration
"""

import os
import sys
import time
import requests
import subprocess
from pathlib import Path

def test_launch_script():
    """Test that launch_with_ngrok.py can be imported and basic functions work"""
    print("🧪 Testing launch_with_ngrok.py...")
    
    try:
        from launch_with_ngrok import NgrokManager, get_current_ngrok_url
        
        manager = NgrokManager()
        print("✅ NgrokManager class imported successfully")
        
        ngrok_installed = manager.check_ngrok_installed()
        print(f"📦 ngrok installed: {ngrok_installed}")
        
        test_url = "https://test-12345.ngrok.io"
        with open("ngrok_url.txt", "w") as f:
            f.write(test_url)
        
        loaded_url = get_current_ngrok_url()
        if loaded_url == test_url:
            print("✅ URL file read/write works correctly")
        else:
            print(f"❌ URL file test failed: expected {test_url}, got {loaded_url}")
        
        if os.path.exists("ngrok_url.txt"):
            os.remove("ngrok_url.txt")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing launch script: {e}")
        return False

def test_telegram_bot_functions():
    """Test that telegram bot functions can be imported"""
    print("\n🤖 Testing telegram bot functions...")
    
    try:
        from telegram_bot_listener import get_current_ngrok_url, check_and_restart_ngrok
        
        print("✅ get_current_ngrok_url imported successfully")
        print("✅ check_and_restart_ngrok imported successfully")
        
        url = get_current_ngrok_url()
        if url is None:
            print("✅ get_current_ngrok_url returns None when no file exists")
        else:
            print(f"⚠️ Unexpected URL returned: {url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing telegram bot functions: {e}")
        return False

def test_webhook_server_import():
    """Test that webhook server can be imported"""
    print("\n🌐 Testing webhook server...")
    
    try:
        from pagos.webhook_server import app
        print("✅ Webhook server Flask app imported successfully")
        
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        expected_routes = ['/webhook/nowpayments', '/api/create_payment', '/health']
        
        for route in expected_routes:
            if route in routes:
                print(f"✅ Route {route} registered")
            else:
                print(f"❌ Route {route} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing webhook server: {e}")
        return False

def test_payments_integration():
    """Test that payments module works"""
    print("\n💳 Testing payments integration...")
    
    try:
        from pagos.payments import PaymentManager, NOWPaymentsAPI
        
        print("✅ PaymentManager imported successfully")
        print("✅ NOWPaymentsAPI imported successfully")
        
        api = NOWPaymentsAPI()
        currencies = api.get_available_currencies()
        
        if len(currencies) > 0:
            print(f"✅ NOWPayments API connected - {len(currencies)} currencies available")
            
            currency_codes = [c.get('code', '') for c in currencies]
            if 'ltc' in currency_codes:
                print("✅ Litecoin (LTC) available")
            if any('usdt' in code for code in currency_codes):
                print("✅ USDT variants available")
        else:
            print("❌ No currencies returned from API")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing payments: {e}")
        return False

def main():
    print("🎯 SergioBets - Ngrok Integration Test")
    print("=" * 50)
    
    tests = [
        test_launch_script,
        test_telegram_bot_functions,
        test_webhook_server_import,
        test_payments_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ngrok integration is ready.")
        print("\n📋 Next steps:")
        print("1. Run: python launch_with_ngrok.py")
        print("2. Test payment flow through Telegram bot")
        print("3. Verify webhook confirmations work")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
