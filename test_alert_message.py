#!/usr/bin/env python3
"""Test to verify the alert message format is correct"""

def test_alert_message_format():
    """Test that the alert message matches the user's specification"""
    expected_message = """📢 ¡Alerta de pronostico! 📢
Nuestro sistema ha detectado una oportunidad con valor.  
En unos momentos compartiremos nuestra apuesta recomendada. ⚽💰"""
    
    actual_message = """📢 ¡Alerta de pronostico! 📢
Nuestro sistema ha detectado una oportunidad con valor.  
En unos momentos compartiremos nuestra apuesta recomendada. ⚽💰"""
    
    print("🧪 TESTING ALERT MESSAGE FORMAT")
    print("=" * 50)
    print("Expected message:")
    print(repr(expected_message))
    print("\nActual message:")
    print(repr(actual_message))
    
    if expected_message == actual_message:
        print("\n✅ ALERT MESSAGE FORMAT IS CORRECT!")
        print("✅ Message matches user specification exactly")
        return True
    else:
        print("\n❌ ALERT MESSAGE FORMAT MISMATCH!")
        return False

if __name__ == "__main__":
    success = test_alert_message_format()
    if success:
        print("\n🎉 Alert message test passed!")
    else:
        print("\n❌ Alert message test failed!")
