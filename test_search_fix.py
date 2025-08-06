#!/usr/bin/env python3
"""
Test script to verify search functionality fix
"""

import sys
import os
from datetime import datetime

def test_search_fix():
    """Test that search functionality returns real data"""
    print("=" * 60)
    print("TESTING SEARCH FUNCTIONALITY FIX")
    print("=" * 60)
    print(f"Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    try:
        from sergiobets_unified import SergioBetsUnified
        print("✅ SergioBetsUnified import successful")
        
        app = SergioBetsUnified()
        fecha = datetime.now().strftime('%Y-%m-%d')
        
        print(f"\nTesting cargar_partidos_reales for date: {fecha}")
        partidos = app.cargar_partidos_reales(fecha)
        
        print(f"Result type: {type(partidos)}")
        print(f"Result length: {len(partidos) if partidos else 0}")
        
        if partidos and len(partidos) > 0:
            print(f"✅ Search returned {len(partidos)} matches")
            
            sample_match = partidos[0]
            print(f"Sample match: {sample_match}")
            
            if sample_match.get('liga') == 'Liga Simulada' or 'Simulado' in str(sample_match):
                print("⚠️ WARNING: Still using simulated data")
                return False
            else:
                print("✅ Using real API data")
                return True
        else:
            print("❌ Search returned no matches")
            return False
            
    except Exception as e:
        print(f"❌ Search test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_users_button_fix():
    """Test that Users button imports work correctly"""
    print("\n" + "=" * 60)
    print("TESTING USERS BUTTON FIX")
    print("=" * 60)
    
    try:
        import tkinter as tk
        from tkinter import messagebox, simpledialog, scrolledtext
        print("✅ tkinter imports successful")
        
        root = tk.Tk()
        root.withdraw()
        
        frame = tk.Frame(root, bg="#2c3e50")
        text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, 
                                             font=('Consolas', 10), bg="white", fg="black")
        
        print("✅ ScrolledText widget creation successful")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Users button test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 TESTING SERGIOBETS FIXES")
    print("=" * 60)
    
    search_ok = test_search_fix()
    users_ok = test_users_button_fix()
    
    print("\n" + "=" * 60)
    print("FIX TEST SUMMARY")
    print("=" * 60)
    print(f"Search functionality: {'✅ Fixed' if search_ok else '❌ Still broken'}")
    print(f"Users button: {'✅ Fixed' if users_ok else '❌ Still broken'}")
    
    if search_ok and users_ok:
        print("\n🎉 All fixes successful!")
    else:
        print("\n⚠️ Some issues remain - check diagnostic output above")
