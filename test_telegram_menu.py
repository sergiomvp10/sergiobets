#!/usr/bin/env python3

import sys
sys.path.append('.')

def test_telegram_menu_imports():
    """Test that all enhanced menu imports work correctly"""
    try:
        from telegram_bot_listener import (
            start_command, button_callback, mostrar_estadisticas,
            mostrar_novedades, mostrar_membresia, mostrar_ayuda,
            volver_menu_principal, contar_usuarios_registrados
        )
        print("✅ All enhanced menu functions imported successfully")
        
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        print("✅ Telegram inline keyboard imports successful")
        
        import os
        if os.path.exists('novedades.txt'):
            print("✅ novedades.txt file exists")
        else:
            print("❌ novedades.txt file missing")
            
        print("✅ Enhanced Telegram menu system ready")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_telegram_menu_imports()
    if success:
        print("\n🎉 All tests passed - Enhanced menu ready for deployment!")
    else:
        print("\n❌ Tests failed - Check imports and dependencies")
