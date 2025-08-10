#!/usr/bin/env python3
"""
Test script to verify token fix after updating .env file
"""

import sys
import os

def test_fresh_imports():
    """Test importing tokens with fresh Python process"""
    print("=== TESTING FRESH TOKEN IMPORTS ===")
    
    try:
        modules_to_clear = ['telegram_utils', 'telegram_bot_listener', 'crudo', 'sergiobets_unified']
        for module in modules_to_clear:
            if module in sys.modules:
                del sys.modules[module]
                print(f"Cleared {module} from cache")
        
        from dotenv import load_dotenv
        load_dotenv()
        env_token = os.getenv('TELEGRAM_BOT_TOKEN')
        print(f"✅ Environment token: {env_token[:10]}...")
        
        import telegram_utils
        utils_token = telegram_utils.TELEGRAM_TOKEN
        print(f"✅ telegram_utils.py token: {utils_token[:10]}...")
        
        import telegram_bot_listener
        listener_token = telegram_bot_listener.TELEGRAM_TOKEN
        print(f"✅ telegram_bot_listener.py token: {listener_token[:10]}...")
        
        if utils_token == listener_token == env_token:
            print("✅ All tokens match")
            if utils_token.startswith('8487580276'):
                print("✅ NEW TOKEN CONFIRMED - imports are working correctly!")
                return True
            else:
                print(f"❌ Still importing OLD TOKEN: {utils_token[:10]}...")
                return False
        else:
            print("❌ Token mismatch between sources!")
            return False
            
    except Exception as e:
        print(f"❌ Error importing tokens: {e}")
        return False

if __name__ == "__main__":
    success = test_fresh_imports()
    if success:
        print("\n✅ TOKEN FIX SUCCESSFUL - Ready to test bot")
    else:
        print("\n❌ TOKEN FIX FAILED - Need further investigation")
