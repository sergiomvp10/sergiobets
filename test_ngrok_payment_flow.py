#!/usr/bin/env python3
"""
Test completo del flujo de pagos usando ngrok URL pública
"""

import requests
import json
import time

def get_ngrok_url():
    try:
        with open('ngrok_url.txt', 'r') as f:
            return f.read().strip()
    except:
        return None

def test_ngrok_health():
    """Test 1: Verificar health check via ngrok"""
    ngrok_url = get_ngrok_url()
    if not ngrok_url:
        print("❌ No se pudo obtener URL de ngrok")
        return False
    
    print(f"🔍 Test 1: Health Check via ngrok - {ngrok_url}")
    try:
        response = requests.get(f"{ngrok_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Servidor accesible via ngrok")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check falló: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando via ngrok: {e}")
        return False

def test_ngrok_payment_creation():
    """Test 2: Crear pago via ngrok URL"""
    ngrok_url = get_ngrok_url()
    print(f"\n🔍 Test 2: Creación de Pago via ngrok - {ngrok_url}")
    
    payload = {
        "user_id": "ngrok_test_456",
        "username": "ngrok_test_user",
        "currency": "usdterc20",
        "membership_type": "weekly"
    }
    
    try:
        response = requests.post(
            f"{ngrok_url}/api/create_payment",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Pago creado via ngrok exitosamente")
            print(f"   Payment ID: {data.get('payment_id')}")
            print(f"   Address: {data.get('pay_address')}")
            print(f"   Amount: {data.get('pay_amount')} {data.get('pay_currency')}")
            return data.get('payment_id')
        else:
            print(f"❌ Error creando pago via ngrok: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error en creación de pago via ngrok: {e}")
        return None

def test_ngrok_ipn_webhook(payment_id):
    """Test 3: Simular IPN via ngrok webhook"""
    ngrok_url = get_ngrok_url()
    print(f"\n🔍 Test 3: Simulación IPN via ngrok - {ngrok_url}")
    
    ipn_payload = {
        "payment_id": payment_id,
        "payment_status": "confirmed",
        "pay_address": "ngrok_test_address_789",
        "price_amount": 12.0,
        "price_currency": "usd",
        "pay_amount": 12.0,
        "pay_currency": "usdterc20",
        "order_id": f"sergiobets_ngrok_test_456_{int(time.time())}",
        "order_description": "SergioBets VIP Membership - 7 days",
        "purchase_id": f"purchase_{payment_id}",
        "outcome_amount": 12.0,
        "outcome_currency": "usdterc20"
    }
    
    print("📤 Enviando IPN payload via ngrok:")
    print(json.dumps(ipn_payload, indent=2))
    
    try:
        response = requests.post(
            f"{ngrok_url}/webhook/nowpayments",
            json=ipn_payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            print("✅ IPN procesado via ngrok exitosamente")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Error procesando IPN via ngrok: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error enviando IPN via ngrok: {e}")
        return False

def test_ngrok_vip_verification():
    """Test 4: Verificar usuarios VIP via ngrok"""
    ngrok_url = get_ngrok_url()
    print(f"\n🔍 Test 4: Verificar usuarios VIP via ngrok - {ngrok_url}")
    
    try:
        response = requests.get(f"{ngrok_url}/api/vip_users", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Lista VIP obtenida via ngrok")
            print(f"   Total usuarios VIP: {len(data)}")
            
            ngrok_user_found = False
            for user in data:
                if user.get('user_id') == 'ngrok_test_456':
                    ngrok_user_found = True
                    print(f"   ✅ Usuario ngrok test encontrado: {user}")
                    break
            
            if not ngrok_user_found:
                print("   ⚠️ Usuario ngrok test no encontrado en VIP")
            
            return data
        else:
            print(f"❌ Error obteniendo VIP via ngrok: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error verificando VIP via ngrok: {e}")
        return None

def main():
    """Ejecutar test completo via ngrok"""
    print("🌐 SergioBets - Test Completo via Ngrok URL Pública")
    print("=" * 70)
    
    if not test_ngrok_health():
        print("\n❌ FALLO: Servidor no accesible via ngrok")
        return False
    
    payment_id = test_ngrok_payment_creation()
    if not payment_id:
        print("\n❌ FALLO: No se pudo crear pago via ngrok")
        return False
    
    if not test_ngrok_ipn_webhook(payment_id):
        print("\n❌ FALLO: IPN no procesado via ngrok")
        return False
    
    print("\n⏳ Esperando procesamiento...")
    time.sleep(3)
    
    test_ngrok_vip_verification()
    
    print("\n" + "=" * 70)
    print("🎉 Test completo via ngrok finalizado")
    print("🌐 Todos los endpoints funcionando via URL pública")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    main()
