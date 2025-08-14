#!/usr/bin/env python3
"""Test the new Telegram bot token functionality"""

import asyncio
import sys
import os
sys.path.append('.')

async def test_new_token():
    """Test if the new token works"""
    new_token = '8487580276:AAE9aa9dx3Vbbuq9OsKr_d-26mkNQ6csc0c'
    
    try:
        from telegram.ext import Application
        
        print(f"Testing new token: {new_token[:10]}...")
        
        app = Application.builder().token(new_token).build()
        bot = app.bot
        me = await bot.get_me()
        
        print(f'✅ NEW TOKEN WORKS: @{me.username} - {me.first_name}')
        print(f'   Bot ID: {me.id}')
        print(f'   Can join groups: {me.can_join_groups}')
        print(f'   Can read all messages: {me.can_read_all_group_messages}')
        
        return True
        
    except Exception as e:
        print(f'❌ New token failed: {e}')
        return False

if __name__ == "__main__":
    result = asyncio.run(test_new_token())
    if result:
        print("\n✅ New token is valid and ready to use!")
    else:
        print("\n❌ New token has issues - check token validity")
