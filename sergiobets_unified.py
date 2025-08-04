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
import logging
import traceback
from pathlib import Path

def setup_logging():
    """Setup comprehensive logging for debugging"""
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sergiobets_debug.log')
    
    logger = logging.getLogger('SergioBets')
    logger.setLevel(logging.DEBUG)
    
    file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()
logger.info("=== SergioBets Starting ===")
logger.info(f"Python version: {sys.version}")
logger.info(f"Platform: {sys.platform}")
logger.info(f"Working directory: {os.getcwd()}")
logger.info(f"Script path: {os.path.abspath(__file__)}")

try:
    logger.info("Importing required modules...")
    logger.debug("✅ All imports successful")
except Exception as e:
    logger.error(f"❌ Error during imports: {e}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    input("Press Enter to exit...")
    sys.exit(1)

class SergioBetsUnified:
    def __init__(self):
        logger.info("Initializing SergioBetsUnified...")
        try:
            self.webhook_thread = None
            self.ngrok_process = None
            self.bot_process = None
            self.ngrok_url = None
            self.running = True
            logger.info("✅ SergioBetsUnified initialized successfully")
        except Exception as e:
            logger.error(f"❌ Error initializing SergioBetsUnified: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
        
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Manejar señales de interrupción"""
        if not hasattr(self, '_stopping'):
            self._stopping = True
            logger.info("🛑 Signal received, stopping SergioBets...")
            print("\n🛑 Deteniendo SergioBets...")
            self.running = False
            self.stop_all_services()
            sys.exit(0)
    
    def check_dependencies(self):
        """Verificar dependencias necesarias"""
        logger.info("🔍 Checking dependencies...")
        print("🔍 Verificando dependencias...")
        
        try:
            required_files = [
                "pagos/webhook_server.py",
                "telegram_bot_listener.py",
                ".env"
            ]
            
            for file_path in required_files:
                logger.debug(f"Checking file: {file_path}")
                if not os.path.exists(file_path):
                    logger.error(f"❌ Required file not found: {file_path}")
                    print(f"❌ Archivo requerido no encontrado: {file_path}")
                    return False
                else:
                    logger.debug(f"✅ File found: {file_path}")
            
            try:
                logger.debug("Checking ngrok...")
                result = subprocess.run(["ngrok", "version"], capture_output=True, text=True, timeout=10)
                if result.returncode != 0:
                    logger.error(f"❌ ngrok not working: return code {result.returncode}")
                    print("❌ ngrok no está instalado o no está en PATH")
                    return False
                logger.info(f"✅ ngrok found: {result.stdout.strip()}")
                print(f"✅ ngrok encontrado: {result.stdout.strip()}")
            except FileNotFoundError:
                logger.error("❌ ngrok not found")
                print("❌ ngrok no está instalado")
                return False
            except subprocess.TimeoutExpired:
                logger.error("❌ ngrok timeout")
                print("❌ ngrok timeout")
                return False
            
            logger.info("✅ All dependencies verified")
            print("✅ Todas las dependencias verificadas")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error checking dependencies: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            print(f"❌ Error verificando dependencias: {e}")
            return False
    
    def start_webhook_server(self):
        """Iniciar servidor webhook"""
        logger.info("🚀 Starting webhook server...")
        print("🚀 Iniciando servidor webhook...")
        try:
            # Import and run webhook server directly instead of subprocess
            logger.debug("Importing webhook server...")
            from pagos.webhook_server import app
            logger.debug("✅ Webhook server imported successfully")
            
            def run_flask():
                try:
                    logger.info("Starting Flask app...")
                    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
                except Exception as e:
                    logger.error(f"❌ Error in Flask app: {e}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
            
            logger.debug("Creating webhook thread...")
            self.webhook_thread = threading.Thread(target=run_flask, daemon=True)
            self.webhook_thread.start()
            logger.debug("✅ Webhook thread started")
            
            logger.debug("Waiting 3 seconds for server to start...")
            time.sleep(3)
            
            try:
                logger.debug("Testing health endpoint...")
                response = requests.get("http://localhost:5000/health", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ Webhook server started successfully")
                    print("✅ Servidor webhook iniciado correctamente")
                    return True
                else:
                    logger.error(f"❌ Health check failed: {response.status_code}")
                    print(f"❌ Health check falló: {response.status_code}")
                    return False
            except Exception as e:
                logger.error(f"❌ Error checking webhook server: {e}")
                print(f"❌ Error verificando servidor webhook: {e}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting webhook server: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
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
    try:
        logger.info("=== Starting main function ===")
        print("🎯 SergioBets - Sistema Unificado de Pagos")
        print("=" * 60)
        
        logger.debug("Creating SergioBetsUnified instance...")
        app = SergioBetsUnified()
        
        logger.debug("Setting up signal handlers...")
        signal.signal(signal.SIGINT, app.signal_handler)
        signal.signal(signal.SIGTERM, app.signal_handler)
        
        logger.info("Running SergioBets application...")
        success = app.run()
        
        logger.info(f"Application finished with success: {success}")
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"❌ Critical error in main: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        print(f"❌ Error crítico: {e}")
        print("Ver sergiobets_debug.log para más detalles")
        input("Presiona Enter para salir...")
        return 1

if __name__ == "__main__":
    try:
        logger.info("=== SergioBets Application Starting ===")
        exit_code = main()
        logger.info(f"=== SergioBets Application Finished (exit code: {exit_code}) ===")
        
        if exit_code != 0:
            input("Presiona Enter para salir...")
        
        sys.exit(exit_code)
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        print(f"❌ Error fatal: {e}")
        print("Ver sergiobets_debug.log para más detalles")
        input("Presiona Enter para salir...")
        sys.exit(1)
