#!/usr/bin/env python3
"""Test bot user traceability system"""

from access_manager import access_manager

def test_bot_user_traceability():
    """Test that users are properly tracked by bot_username"""
    print("🧪 TESTING BOT USER TRACEABILITY")
    print("=" * 50)
    
    test_user_id = "test_traceability_123"
    success = access_manager.registrar_usuario(test_user_id, "testuser", "Test User", "BetGeniuXbot")
    
    if success:
        print("✅ User registration with bot_username works")
    else:
        print("❌ User registration failed")
        return False
    
    usuarios_bot = access_manager.listar_usuarios_por_bot("BetGeniuXbot")
    found_user = any(user["user_id"] == test_user_id for user in usuarios_bot)
    
    if found_user:
        print("✅ Bot-specific user listing works")
    else:
        print("❌ Bot-specific user listing failed")
        return False
    
    count = access_manager.contar_usuarios_por_bot("BetGeniuXbot")
    if count > 0:
        print(f"✅ Bot user counting works: {count} usuarios")
    else:
        print("❌ Bot user counting failed")
        return False
    
    user = access_manager.obtener_usuario(test_user_id)
    if user and user.get("bot_username") == "BetGeniuXbot":
        print("✅ User has correct bot_username traceability")
    else:
        print("❌ User bot_username traceability failed")
        return False
    
    print("\n🎉 Bot user traceability system working correctly!")
    return True

if __name__ == "__main__":
    test_bot_user_traceability()
