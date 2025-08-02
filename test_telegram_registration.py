#!/usr/bin/env python3

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_telegram_registration():
    print("=== TESTING TELEGRAM USER REGISTRATION ===")
    
    try:
        from telegram_bot_listener import registrar_usuario, cargar_usuarios_registrados, obtener_usuarios_registrados, contar_usuarios_registrados
        
        test_file = 'test_usuarios.txt'
        
        if os.path.exists(test_file):
            os.remove(test_file)
        
        import telegram_bot_listener
        telegram_bot_listener.USUARIOS_FILE = test_file
        
        print("1. Testing user registration...")
        
        resultado1 = registrar_usuario(123456789, "testuser1", "Juan")
        print(f"   Registro usuario 1: {'✅' if resultado1 else '❌'}")
        
        resultado2 = registrar_usuario(987654321, "testuser2", "María")
        print(f"   Registro usuario 2: {'✅' if resultado2 else '❌'}")
        
        resultado3 = registrar_usuario(123456789, "testuser1", "Juan")
        print(f"   Registro duplicado (debe fallar): {'✅' if not resultado3 else '❌'}")
        
        print("\n2. Testing user loading...")
        usuarios_cargados = cargar_usuarios_registrados()
        print(f"   Usuarios cargados: {len(usuarios_cargados)}")
        print(f"   IDs cargados: {list(usuarios_cargados)}")
        
        print("\n3. Testing user retrieval...")
        usuarios_completos = obtener_usuarios_registrados()
        print(f"   Usuarios completos: {len(usuarios_completos)}")
        for usuario in usuarios_completos:
            print(f"   - {usuario['user_id']} | {usuario['username']} | {usuario['first_name']}")
        
        print("\n4. Testing user count...")
        total_usuarios = contar_usuarios_registrados()
        print(f"   Total usuarios registrados: {total_usuarios}")
        
        print("\n5. Testing file format...")
        if os.path.exists(test_file):
            with open(test_file, 'r', encoding='utf-8') as f:
                contenido = f.read()
                print(f"   Contenido del archivo:")
                for linea in contenido.strip().split('\n'):
                    if linea.strip():
                        print(f"   {linea}")
        
        if os.path.exists(test_file):
            os.remove(test_file)
        
        print("\n✅ Telegram registration test completed")
        return True
        
    except Exception as e:
        print(f"❌ Error in telegram registration test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_telegram_registration()
    if success:
        print("✅ Telegram registration test passed")
    else:
        print("❌ Telegram registration test failed")
