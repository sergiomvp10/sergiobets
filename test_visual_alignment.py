#!/usr/bin/env python3

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_visual_alignment():
    """Test that partidos section uses same visual style as predicciones IA"""
    print("=== TESTING VISUAL ALIGNMENT ===")
    
    try:
        with open('crudo.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("1. Testing frame styling...")
        
        if "frame_partido = tk.Frame(frame_checkboxes, bg='#B2F0E8', relief='ridge', bd=1)" in content:
            print("   ✅ Frame uses ridge relief and border like predicciones IA")
        else:
            print("   ❌ Frame styling doesn't match predicciones IA")
            return False
        
        if "checkbox_frame = tk.Frame(frame_partido, bg='#B2F0E8')" in content:
            print("   ✅ Checkbox frame structure matches predicciones IA")
        else:
            print("   ❌ Checkbox frame structure missing")
            return False
        
        print("\n2. Testing font styling...")
        
        if "font=('Segoe UI', 9)" in content and "font=('Segoe UI', 8)" in content:
            print("   ✅ Uses Segoe UI fonts like predicciones IA")
        else:
            print("   ❌ Font doesn't match predicciones IA")
            return False
        
        print("\n3. Testing padding structure...")
        
        if "padx=5, pady=3" in content:
            print("   ✅ Padding matches predicciones IA structure")
        else:
            print("   ❌ Padding doesn't match predicciones IA")
            return False
        
        print("\n4. Testing icon usage...")
        
        if "⚽ PARTIDO #" in content and "⏰" in content and "💰" in content and "🏠" in content:
            print("   ✅ Uses appropriate icons like predicciones IA")
        else:
            print("   ❌ Icon usage doesn't match predicciones IA style")
            return False
        
        print("\n✅ Visual alignment test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error in visual alignment test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_visual_alignment()
    if success:
        print("✅ Visual alignment test passed")
    else:
        print("❌ Visual alignment test failed")
