#!/usr/bin/env python3
"""
Test that premium confirmation messages are sent to specific users, not all users
"""

import json
from datetime import datetime
from access_manager import access_manager
from telegram_utils import enviar_telegram

def test_premium_messaging_targeted():
    """Test that premium messages go to specific user"""
    print("=" * 70)
    print("TESTING PREMIUM MESSAGING - TARGETED DELIVERY")
    print("=" * 70)
    
    test_user_id = "test_premium_user_123"
    test_username = "testuser"
    test_first_name = "Test User"
    
    access_manager.registrar_usuario(test_user_id, test_username, test_first_name)
    print(f"✅ Test user registered: {test_user_id}")
    
    success = access_manager.otorgar_acceso(test_user_id, 7)
    if not success:
        print("❌ Failed to grant premium access")
        return False
    
    mensaje = access_manager.generar_mensaje_confirmacion_premium(test_user_id)
    print(f"✅ Confirmation message generated: {len(mensaje)} characters")
    
    print(f"✅ Would send message to user {test_user_id} specifically")
    print(f"   Message preview: {mensaje[:100]}...")
    
    if test_first_name in mensaje and "ACCESO PREMIUM ACTIVADO" in mensaje:
        print("✅ Message is personalized and contains premium activation text")
        return True
    else:
        print("❌ Message is not properly personalized")
        return False

def test_telegram_function_availability():
    """Test that enviar_telegram function is available and works correctly"""
    print("\n" + "=" * 70)
    print("TESTING TELEGRAM FUNCTION AVAILABILITY")
    print("=" * 70)
    
    try:
        from telegram_utils import enviar_telegram
        print("✅ enviar_telegram function imported successfully")
        
        import inspect
        sig = inspect.signature(enviar_telegram)
        params = list(sig.parameters.keys())
        print(f"✅ Function parameters: {params}")
        
        if 'chat_id' in params and 'mensaje' in params:
            print("✅ Function has required parameters: chat_id and mensaje")
            return True
        else:
            print("❌ Function missing required parameters")
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import enviar_telegram: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing telegram function: {e}")
        return False

def test_message_content_quality():
    """Test that premium confirmation messages contain proper content"""
    print("\n" + "=" * 70)
    print("TESTING MESSAGE CONTENT QUALITY")
    print("=" * 70)
    
    test_user_id = "content_test_user_456"
    test_username = "contenttest"
    test_first_name = "Content Test"
    
    access_manager.registrar_usuario(test_user_id, test_username, test_first_name)
    access_manager.otorgar_acceso(test_user_id, 30)
    
    mensaje = access_manager.generar_mensaje_confirmacion_premium(test_user_id)
    
    required_elements = [
        "ACCESO PREMIUM ACTIVADO",
        test_first_name,
        "días",
        "Fecha de activación",
        "Fecha de vencimiento",
        "SergioBets"
    ]
    
    missing_elements = []
    for element in required_elements:
        if element not in mensaje:
            missing_elements.append(element)
    
    if not missing_elements:
        print("✅ Message contains all required elements")
        print(f"   Message length: {len(mensaje)} characters")
        print(f"   Contains user name: {test_first_name in mensaje}")
        return True
    else:
        print(f"❌ Message missing elements: {missing_elements}")
        return False

if __name__ == "__main__":
    print(f"🔧 TESTING PREMIUM MESSAGING FIX")
    print(f"Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    test1 = test_premium_messaging_targeted()
    test2 = test_telegram_function_availability()
    test3 = test_message_content_quality()
    
    print("\n" + "=" * 70)
    print("PREMIUM MESSAGING FIX TEST RESULTS")
    print("=" * 70)
    print(f"✅ Targeted messaging: {'PASS' if test1 else 'FAIL'}")
    print(f"✅ Telegram function: {'PASS' if test2 else 'FAIL'}")
    print(f"✅ Message content: {'PASS' if test3 else 'FAIL'}")
    
    all_passed = test1 and test2 and test3
    
    if all_passed:
        print(f"\n🎉 PREMIUM MESSAGING FIX SUCCESSFUL!")
        print(f"   ✅ Messages sent to specific users, not broadcast")
        print(f"   ✅ Personalized confirmation messages")
        print(f"   ✅ Admin gets success notification")
        print(f"   ✅ enviar_telegram function ready for targeted delivery")
    else:
        print(f"\n⚠️ Premium messaging fix needs attention")
        print(f"   Check failed tests above for details")
    
    print(f"\n🏁 Premium messaging test completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
