#!/usr/bin/env python3
"""
Debug script to investigate why launch_with_ngrok.py hangs at webhook server startup
"""

import subprocess
import sys
import time
import threading
import os

def test_webhook_startup_with_output():
    """Test webhook server startup with real-time output capture"""
    print("🔍 Testing webhook server startup with real-time output...")
    
    try:
        process = subprocess.Popen(
            [sys.executable, "pagos/start_webhook_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        def read_output():
            """Read output in real-time"""
            for line in iter(process.stdout.readline, ''):
                print(f"WEBHOOK OUTPUT: {line.strip()}")
        
        output_thread = threading.Thread(target=read_output, daemon=True)
        output_thread.start()
        
        print("⏳ Waiting 10 seconds for webhook server to start...")
        time.sleep(10)
        
        if process.poll() is None:
            print("✅ Webhook server process is still running")
            
            import requests
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
        else:
            print("❌ Webhook server process terminated")
            result = False
        
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)
        
        return result
        
    except Exception as e:
        print(f"❌ Exception in webhook startup test: {e}")
        return False

def test_launch_ngrok_subprocess():
    """Test the exact subprocess call that launch_with_ngrok.py uses"""
    print("\n🔍 Testing exact subprocess call from launch_with_ngrok.py...")
    
    try:
        process = subprocess.Popen([
            sys.executable, 'pagos/start_webhook_server.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        print("⏳ Waiting 5 seconds (same as launch_with_ngrok.py)...")
        time.sleep(5)
        
        if process.poll() is None:
            print("✅ Process still running after 5 seconds")
            
            try:
                stdout, stderr = process.communicate(timeout=5)
                print("❌ Process terminated during communicate()")
                if stdout:
                    print(f"STDOUT: {stdout}")
                if stderr:
                    print(f"STDERR: {stderr}")
                return False
            except subprocess.TimeoutExpired:
                print("⚠️ Process still running after communicate timeout")
                process.kill()
                return True
        else:
            print("❌ Process terminated early")
            stdout, stderr = process.communicate()
            if stdout:
                print(f"STDOUT: {stdout}")
            if stderr:
                print(f"STDERR: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Exception in launch ngrok subprocess test: {e}")
        return False

if __name__ == "__main__":
    print("🧪 SergioBets Launch Hanging Debug")
    print("=" * 60)
    
    test1_result = test_webhook_startup_with_output()
    
    test2_result = test_launch_ngrok_subprocess()
    
    print("\n" + "=" * 60)
    print("📊 Results:")
    print(f"Real-time output test: {'✅ SUCCESS' if test1_result else '❌ FAILED'}")
    print(f"Launch ngrok subprocess test: {'✅ SUCCESS' if test2_result else '❌ FAILED'}")
    
    if not test1_result and not test2_result:
        print("\n🔍 Both tests failed - webhook server has fundamental issues")
    elif test1_result and not test2_result:
        print("\n🔍 Real-time works but subprocess call fails - likely buffer/communication issue")
    elif not test1_result and test2_result:
        print("\n🔍 Subprocess works but real-time fails - likely threading issue")
    else:
        print("\n🔍 Both tests passed - issue might be elsewhere in launch_with_ngrok.py")
