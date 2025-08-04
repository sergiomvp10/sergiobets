#!/usr/bin/env python3
"""
Debug script to test webhook server startup and capture exact error output
"""

import subprocess
import sys
import time
import requests

def test_subprocess_webhook():
    """Test running start_webhook_server.py via subprocess and capture errors"""
    print("🔍 Testing subprocess execution of start_webhook_server.py...")
    try:
        process = subprocess.Popen(
            [sys.executable, "pagos/start_webhook_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        time.sleep(5)
        
        if process.poll() is None:
            print("✅ Subprocess webhook server is running")
            
            try:
                response = requests.get("http://localhost:5000/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Health endpoint responding")
                    result = True
                else:
                    print(f"❌ Health endpoint error: {response.status_code}")
                    result = False
            except Exception as e:
                print(f"❌ Health endpoint failed: {e}")
                result = False
            
            process.terminate()
            process.wait()
            return result
        else:
            stdout, stderr = process.communicate()
            print("❌ Subprocess webhook server failed to start")
            if stdout:
                print(f"STDOUT:\n{stdout}")
            if stderr:
                print(f"STDERR:\n{stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Exception running subprocess webhook: {e}")
        return False

if __name__ == "__main__":
    print("🧪 SergioBets Webhook Startup Debug")
    print("=" * 50)
    
    subprocess_result = test_subprocess_webhook()
    
    print("\n" + "=" * 50)
    print("📊 Results:")
    print(f"Subprocess start_webhook_server.py: {'✅ SUCCESS' if subprocess_result else '❌ FAILED'}")
