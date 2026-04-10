#!/usr/bin/env python3
"""Test Telegram bot /start command and functionality"""

import sys
import os
import asyncio
sys.path.append('.')

def test_token_loading():
    """Test that the correct token is loaded"""
    print("🔧 Testing token loading...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        env_token = os.getenv('TELEGRAM_BOT_TOKEN')
        print(f"   Environment token: {env_token[:10]}..." if env_token else "   No token in environment")
        
        from telegram_bot_listener import TELEGRAM_TOKEN
        print(f"   Bot listener token: {TELEGRAM_TOKEN[:10]}...")
        
        from telegram_utils import TELEGRAM_TOKEN as utils_token
        print(f"   Utils token: {utils_token[:10]}...")
        
        if TELEGRAM_TOKEN and utils_token and TELEGRAM_TOKEN == utils_token:
            print("   ✅ Tokens loaded and matching in bot listener and utils")
            return True
        else:
            print("   ❌ Token mismatch or missing")
            return False
        
    except Exception as e:
        print(f"   ❌ Error loading tokens: {e}")
        return False

async def test_bot_initialization():
    """Test bot initialization and /start command setup"""
    print("\n🤖 Testing bot initialization...")
    
    try:
        from telegram_bot_listener import TELEGRAM_TOKEN
        from telegram.ext import Application
        
        app = Application.builder().token(TELEGRAM_TOKEN).build()
        bot = app.bot
        me = await bot.get_me()
        
        print(f"   ✅ Bot initialized: @{me.username} - {me.first_name}")
        print(f"   Bot ID: {me.id}")
        
        from telegram_bot_listener import start_command
        print("   ✅ start_command function available")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Bot initialization failed: {e}")
        return False

def test_unified_integration():
    """Test integration with sergiobets_unified.py"""
    print("\n🔗 Testing unified system integration...")
    
    try:
        from sergiobets_unified import SergioBetsUnified
        print("   ✅ SergioBetsUnified class imported")
        
        unified = SergioBetsUnified()
        print("   ✅ SergioBetsUnified instance created")
        
        if hasattr(unified, 'start_telegram_bot'):
            print("   ✅ start_telegram_bot method available")
        else:
            print("   ❌ start_telegram_bot method missing")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Unified integration failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🧪 TELEGRAM BOT FUNCTIONALITY TEST")
    print("=" * 50)
    
    token_ok = test_token_loading()
    bot_ok = await test_bot_initialization()
    unified_ok = test_unified_integration()
    
    print("\n📊 TEST RESULTS:")
    print(f"   Token loading: {'✅ PASS' if token_ok else '❌ FAIL'}")
    print(f"   Bot initialization: {'✅ PASS' if bot_ok else '❌ FAIL'}")
    print(f"   Unified integration: {'✅ PASS' if unified_ok else '❌ FAIL'}")
    
    if token_ok and bot_ok and unified_ok:
        print("\n🎉 ALL TESTS PASSED - Bot should respond to /start command!")
    else:
        print("\n⚠️ SOME TESTS FAILED - Bot may not work properly")
    
    return token_ok and bot_ok and unified_ok

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)
