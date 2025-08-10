#!/usr/bin/env python3
"""
Test script to verify rebranding is complete and application works
"""

import sys
import os

def test_import():
    """Test that the main class can be imported with new name"""
    try:
        from sergiobets_unified import BetGeniuXUnified
        print("✅ Import successful - BetGeniuXUnified class found")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Other error: {e}")
        return False

def test_class_instantiation():
    """Test that the class can be instantiated"""
    try:
        from sergiobets_unified import BetGeniuXUnified
        app = BetGeniuXUnified()
        print("✅ Class instantiation successful")
        return True
    except Exception as e:
        print(f"❌ Class instantiation failed: {e}")
        return False

if __name__ == "__main__":
    print("=== TESTING REBRANDING COMPLETION ===")
    
    success1 = test_import()
    success2 = test_class_instantiation()
    
    if success1 and success2:
        print("\n✅ Rebranding tests passed - application should work correctly")
        sys.exit(0)
    else:
        print("\n❌ Some rebranding tests failed")
        sys.exit(1)
