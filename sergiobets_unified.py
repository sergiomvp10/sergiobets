#!/usr/bin/env python3
"""
SergioBets - Sistema Unificado de Pagos NOWPayments
Aplicación única que maneja webhook server, ngrok tunnel y bot de Telegram
"""

import os
import sys
import time
import signal
import threading
import subprocess
import requests
import json
from pathlib import Path

class SergioBetsUnified:
    def __init__(self):
        self.webhook_thread = None
        self.ngrok_process = None
        self.bot_process = None
        self.ngrok_url = None
        self.running = True
        
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Manejar señales de interrupción"""
        print("\n🛑 Deteniendo SergioBets...")
        self.running = False
        self.stop_all_services()
        sys.exit(0)
    
    def check_dependencies(self):
        """Verificar dependencias necesarias"""
        print("🔍 Verificando dependencias...")
        
        required_files = [
            "pagos/webhook_server.py",
            "telegram_bot_listener.py",
            ".env"
        ]
        
        for file_path in required_files:
            if not os.path.exists(file_path):
                print(f"❌ Archivo requerido no encontrado: {file_path}")
                return False
        
        try:
            result = subprocess.run(["ngrok", "version"], capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ ngrok no está instalado o no está en PATH")
                return False
            print(f"✅ ngrok encontrado: {result.stdout.strip()}")
        except FileNotFoundError:
            print("❌ ngrok no está instalado")
            return False
        
        print("✅ Todas las dependencias verificadas")
        return True
    
    def start_webhook_server(self):
        """Iniciar servidor webhook"""
        print("🚀 Iniciando servidor webhook...")
        try:
            # Import and run webhook server directly instead of subprocess
            from pagos.webhook_server import app
            
            def run_flask():
                app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
            
            self.webhook_thread = threading.Thread(target=run_flask, daemon=True)
            self.webhook_thread.start()
            
            time.sleep(3)
            
            try:
                response = requests.get("http://localhost:5000/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Servidor webhook iniciado correctamente")
                    return True
                else:
                    print(f"❌ Health check falló: {response.status_code}")
                    return False
            except Exception as e:
                print(f"❌ Error verificando servidor webhook: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Error iniciando webhook server: {e}")
            return False
    
    def start_ngrok_tunnel(self):
        """Iniciar túnel ngrok"""
        print("🌐 Iniciando túnel ngrok...")
        try:
            self.ngrok_process = subprocess.Popen(
                ["ngrok", "http", "5000", "--log=stdout"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            time.sleep(5)
            
            self.ngrok_url = self.get_ngrok_url()
            if self.ngrok_url:
                print(f"✅ Túnel ngrok iniciado: {self.ngrok_url}")
                
                with open("ngrok_url.txt", "w") as f:
                    f.write(self.ngrok_url)
                
                return True
            else:
                print("❌ No se pudo obtener URL de ngrok")
                return False
                
        except Exception as e:
            print(f"❌ Error iniciando ngrok: {e}")
            return False
    
    def get_ngrok_url(self):
        """Obtener URL pública de ngrok"""
        try:
            response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=10)
            if response.status_code == 200:
                data = response.json()
                for tunnel in data.get("tunnels", []):
                    if tunnel.get("proto") == "https":
                        return tunnel.get("public_url")
        except:
            pass
        return None
    
    def start_telegram_bot(self):
        """Iniciar bot de Telegram"""
        print("🤖 Iniciando bot de Telegram...")
        try:
            self.bot_process = subprocess.Popen(
                [sys.executable, "telegram_bot_listener.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            time.sleep(2)
            print("✅ Bot de Telegram iniciado")
            return True
            
        except Exception as e:
            print(f"❌ Error iniciando bot de Telegram: {e}")
            return False
    
    def stop_all_services(self):
        """Detener todos los servicios"""
        print("🛑 Deteniendo servicios...")
        
        if self.bot_process:
            try:
                self.bot_process.terminate()
                self.bot_process.wait(timeout=5)
                print("✅ Bot de Telegram detenido")
            except:
                self.bot_process.kill()
        
        if self.ngrok_process:
            try:
                self.ngrok_process.terminate()
                self.ngrok_process.wait(timeout=5)
                print("✅ Túnel ngrok detenido")
            except:
                self.ngrok_process.kill()
        
        if hasattr(self, 'webhook_thread') and self.webhook_thread:
            print("✅ Servidor webhook detenido")
    
    def monitor_services(self):
        """Monitorear servicios en segundo plano"""
        while self.running:
            time.sleep(10)
            
            try:
                response = requests.get("http://localhost:5000/health", timeout=3)
                if response.status_code != 200:
                    print("⚠️ Servidor webhook no responde")
            except:
                print("⚠️ Servidor webhook no accesible")
            
            current_url = self.get_ngrok_url()
            if current_url != self.ngrok_url:
                print(f"⚠️ URL de ngrok cambió: {current_url}")
                self.ngrok_url = current_url
                if current_url:
                    with open("ngrok_url.txt", "w") as f:
                        f.write(current_url)
    
    def run(self):
        """Ejecutar aplicación principal"""
        print("🎯 SergioBets - Sistema Unificado de Pagos")
        print("=" * 60)
        
        if not self.check_dependencies():
            print("❌ Faltan dependencias. Abortando.")
            return False
        
        if not self.start_webhook_server():
            print("❌ No se pudo iniciar servidor webhook")
            return False
        
        if not self.start_ngrok_tunnel():
            print("❌ No se pudo iniciar túnel ngrok")
            self.stop_all_services()
            return False
        
        if not self.start_telegram_bot():
            print("❌ No se pudo iniciar bot de Telegram")
            self.stop_all_services()
            return False
        
        print("\n" + "=" * 60)
        print("🎉 ¡SergioBets iniciado correctamente!")
        print(f"🌐 URL pública: {self.ngrok_url}")
        print(f"📡 Webhook: {self.ngrok_url}/webhook/nowpayments")
        print(f"🔧 API: {self.ngrok_url}/api/create_payment")
        print("=" * 60)
        
        print("\n📋 Próximos pasos:")
        print("1. Configura esta URL en NOWPayments dashboard")
        print("2. El bot de Telegram ya está activo")
        print("3. ¡El sistema está listo para recibir pagos!")
        print("\n🛑 Presiona Ctrl+C para detener")
        
        monitor_thread = threading.Thread(target=self.monitor_services, daemon=True)
        monitor_thread.start()
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        
        self.stop_all_services()
        print("✅ SergioBets detenido correctamente")
        return True

def main():
    """Función principal"""
    app = SergioBetsUnified()
    success = app.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
