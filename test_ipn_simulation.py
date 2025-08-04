#!/usr/bin/env python3
"""
Test de simulación IPN de NOWPayments
"""

import requests
import json
import time

def simulate_ipn_webhook(payment_id):
    """Simular IPN de NOWPayments"""
    print(f"🔍 Testing IPN Webhook Simulation for Payment {payment_id}")
    
    ipn_payload = {
        "payment_id": payment_id,
        "payment_status": "confirmed",
        "pay_address": "test_address_simulation",
        "price_amount": 12.0,
        "price_currency": "usd",
        "pay_amount": 0.10711851,
        "pay_currency": "ltc",
        "order_id": f"sergiobets_test_user_123_{int(time.time())}",
        "order_description": "SergioBets VIP Membership - 7 days",
        "purchase_id": f"purchase_{payment_id}",
        "outcome_amount": 0.10711851,
        "outcome_currency": "ltc"
    }
    
    print("📤 Sending IPN payload:")
    print(json.dumps(ipn_payload, indent=2))
    
    try:
        response = requests.post(
            "http://localhost:5000/webhook/nowpayments",
            json=ipn_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ IPN processed successfully")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Error processing IPN: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error sending IPN: {e}")
        return False

if __name__ == "__main__":
    simulate_ipn_webhook("test_payment_123")
