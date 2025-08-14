#!/usr/bin/env python3
"""Test actually starting the bot to see if it responds"""

import sys
import asyncio
import threading
import time
import signal
sys.path.append('.')

def test_actual_bot_start():
    """Actually start the bot for a short time to test /start response"""
    print("🚀 TESTING ACTUAL BOT START")
    print("=" * 40)
    print("⚠️ This will start the bot for 30 seconds to test /start command")
    print("📱 Try sending /start to @BetGeniuXbot during this time")
    print()
    
    bot_thread = None
    
    def signal_handler(sig, frame):
        print("\n🛑 Stopping bot test...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        from telegram_bot_listener import iniciar_bot_en_hilo
        
        print("🤖 Starting bot in thread...")
        bot_thread = iniciar_bot_en_hilo()
        
        print("✅ Bot started successfully!")
        print("📱 Bot should now respond to /start command")
        print("⏰ Test will run for 30 seconds...")
        print("🔍 Try sending /start to @BetGeniuXbot now!")
        print()
        
        for i in range(30, 0, -1):
            print(f"⏳ {i} seconds remaining... (Ctrl+C to stop early)", end='\r')
            time.sleep(1)
        
        print("\n✅ Test completed!")
        print("📊 If the bot responded to /start, the issue is resolved!")
        print("❌ If the bot didn't respond, there may be deeper issues")
        
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n🛑 Test finished")

if __name__ == "__main__":
    test_actual_bot_start()
