#!/usr/bin/env python3
"""
Test VIP Access System for BetGeniuX
"""

import os
import json
import shutil
from datetime import datetime, timedelta
from access_manager import AccessManager

def test_vip_access_system():
    """Test the complete VIP access management system"""
    print("=== TESTING VIP ACCESS SYSTEM ===")
    
    test_manager = AccessManager("test_usuarios.json")
    
    if os.path.exists("test_usuarios.json"):
        os.remove("test_usuarios.json")
    
    print("\n1. Testing user registration...")
    
    result1 = test_manager.registrar_usuario("123456", "testuser", "Test User")
    result2 = test_manager.registrar_usuario("789012", "premiumuser", "Premium User")
    
    if result1 and result2:
        print("   ✅ User registration works")
    else:
        print("   ❌ User registration failed")
        return False
    
    print("\n2. Testing premium access granting...")
    
    result = test_manager.otorgar_acceso("123456", 7)
    if result:
        print("   ✅ Premium access granting works")
    else:
        print("   ❌ Premium access granting failed")
        return False
    
    print("\n3. Testing access verification...")
    
    has_access = test_manager.verificar_acceso("123456")
    no_access = test_manager.verificar_acceso("789012")
    
    if has_access and not no_access:
        print("   ✅ Access verification works correctly")
    else:
        print("   ❌ Access verification failed")
        return False
    
    print("\n4. Testing user banning...")
    
    result = test_manager.banear_usuario("123456")
    banned_access = test_manager.verificar_acceso("123456")
    
    if result and not banned_access:
        print("   ✅ User banning works correctly")
    else:
        print("   ❌ User banning failed")
        return False
    
    print("\n5. Testing expired user cleanup...")
    
    test_manager.registrar_usuario("999999", "expireduser", "Expired User")
    
    users = test_manager._load_users()
    for user in users:
        if user["user_id"] == "999999":
            user["premium"] = True
            user["fecha_expiracion"] = (datetime.now() - timedelta(days=1)).isoformat()
    test_manager._save_users(users)
    
    cleaned_count = test_manager.limpiar_usuarios_expirados()
    expired_access = test_manager.verificar_acceso("999999")
    
    if cleaned_count > 0 and not expired_access:
        print("   ✅ Expired user cleanup works")
    else:
        print("   ❌ Expired user cleanup failed")
        return False
    
    print("\n6. Testing statistics...")
    
    stats = test_manager.obtener_estadisticas()
    
    if isinstance(stats, dict) and "total_usuarios" in stats:
        print(f"   ✅ Statistics work: {stats}")
    else:
        print("   ❌ Statistics failed")
        return False
    
    print("\n7. Testing legacy migration...")
    
    with open("test_usuarios_legacy.txt", "w", encoding="utf-8") as f:
        f.write("111111 - legacyuser - Legacy User\n")
        f.write("222222 - anotheruser - Another User\n")
    
    legacy_manager = AccessManager("test_usuarios_migrated.json")
    legacy_manager.legacy_file = "test_usuarios_legacy.txt"
    legacy_manager._migrate_from_legacy_if_needed()
    
    migrated_users = legacy_manager.listar_usuarios()
    
    if len(migrated_users) >= 2:
        print("   ✅ Legacy migration works")
    else:
        print("   ❌ Legacy migration failed")
        return False
    
    test_files = [
        "test_usuarios.json",
        "test_usuarios_migrated.json", 
        "test_usuarios_legacy.txt"
    ]
    
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
    
    for file in os.listdir("."):
        if file.startswith("test_usuarios_legacy_backup_"):
            os.remove(file)
    
    print("\n🎉 All VIP access system tests passed!")
    return True

def test_telegram_integration():
    """Test integration with telegram bot listener"""
    print("\n=== TESTING TELEGRAM INTEGRATION ===")
    
    try:
        from telegram_bot_listener import registrar_usuario, cargar_usuarios_registrados, contar_usuarios_registrados
        from access_manager import verificar_acceso, otorgar_acceso, banear_usuario
        
        print("\n1. Testing telegram functions import...")
        print("   ✅ All telegram functions imported successfully")
        
        print("\n2. Testing access management functions...")
        print("   ✅ All access management functions imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Integration error: {e}")
        return False

if __name__ == "__main__":
    success1 = test_vip_access_system()
    success2 = test_telegram_integration()
    
    if success1 and success2:
        print("\n🎉 ALL TESTS PASSED! VIP Access System is ready!")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
