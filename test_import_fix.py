#!/usr/bin/env python3
"""
Test script to verify the import fix for iniciar_bot_en_hilo
"""

def test_telegram_bot_import():
    """Test importing iniciar_bot_en_hilo from telegram_bot_listener"""
    print("🔍 Testing telegram_bot_listener import...")
    try:
        from telegram_bot_listener import iniciar_bot_en_hilo
        print("✅ iniciar_bot_en_hilo imported successfully")
        print(f"✅ Function type: {type(iniciar_bot_en_hilo)}")
        return True
    except ImportError as e:
        print(f"❌ ImportError: {e}")
        return False
    except Exception as e:
        print(f"❌ Other error: {e}")
        return False

def test_crudo_imports():
    """Test all imports needed by crudo.py"""
    print("\n🔍 Testing crudo.py imports...")
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox
        from tkinter.scrolledtext import ScrolledText
        from tkcalendar import DateEntry
        import pygame
        from telegram_utils import enviar_telegram, enviar_telegram_masivo
        from telegram_bot_listener import iniciar_bot_en_hilo
        from ia_bets import filtrar_apuestas_inteligentes, generar_mensaje_ia, simular_datos_prueba, guardar_prediccion_historica
        from league_utils import detectar_liga_por_imagen
        from footystats_api import obtener_partidos_del_dia
        from json_storage import guardar_json, cargar_json
        
        print("✅ All crudo.py imports successful")
        return True
    except Exception as e:
        print(f"❌ crudo.py import error: {e}")
        return False

def test_sergiobets_unified_imports():
    """Test all imports needed by sergiobets_unified.py"""
    print("\n🔍 Testing sergiobets_unified.py imports...")
    try:
        import os
        import sys
        import time
        import signal
        import threading
        import subprocess
        import requests
        import json
        import logging
        import traceback
        from pathlib import Path
        import tkinter as tk
        from tkinter import ttk, messagebox
        from tkinter.scrolledtext import ScrolledText
        from tkcalendar import DateEntry
        import pygame
        from footystats_api import obtener_partidos_del_dia
        from json_storage import guardar_json, cargar_json
        from telegram_utils import enviar_telegram, enviar_telegram_masivo
        from ia_bets import filtrar_apuestas_inteligentes, generar_mensaje_ia, simular_datos_prueba, guardar_prediccion_historica
        from league_utils import detectar_liga_por_imagen
        from telegram_bot_listener import iniciar_bot_en_hilo
        
        print("✅ All sergiobets_unified.py imports successful")
        return True
    except Exception as e:
        print(f"❌ sergiobets_unified.py import error: {e}")
        return False

def main():
    print("🧪 Testing Import Fix for SergioBets")
    print("=" * 50)
    
    tests = [
        ("Telegram Bot Import", test_telegram_bot_import),
        ("Crudo.py Imports", test_crudo_imports),
        ("SergioBets Unified Imports", test_sergiobets_unified_imports)
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All import tests passed! Both applications should work now.")
    else:
        print("❌ Some import tests failed. Check the errors above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit_code = main()
    print(f"\nExit code: {exit_code}")
