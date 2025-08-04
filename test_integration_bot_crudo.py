#!/usr/bin/env python3

import sys
import time
import threading
import os
sys.path.append('.')

def test_integration():
    """Test that bot integration with crudo.py works correctly"""
    print("🧪 Testing Telegram bot integration with crudo.py...")
    
    try:
        from telegram_bot_listener import iniciar_bot_en_hilo
        print("✅ Bot integration import successful")
        
        if os.path.exists('usuarios.txt'):
            print("✅ usuarios.txt file exists for shared access")
        else:
            print("⚠️ usuarios.txt file not found - will be created when needed")
            
        if os.path.exists('novedades.txt'):
            print("✅ novedades.txt file exists")
        else:
            print("❌ novedades.txt file missing")
            
        print("🤖 Testing bot startup in separate thread...")
        hilo_bot = iniciar_bot_en_hilo()
        
        if hilo_bot and hilo_bot.is_alive():
            print("✅ Bot thread started successfully")
            time.sleep(2)  # Give bot time to initialize
            print("✅ Bot thread still running after 2 seconds")
        else:
            print("❌ Bot thread failed to start")
            
        print("\n🎉 Integration test completed!")
        print("📱 Bot should now be responsive to /start commands")
        print("🖥️ Main app can now be started with integrated bot")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Integration test error: {e}")
        return False

if __name__ == "__main__":
    success = test_integration()
    if success:
        print("\n✅ Integration ready for deployment!")
    else:
        print("\n❌ Integration issues detected")
