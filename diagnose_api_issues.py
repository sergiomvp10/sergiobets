#!/usr/bin/env python3
"""
Diagnostic script to identify API and Users button issues
"""

import sys
import os
from datetime import datetime
import requests

def test_footystats_api():
    """Test FootyStats API directly"""
    print("=" * 60)
    print("TESTING FOOTYSTATS API CONNECTIVITY")
    print("=" * 60)
    
    API_KEY = "ba2674c1de1595d6af7c099be1bcef8c915f9324f0c1f0f5ac926106d199dafd"
    BASE_URL = "https://api.football-data-api.com"
    fecha = datetime.now().strftime("%Y-%m-%d")
    
    print(f"Testing API for date: {fecha}")
    endpoint = f"{BASE_URL}/todays-matches"
    params = {
        "key": API_KEY,
        "date": fecha,
        "timezone": "America/Bogota"
    }
    
    try:
        response = requests.get(endpoint, params=params, timeout=10)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            matches = data.get("data", [])
            print(f"✅ API responded successfully")
            print(f"Matches found: {len(matches)}")
            
            if matches:
                print(f"Sample match: {matches[0]}")
                return True, matches
            else:
                print("⚠️ No matches returned for today")
                return True, []
        else:
            print(f"❌ API error response: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ API request failed: {e}")
        return False, None

def test_search_functionality():
    """Test the search functionality from sergiobets_unified"""
    print("\n" + "=" * 60)
    print("TESTING SEARCH FUNCTIONALITY")
    print("=" * 60)
    
    try:
        from footystats_api import obtener_partidos_del_dia
        print("✅ footystats_api import successful")
        
        fecha = datetime.now().strftime("%Y-%m-%d")
        result = obtener_partidos_del_dia(fecha)
        
        print(f"obtener_partidos_del_dia result: {type(result)}")
        print(f"Length: {len(result) if result else 0}")
        
        if result and len(result) > 0:
            print("✅ API function returned data")
            return True
        else:
            print("❌ API function returned no data")
            return False
            
    except Exception as e:
        print(f"❌ Search functionality error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_users_imports():
    """Test imports used in Users button"""
    print("\n" + "=" * 60)
    print("TESTING USERS BUTTON IMPORTS")
    print("=" * 60)
    
    try:
        import tkinter as tk
        print("✅ tkinter import successful")
        
        from tkinter import messagebox, scrolledtext, simpledialog
        print("✅ tkinter submodules import successful")
        
        try:
            from access_manager import access_manager
            print("✅ access_manager import successful")
            
            stats = access_manager.obtener_estadisticas()
            print(f"✅ obtener_estadisticas returned: {type(stats)} - {stats}")
            
            usuarios = access_manager.listar_usuarios()
            print(f"✅ listar_usuarios returned: {type(usuarios)} - length: {len(usuarios) if usuarios else 0}")
            
        except ImportError as e:
            print(f"⚠️ access_manager import failed: {e}")
            print("   This is expected if access_manager.py doesn't exist")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Users imports error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_widget_creation():
    """Test creating the problematic scrolledtext widget"""
    print("\n" + "=" * 60)
    print("TESTING SCROLLEDTEXT WIDGET CREATION")
    print("=" * 60)
    
    try:
        import tkinter as tk
        from tkinter import scrolledtext
        
        root = tk.Tk()
        root.withdraw()
        
        frame = tk.Frame(root, bg="#2c3e50")
        frame.pack(fill='both', expand=True)
        
        text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, 
                                             font=('Consolas', 10), bg="white", fg="black")
        text_area.pack(fill='both', expand=True)
        
        print("✅ ScrolledText widget created successfully")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ ScrolledText widget creation error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 DIAGNOSING SERGIOBETS API AND USERS ISSUES")
    print("=" * 60)
    print(f"Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    api_ok, api_data = test_footystats_api()
    search_ok = test_search_functionality()
    users_ok = test_users_imports()
    widget_ok = test_widget_creation()
    
    print("\n" + "=" * 60)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 60)
    print(f"Direct API test: {'✅ Working' if api_ok else '❌ Failed'}")
    print(f"Search function: {'✅ Working' if search_ok else '❌ Failed'}")
    print(f"Users imports: {'✅ Working' if users_ok else '❌ Failed'}")
    print(f"ScrolledText widget: {'✅ Working' if widget_ok else '❌ Failed'}")
    
    if api_ok and not search_ok:
        print("\n🔧 ISSUE IDENTIFIED:")
        print("- API is working but search function is failing")
        print("- Likely missing dependencies or import issues")
    
    if not api_ok:
        print("\n🔧 API ISSUE IDENTIFIED:")
        print("- FootyStats API is not responding correctly")
        print("- Check API key, endpoint, or rate limits")
    
    if not users_ok or not widget_ok:
        print("\n🔧 USERS BUTTON ISSUE IDENTIFIED:")
        print("- Import or access_manager issues")
        print("- Check tkinter scrolledtext widget creation")
