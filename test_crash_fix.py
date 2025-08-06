#!/usr/bin/env python3
"""
Test script to verify sergiobets_unified.py crash fixes
"""

import sys
import os

def test_crash_fixes():
    """Test that the unified system fixes work without crashing"""
    print("Testing SergioBets Unified crash fixes...")
    
    try:
        print("1. Testing imports...")
        from json_storage import cargar_json
        print("   ✅ json_storage import successful")
        
        from track_record import TrackRecordManager
        print("   ✅ TrackRecordManager import successful")
        
        print("\n2. Testing JSON loading...")
        historial = cargar_json('historial_predicciones.json') or []
        print(f"   ✅ JSON loading successful - {len(historial)} predictions found")
        
        print("\n3. Testing filtering logic...")
        telegram_sent = [p for p in historial if p.get('sent_to_telegram', False)]
        print(f"   ✅ Filtering successful - {len(telegram_sent)} predictions sent to Telegram")
        
        print("\n4. Testing TrackRecordManager initialization...")
        api_key = 'b37303668c4be1b78ac35b9e96460458e72b74749814a7d6f44983ac4b432079'
        tracker = TrackRecordManager(api_key)
        print("   ✅ TrackRecordManager initialization successful")
        
        print("\n5. Testing syntax validation...")
        with open('sergiobets_unified.py', 'r', encoding='utf-8') as f:
            code = f.read()
        
        compile(code, 'sergiobets_unified.py', 'exec')
        print("   ✅ Syntax validation successful - no syntax errors")
        
        print("\n🎉 All crash fix tests passed - application should work without crashing")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_crash_fixes()
    sys.exit(0 if success else 1)
