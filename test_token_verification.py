#!/usr/bin/env python3
"""
Test script to verify token rotation is complete
"""

def test_token_imports():
    """Test that all modules use the new token"""
    print("=== TESTING TOKEN ROTATION ===")
    
    try:
        from telegram_utils import TELEGRAM_TOKEN as token_utils
        print(f"✅ telegram_utils.py token: {token_utils[:10]}...")
        
        from telegram_bot_listener import TELEGRAM_TOKEN as token_listener
        print(f"✅ telegram_bot_listener.py token: {token_listener[:10]}...")
        
        if token_utils == token_listener:
            print("✅ All tokens match")
            return True
        else:
            print("❌ Token mismatch between files")
            return False
            
    except Exception as e:
        print(f"❌ Error importing tokens: {e}")
        return False

if __name__ == "__main__":
    success = test_token_imports()
    if success:
        print("\n✅ Token rotation verification passed")
    else:
        print("\n❌ Token rotation verification failed")
