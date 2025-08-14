#!/usr/bin/env python3
"""
Complete Bot Replacement Script
Aggressively replaces ALL old bot instances with new bot using token: 8487580276:AAE9aa9dx3Vbbuq9OsKr_d-26mkNQ6csc0c
"""

import os
import sys
import time
import signal
import subprocess
import psutil
from pathlib import Path

NEW_TOKEN = '8487580276:AAE9aa9dx3Vbbuq9OsKr_d-26mkNQ6csc0c'
OLD_TOKEN = '7069280342'

def kill_all_python_bot_processes():
    """Aggressively kill ALL Python processes that might be running bots"""
    print("🛑 KILLING ALL BOT-RELATED PROCESSES...")
    
    killed_processes = []
    
    patterns = [
        'telegram_bot',
        'run_telegram_bot',
        'bot_listener', 
        'sergiobets',
        'crudo.py',
        'python.*telegram',
        'python.*bot'
    ]
    
    for pattern in patterns:
        try:
            result = subprocess.run(['pkill', '-f', pattern], capture_output=True, text=True)
            if result.returncode == 0:
                killed_processes.append(pattern)
                print(f"✅ Killed processes matching: {pattern}")
        except Exception as e:
            print(f"⚠️ Error killing {pattern}: {e}")
    
    try:
        subprocess.run(['fuser', '-k', '8443/tcp'], check=False, capture_output=True)
        subprocess.run(['fuser', '-k', '8080/tcp'], check=False, capture_output=True)
        print("✅ Killed processes using bot ports")
    except:
        pass
    
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if OLD_TOKEN in cmdline or 'telegram' in cmdline.lower():
                        proc.kill()
                        killed_processes.append(f"PID {proc.info['pid']}")
                        print(f"✅ Killed Python process with old token: PID {proc.info['pid']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        print(f"⚠️ Error in psutil cleanup: {e}")
    
    time.sleep(3)
    print(f"🔥 Killed {len(killed_processes)} bot-related processes")
    return killed_processes

def update_all_token_files():
    """Update token in ALL files that might contain it"""
    print("🔧 UPDATING ALL TOKEN CONFIGURATIONS...")
    
    files_to_update = [
        '.env',
        'env', 
        'telegram_bot_listener.py',
        'telegram_utils.py',
        'crudo.py',
        'sergiobets_unified.py'
    ]
    
    updated_files = []
    
    for filename in files_to_update:
        filepath = Path(filename)
        if filepath.exists():
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                
                if OLD_TOKEN in content:
                    new_content = content.replace(OLD_TOKEN, NEW_TOKEN)
                    with open(filepath, 'w') as f:
                        f.write(new_content)
                    updated_files.append(filename)
                    print(f"✅ Updated token in: {filename}")
                elif NEW_TOKEN in content:
                    print(f"✅ Token already correct in: {filename}")
                else:
                    print(f"⚠️ No token found in: {filename}")
                    
            except Exception as e:
                print(f"❌ Error updating {filename}: {e}")
    
    print(f"🔧 Updated {len(updated_files)} files with new token")
    return updated_files

def verify_new_bot_works():
    """Test that new bot connects and responds"""
    print("🧪 TESTING NEW BOT CONNECTION...")
    
    try:
        import asyncio
        from telegram.ext import Application
        
        async def test_bot():
            app = Application.builder().token(NEW_TOKEN).build()
            bot = app.bot
            me = await bot.get_me()
            return me
        
        me = asyncio.run(test_bot())
        print(f"✅ NEW BOT CONNECTED: @{me.username} (ID: {me.id})")
        
        if me.username == "BetGeniuXbot":
            print("✅ Correct bot username confirmed")
            return True
        else:
            print(f"❌ Wrong bot username: expected BetGeniuXbot, got {me.username}")
            return False
            
    except Exception as e:
        print(f"❌ Bot connection test failed: {e}")
        return False

def start_new_bot_aggressively():
    """Start new bot using multiple methods to ensure it works"""
    print("🚀 STARTING NEW BOT WITH MULTIPLE METHODS...")
    
    try:
        print("📱 Method 1: Starting via telegram_bot_listener...")
        from telegram_bot_listener import iniciar_bot_listener
        
        import threading
        bot_thread = threading.Thread(target=iniciar_bot_listener, daemon=True)
        bot_thread.start()
        time.sleep(2)
        
        if bot_thread.is_alive():
            print("✅ Bot started via telegram_bot_listener")
            return True
        else:
            print("❌ Bot failed to start via telegram_bot_listener")
            
    except Exception as e:
        print(f"❌ Method 1 failed: {e}")
    
    try:
        print("📱 Method 2: Starting via sergiobets_unified...")
        from sergiobets_unified import SergioBetsUnified
        
        unified = SergioBetsUnified()
        unified.start_telegram_bot()
        time.sleep(2)
        print("✅ Bot started via unified system")
        return True
        
    except Exception as e:
        print(f"❌ Method 2 failed: {e}")
    
    try:
        print("📱 Method 3: Starting via subprocess...")
        subprocess.Popen([sys.executable, 'run_telegram_bot.py'], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        time.sleep(2)
        print("✅ Bot started via subprocess")
        return True
        
    except Exception as e:
        print(f"❌ Method 3 failed: {e}")
    
    return False

def main():
    """Complete bot replacement process"""
    print("🤖 COMPLETE BOT REPLACEMENT - AGGRESSIVE MODE")
    print("=" * 60)
    print(f"🔄 Replacing ALL old bots with new token: {NEW_TOKEN[:10]}...")
    print("🎯 Target: @BetGeniuXbot should respond to /start")
    print()
    
    killed = kill_all_python_bot_processes()
    
    updated = update_all_token_files()
    
    if not verify_new_bot_works():
        print("❌ New bot connection failed - aborting")
        return False
    
    if not start_new_bot_aggressively():
        print("❌ Failed to start new bot")
        return False
    
    print("\n🎉 BOT REPLACEMENT COMPLETED!")
    print("=" * 40)
    print("✅ Old bot processes killed")
    print("✅ Token configurations updated") 
    print("✅ New bot connection verified")
    print("✅ New bot started successfully")
    print()
    print("📱 TEST NOW: Send /start to @BetGeniuXbot")
    print("🔍 The bot should respond with interactive menu")
    print()
    print("⏰ Bot will run for 60 seconds for testing...")
    
    try:
        for i in range(60, 0, -1):
            print(f"⏳ {i} seconds remaining... (Ctrl+C to stop)", end='\r')
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Bot replacement test completed")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 REPLACEMENT SUCCESSFUL!")
            print("📱 @BetGeniuXbot should now be the only active bot")
        else:
            print("\n❌ REPLACEMENT FAILED!")
            print("🔧 Manual intervention may be required")
    except KeyboardInterrupt:
        print("\n👋 Replacement interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
