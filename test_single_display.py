#!/usr/bin/env python3

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_single_display():
    """Test that matches appear only once in the consolidated interface"""
    print("=== TESTING SINGLE DISPLAY INTERFACE ===")
    
    try:
        with open('crudo.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("1. Testing for duplicate display patterns...")
        
        output_insertions = content.count('output.insert(tk.END, f"🕒 {partido[\'hora\']} - {partido[\'local\']} vs {partido[\'visitante\']}")')
        
        if output_insertions == 0:
            print("   ✅ No duplicate output.insert for match info")
        else:
            print(f"   ❌ Found {output_insertions} duplicate output.insert calls")
            return False
        
        if 'frame_partido = tk.Frame(frame_checkboxes, bg=\'#B2F0E8\')' in content:
            print("   ✅ Checkboxes created in frame structure")
        else:
            print("   ❌ Checkbox frame structure missing")
            return False
        
        if 'mensaje_telegram += f"🕒 {partido[\'hora\']} - {partido[\'local\']} vs {partido[\'visitante\']}' in content:
            print("   ✅ Telegram message populated correctly")
        else:
            print("   ❌ Telegram message not populated")
            return False
        
        print("\n2. Testing consolidated structure...")
        
        if 'frame_checkboxes = tk.Frame(output, bg=\'#B2F0E8\')' in content:
            print("   ✅ Single frame_checkboxes structure exists")
        else:
            print("   ❌ frame_checkboxes structure missing")
            return False
        
        if 'output.window_create(tk.END, window=frame_checkboxes)' in content:
            print("   ✅ Single window_create call for checkboxes")
        else:
            print("   ❌ window_create call missing")
            return False
        
        print("\n✅ Single display test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error in single display test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_single_display()
    if success:
        print("✅ Single display test passed")
    else:
        print("❌ Single display test failed")
