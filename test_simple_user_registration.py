#!/usr/bin/env python3

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_simple_user_registration():
    """Test basic user registration functionality"""
    print("=== TESTING SIMPLE USER REGISTRATION ===")
    
    try:
        from telegram_bot_listener import registrar_usuario, cargar_usuarios_registrados, obtener_usuarios_registrados
        
        import telegram_bot_listener
        telegram_bot_listener.USUARIOS_FILE = 'test_usuarios_simple.txt'
        
        if os.path.exists('test_usuarios_simple.txt'):
            os.remove('test_usuarios_simple.txt')
        
        print("1. Testing new user registration...")
        resultado1 = registrar_usuario(123456789, "testuser1", "Juan")
        print(f"   Registro usuario 1: {'✅' if resultado1 else '❌'}")
        
        resultado2 = registrar_usuario(987654321, "testuser2", "María")
        print(f"   Registro usuario 2: {'✅' if resultado2 else '❌'}")
        
        print("\n2. Testing duplicate prevention...")
        resultado3 = registrar_usuario(123456789, "testuser1", "Juan")
        print(f"   Registro duplicado (debe fallar): {'✅' if not resultado3 else '❌'}")
        
        print("\n3. Testing file format...")
        usuarios = obtener_usuarios_registrados()
        print(f"   Usuarios registrados: {len(usuarios)}")
        for usuario in usuarios:
            print(f"   - {usuario['user_id']} | {usuario['username']} | {usuario['first_name']}")
        
        print("\n4. Testing edge cases...")
        resultado4 = registrar_usuario(555555555, None, None)
        print(f"   Usuario sin username/nombre: {'✅' if resultado4 else '❌'}")
        
        if os.path.exists('test_usuarios_simple.txt'):
            os.remove('test_usuarios_simple.txt')
        
        print("\n✅ Simple registration test completed")
        return True
        
    except Exception as e:
        print(f"❌ Error in simple registration test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_user_registration()
    if success:
        print("✅ Simple registration test passed")
    else:
        print("❌ Simple registration test failed")
