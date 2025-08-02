#!/usr/bin/env python3

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_visual_consistency():
    """Test that both sections have consistent visual structure"""
    print("=== TESTING VISUAL CONSISTENCY ===")
    
    try:
        with open('crudo.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("1. Testing frame containers...")
        
        if "frame_predicciones = tk.Frame(root, bg=\"#f1f3f4\")" in content:
            print("   ✅ frame_predicciones container exists")
        else:
            print("   ❌ frame_predicciones container missing")
            return False
            
        if "frame_partidos = tk.Frame(root, bg=\"#f1f3f4\")" in content:
            print("   ✅ frame_partidos container exists")
        else:
            print("   ❌ frame_partidos container missing")
            return False
        
        print("\n2. Testing title styling...")
        
        title_pattern = 'titulo_label = tk.Label(titulo_frame, text=titulo_text, bg="#34495e", fg="white"'
        title_count = content.count(title_pattern)
        
        if title_count >= 2:
            print("   ✅ Both sections use consistent title styling")
        else:
            print(f"   ❌ Title styling inconsistent (found {title_count} instances)")
            return False
        
        print("\n3. Testing card styling...")
        
        if 'relief=\'ridge\', bd=1' in content:
            print("   ✅ Card styling with ridge relief applied")
        else:
            print("   ❌ Card styling missing")
            return False
        
        print("\n4. Testing font consistency...")
        
        if "font=('Segoe UI', 9)" in content and "font=('Segoe UI', 8)" in content:
            print("   ✅ Consistent Segoe UI fonts used")
        else:
            print("   ❌ Font consistency missing")
            return False
        
        print("\n5. Testing cleanup functions...")
        
        if "def limpiar_frame_partidos():" in content:
            print("   ✅ Cleanup function for partidos exists")
        else:
            print("   ❌ Cleanup function for partidos missing")
            return False
        
        print("\n6. Testing full-width layout...")
        
        if "frame_partidos.pack(pady=5, padx=10, fill='x')" in content:
            print("   ✅ Partidos frame uses full-width layout")
        else:
            print("   ❌ Partidos frame missing full-width layout")
            return False
        
        print("\n7. Testing centered title...")
        
        if "🗓️ PARTIDOS PROGRAMADOS PARA LA JORNADA DEL:" in content:
            print("   ✅ Centered title with proper formatting")
        else:
            print("   ❌ Centered title missing")
            return False
        
        print("\n✅ Visual consistency test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error in visual consistency test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_visual_consistency()
    if success:
        print("✅ Visual consistency test passed")
    else:
        print("❌ Visual consistency test failed")
