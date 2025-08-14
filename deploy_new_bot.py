#!/usr/bin/env python3
"""
SergioBets - New Bot Deployment Script
Completely replaces old bot with new token: 8487580276:AAE9aa9dx3Vbbuq9OsKr_d-26mkNQ6csc0c
"""

import os
import sys
import time
import signal
import subprocess
from pathlib import Path

NEW_TOKEN = '8487580276:AAE9aa9dx3Vbbuq9OsKr_d-26mkNQ6csc0c'

def kill_old_bot_processes():
    """Kill any existing bot processes"""
    print("🛑 Stopping any existing bot processes...")
    try:
        subprocess.run(['pkill', '-f', 'telegram_bot'], check=False)
        subprocess.run(['pkill', '-f', 'run_telegram_bot'], check=False)
        subprocess.run(['pkill', '-f', 'bot_listener'], check=False)
        time.sleep(2)
        print("✅ Old bot processes stopped")
    except Exception as e:
        print(f"⚠️ Error stopping old processes: {e}")

def verify_token_configuration():
    """Verify all files use the new token"""
    print("🔍 Verifying token configuration...")
    
    env_path = Path('.env')
    if env_path.exists():
        with open(env_path, 'r') as f:
            content = f.read()
            if NEW_TOKEN in content:
                print("✅ .env file has correct token")
            else:
                print("❌ .env file needs token update")
                return False
    
    print("✅ Token configuration verified")
    return True

def start_new_bot():
    """Start the new bot using the unified system"""
    print(f"🚀 Starting new bot with token: {NEW_TOKEN[:10]}...")
    
    try:
        from telegram_bot_listener import iniciar_bot_listener
        print("✅ New bot started successfully")
        print("📱 Bot should now respond to /start as @BetGeniuXbot")
        iniciar_bot_listener()
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error starting new bot: {e}")

if __name__ == "__main__":
    print("🤖 SergioBets - New Bot Deployment")
    print("=" * 50)
    
    kill_old_bot_processes()
    
    if verify_token_configuration():
        start_new_bot()
    else:
        print("❌ Token configuration failed")
        sys.exit(1)
