#!/usr/bin/env python3
"""
Script de pruebas para el sistema de pagos NOWPayments
"""

import os
import json
import requests
from dotenv import load_dotenv
from payments import NOWPaymentsAPI, PaymentManager

load_dotenv()

def test_nowpayments_api():
    """Probar conexión con NOWPayments API"""
    print("🔧 Probando NOWPayments API...")
    
    api = NOWPaymentsAPI()
    
    currencies = api.get_available_currencies()
    print(f"✅ Monedas disponibles: {len(currencies)}")
    
    usdt_variants = [c for c in currencies if "usdt" in c.lower()]
    ltc_available = "ltc" in currencies
    
    print(f"💰 USDT variants: {usdt_variants}")
    print(f"🪙 LTC disponible: {ltc_available}")
    
    return len(currencies) > 0

def test_payment_creation():
    """Probar creación de pagos"""
    print("\n💳 Probando creación de pagos...")
    
    payment_manager = PaymentManager()
    
    test_payment = payment_manager.create_membership_payment(
        user_id="test_123",
        username="test_user",
        currency="ltc",
        membership_type="weekly"
    )
    
    if test_payment.get("success"):
        print("✅ Pago de prueba creado exitosamente")
        print(f"   Payment ID: {test_payment.get('payment_id')}")
        print(f"   Address: {test_payment.get('pay_address')}")
        print(f"   Amount: {test_payment.get('pay_amount')} {test_payment.get('pay_currency')}")
        return test_payment
    else:
        print(f"❌ Error creando pago: {test_payment.get('error')}")
        return None

def test_webhook_server():
    """Probar servidor de webhooks"""
    print("\n🌐 Probando servidor de webhooks...")
    
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor de webhooks funcionando")
            return True
        else:
            print(f"❌ Servidor respondió con código: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor de webhooks")
        print("   Asegúrate de ejecutar: python pagos/start_webhook_server.py")
        return False
    except Exception as e:
        print(f"❌ Error probando webhook: {e}")
        return False

def test_api_endpoint():
    """Probar endpoint de API"""
    print("\n🔧 Probando API endpoint...")
    
    test_data = {
        "user_id": "test_api_123",
        "username": "test_api_user",
        "currency": "ltc",
        "membership_type": "weekly"
    }
    
    try:
        response = requests.post(
            "http://localhost:5000/api/create_payment",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API endpoint funcionando")
            print(f"   Payment ID: {data.get('payment_id')}")
            return True
        else:
            print(f"❌ API respondió con código: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor API")
        return False
    except Exception as e:
        print(f"❌ Error probando API: {e}")
        return False

def main():
    """Ejecutar todas las pruebas"""
    print("🧪 SergioBets - Pruebas del Sistema de Pagos")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 4
    
    if test_nowpayments_api():
        tests_passed += 1
    
    if test_payment_creation():
        tests_passed += 1
    
    if test_webhook_server():
        tests_passed += 1
        
        if test_api_endpoint():
            tests_passed += 1
    else:
        print("⏭️  Saltando prueba de API endpoint (servidor no disponible)")
    
    print("\n" + "=" * 50)
    print(f"📊 Resultados: {tests_passed}/{total_tests} pruebas pasaron")
    
    if tests_passed == total_tests:
        print("🎉 ¡Todas las pruebas pasaron! Sistema listo para usar.")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa la configuración.")
    
    print("\n📋 Próximos pasos:")
    print("1. Ejecutar: python pagos/start_webhook_server.py")
    print("2. Exponer puerto 5000 públicamente (ngrok, etc.)")
    print("3. Configurar webhook URL en NOWPayments dashboard")
    print("4. Probar flujo completo desde Telegram bot")

if __name__ == "__main__":
    main()
