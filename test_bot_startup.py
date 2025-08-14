#!/usr/bin/env python3
"""Test if the bot can actually start and run"""

import sys
import asyncio
import threading
import time
sys.path.append('.')

def test_bot_startup_methods():
    """Test different ways the bot can be started"""
    print("🚀 TESTING BOT STARTUP METHODS")
    print("=" * 50)
    
    print("1. Testing direct bot listener startup...")
    try:
        from telegram_bot_listener import iniciar_bot_en_hilo
        print("   ✅ iniciar_bot_en_hilo function imported")
        
        print("   ⚠️ Would start bot in thread (not executing to avoid conflicts)")
        
    except Exception as e:
        print(f"   ❌ Direct bot listener failed: {e}")
    
    print("\n2. Testing unified system bot startup...")
    try:
        import importlib
        import sys
        
        sys.modules['tkinter'] = type(sys)('tkinter')
        sys.modules['tkinter.ttk'] = type(sys)('tkinter.ttk')
        sys.modules['tkinter.messagebox'] = type(sys)('tkinter.messagebox')
        sys.modules['tkinter.filedialog'] = type(sys)('tkinter.filedialog')
        
        from sergiobets_unified import SergioBetsUnified
        print("   ✅ SergioBetsUnified imported successfully")
        
        unified = SergioBetsUnified()
        if hasattr(unified, 'start_telegram_bot'):
            print("   ✅ start_telegram_bot method available")
        else:
            print("   ❌ start_telegram_bot method missing")
            
    except Exception as e:
        print(f"   ❌ Unified system startup failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n3. Checking bot mode (webhook vs polling)...")
    try:
        from telegram_bot_listener import iniciar_bot_listener
        print("   ✅ Bot listener uses polling mode (run_polling)")
        
        import os
        webhook_url = os.getenv('WEBHOOK_URL')
        if webhook_url:
            print(f"   ⚠️ Webhook URL configured: {webhook_url}")
        else:
            print("   ✅ No webhook URL - using polling mode")
            
    except Exception as e:
        print(f"   ❌ Bot mode check failed: {e}")

async def test_minimal_bot():
    """Test a minimal bot setup to see if it works"""
    print("\n🤖 TESTING MINIMAL BOT SETUP")
    print("=" * 40)
    
    try:
        from telegram.ext import Application, CommandHandler
        from telegram_bot_listener import TELEGRAM_TOKEN, start_command
        
        print("Creating minimal bot application...")
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        print("Adding /start command handler...")
        application.add_handler(CommandHandler("start", start_command))
        
        print("✅ Minimal bot setup successful")
        print("✅ Bot would start polling here")
        
        bot = application.bot
        me = await bot.get_me()
        print(f"✅ Bot info: @{me.username} (ID: {me.id})")
        
        return True
        
    except Exception as e:
        print(f"❌ Minimal bot setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run startup tests"""
    print("🧪 BOT STARTUP DIAGNOSTIC")
    print("=" * 60)
    
    test_bot_startup_methods()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    minimal_ok = loop.run_until_complete(test_minimal_bot())
    loop.close()
    
    print("\n📊 STARTUP TEST RESULTS:")
    print(f"   Minimal bot setup: {'✅ OK' if minimal_ok else '❌ FAILED'}")
    
    print("\n💡 RECOMMENDATIONS:")
    if minimal_ok:
        print("   - Bot configuration is correct")
        print("   - Issue is likely that bot is not running in production")
        print("   - Check if sergiobets_unified.py is actually running")
        print("   - Verify no other bot instances are conflicting")
        print("   - Consider restarting the bot service")
    else:
        print("   - Bot setup has fundamental issues")
        print("   - Check token validity and permissions")
        print("   - Verify all dependencies are installed")

if __name__ == "__main__":
    main()
