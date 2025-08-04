#!/usr/bin/env python3
"""
SergioBets - Launcher con ngrok
Inicia el servidor webhook y configura túnel ngrok automáticamente
"""

import os
import sys
import time
import json
import requests
import subprocess
import threading
from pathlib import Path

WEBHOOK_PORT = 5000
NGROK_API_URL = "http://127.0.0.1:4040/api/tunnels"
NGROK_URL_FILE = "ngrok_url.txt"

class NgrokManager:
    def __init__(self):
        self.webhook_process = None
        self.ngrok_process = None
        self.public_url = None
        
    def check_ngrok_installed(self):
        """Verificar si ngrok está instalado"""
        try:
            result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def start_webhook_server(self):
        """Iniciar servidor webhook en background"""
        print("🚀 Iniciando servidor webhook...")
        try:
            self.webhook_process = subprocess.Popen([
                sys.executable, 'pagos/start_webhook_server.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            time.sleep(3)
            
            if self.webhook_process.poll() is None:
                print("✅ Servidor webhook iniciado correctamente")
                return True
            else:
                print("❌ Error iniciando servidor webhook")
                return False
        except Exception as e:
            print(f"❌ Error iniciando servidor: {e}")
            return False
    
    def start_ngrok_tunnel(self):
        """Iniciar túnel ngrok"""
        print("🌐 Iniciando túnel ngrok...")
        try:
            self.ngrok_process = subprocess.Popen([
                'ngrok', 'http', str(WEBHOOK_PORT)
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            time.sleep(5)
            
            if self.ngrok_process.poll() is None:
                print("✅ Túnel ngrok iniciado correctamente")
                return True
            else:
                stdout, stderr = self.ngrok_process.communicate()
                print("❌ Error iniciando túnel ngrok")
                if stderr:
                    print(f"🔍 Error details: {stderr.decode()}")
                if stdout:
                    print(f"🔍 Output: {stdout.decode()}")
                return False
        except Exception as e:
            print(f"❌ Error iniciando ngrok: {e}")
            return False
    
    def get_ngrok_url(self, max_retries=10):
        """Obtener URL pública de ngrok desde su API"""
        print("🔍 Obteniendo URL pública de ngrok...")
        
        for attempt in range(max_retries):
            try:
                response = requests.get(NGROK_API_URL, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    tunnels = data.get('tunnels', [])
                    
                    for tunnel in tunnels:
                        if tunnel.get('proto') == 'https':
                            self.public_url = tunnel.get('public_url')
                            print(f"✅ URL pública obtenida: {self.public_url}")
                            return self.public_url
                
                print(f"⏳ Intento {attempt + 1}/{max_retries} - Esperando ngrok...")
                time.sleep(2)
                
            except requests.exceptions.RequestException as e:
                print(f"⏳ Intento {attempt + 1}/{max_retries} - API ngrok no disponible")
                time.sleep(2)
        
        print("❌ No se pudo obtener la URL de ngrok")
        return None
    
    def save_ngrok_url(self):
        """Guardar URL de ngrok en archivo"""
        if self.public_url:
            try:
                with open(NGROK_URL_FILE, 'w') as f:
                    f.write(self.public_url)
                print(f"💾 URL guardada en {NGROK_URL_FILE}")
            except Exception as e:
                print(f"❌ Error guardando URL: {e}")
    
    def load_ngrok_url(self):
        """Cargar URL de ngrok desde archivo"""
        try:
            if os.path.exists(NGROK_URL_FILE):
                with open(NGROK_URL_FILE, 'r') as f:
                    url = f.read().strip()
                    if url:
                        self.public_url = url
                        return url
        except Exception as e:
            print(f"⚠️ Error cargando URL guardada: {e}")
        return None
    
    def check_ngrok_running(self):
        """Verificar si ngrok está corriendo"""
        try:
            response = requests.get(NGROK_API_URL, timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def stop_services(self):
        """Detener servicios"""
        print("\n🛑 Deteniendo servicios...")
        
        if self.webhook_process:
            self.webhook_process.terminate()
            print("✅ Servidor webhook detenido")
        
        if self.ngrok_process:
            self.ngrok_process.terminate()
            print("✅ Túnel ngrok detenido")
    
    def launch(self):
        """Lanzar sistema completo"""
        print("🎯 SergioBets - Launcher con ngrok")
        print("=" * 50)
        
        if not self.check_ngrok_installed():
            print("❌ ngrok no está instalado")
            print("📥 Instala ngrok desde: https://ngrok.com/download")
            return False
        
        if self.check_ngrok_running():
            print("🔄 ngrok ya está corriendo, obteniendo URL...")
            url = self.get_ngrok_url()
            if url:
                self.save_ngrok_url()
                print(f"✅ Sistema listo con URL: {url}")
                return True
        
        if not self.start_webhook_server():
            return False
        
        if not self.start_ngrok_tunnel():
            self.stop_services()
            return False
        
        url = self.get_ngrok_url()
        if not url:
            self.stop_services()
            return False
        
        self.save_ngrok_url()
        
        print("\n" + "=" * 50)
        print("🎉 ¡Sistema iniciado correctamente!")
        print(f"🌐 URL pública: {self.public_url}")
        print(f"📡 Webhook endpoint: {self.public_url}/webhook/nowpayments")
        print(f"🔧 API endpoint: {self.public_url}/api/create_payment")
        print("=" * 50)
        print("\n📋 Próximos pasos:")
        print("1. Configura esta URL en NOWPayments dashboard")
        print("2. Inicia tu bot de Telegram")
        print("3. ¡El sistema está listo para recibir pagos!")
        print("\n⚠️  Mantén esta terminal abierta para que el túnel funcione")
        print("🛑 Presiona Ctrl+C para detener")
        
        return True

def get_current_ngrok_url():
    """Función helper para obtener URL actual de ngrok"""
    try:
        if os.path.exists(NGROK_URL_FILE):
            with open(NGROK_URL_FILE, 'r') as f:
                return f.read().strip()
    except:
        pass
    return None

def main():
    manager = NgrokManager()
    
    try:
        if manager.launch():
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo sistema...")
        manager.stop_services()
        print("✅ Sistema detenido correctamente")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        manager.stop_services()

if __name__ == "__main__":
    main()
