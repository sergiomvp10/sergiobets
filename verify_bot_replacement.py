#!/usr/bin/env python3
"""Verify that the new bot has completely replaced the old one"""

import asyncio
import sys

async def verify_new_bot():
    """Test that the new bot is working correctly"""
    print("🧪 VERIFYING NEW BOT REPLACEMENT")
    print("=" * 50)
    
    try:
        from telegram.ext import Application
        from telegram_bot_listener import TELEGRAM_TOKEN
        
        print(f"🔑 Testing token: {TELEGRAM_TOKEN[:10]}...")
        
        app = Application.builder().token(TELEGRAM_TOKEN).build()
        bot = app.bot
        me = await bot.get_me()
        
        print(f"✅ NEW BOT VERIFIED: @{me.username}")
        print(f"   Bot ID: {me.id}")
        print(f"   First Name: {me.first_name}")
        
        if me.username == "BetGeniuXbot":
            print("✅ Correct bot username confirmed")
            return True
        else:
            print(f"❌ Wrong bot username: expected BetGeniuXbot, got {me.username}")
            return False
            
    except Exception as e:
        print(f"❌ Bot verification failed: {e}")
        return False

async def test_prediction_sending():
    """Test that prediction sending works"""
    print("\n📤 Testing prediction sending functionality...")
    
    try:
        from telegram_utils import enviar_telegram_masivo
        
        test_message = "🧪 Test message from new bot - prediction sending works!"
        result = enviar_telegram_masivo(test_message)
        
        if result.get("exito"):
            print("✅ Prediction sending functionality verified")
            return True
        else:
            print("❌ Prediction sending failed")
            return False
            
    except Exception as e:
        print(f"❌ Prediction sending test failed: {e}")
        return False

if __name__ == "__main__":
    async def main():
        bot_ok = await verify_new_bot()
        prediction_ok = await test_prediction_sending()
        
        if bot_ok and prediction_ok:
            print("\n🎉 NEW BOT REPLACEMENT SUCCESSFUL!")
            print("   - Old bot should no longer respond")
            print("   - New bot @BetGeniuXbot is active")
            print("   - Prediction sending works")
        else:
            print("\n❌ Bot replacement incomplete")
            
    asyncio.run(main())
