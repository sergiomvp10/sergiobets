#!/usr/bin/env python3
"""
Test complete VIP access integration with SergioBets
"""

import os
import json
import sys
from datetime import datetime, timedelta

def test_access_manager_integration():
    """Test access_manager integration with telegram bot"""
    print("=== TESTING ACCESS MANAGER INTEGRATION ===")
    
    try:
        from access_manager import access_manager, verificar_acceso, otorgar_acceso, banear_usuario
        print("✅ Access manager imports successful")
        
        from telegram_bot_listener import registrar_usuario, cargar_usuarios_registrados, contar_usuarios_registrados
        print("✅ Telegram bot integration imports successful")
        
        result = registrar_usuario("test123", "testuser", "Test User")
        print(f"✅ User registration: {result}")
        
        usuarios = cargar_usuarios_registrados()
        print(f"✅ User loading: {len(usuarios)} users loaded")
        
        count = contar_usuarios_registrados()
        print(f"✅ User counting: {count} users")
        
        if otorgar_acceso("test123", 7):
            print("✅ Premium access granting works")
        else:
            print("❌ Premium access granting failed")
            return False
        
        if verificar_acceso("test123"):
            print("✅ Access verification works")
        else:
            print("❌ Access verification failed")
            return False
        
        if banear_usuario("test123"):
            print("✅ User banning works")
        else:
            print("❌ User banning failed")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Integration error: {e}")
        return False

def test_premium_workflow():
    """Test complete premium access workflow"""
    print("\n=== TESTING PREMIUM WORKFLOW ===")
    
    try:
        from access_manager import access_manager
        
        user_id = "workflow_test_123"
        access_manager.registrar_usuario(user_id, "workflowuser", "Workflow User")
        
        if not access_manager.verificar_acceso(user_id):
            print("✅ Initial state: No premium access")
        else:
            print("❌ Initial state incorrect")
            return False
        
        if access_manager.otorgar_acceso(user_id, 7):
            print("✅ Premium access granted")
        else:
            print("❌ Failed to grant premium access")
            return False
        
        if access_manager.verificar_acceso(user_id):
            print("✅ Premium access verified")
        else:
            print("❌ Premium access verification failed")
            return False
        
        user_info = access_manager.obtener_usuario(user_id)
        if user_info and user_info.get('premium') and user_info.get('fecha_expiracion'):
            print("✅ User info contains premium data")
        else:
            print("❌ User info missing premium data")
            return False
        
        stats = access_manager.obtener_estadisticas()
        if stats.get('usuarios_premium', 0) > 0:
            print("✅ Statistics show premium users")
        else:
            print("❌ Statistics don't show premium users")
            return False
        
        if access_manager.banear_usuario(user_id):
            print("✅ User banned successfully")
        else:
            print("❌ Failed to ban user")
            return False
        
        if not access_manager.verificar_acceso(user_id):
            print("✅ Ban verified: No premium access")
        else:
            print("❌ Ban verification failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow error: {e}")
        return False

def test_data_migration():
    """Test data migration from usuarios.txt to usuarios.json"""
    print("\n=== TESTING DATA MIGRATION ===")
    
    try:
        from access_manager import AccessManager
        
        test_legacy_content = """123456 - testuser1 - Test User 1
789012 - testuser2 - Test User 2
555555 - testuser3 - Test User 3"""
        
        with open("test_legacy_usuarios.txt", "w", encoding="utf-8") as f:
            f.write(test_legacy_content)
        
        test_manager = AccessManager("test_migrated_usuarios.json")
        test_manager.legacy_file = "test_legacy_usuarios.txt"
        test_manager._migrate_from_legacy_if_needed()
        
        migrated_users = test_manager.listar_usuarios()
        
        if len(migrated_users) >= 3:
            print(f"✅ Migration successful: {len(migrated_users)} users migrated")
            
            for user in migrated_users[:1]:
                required_fields = ['user_id', 'username', 'first_name', 'premium', 'fecha_expiracion', 'fecha_registro']
                if all(field in user for field in required_fields):
                    print("✅ User structure is correct")
                    break
            else:
                print("❌ User structure is incorrect")
                return False
        else:
            print("❌ Migration failed")
            return False
        
        for file in ["test_legacy_usuarios.txt", "test_migrated_usuarios.json"]:
            if os.path.exists(file):
                os.remove(file)
        
        for file in os.listdir("."):
            if file.startswith("test_legacy_usuarios_backup_"):
                os.remove(file)
        
        return True
        
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return False

def main():
    """Run all VIP integration tests"""
    print("🎯 TESTING COMPLETE VIP ACCESS INTEGRATION")
    print("=" * 60)
    
    tests = [
        test_access_manager_integration,
        test_premium_workflow,
        test_data_migration
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS:")
    
    test_names = [
        "Access Manager Integration",
        "Premium Workflow",
        "Data Migration"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {i+1}. {name}: {status}")
    
    all_passed = all(results)
    
    if all_passed:
        print("\n🎉 ALL VIP INTEGRATION TESTS PASSED!")
        print("✅ VIP Access System is fully integrated and ready!")
    else:
        print("\n❌ Some integration tests failed.")
        print("🔧 Please check the implementation.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
