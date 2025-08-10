#!/usr/bin/env python3
"""
Test script to verify sergiobets_unified.py works with new token
"""

def test_unified_imports():
    """Test that sergiobets_unified.py can import and access the new token"""
    print("=== TESTING SERGIOBETS_UNIFIED TOKEN ACCESS ===")
    
    try:
        from telegram_utils import TELEGRAM_TOKEN
        print(f"✅ telegram_utils token imported: {TELEGRAM_TOKEN[:10]}...")
        
        from sergiobets_unified import BetGeniuXUnified
        print("✅ BetGeniuXUnified class imported successfully")
        
        app = BetGeniuXUnified()
        print("✅ BetGeniuXUnified instantiated successfully")
        
        if TELEGRAM_TOKEN.startswith('8487580276'):
            print("✅ New token confirmed in sergiobets_unified.py context")
            return True
        else:
            print(f"❌ Wrong token detected: {TELEGRAM_TOKEN[:10]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error testing sergiobets_unified.py: {e}")
        return False

if __name__ == "__main__":
    success = test_unified_imports()
    if success:
        print("\n✅ sergiobets_unified.py token verification passed")
    else:
        print("\n❌ sergiobets_unified.py token verification failed")
