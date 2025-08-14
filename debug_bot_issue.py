#!/usr/bin/env python3
"""Debug why the bot doesn't respond to /start"""

import sys
import os
import asyncio
sys.path.append('.')

async def debug_bot_configuration():
    """Debug bot configuration step by step"""
    print("🔍 DEBUGGING BOT CONFIGURATION")
    print("=" * 50)
    
    print("1. Environment variable loading:")
    from dotenv import load_dotenv
    load_dotenv()
    env_token = os.getenv('TELEGRAM_BOT_TOKEN')
    print(f"   .env token: {env_token[:10] + '...' if env_token else 'NOT_FOUND'}")
    
    print("\n2. Module token loading:")
    from telegram_bot_listener import TELEGRAM_TOKEN as bot_token
    from telegram_utils import TELEGRAM_TOKEN as utils_token
    print(f"   Bot listener: {bot_token[:10]}...")
    print(f"   Utils: {utils_token[:10]}...")
    
    print("\n3. Testing bot API connection:")
    try:
        from telegram.ext import Application
        app = Application.builder().token(bot_token).build()
        bot = app.bot
        me = await bot.get_me()
        print(f"   ✅ Bot API works: @{me.username}")
        print(f"   Bot ID: {me.id}")
    except Exception as e:
        print(f"   ❌ Bot API failed: {e}")
        return False
    
    print("\n4. Bot listener configuration:")
    try:
        from telegram_bot_listener import iniciar_bot_listener, start_command
        print("   ✅ Bot listener functions imported")
        
        app = Application.builder().token(bot_token).build()
        from telegram.ext import CommandHandler, CallbackQueryHandler
        
        app.add_handler(CommandHandler("start", start_command))
        print("   ✅ /start command handler added")
        
    except Exception as e:
        print(f"   ❌ Bot listener setup failed: {e}")
        return False
    
    print("\n5. Unified system integration:")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("sergiobets_unified", "sergiobets_unified.py")
        unified_module = importlib.util.module_from_spec(spec)
        
        print("   ✅ Unified module can be imported")
        
        if hasattr(unified_module, 'SergioBetsUnified'):
            print("   ✅ SergioBetsUnified class exists")
        else:
            print("   ❌ SergioBetsUnified class missing")
            
    except Exception as e:
        print(f"   ❌ Unified system check failed: {e}")
    
    print("\n6. Potential issues to check:")
    print("   - Is the bot actually running in production?")
    print("   - Are there multiple bot instances conflicting?")
    print("   - Is the webhook URL configured correctly?")
    print("   - Are there firewall/network issues?")
    print("   - Is the bot token revoked or restricted?")
    
    return True

async def test_manual_bot_start():
    """Try to manually start the bot to see what happens"""
    print("\n🚀 MANUAL BOT START TEST")
    print("=" * 30)
    
    try:
        from telegram_bot_listener import iniciar_bot_listener
        print("Starting bot listener manually...")
        
        from telegram.ext import Application
        from telegram_bot_listener import TELEGRAM_TOKEN, start_command
        
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        application.add_handler(CommandHandler("start", start_command))
        
        print("✅ Bot application configured successfully")
        print("✅ /start handler registered")
        print("⚠️ Bot would start polling here (not running to avoid conflicts)")
        
        return True
        
    except Exception as e:
        print(f"❌ Manual bot start failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all debug tests"""
    config_ok = await debug_bot_configuration()
    start_ok = await test_manual_bot_start()
    
    print("\n📊 DEBUG SUMMARY:")
    print(f"   Configuration: {'✅ OK' if config_ok else '❌ FAILED'}")
    print(f"   Manual start: {'✅ OK' if start_ok else '❌ FAILED'}")
    
    if config_ok and start_ok:
        print("\n🤔 Bot configuration appears correct.")
        print("   The issue might be:")
        print("   - Bot not actually running in production")
        print("   - Network/firewall blocking bot")
        print("   - Multiple bot instances causing conflicts")
        print("   - Webhook configuration issues")
    else:
        print("\n❌ Found configuration issues that need fixing")

if __name__ == "__main__":
    from telegram.ext import CommandHandler
    asyncio.run(main())
