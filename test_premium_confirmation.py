#!/usr/bin/env python3
"""
Test premium confirmation message functionality
"""

import sys
from datetime import datetime

def test_confirmation_message():
    """Test premium confirmation message generation"""
    print("=== TESTING PREMIUM CONFIRMATION MESSAGE ===")
    
    try:
        from access_manager import access_manager
        
        test_user_id = "confirmation_test_123"
        access_manager.registrar_usuario(test_user_id, "testuser", "Test User")
        print("✅ Test user registered")
        
        if access_manager.otorgar_acceso(test_user_id, 7):
            print("✅ Premium access granted")
        else:
            print("❌ Failed to grant premium access")
            return False
        
        mensaje = access_manager.generar_mensaje_confirmacion_premium(test_user_id)
        
        if mensaje and "ACCESO PREMIUM ACTIVADO" in mensaje:
            print("✅ Confirmation message generated successfully")
            print("\n" + "="*60)
            print("MENSAJE DE CONFIRMACIÓN GENERADO:")
            print("="*60)
            print(mensaje)
            print("="*60)
            
            required_elements = [
                "ACCESO PREMIUM ACTIVADO",
                "Días adquiridos:",
                "Fecha de activación:",
                "Fecha de vencimiento:",
                "Gracias por confiar en BetGeniuX"
            ]
            
            for element in required_elements:
                if element in mensaje:
                    print(f"✅ Contains: {element}")
                else:
                    print(f"❌ Missing: {element}")
                    return False
            
            return True
        else:
            print("❌ Failed to generate confirmation message")
            return False
            
    except Exception as e:
        print(f"❌ Error testing confirmation message: {e}")
        return False

def test_confirmation_edge_cases():
    """Test confirmation message edge cases"""
    print("\n=== TESTING CONFIRMATION EDGE CASES ===")
    
    try:
        from access_manager import access_manager
        
        mensaje = access_manager.generar_mensaje_confirmacion_premium("nonexistent_user")
        if "Usuario no encontrado" in mensaje:
            print("✅ Handles non-existent user correctly")
        else:
            print("❌ Failed to handle non-existent user")
            return False
        
        test_user_id = "no_premium_test"
        access_manager.registrar_usuario(test_user_id, "nopremium", "No Premium User")
        
        mensaje = access_manager.generar_mensaje_confirmacion_premium(test_user_id)
        if "no tiene acceso premium activo" in mensaje:
            print("✅ Handles user without premium correctly")
        else:
            print("❌ Failed to handle user without premium")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing edge cases: {e}")
        return False

def main():
    """Run all confirmation message tests"""
    print("🎯 TESTING PREMIUM CONFIRMATION MESSAGE SYSTEM")
    print("=" * 60)
    
    tests = [
        test_confirmation_message,
        test_confirmation_edge_cases
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
        "Premium Confirmation Message",
        "Confirmation Edge Cases"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {i+1}. {name}: {status}")
    
    all_passed = all(results)
    
    if all_passed:
        print("\n🎉 ALL CONFIRMATION MESSAGE TESTS PASSED!")
        print("✅ Premium confirmation system is ready!")
    else:
        print("\n❌ Some confirmation tests failed.")
        print("🔧 Please check the implementation.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
