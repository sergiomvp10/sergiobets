#!/usr/bin/env python3
"""
Test IPN con payment ID real
"""

import requests
import json
import time

def test_real_ipn():
    """Test IPN con payment ID real creado anteriormente"""
    payment_id = "4452555658"
    
    print(f"🔍 Testing Real IPN for Payment ID: {payment_id}")
    
    ipn_payload = {
        "payment_id": payment_id,
        "payment_status": "confirmed",
        "pay_address": "MQ94yV6uG8u9jgkLssSGEpTVp4Zu7Y92Eb",
        "price_amount": 12.0,
        "price_currency": "usd",
        "pay_amount": 0.10685508,
        "pay_currency": "ltc",
        "order_id": f"sergiobets_test_user_123_{int(time.time())}",
        "order_description": "SergioBets VIP Membership - 7 days",
        "purchase_id": f"purchase_{payment_id}",
        "outcome_amount": 0.10685508,
        "outcome_currency": "ltc"
    }
    
    print("📤 Sending Real IPN payload:")
    print(json.dumps(ipn_payload, indent=2))
    
    try:
        response = requests.post(
            "http://localhost:5000/webhook/nowpayments",
            json=ipn_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Real IPN processed successfully")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Error processing real IPN: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error sending real IPN: {e}")
        return False

if __name__ == "__main__":
    test_real_ipn()
