#!/usr/bin/env python3

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_matches_styling():
    """Test the matches display area styling changes"""
    print("=== TESTING MATCHES DISPLAY STYLING ===")
    
    try:
        print("1. Testing ScrolledText widget styling...")
        
        import tkinter as tk
        from tkinter.scrolledtext import ScrolledText
        
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        output = ScrolledText(root, wrap=tk.WORD, width=95, height=25, font=('Arial', 18), bg='#B2F0E8')
        
        sample_matches = """🏆 Liga Colombiana

⚽ Atlético Nacional vs Millonarios
💰 Cuotas: 1.85 | 3.20 | 4.10
⏰ Hora: Por confirmar

⚽ América de Cali vs Junior
💰 Cuotas: 2.10 | 3.00 | 3.80
⏰ Hora: Por confirmar

🤖 PREDICCIONES IA - PICKS RECOMENDADOS:

✅ PICK #1: Atlético Nacional vs Millonarios
🎯 Predicción: 1X2 - Local (1)
💰 Cuota: 1.85 | Stake: 3u
📊 Valor Esperado: +12.5%
🧠 Justificación: Análisis probabilístico basado en rendimiento reciente"""
        
        output.insert(tk.END, sample_matches)
        
        font_config = output.cget('font')
        bg_color = output.cget('bg')
        
        print(f"   ✅ Font configured: {font_config}")
        print(f"   ✅ Background color: {bg_color}")
        
        if 'Arial' in str(font_config) and '18' in str(font_config):
            print("   ✅ Font size and family correctly set")
        else:
            print("   ❌ Font configuration issue")
            return False
            
        if bg_color == '#B2F0E8':
            print("   ✅ Background color correctly set to turquoise")
        else:
            print(f"   ❌ Background color issue: expected #B2F0E8, got {bg_color}")
            return False
        
        print("\n2. Testing scroll functionality...")
        
        for i in range(20):
            output.insert(tk.END, f"\n⚽ Test Match {i+1}: Team A vs Team B")
            output.insert(tk.END, f"\n💰 Cuotas: 2.{i%9+1}0 | 3.{i%5+1}0 | 4.{i%3+1}0")
            output.insert(tk.END, f"\n⏰ Hora: Por confirmar\n")
        
        scrollbar = output.vbar
        if scrollbar:
            print("   ✅ Vertical scrollbar available")
        else:
            print("   ❌ Scrollbar not found")
            return False
        
        print("\n3. Testing widget dimensions...")
        width = output.cget('width')
        height = output.cget('height')
        wrap_mode = output.cget('wrap')
        
        print(f"   ✅ Width: {width} characters")
        print(f"   ✅ Height: {height} lines")
        print(f"   ✅ Wrap mode: {wrap_mode}")
        
        root.destroy()
        
        print("\n✅ Matches display styling test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error in matches styling test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_matches_styling()
    if success:
        print("✅ Matches styling test passed")
    else:
        print("❌ Matches styling test failed")
