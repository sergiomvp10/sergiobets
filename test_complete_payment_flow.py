#!/usr/bin/env python3
"""
Test completo del flujo de pagos SergioBets
Simula el flujo completo: creación de pago → IPN webhook → activación VIP
"""

import os
import sys
import json
import time
import requests
from datetime import datetime

WEBHOOK_URL = "http://localhost:5000"
TEST_USER_ID = "987654321"
TEST_USERNAME = "test_user_devin"

def test_health_check():
    """Test 1: Verificar que el servidor esté corriendo"""
    print("🔍 Test 1: Health Check")
    try:
        response = requests.get(f"{WEBHOOK_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor webhook corriendo correctamente")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check falló: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        return False

def test_payment_creation():
    """Test 2: Crear un pago de prueba"""
    print("\n🔍 Test 2: Creación de Pago")
    try:
        payload = {
            "user_id": TEST_USER_ID,
            "username": TEST_USERNAME,
            "currency": "ltc",
            "membership_type": "weekly"
        }
        
        response = requests.post(
            f"{WEBHOOK_URL}/api/create_payment",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Pago creado exitosamente")
            print(f"   Payment ID: {data.get('payment_id')}")
            print(f"   Address: {data.get('pay_address')}")
            print(f"   Amount: {data.get('pay_amount')} {data.get('pay_currency')}")
            return data.get('payment_id')
        else:
            print(f"❌ Error creando pago: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error en creación de pago: {e}")
        return None

def test_payment_status(payment_id):
    """Test 3: Verificar estado del pago"""
    print(f"\n🔍 Test 3: Estado del Pago {payment_id}")
    try:
        response = requests.get(f"{WEBHOOK_URL}/api/payment_status/{payment_id}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Estado del pago obtenido")
            print(f"   Status: {data.get('payment_status', 'unknown')}")
            return data
        else:
            print(f"❌ Error obteniendo estado: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error verificando estado: {e}")
        return None

def simulate_nowpayments_ipn(payment_id):
    """Test 4: Simular IPN de NOWPayments"""
    print(f"\n🔍 Test 4: Simulación IPN NOWPayments")
    
    ipn_payload = {
        "payment_id": payment_id,
        "payment_status": "confirmed",
        "pay_address": "test_address_123",
        "price_amount": 12.0,
        "price_currency": "usd",
        "pay_amount": 0.10711851,
        "pay_currency": "ltc",
        "order_id": f"sergiobets_{TEST_USER_ID}_{int(time.time())}",
        "order_description": "SergioBets VIP Membership - 7 days",
        "purchase_id": f"purchase_{payment_id}",
        "outcome_amount": 0.10711851,
        "outcome_currency": "ltc"
    }
    
    print(f"📤 Enviando IPN payload:")
    print(json.dumps(ipn_payload, indent=2))
    
    try:
        response = requests.post(
            f"{WEBHOOK_URL}/webhook/nowpayments",
            json=ipn_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ IPN procesado exitosamente")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Error procesando IPN: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error enviando IPN: {e}")
        return False

def test_vip_users():
    """Test 5: Verificar usuarios VIP"""
    print("\n🔍 Test 5: Verificar Usuarios VIP")
    try:
        response = requests.get(f"{WEBHOOK_URL}/api/vip_users", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Lista de usuarios VIP obtenida")
            print(f"   Total usuarios VIP: {len(data)}")
            
            test_user_found = False
            for user in data:
                if user.get('user_id') == TEST_USER_ID:
                    test_user_found = True
                    print(f"   ✅ Usuario de prueba encontrado: {user}")
                    break
            
            if not test_user_found:
                print(f"   ⚠️ Usuario de prueba {TEST_USER_ID} no encontrado en VIP")
            
            return data
        else:
            print(f"❌ Error obteniendo usuarios VIP: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error verificando usuarios VIP: {e}")
        return None

def test_payment_history():
    """Test 6: Verificar historial de pagos"""
    print("\n🔍 Test 6: Historial de Pagos")
    try:
        response = requests.get(f"{WEBHOOK_URL}/api/payment_history", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Historial de pagos obtenido")
            print(f"   Total pagos registrados: {len(data)}")
            
            test_payment_found = False
            for payment in data:
                if payment.get('user_id') == TEST_USER_ID:
                    test_payment_found = True
                    print(f"   ✅ Pago de prueba encontrado: {payment}")
                    break
            
            if not test_payment_found:
                print(f"   ⚠️ Pago de prueba para usuario {TEST_USER_ID} no encontrado")
            
            return data
        else:
            print(f"❌ Error obteniendo historial: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error verificando historial: {e}")
        return None

def main():
    """Ejecutar todos los tests del flujo de pagos"""
    print("🎯 SergioBets - Test Completo del Sistema de Pagos")
    print("=" * 60)
    
    if not test_health_check():
        print("\n❌ FALLO: Servidor webhook no está corriendo")
        print("   Ejecuta: python pagos/start_webhook_server.py")
        return False
    
    payment_id = test_payment_creation()
    if not payment_id:
        print("\n❌ FALLO: No se pudo crear el pago")
        return False
    
    test_payment_status(payment_id)
    
    if not simulate_nowpayments_ipn(payment_id):
        print("\n❌ FALLO: IPN no fue procesado correctamente")
        return False
    
    print("\n⏳ Esperando procesamiento...")
    time.sleep(2)
    
    test_vip_users()
    
    test_payment_history()
    
    print("\n" + "=" * 60)
    print("🎉 Test completo finalizado")
    print("📋 Revisa los resultados arriba para verificar el flujo")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    main()
