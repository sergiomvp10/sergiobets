#!/usr/bin/env python3
"""
Test de creación de pagos para verificar endpoint
"""

import requests
import json

def test_payment_creation():
    """Test crear un pago via API"""
    print("🔍 Testing Payment Creation API")
    
    payload = {
        "user_id": "test_user_123",
        "username": "test_devin",
        "currency": "ltc",
        "membership_type": "weekly"
    }
    
    try:
        response = requests.post(
            "http://localhost:5000/api/create_payment",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Payment created successfully")
            print(f"   Payment ID: {data.get('payment_id')}")
            print(f"   Address: {data.get('pay_address')}")
            print(f"   Amount: {data.get('pay_amount')} {data.get('pay_currency')}")
            return data.get('payment_id')
        else:
            print(f"❌ Error creating payment: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error in payment creation: {e}")
        return None

if __name__ == "__main__":
    test_payment_creation()
