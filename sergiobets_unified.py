#!/usr/bin/env python3
"""
SergioBets - Sistema Completo con GUI y Pagos NOWPayments
Aplicación única que maneja GUI, webhook server, ngrok tunnel y bot de Telegram
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
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from tkcalendar import DateEntry
import pygame
from datetime import date, timedelta, datetime
from dotenv import load_dotenv, find_dotenv

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)
load_dotenv(find_dotenv(filename=".env", usecwd=True), override=True)

from footystats_api import obtener_partidos_del_dia
from json_storage import guardar_json, cargar_json
from telegram_utils import enviar_telegram, enviar_telegram_masivo
from ia_bets import filtrar_apuestas_inteligentes, generar_mensaje_ia, simular_datos_prueba, limpiar_cache_predicciones, guardar_prediccion_historica
from league_utils import detectar_liga_por_imagen
from track_record import TrackRecordManager

class ScrollableFrame(ttk.Frame):
    """Frame con scroll vertical para listas dinámicas"""
    def __init__(self, parent, style='TFrame', padding=0, bg='#F3F4F6', *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, bg=bg)
        self.vsb = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.inner = ttk.Frame(self.canvas, style=style, padding=padding)
        
        self.inner_id = self.canvas.create_window((0, 0), window=self.inner, anchor='nw')
        self.canvas.configure(yscrollcommand=self.vsb.set)
        
        self.canvas.grid(row=0, column=0, sticky='nsew')
        self.vsb.grid(row=0, column=1, sticky='ns')
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.inner.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfigure(self.inner_id, width=self.canvas.winfo_width()))
        
        self.canvas.bind_all('<MouseWheel>', self._on_mousewheel)
        self.canvas.bind_all('<Button-4>', self._on_mousewheel_linux)
        self.canvas.bind_all('<Button-5>', self._on_mousewheel_linux)
    
    def _on_mousewheel(self, event):
        delta = int(-1*(event.delta/120)) if event.delta else 0
        self.canvas.yview_scroll(delta, 'units')
    
    def _on_mousewheel_linux(self, event):
        self.canvas.yview_scroll(-1 if event.num == 4 else 1, 'units')
    
    def update_theme(self, bg_color):
        """Actualiza el color de fondo del canvas"""
        self.canvas.config(bg=bg_color)

class ThemeManager:
    """Gestiona temas claro y oscuro para la aplicación"""
    def __init__(self, root):
        from tkinter import font as tkfont
        self.root = root
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.base_font = tkfont.nametofont('TkDefaultFont')
        self.base_font.configure(family='Segoe UI', size=10)
        self.heading_font = tkfont.Font(family='Segoe UI', size=11, weight='bold')
        self.title_font = tkfont.Font(family='Segoe UI', size=14, weight='bold')
        
        self.light = dict(
            bg="#F3F4F6",
            surface="#FFFFFF",
            fg="#111827",
            muted="#6B7280",
            primary="#2563EB",
            primary_hover="#1D4ED8",
            accent="#10B981",
            border="#E5E7EB",
            button_bg="#2563EB",
            button_fg="#FFFFFF",
            entry_bg="#FFFFFF",
            entry_fg="#111827",
            output_bg="#F0F9FF",
            secondary_bg="#F9FAFB"
        )
        
        self.dark = dict(
            bg="#0B1220",
            surface="#111827",
            fg="#E5E7EB",
            muted="#9CA3AF",
            primary="#3B82F6",
            primary_hover="#1D4ED8",
            accent="#22C55E",
            border="#374151",
            button_bg="#3B82F6",
            button_fg="#FFFFFF",
            entry_bg="#1F2937",
            entry_fg="#E5E7EB",
            output_bg="#1F2937",
            secondary_bg="#0F172A"
        )
        
        self.current_mode = 'light'
    
    def apply(self, mode='light'):
        """Aplica el tema especificado"""
        self.current_mode = mode
        p = self.light if mode == 'light' else self.dark
        
        self.root.configure(bg=p['bg'])
        
        self.style.configure('TFrame', background=p['bg'])
        self.style.configure('Surface.TFrame', background=p['surface'], relief='flat')
        self.style.configure('Toolbar.TFrame', background=p['surface'], relief='flat')
        self.style.configure('Card.TFrame', background=p['surface'], relief='solid', borderwidth=1)
        self.style.configure('Header.TFrame', background=p['primary'], relief='flat')
        
        self.style.configure('TLabel', background=p['surface'], foreground=p['fg'], font=('Segoe UI', 10))
        self.style.configure('Muted.TLabel', background=p['surface'], foreground=p['muted'])
        self.style.configure('Title.TLabel', background=p['surface'], foreground=p['fg'], font=('Segoe UI', 14, 'bold'))
        self.style.configure('ItemTitle.TLabel', background=p['surface'], foreground=p['fg'], font=('Segoe UI', 11, 'bold'))
        self.style.configure('ItemSub.TLabel', background=p['surface'], foreground=p['muted'], font=('Segoe UI', 10))
        self.style.configure('Header.TLabel', background=p['primary'], foreground=p['button_fg'], font=('Segoe UI', 12, 'bold'))
        
        self.style.configure('TButton',
                           background=p['button_bg'],
                           foreground=p['button_fg'],
                           borderwidth=0,
                           padding=(12, 8),
                           font=('Segoe UI', 10, 'bold'))
        self.style.map('TButton',
                      background=[('active', p['primary_hover']), ('pressed', p['primary_hover'])],
                      foreground=[('disabled', p['muted'])])
        
        self.style.configure('Secondary.TButton',
                           background=p['secondary_bg'],
                           foreground=p['fg'],
                           borderwidth=1,
                           padding=(10, 6),
                           font=('Segoe UI', 10))
        self.style.map('Secondary.TButton',
                      background=[('active', p['surface']), ('pressed', p['surface'])])
        
        self.style.configure('TEntry',
                           fieldbackground=p['entry_bg'],
                           foreground=p['entry_fg'],
                           borderwidth=1,
                           relief='solid')
        self.style.configure('TCombobox',
                           fieldbackground=p['entry_bg'],
                           foreground=p['entry_fg'],
                           background=p['surface'],
                           borderwidth=1,
                           arrowcolor=p['fg'])
        self.style.map('TCombobox',
                      fieldbackground=[('readonly', p['entry_bg'])],
                      selectbackground=[('readonly', p['primary'])],
                      selectforeground=[('readonly', p['button_fg'])])
        
        self.style.configure('TNotebook',
                           background=p['bg'],
                           borderwidth=0,
                           tabmargins=(6, 6, 6, 0))
        self.style.configure('TNotebook.Tab',
                           padding=(16, 10),
                           background=p['secondary_bg'],
                           foreground=p['fg'],
                           borderwidth=0,
                           font=('Segoe UI', 10, 'bold'))
        self.style.map('TNotebook.Tab',
                      background=[('selected', p['primary'])],
                      foreground=[('selected', p['button_fg'])],
                      expand=[('selected', (1, 1, 1, 0))])
        
        self.style.configure('Toggle.TCheckbutton',
                           background=p['surface'],
                           foreground=p['fg'],
                           font=('Segoe UI', 10))
        self.style.map('Toggle.TCheckbutton',
                      background=[('active', p['surface'])])
        
        self.style.configure('TSeparator', background=p['border'])
        
        self.style.configure('Vertical.TScrollbar', background=p['surface'], troughcolor=p['bg'])
        self.style.configure('Horizontal.TScrollbar', background=p['surface'], troughcolor=p['bg'])
        
        return p

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
            self.bot_thread = None
            self.ngrok_process = None
            self.ngrok_url = None
            self.running = True
            
            try:
                from daily_counter import reset_daily_counter, get_current_date, load_counter_data
                counter_data = load_counter_data()
                if counter_data.get("date") != get_current_date():
                    reset_daily_counter()
                    logger.info("✅ Daily counter reset for new day")
            except ImportError:
                logger.warning("⚠️ Daily counter module not available")
                pass
            
            logger.info("✅ SergioBetsUnified initialized successfully")
        except Exception as e:
            logger.error(f"❌ Error initializing SergioBetsUnified: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
        
        self.cleanup_cache_periodically()
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
        logger.info("🤖 Starting Telegram bot...")
        print("🤖 Iniciando bot de Telegram...")
        try:
            # Import and run the bot directly instead of subprocess
            logger.debug("Importing telegram bot...")
            
            def run_bot():
                try:
                    logger.info("Starting Telegram bot in thread...")
                    # Import and call the bot listener function directly
                    import sys
                    import asyncio
                    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
                    
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    # Import the iniciar_bot_en_hilo function which is designed for threading
                    from telegram_bot_listener import iniciar_bot_en_hilo
                    logger.info("Successfully imported iniciar_bot_en_hilo")
                    
                    logger.info("Calling iniciar_bot_en_hilo()...")
                    iniciar_bot_en_hilo()
                    
                except Exception as e:
                    logger.error(f"❌ Error in Telegram bot thread: {e}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
            
            logger.debug("Creating bot thread...")
            self.bot_thread = threading.Thread(target=run_bot, daemon=True)
            self.bot_thread.start()
            logger.debug("✅ Bot thread started")
            
            logger.debug("Waiting 3 seconds for bot to initialize...")
            time.sleep(3)
            
            logger.info("✅ Telegram bot started successfully")
            print("✅ Bot de Telegram iniciado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error starting Telegram bot: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            print(f"❌ Error iniciando bot de Telegram: {e}")
            return False
    
    def stop_all_services(self):
        """Detener todos los servicios"""
        logger.info("🛑 Stopping all services...")
        print("🛑 Deteniendo servicios...")
        
        if hasattr(self, 'bot_thread') and self.bot_thread:
            logger.debug("Stopping Telegram bot thread...")
            print("✅ Bot de Telegram detenido")
        
        if self.ngrok_process:
            try:
                logger.debug("Terminating ngrok process...")
                self.ngrok_process.terminate()
                self.ngrok_process.wait(timeout=5)
                logger.debug("✅ Ngrok process terminated")
                print("✅ Túnel ngrok detenido")
            except Exception as e:
                logger.debug(f"Force killing ngrok process: {e}")
                self.ngrok_process.kill()
        
        if hasattr(self, 'webhook_thread') and self.webhook_thread:
            logger.debug("Webhook thread will stop with main process")
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
    
    def setup_gui(self):
        """Setup the Tkinter GUI interface with modern theme and responsive layout"""
        import tkinter as tk
        from tkinter import ttk, messagebox
        from tkcalendar import DateEntry
        
        self.root = tk.Tk()
        self.root.title("🧐 SergioBets v.2 – Sistema Completo con Pagos")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)
        try:
            self.root.state('zoomed')
        except:
            pass
        
        self.theme = ThemeManager(self.root)
        self.dark_mode_var = tk.BooleanVar(value=False)
        palette = self.theme.apply('light')
        
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        self.entry_fecha = None
        self.combo_ligas = None
        self.frame_predicciones = None
        self.frame_partidos = None
        self.ligas_disponibles = set()
        self.checkboxes_predicciones = []
        self.checkboxes_partidos = []
        self.predicciones_actuales = []
        self.partidos_actuales = []
        self.mensaje_telegram = ""
        self.progreso_data = {"deposito": 100.0, "meta": 300.0, "saldo_actual": 100.0}
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        
        self.tab_principal = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.tab_principal, text="🏠 Principal")
        
        self.tab_ajustes = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.tab_ajustes, text="⚙️ Ajustes")
        
        self.tab_principal.grid_rowconfigure(0, weight=0)  # Toolbar
        self.tab_principal.grid_rowconfigure(1, weight=0)  # Separator
        self.tab_principal.grid_rowconfigure(2, weight=1)  # Predicciones (scrollable)
        self.tab_principal.grid_rowconfigure(3, weight=1)  # Partidos (scrollable)
        self.tab_principal.grid_columnconfigure(0, weight=1)
        
        toolbar = ttk.Frame(self.tab_principal, style='Toolbar.TFrame', padding=10)
        toolbar.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        
        toolbar.grid_columnconfigure(0, weight=0)  # Filtros
        toolbar.grid_columnconfigure(1, weight=1)  # Acciones
        toolbar.grid_columnconfigure(2, weight=0)  # Dark mode toggle
        
        filters_frame = ttk.Frame(toolbar, style='Toolbar.TFrame')
        filters_frame.grid(row=0, column=0, sticky='w', padx=(0, 10))
        
        ttk.Label(filters_frame, text="📅 Fecha:").grid(row=0, column=0, padx=(0, 5))
        self.entry_fecha = DateEntry(filters_frame, width=12, background="darkblue", 
                                     foreground="white", borderwidth=2, 
                                     date_pattern='yyyy-MM-dd', showothermonthdays=False, 
                                     showweeknumbers=False)
        self.entry_fecha.grid(row=0, column=1, padx=(0, 15))
        
        ttk.Label(filters_frame, text="🏆 Liga:").grid(row=0, column=2, padx=(0, 5))
        self.combo_ligas = ttk.Combobox(filters_frame, state='readonly', width=25)
        self.combo_ligas.grid(row=0, column=3)
        self.combo_ligas.set('Todas')
        self.combo_ligas.bind('<<ComboboxSelected>>', self.on_liga_changed)
        
        actions_frame = ttk.Frame(toolbar, style='Toolbar.TFrame')
        actions_frame.grid(row=0, column=1, sticky='ew', padx=10)
        
        for i in range(8):
            actions_frame.grid_columnconfigure(i, weight=1, uniform='actions')
        
        ttk.Button(actions_frame, text="🔍 Buscar", command=self.buscar_en_hilo).grid(
            row=0, column=0, sticky='ew', padx=2)
        ttk.Button(actions_frame, text="♻️ Regenerar", style='Secondary.TButton', 
                  command=self.regenerar_en_hilo).grid(row=0, column=1, sticky='ew', padx=2)
        ttk.Button(actions_frame, text="📢 Alerta", style='Secondary.TButton', 
                  command=self.enviar_alerta).grid(row=0, column=2, sticky='ew', padx=2)
        ttk.Button(actions_frame, text="🎁 Promo", style='Secondary.TButton', 
                  command=self.enviar_promocion).grid(row=0, column=3, sticky='ew', padx=2)
        ttk.Button(actions_frame, text="🧹 Cache", style='Secondary.TButton', 
                  command=self.limpiar_cache_api).grid(row=0, column=4, sticky='ew', padx=2)
        ttk.Button(actions_frame, text="📌 Enviar", command=self.enviar_predicciones_seleccionadas).grid(
            row=0, column=5, sticky='ew', padx=2)
        ttk.Button(actions_frame, text="📊 Track", command=self.abrir_track_record).grid(
            row=0, column=6, sticky='ew', padx=2)
        ttk.Button(actions_frame, text="👥 Users", command=self.abrir_usuarios).grid(
            row=0, column=7, sticky='ew', padx=2)
        
        def toggle_theme():
            mode = 'dark' if self.dark_mode_var.get() else 'light'
            palette = self.theme.apply(mode)
            self.update_custom_widgets_theme(palette)
            toggle_btn.config(text="☀️ Modo claro" if mode == 'dark' else "🌙 Modo oscuro")
        
        toggle_btn = ttk.Checkbutton(toolbar, text="🌙 Modo oscuro", 
                                     variable=self.dark_mode_var,
                                     command=toggle_theme,
                                     style='Toggle.TCheckbutton')
        toggle_btn.grid(row=0, column=2, sticky='e', padx=(10, 0))
        
        ttk.Separator(self.tab_principal, orient='horizontal').grid(
            row=1, column=0, sticky='ew', pady=(5, 10))
        
        # ScrollableFrame para predicciones
        self.sf_predicciones = ScrollableFrame(self.tab_principal, style='TFrame')
        self.sf_predicciones.grid(row=2, column=0, sticky='nsew', padx=10, pady=5)
        self.sf_predicciones.inner.grid_columnconfigure(0, weight=1)
        
        self.sf_partidos = ScrollableFrame(self.tab_principal, style='TFrame')
        self.sf_partidos.grid(row=3, column=0, sticky='nsew', padx=10, pady=5)
        self.sf_partidos.inner.grid_columnconfigure(0, weight=1)
        
        self.frame_predicciones = self.sf_predicciones.inner
        self.frame_partidos = self.sf_partidos.inner
        
        self.setup_settings_tab()
        
        print("✅ GUI setup completed with modern theme")
    
    def update_custom_widgets_theme(self, palette):
        """Actualiza widgets personalizados que no usan ttk"""
        try:
            if hasattr(self, 'sf_predicciones') and self.sf_predicciones:
                self.sf_predicciones.update_theme(palette['bg'])
            if hasattr(self, 'sf_partidos') and self.sf_partidos:
                self.sf_partidos.update_theme(palette['bg'])
        except Exception as e:
            logger.warning(f"Error updating custom widgets theme: {e}")
    
    def cargar_configuracion(self):
        """Carga la configuración desde config_app.json"""
        config = cargar_json("config_app.json")
        if config is None:
            config = {"odds_min": 1.30, "odds_max": 1.60}
            guardar_json("config_app.json", config)
        return config

    def guardar_configuracion(self, config):
        """Guarda la configuración en config_app.json"""
        guardar_json("config_app.json", config)

    def setup_settings_tab(self):
        """Setup the Settings tab content"""
        import tkinter as tk
        from tkinter import ttk, messagebox
        
        frame_ajustes_content = tk.Frame(self.tab_ajustes, bg="#f1f3f4")
        frame_ajustes_content.pack(pady=50, padx=50, fill='both', expand=True)
        
        ttk.Label(frame_ajustes_content, text="⚙️ Configuración de Filtros de Cuotas", font=('Segoe UI', 14, 'bold')).pack(pady=(0, 30))
        
        config_actual = self.cargar_configuracion()
        
        frame_min_tab = tk.Frame(frame_ajustes_content, bg="#f1f3f4")
        frame_min_tab.pack(pady=15, fill='x')
        
        ttk.Label(frame_min_tab, text="Cuota mínima:", font=('Segoe UI', 12)).pack(side=tk.LEFT)
        self.entry_min_tab = tk.Entry(frame_min_tab, font=('Segoe UI', 12), width=15)
        self.entry_min_tab.pack(side=tk.RIGHT)
        self.entry_min_tab.insert(0, str(config_actual.get("odds_min", 1.30)))
        
        frame_max_tab = tk.Frame(frame_ajustes_content, bg="#f1f3f4")
        frame_max_tab.pack(pady=15, fill='x')
        
        ttk.Label(frame_max_tab, text="Cuota máxima:", font=('Segoe UI', 12)).pack(side=tk.LEFT)
        self.entry_max_tab = tk.Entry(frame_max_tab, font=('Segoe UI', 12), width=15)
        self.entry_max_tab.pack(side=tk.RIGHT)
        self.entry_max_tab.insert(0, str(config_actual.get("odds_max", 1.60)))
        
        frame_info_tab = tk.Frame(frame_ajustes_content, bg="#f1f3f4")
        frame_info_tab.pack(pady=30, fill='x')
        
        info_text_tab = "ℹ️ Formato: Decimal EU\n📊 Límite mínimo técnico: 1.01\n🎯 Solo se mostrarán apuestas en el rango seleccionado"
        ttk.Label(frame_info_tab, text=info_text_tab, font=('Segoe UI', 10), foreground='#666666').pack()
        
        frame_boton_tab = tk.Frame(frame_ajustes_content, bg="#f1f3f4")
        frame_boton_tab.pack(pady=30)
        
        ttk.Button(frame_boton_tab, text="💾 Guardar", command=self.guardar_ajustes_tab).pack()

    def guardar_ajustes_tab(self):
        """Guardar configuración desde la pestaña de ajustes"""
        import tkinter as tk
        from tkinter import messagebox
        
        try:
            odds_min = float(self.entry_min_tab.get())
            odds_max = float(self.entry_max_tab.get())
            
            if odds_min < 1.01:
                messagebox.showerror("Error", "La cuota mínima debe ser al menos 1.01")
                return
            
            if odds_max < odds_min:
                messagebox.showerror("Error", "La cuota máxima debe ser mayor o igual a la mínima")
                return
            
            nueva_config = {"odds_min": odds_min, "odds_max": odds_max}
            self.guardar_configuracion(nueva_config)
            
            messagebox.showinfo("Éxito", "Configuración guardada correctamente")
            
        except ValueError:
            messagebox.showerror("Error", "Por favor ingresa valores numéricos válidos")
    
    def cargar_partidos_reales(self, fecha):
        """Cargar partidos reales de la API - solo para la fecha exacta solicitada"""
        try:
            print(f"🔍 Cargando partidos reales para {fecha}...")
            datos_api = obtener_partidos_del_dia(fecha)
            partidos = []

            if not datos_api or len(datos_api) == 0:
                print(f"ℹ️ No hay partidos disponibles para {fecha}")
                print(f"   Tipo de respuesta: {type(datos_api)}")
                print(f"   Contenido: {datos_api}")
                return []  # Retornar lista vacía cuando no hay partidos reales

            print(f"✅ API devolvió {len(datos_api)} partidos para {fecha}")
            
            for partido in datos_api:
                try:
                    liga_detectada = detectar_liga_por_imagen(
                        partido.get("home_image", ""), 
                        partido.get("away_image", "")
                    )
                    from league_utils import convertir_timestamp_unix
                    hora_partido = convertir_timestamp_unix(partido.get("date_unix"))
                    
                    partidos.append({
                        "hora": hora_partido,
                        "liga": liga_detectada,
                        "local": partido.get("home_name", f"Team {partido.get('homeID', 'Home')}"),
                        "visitante": partido.get("away_name", f"Team {partido.get('awayID', 'Away')}"),
                        "cuotas": {
                            "casa": "FootyStats",
                            "local": str(partido.get("odds_ft_1", "2.00")),
                            "empate": str(partido.get("odds_ft_x", "3.00")),
                            "visitante": str(partido.get("odds_ft_2", "4.00")),
                            "btts_si": str(partido.get("odds_btts_yes", "0")),
                            "btts_no": str(partido.get("odds_btts_no", "0")),
                            "over_15": str(partido.get("odds_ft_over15", "0")),
                            "under_15": str(partido.get("odds_ft_under15", "0")),
                            "over_25": str(partido.get("odds_ft_over25", "0")),
                            "under_25": str(partido.get("odds_ft_under25", "0")),
                            "corners_over_85": str(partido.get("odds_corners_over_85", "0")),
                            "corners_over_95": str(partido.get("odds_corners_over_95", "0")),
                            "corners_over_105": str(partido.get("odds_corners_over_105", "0")),
                            "1h_over_05": str(partido.get("odds_1st_half_over05", "0")),
                            "1h_over_15": str(partido.get("odds_1st_half_over15", "0"))
                        },
                        "cuotas_disponibles": {
                            "local": partido.get("odds_ft_1", 0),
                            "empate": partido.get("odds_ft_x", 0),
                            "visitante": partido.get("odds_ft_2", 0),
                            
                            "over_05": partido.get("odds_ft_over05", 0),
                            "under_05": partido.get("odds_ft_under05", 0),
                            "over_15": partido.get("odds_ft_over15", 0),
                            "under_15": partido.get("odds_ft_under15", 0),
                            "over_25": partido.get("odds_ft_over25", 0),
                            "under_25": partido.get("odds_ft_under25", 0),
                            "over_35": partido.get("odds_ft_over35", 0),
                            "under_35": partido.get("odds_ft_under35", 0),
                            "over_45": partido.get("odds_ft_over45", 0),
                            "under_45": partido.get("odds_ft_under45", 0),
                            "over_55": partido.get("odds_ft_over55", 0),
                            "under_55": partido.get("odds_ft_under55", 0),
                            
                            "btts_si": partido.get("odds_btts_yes", 0),
                            "btts_no": partido.get("odds_btts_no", 0),
                            
                            "1h_over_05": partido.get("odds_1st_half_over05", 0),
                            "1h_under_05": partido.get("odds_1st_half_under05", 0),
                            "1h_over_15": partido.get("odds_1st_half_over15", 0),
                            "1h_under_15": partido.get("odds_1st_half_under15", 0),
                            "1h_over_25": partido.get("odds_1st_half_over25", 0),
                            "1h_under_25": partido.get("odds_1st_half_under25", 0),
                            "1h_over_35": partido.get("odds_1st_half_over35", 0),
                            "1h_under_35": partido.get("odds_1st_half_under35", 0),
                            "1h_result_1": partido.get("odds_1st_half_result_1", 0),
                            "1h_result_x": partido.get("odds_1st_half_result_x", 0),
                            "1h_result_2": partido.get("odds_1st_half_result_2", 0),
                            
                            "2h_over_05": partido.get("odds_2nd_half_over05", 0),
                            "2h_under_05": partido.get("odds_2nd_half_under05", 0),
                            "2h_over_15": partido.get("odds_2nd_half_over15", 0),
                            "2h_under_15": partido.get("odds_2nd_half_under15", 0),
                            "2h_over_25": partido.get("odds_2nd_half_over25", 0),
                            "2h_under_25": partido.get("odds_2nd_half_under25", 0),
                            "2h_result_1": partido.get("odds_2nd_half_result_1", 0),
                            "2h_result_x": partido.get("odds_2nd_half_result_x", 0),
                            "2h_result_2": partido.get("odds_2nd_half_result_2", 0),
                            
                            "dc_1x": partido.get("odds_doublechance_1x", 0),
                            "dc_12": partido.get("odds_doublechance_12", 0),
                            "dc_x2": partido.get("odds_doublechance_x2", 0),
                            
                            "corners_over_85": partido.get("odds_corners_over_85", 0),
                            "corners_under_85": partido.get("odds_corners_under_85", 0),
                            "corners_over_95": partido.get("odds_corners_over_95", 0),
                            "corners_under_95": partido.get("odds_corners_under_95", 0),
                            "corners_over_105": partido.get("odds_corners_over_105", 0),
                            "corners_under_105": partido.get("odds_corners_under_105", 0),
                            "corners_over_115": partido.get("odds_corners_over_115", 0),
                            "corners_under_115": partido.get("odds_corners_under_115", 0),
                            
                            "handicap_home_minus_05": partido.get("odds_handicap_home_-0_5", 0),
                            "handicap_home_plus_05": partido.get("odds_handicap_home_+0_5", 0),
                            "handicap_away_minus_05": partido.get("odds_handicap_away_-0_5", 0),
                            "handicap_away_plus_05": partido.get("odds_handicap_away_+0_5", 0),
                            "handicap_home_minus_10": partido.get("odds_handicap_home_-1_0", 0),
                            "handicap_home_plus_10": partido.get("odds_handicap_home_+1_0", 0),
                            "handicap_away_minus_10": partido.get("odds_handicap_away_-1_0", 0),
                            "handicap_away_plus_10": partido.get("odds_handicap_away_+1_0", 0),
                            
                            "cards_over_35": partido.get("odds_cards_over_35", 0),
                            "cards_under_35": partido.get("odds_cards_under_35", 0),
                            "cards_over_45": partido.get("odds_cards_over_45", 0),
                            "cards_under_45": partido.get("odds_cards_under_45", 0),
                            "cards_over_55": partido.get("odds_cards_over_55", 0),
                            "cards_under_55": partido.get("odds_cards_under_55", 0)
                        }
                    })
                except Exception as partido_error:
                    print(f"⚠️ Error procesando partido individual: {partido_error}")
                    continue

            print(f"✅ Procesados {len(partidos)} partidos reales para {fecha}")
            return partidos
                
        except Exception as e:
            print(f"❌ Error cargando partidos reales: {e}")
            import traceback
            print(f"Traceback completo: {traceback.format_exc()}")
            print("ℹ️ Retornando lista vacía debido al error")
            return []  # Retornar lista vacía en caso de error

    def buscar_en_hilo(self):
        """Buscar en hilo separado"""
        try:
            from thread_pool_manager import thread_manager
            executor = thread_manager.get_executor()
            self.future_busqueda = executor.submit(self.buscar)
        except ImportError:
            threading.Thread(target=self.buscar).start()

    def regenerar_en_hilo(self):
        """Regenerar predicciones en hilo separado"""
        try:
            from thread_pool_manager import thread_manager
            executor = thread_manager.get_executor()
            self.future_regeneracion = executor.submit(lambda: self.buscar(opcion_numero=2))
        except ImportError:
            threading.Thread(target=lambda: self.buscar(opcion_numero=2)).start()

    def buscar(self, opcion_numero=1):
        """Buscar partidos y predicciones"""
        try:
            fecha = self.entry_fecha.get()
            self.ligas_disponibles.clear()
            
            if opcion_numero == 1:
                limpiar_cache_predicciones()

            partidos = self.cargar_partidos_reales(fecha)
            
            self.limpiar_frame_predicciones()
            self.limpiar_frame_partidos()

            if not partidos or len(partidos) == 0:
                self.actualizar_ligas()  # Actualizar con lista vacía
                self.mensaje_telegram = f"No hay partidos disponibles para {fecha}"
                messagebox.showinfo("Sin partidos", f"ℹ️ No hay partidos disponibles para {fecha}\n📅 Intenta con otra fecha que tenga partidos programados")
                return

            for partido in partidos:
                liga = partido["liga"]
                self.ligas_disponibles.add(liga)

            self.actualizar_ligas()

            liga_filtrada = self.combo_ligas.get()
            if liga_filtrada not in ['Todas'] + sorted(list(self.ligas_disponibles)):
                self.combo_ligas.set('Todas')
                liga_filtrada = 'Todas'

            if liga_filtrada == 'Todas':
                partidos_filtrados = partidos
            else:
                partidos_filtrados = [p for p in partidos if p["liga"] == liga_filtrada]
            
            predicciones_ia = filtrar_apuestas_inteligentes(partidos_filtrados, opcion_numero)
            
            config = self.cargar_configuracion()
            odds_min = config.get("odds_min", 1.30)
            odds_max = config.get("odds_max", 1.60)
            
            titulo_extra = ""
            if opcion_numero == 2:
                titulo_extra = " - ALTERNATIVAS (2das OPCIONES)"
            
            self.mostrar_predicciones_con_checkboxes(predicciones_ia, liga_filtrada, titulo_extra)
            self.mostrar_partidos_con_checkboxes(partidos_filtrados, liga_filtrada, fecha)

            preview_counter_numbers = list(range(1, len(predicciones_ia) + 1))
            self.mensaje_telegram = generar_mensaje_ia(predicciones_ia, fecha, preview_counter_numbers)
            if liga_filtrada == 'Todas':
                self.mensaje_telegram += f"\n\n⚽ TODOS LOS PARTIDOS ({fecha})\n\n"
            else:
                self.mensaje_telegram += f"\n\n⚽ PARTIDOS - {liga_filtrada} ({fecha})\n\n"

            for liga in sorted(set(p["liga"] for p in partidos_filtrados)):
                if liga_filtrada != 'Todas' and liga_filtrada != liga:
                    continue
                self.mensaje_telegram += f"🔷 {liga}\n"
                
                liga_partidos = [p for p in partidos_filtrados if p["liga"] == liga]
                for partido in liga_partidos:
                    self.mensaje_telegram += f"🕒 {partido['hora']} - {partido['local']} vs {partido['visitante']}\n"
                    self.mensaje_telegram += f"🏦 Casa: {partido['cuotas']['casa']} | 💰 Cuotas -> Local: {partido['cuotas']['local']}, Empate: {partido['cuotas']['empate']}, Visitante: {partido['cuotas']['visitante']}\n\n"


            self.guardar_datos_json(fecha)
            
        except Exception as e:
            error_msg = f"❌ Error al buscar partidos: {e}"
            print(error_msg)
            messagebox.showerror("Error", f"Error al cargar partidos: {e}")

    def actualizar_ligas(self):
        """Actualizar lista de ligas disponibles"""
        ligas = sorted(self.ligas_disponibles)
        self.combo_ligas['values'] = ['Todas'] + ligas
        if self.combo_ligas.get() not in self.combo_ligas['values']:
            self.combo_ligas.set('Todas')

    def on_liga_changed(self, event=None):
        """Callback cuando se cambia la selección de liga"""
        if self.ligas_disponibles:
            self.buscar()

    def guardar_datos_json(self, fecha):
        """Guardar datos en JSON"""
        guardar_json("partidos.json", self.cargar_partidos_reales(fecha))
        guardar_json("progreso.json", self.progreso_data)
    
    def limpiar_frame_predicciones(self):
        """Limpiar el frame de predicciones y checkboxes"""
        for widget in self.frame_predicciones.winfo_children():
            widget.destroy()
        self.checkboxes_predicciones.clear()
        self.predicciones_actuales.clear()

    def limpiar_frame_partidos(self):
        """Limpiar el frame de partidos y checkboxes"""
        for widget in self.frame_partidos.winfo_children():
            widget.destroy()
        self.checkboxes_partidos.clear()
        self.partidos_actuales.clear()

    def mostrar_predicciones_con_checkboxes(self, predicciones, liga_filtrada, titulo_extra=""):
        """Mostrar predicciones con checkboxes para selección usando grid y estilos modernos"""
        self.limpiar_frame_predicciones()
        
        if not predicciones:
            return
        
        titulo_text = "🎯 BETGENIUX® - SELECCIONA PRONÓSTICOS PARA ENVIAR"
        if liga_filtrada != 'Todas':
            titulo_text += f" - {liga_filtrada}"
        titulo_text += titulo_extra
        
        header = ttk.Frame(self.frame_predicciones, style='Header.TFrame', padding=(10, 8))
        header.grid(row=0, column=0, sticky='ew', pady=(0, 8))
        header.grid_columnconfigure(0, weight=1)
        ttk.Label(header, text=titulo_text, style='Header.TLabel').grid(row=0, column=0, sticky='w')
        
        for i, pred in enumerate(predicciones, 1):
            self.predicciones_actuales.append(pred)
            
            rowf = ttk.Frame(self.frame_predicciones, style='Card.TFrame', padding=(10, 8))
            rowf.grid(row=i, column=0, sticky='ew', pady=4)
            rowf.grid_columnconfigure(1, weight=1)
            
            var_checkbox = tk.BooleanVar()
            self.checkboxes_predicciones.append(var_checkbox)
            
            chk = ttk.Checkbutton(rowf, variable=var_checkbox)
            chk.grid(row=0, column=0, padx=(0, 10), sticky='nw')
            
            pred_text = f"🎯 PRONÓSTICO #{i}: {pred['prediccion']} | ⚽ {pred['partido']} | 💰 {pred['cuota']} | ⏰ {pred['hora']}"
            title = ttk.Label(rowf, text=pred_text, style='ItemTitle.TLabel', anchor='w', justify='left')
            title.grid(row=0, column=1, sticky='ew')
            title.bind('<Configure>', lambda e, lbl=title: lbl.config(wraplength=max(lbl.winfo_width()-10, 200)))
            
            sub_text = f"📝 {pred['razon']}"
            sub = ttk.Label(rowf, text=sub_text, style='ItemSub.TLabel', anchor='w', justify='left')
            sub.grid(row=1, column=1, sticky='ew', pady=(4, 0))
            sub.bind('<Configure>', lambda e, lbl=sub: lbl.config(wraplength=max(lbl.winfo_width()-10, 200)))

    def mostrar_partidos_con_checkboxes(self, partidos_filtrados, liga_filtrada, fecha):
        """Mostrar partidos con checkboxes para selección usando grid y estilos modernos"""
        self.limpiar_frame_partidos()
        
        if not partidos_filtrados:
            return
        
        titulo_text = f"🗓️ PARTIDOS PROGRAMADOS PARA LA JORNADA DEL: {fecha}"
        if liga_filtrada != 'Todas':
            titulo_text += f" - {liga_filtrada}"
        
        header = ttk.Frame(self.frame_partidos, style='Header.TFrame', padding=(10, 8))
        header.grid(row=0, column=0, sticky='ew', pady=(0, 8))
        header.grid_columnconfigure(0, weight=1)
        ttk.Label(header, text=titulo_text, style='Header.TLabel').grid(row=0, column=0, sticky='w')
        
        for i, partido in enumerate(partidos_filtrados, 1):
            self.partidos_actuales.append(partido)
            
            rowf = ttk.Frame(self.frame_partidos, style='Card.TFrame', padding=(10, 8))
            rowf.grid(row=i, column=0, sticky='ew', pady=4)
            rowf.grid_columnconfigure(1, weight=1)
            
            var_checkbox = tk.BooleanVar()
            self.checkboxes_partidos.append(var_checkbox)
            
            chk = ttk.Checkbutton(rowf, variable=var_checkbox)
            chk.grid(row=0, column=0, padx=(0, 10), sticky='nw')
            
            partido_text = f"⚽ PARTIDO #{i}: {partido['local']} vs {partido['visitante']} | ⏰ {partido['hora']} | 💰 {partido['cuotas']['local']}-{partido['cuotas']['empate']}-{partido['cuotas']['visitante']}"
            main = ttk.Label(rowf, text=partido_text, style='ItemTitle.TLabel', anchor='w', justify='left')
            main.grid(row=0, column=1, sticky='ew', padx=(0, 10))
            main.bind('<Configure>', lambda e, lbl=main: lbl.config(wraplength=max(lbl.winfo_width()-10, 200)))
            
            sub_text = f"🏠 Casa: {partido['cuotas']['casa']} | 🏆 Liga: {partido['liga']}"
            sub = ttk.Label(rowf, text=sub_text, style='ItemSub.TLabel', anchor='w', justify='left')
            sub.grid(row=1, column=1, sticky='ew', pady=(4, 0))
            sub.bind('<Configure>', lambda e, lbl=sub: lbl.config(wraplength=max(lbl.winfo_width()-10, 200)))
            
            btn = ttk.Button(rowf, text="🔎 Analizar", style='Secondary.TButton',
                           command=lambda p=partido: self.analizar_partido_individual(p))
            btn.grid(row=0, column=2, rowspan=2, padx=(10, 0), sticky='e')

    def analizar_partido_individual(self, partido):
        """Analiza un partido individual y muestra el resultado con opciones detalladas"""
        try:
            from ia_bets import analizar_partido_individual
            
            resultado = analizar_partido_individual(partido, bypass_filters=True)
            
            if resultado["success"]:
                self.mostrar_resultado_analisis_individual(resultado)
            else:
                import tkinter.messagebox as messagebox
                messagebox.showwarning("Sin Predicción", 
                                     f"No se pudo generar predicción para:\n{resultado['partido']}\n\nError: {resultado['error']}")
                
        except Exception as e:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Error", f"Error en análisis: {str(e)}")
    
    def mostrar_resultado_analisis_individual(self, resultado):
        """Muestra resultado de análisis individual con mejor pick + botones de acción"""
        import tkinter as tk
        from tkinter import messagebox
        
        popup = tk.Toplevel(self.root)
        popup.title("🔍 Análisis Individual")
        popup.geometry("500x400")
        popup.configure(bg="#ecf0f1")
        popup.resizable(False, False)
        
        popup.transient(self.root)
        popup.grab_set()
        
        header_frame = tk.Frame(popup, bg="#34495e")
        header_frame.pack(fill='x', pady=(0,10))
        
        header_label = tk.Label(header_frame, text="🎯 ANÁLISIS INDIVIDUAL", 
                               bg="#34495e", fg="white", font=('Segoe UI', 12, 'bold'), pady=10)
        header_label.pack()
        
        match_frame = tk.Frame(popup, bg="#ecf0f1")
        match_frame.pack(fill='x', padx=20, pady=5)
        
        match_label = tk.Label(match_frame, text=f"⚽️ {resultado['partido']}", 
                              bg="#ecf0f1", font=('Segoe UI', 11, 'bold'))
        match_label.pack()
        
        liga_label = tk.Label(match_frame, text=f"🏆 {resultado['liga']} | ⏰ {resultado['hora']}", 
                             bg="#ecf0f1", font=('Segoe UI', 9), fg="#7f8c8d")
        liga_label.pack()
        
        pick_frame = tk.Frame(popup, bg="#d5f4e6", relief='ridge', bd=2)
        pick_frame.pack(fill='x', padx=20, pady=10)
        
        pick_title = tk.Label(pick_frame, text="🥇 MEJOR PICK", 
                             bg="#d5f4e6", font=('Segoe UI', 10, 'bold'), pady=5)
        pick_title.pack()
        
        mejor = resultado['mejor_pick']
        edge_pct = mejor.get('edge_percentage', mejor['valor_esperado'] * 100)
        
        pick_text = f"🔮 {mejor['prediccion']}\n"
        pick_text += f"💰 Cuota: {mejor['cuota']} | Stake: {mejor['stake_recomendado']}u\n"
        pick_text += f"📊 Confianza: {mejor['confianza']}% | VE: +{mejor['valor_esperado']:.3f}\n"
        
        if edge_pct < 5:
            pick_text += f"⚠️ Edge bajo: {edge_pct:.1f}% - no cumple criterio para publicación automática"
        else:
            pick_text += f"✅ Edge: {edge_pct:.1f}% - cumple criterios de publicación"
        
        pick_label = tk.Label(pick_frame, text=pick_text, bg="#d5f4e6", 
                             font=('Segoe UI', 9), justify='left')
        pick_label.pack(pady=5)
        
        buttons_frame = tk.Frame(popup, bg="#ecf0f1")
        buttons_frame.pack(fill='x', padx=20, pady=10)
        
        detail_btn = tk.Button(buttons_frame, text="📊 Ver Detalle", bg="#9b59b6", fg="white",
                              font=('Segoe UI', 9), relief='flat', cursor='hand2',
                              command=lambda: self.mostrar_detalle_mercados_individual(resultado))
        detail_btn.pack(side=tk.LEFT, padx=5)
        
        save_btn = tk.Button(buttons_frame, text="💾 Guardar", bg="#27ae60", fg="white",
                            font=('Segoe UI', 9), relief='flat', cursor='hand2',
                            command=lambda: self.guardar_analisis_manual_individual(resultado))
        save_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = tk.Button(buttons_frame, text="❌ Cerrar", bg="#e74c3c", fg="white",
                             font=('Segoe UI', 9), relief='flat', cursor='hand2',
                             command=popup.destroy)
        close_btn.pack(side=tk.RIGHT, padx=5)
        
        print(f"📋 ANÁLISIS INDIVIDUAL: {resultado['partido']}")
        print(f"   Mejor pick: {mejor['prediccion']} @ {mejor['cuota']}")
        print(f"   Edge: {edge_pct:.1f}% | Cumple publicación: {'Sí' if mejor.get('cumple_publicacion', False) else 'No'}")
        print(f"   Mercados analizados: {len(resultado['todos_mercados'])}")
    
    def mostrar_detalle_mercados_individual(self, resultado):
        """Muestra tabla detallada de todos los mercados analizados"""
        import tkinter as tk
        from tkinter import ttk
        
        detail_popup = tk.Toplevel(self.root)
        detail_popup.title("📊 Detalle de Mercados")
        detail_popup.geometry("700x500")
        detail_popup.configure(bg="#ecf0f1")
        
        header_label = tk.Label(detail_popup, text=f"📊 TODOS LOS MERCADOS - {resultado['partido']}", 
                               bg="#34495e", fg="white", font=('Segoe UI', 11, 'bold'), pady=10)
        header_label.pack(fill='x')
        
        tree_frame = tk.Frame(detail_popup, bg="#ecf0f1")
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ('Mercado', 'Cuota', 'Edge %', 'Cumple', 'Stake')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        tree.heading('Mercado', text='Mercado')
        tree.heading('Cuota', text='Cuota')
        tree.heading('Edge %', text='Edge %')
        tree.heading('Cumple', text='Cumple Pub.')
        tree.heading('Stake', text='Stake')
        
        tree.column('Mercado', width=250)
        tree.column('Cuota', width=80)
        tree.column('Edge %', width=100)
        tree.column('Cumple', width=100)
        tree.column('Stake', width=80)
        
        for i, mercado in enumerate(resultado['todos_mercados']):
            edge_pct = mercado.get('edge_percentage', mercado['valor_esperado'] * 100)
            cumple = "✅ Sí" if mercado.get('cumple_publicacion', False) else "⚠️ No"
            
            tree.insert('', 'end', values=(
                mercado['descripcion'],
                f"{mercado['cuota']:.2f}",
                f"{edge_pct:.1f}%",
                cumple,
                f"{mercado['stake_recomendado']}u"
            ))
        
        tree.pack(fill='both', expand=True)
        
        close_btn = tk.Button(detail_popup, text="❌ Cerrar", bg="#e74c3c", fg="white",
                             font=('Segoe UI', 9), relief='flat', cursor='hand2',
                             command=detail_popup.destroy)
        close_btn.pack(pady=10)
        
        print(f"📊 DETALLE COMPLETO: {resultado['partido']}")
        for i, mercado in enumerate(resultado['todos_mercados']):
            edge_pct = mercado.get('edge_percentage', mercado['valor_esperado'] * 100)
            cumple = "✅" if mercado.get('cumple_publicacion', False) else "⚠️"
            print(f"   {cumple} {i+1}. {mercado['descripcion']} @ {mercado['cuota']:.2f} (Edge: {edge_pct:.1f}%)")
    
    def guardar_analisis_manual_individual(self, resultado):
        """Guarda el análisis manual en el historial con source=manual"""
        try:
            from ia_bets import guardar_prediccion_historica
            from datetime import datetime
            
            mejor = resultado['mejor_pick']
            prediccion_data = {
                "partido": resultado['partido'],
                "liga": resultado['liga'],
                "prediccion": mejor['prediccion'],
                "cuota": mejor['cuota'],
                "stake_recomendado": mejor['stake_recomendado'],
                "valor_esperado": mejor['valor_esperado'],
                "confianza": mejor['confianza'],
                "source": "manual"  # Mark as manual analysis
            }
            
            fecha = datetime.now().strftime('%Y-%m-%d')
            guardar_prediccion_historica(prediccion_data, fecha)
            
            import tkinter.messagebox as messagebox
            messagebox.showinfo("Guardado", f"Análisis guardado en historial:\n{mejor['prediccion']}")
            
            print(f"💾 GUARDADO MANUAL: {resultado['partido']} - {mejor['prediccion']}")
            
        except Exception as e:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Error", f"Error guardando análisis: {str(e)}")
    
    def mostrar_resultado_analisis(self, resultado):
        """Muestra resultado de análisis con mejor pick + botones de acción"""
        import tkinter as tk
        from tkinter import messagebox
        
        popup = tk.Toplevel(self.root)
        popup.title("🔍 Análisis Individual")
        popup.geometry("500x400")
        popup.configure(bg="#ecf0f1")
        popup.resizable(False, False)
        
        popup.transient(self.root)
        popup.grab_set()
        
        header_frame = tk.Frame(popup, bg="#34495e")
        header_frame.pack(fill='x', pady=(0,10))
        
        header_label = tk.Label(header_frame, text="🎯 ANÁLISIS INDIVIDUAL", 
                               bg="#34495e", fg="white", font=('Segoe UI', 12, 'bold'), pady=10)
        header_label.pack()
        
        match_frame = tk.Frame(popup, bg="#ecf0f1")
        match_frame.pack(fill='x', padx=20, pady=5)
        
        match_label = tk.Label(match_frame, text=f"⚽️ {resultado['partido']}", 
                              bg="#ecf0f1", font=('Segoe UI', 11, 'bold'))
        match_label.pack()
        
        liga_label = tk.Label(match_frame, text=f"🏆 {resultado['liga']} | ⏰ {resultado['hora']}", 
                             bg="#ecf0f1", font=('Segoe UI', 9), fg="#7f8c8d")
        liga_label.pack()
        
        pick_frame = tk.Frame(popup, bg="#d5f4e6", relief='ridge', bd=2)
        pick_frame.pack(fill='x', padx=20, pady=10)
        
        pick_title = tk.Label(pick_frame, text="🥇 MEJOR PICK", 
                             bg="#d5f4e6", font=('Segoe UI', 10, 'bold'), pady=5)
        pick_title.pack()
        
        mejor = resultado['mejor_pick']
        pick_text = f"🎯 Pick: {mejor['prediccion']} @ {mejor['cuota']}\n"
        pick_text += f"💰 Stake: {mejor['stake_recomendado']}u | 📊 Confianza: {mejor['confianza']}%\n"
        
        edge_percentage = mejor.get('edge_percentage', round(mejor['valor_esperado'] * 100, 1))
        
        if mejor.get('cumple_publicacion', False):
            pick_text += f"✅ Edge: {edge_percentage}% (cumple criterio para publicación)"
        else:
            if edge_percentage < 5:
                pick_text += f"⚠️ Edge bajo: {edge_percentage}% (no cumple criterio para publicación automática)"
            else:
                pick_text += f"⚠️ Edge: {edge_percentage}% (cuota fuera de rango de publicación)"
        
        pick_label = tk.Label(pick_frame, text=pick_text, bg="#d5f4e6", 
                             font=('Segoe UI', 9), justify='left')
        pick_label.pack(pady=5)
        
        buttons_frame = tk.Frame(popup, bg="#ecf0f1")
        buttons_frame.pack(fill='x', padx=20, pady=10)
        
        detail_btn = tk.Button(buttons_frame, text="📊 Ver Detalle", bg="#9b59b6", fg="white",
                              font=('Segoe UI', 9), relief='flat', cursor='hand2',
                              command=lambda: self.mostrar_detalle_mercados(resultado))
        detail_btn.pack(side=tk.LEFT, padx=5)
        
        save_btn = tk.Button(buttons_frame, text="💾 Guardar", bg="#27ae60", fg="white",
                            font=('Segoe UI', 9), relief='flat', cursor='hand2',
                            command=lambda: self.guardar_analisis_manual(resultado))
        save_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = tk.Button(buttons_frame, text="❌ Cerrar", bg="#e74c3c", fg="white",
                             font=('Segoe UI', 9), relief='flat', cursor='hand2',
                             command=popup.destroy)
        close_btn.pack(side=tk.RIGHT, padx=5)
        
        edge_percentage = mejor.get('edge_percentage', round(mejor['valor_esperado'] * 100, 1))
        print(f"📋 ANÁLISIS TÉCNICO: {resultado['partido']}")
        print(f"   Mejor pick: {mejor['prediccion']} @ {mejor['cuota']} (Edge: {edge_percentage}%)")
        print(f"   Mercados analizados: {len(resultado['todos_mercados'])}")
        print(f"   Cumple publicación: {'Sí' if mejor.get('cumple_publicacion', False) else 'No'}")
    
    def mostrar_detalle_mercados(self, resultado):
        """Muestra tabla detallada de todos los mercados analizados"""
        import tkinter as tk
        from tkinter import ttk
        
        detail_popup = tk.Toplevel(self.root)
        detail_popup.title("📊 Detalle de Mercados")
        detail_popup.geometry("700x500")
        detail_popup.configure(bg="#ecf0f1")
        
        header_label = tk.Label(detail_popup, text=f"📊 TODOS LOS MERCADOS - {resultado['partido']}", 
                               bg="#34495e", fg="white", font=('Segoe UI', 11, 'bold'), pady=10)
        header_label.pack(fill='x')
        
        tree_frame = tk.Frame(detail_popup, bg="#ecf0f1")
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ('Mercado', 'Cuota', 'Confianza', 'VE', 'Stake')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        tree.heading('Mercado', text='Mercado')
        tree.heading('Cuota', text='Cuota')
        tree.heading('Confianza', text='Confianza %')
        tree.heading('VE', text='Edge %')
        tree.heading('Stake', text='Stake')
        
        tree.column('Mercado', width=250)
        tree.column('Cuota', width=80)
        tree.column('Confianza', width=100)
        tree.column('VE', width=120)
        tree.column('Stake', width=80)
        
        for i, mercado in enumerate(resultado['todos_mercados']):
            edge_pct = round(mercado['valor_esperado'] * 100, 1)
            tree.insert('', 'end', values=(
                mercado['descripcion'],
                f"{mercado['cuota']:.2f}",
                f"{mercado['confianza']:.1f}%",
                f"{edge_pct}%",
                f"{mercado['stake_recomendado']}u"
            ))
        
        tree.pack(fill='both', expand=True)
        
        close_btn = tk.Button(detail_popup, text="❌ Cerrar", bg="#e74c3c", fg="white",
                             font=('Segoe UI', 9), relief='flat', cursor='hand2',
                             command=detail_popup.destroy)
        close_btn.pack(pady=10)
    
    def guardar_analisis_manual(self, resultado):
        """Guarda el análisis manual en el historial con source=manual"""
        try:
            from ia_bets import guardar_prediccion_historica
            from datetime import datetime
            
            mejor = resultado['mejor_pick']
            prediccion_data = {
                "partido": resultado['partido'],
                "liga": resultado['liga'],
                "prediccion": mejor['prediccion'],
                "cuota": mejor['cuota'],
                "stake_recomendado": mejor['stake_recomendado'],
                "valor_esperado": mejor['valor_esperado'],
                "confianza": mejor['confianza'],
                "source": "manual"
            }
            
            fecha = datetime.now().strftime('%Y-%m-%d')
            guardar_prediccion_historica(prediccion_data, fecha)
            
            import tkinter.messagebox as messagebox
            messagebox.showinfo("Guardado", f"Análisis guardado en historial:\n{mejor['prediccion']}")
            
            print(f"💾 GUARDADO MANUAL: {resultado['partido']} - {mejor['prediccion']}")
            
        except Exception as e:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Error", f"Error guardando análisis: {str(e)}")
    
    def mostrar_resultado_analisis(self, resultado):
        """Muestra resultado de análisis con mejor pick + botones de acción"""
        import tkinter as tk
        from tkinter import messagebox
        
        popup = tk.Toplevel(self.root)
        popup.title("🔍 Análisis Individual")
        popup.geometry("500x400")
        popup.configure(bg="#ecf0f1")
        popup.resizable(False, False)
        
        popup.transient(self.root)
        popup.grab_set()
        
        header_frame = tk.Frame(popup, bg="#34495e")
        header_frame.pack(fill='x', pady=(0,10))
        
        header_label = tk.Label(header_frame, text="🎯 ANÁLISIS INDIVIDUAL", 
                               bg="#34495e", fg="white", font=('Segoe UI', 12, 'bold'), pady=10)
        header_label.pack()
        
        match_frame = tk.Frame(popup, bg="#ecf0f1")
        match_frame.pack(fill='x', padx=20, pady=5)
        
        match_label = tk.Label(match_frame, text=f"⚽️ {resultado['partido']}", 
                              bg="#ecf0f1", font=('Segoe UI', 11, 'bold'))
        match_label.pack()
        
        liga_label = tk.Label(match_frame, text=f"🏆 {resultado['liga']} | ⏰ {resultado['hora']}", 
                             bg="#ecf0f1", font=('Segoe UI', 9), fg="#7f8c8d")
        liga_label.pack()
        
        pick_frame = tk.Frame(popup, bg="#d5f4e6", relief='ridge', bd=2)
        pick_frame.pack(fill='x', padx=20, pady=10)
        
        pick_title = tk.Label(pick_frame, text="🥇 MEJOR PICK", 
                             bg="#d5f4e6", font=('Segoe UI', 10, 'bold'), pady=5)
        pick_title.pack()
        
        mejor = resultado['mejor_pick']
        pick_text = f"🎯 Pick: {mejor['prediccion']} @ {mejor['cuota']}\n"
        pick_text += f"💰 Stake: {mejor['stake_recomendado']}u | 📊 Confianza: {mejor['confianza']}%\n"
        
        edge_percentage = mejor.get('edge_percentage', round(mejor['valor_esperado'] * 100, 1))
        
        if mejor.get('cumple_publicacion', False):
            pick_text += f"✅ Edge: {edge_percentage}% (cumple criterio para publicación)"
        else:
            if edge_percentage < 5:
                pick_text += f"⚠️ Edge bajo: {edge_percentage}% (no cumple criterio para publicación automática)"
            else:
                pick_text += f"⚠️ Edge: {edge_percentage}% (cuota fuera de rango de publicación)"
        
        pick_label = tk.Label(pick_frame, text=pick_text, bg="#d5f4e6", 
                             font=('Segoe UI', 9), justify='left')
        pick_label.pack(pady=5)
        
        buttons_frame = tk.Frame(popup, bg="#ecf0f1")
        buttons_frame.pack(fill='x', padx=20, pady=10)
        
        detail_btn = tk.Button(buttons_frame, text="📊 Ver Detalle", bg="#9b59b6", fg="white",
                              font=('Segoe UI', 9), relief='flat', cursor='hand2',
                              command=lambda: self.mostrar_detalle_mercados(resultado))
        detail_btn.pack(side=tk.LEFT, padx=5)
        
        save_btn = tk.Button(buttons_frame, text="💾 Guardar", bg="#27ae60", fg="white",
                            font=('Segoe UI', 9), relief='flat', cursor='hand2',
                            command=lambda: self.guardar_analisis_manual(resultado))
        save_btn.pack(side=tk.LEFT, padx=5)
        
        close_btn = tk.Button(buttons_frame, text="❌ Cerrar", bg="#e74c3c", fg="white",
                             font=('Segoe UI', 9), relief='flat', cursor='hand2',
                             command=popup.destroy)
        close_btn.pack(side=tk.RIGHT, padx=5)
        
        edge_percentage = mejor.get('edge_percentage', round(mejor['valor_esperado'] * 100, 1))
        print(f"📋 ANÁLISIS TÉCNICO: {resultado['partido']}")
        print(f"   Mejor pick: {mejor['prediccion']} @ {mejor['cuota']} (Edge: {edge_percentage}%)")
        print(f"   Mercados analizados: {len(resultado['todos_mercados'])}")
        print(f"   Cumple publicación: {'Sí' if mejor.get('cumple_publicacion', False) else 'No'}")
    
    def mostrar_detalle_mercados(self, resultado):
        """Muestra tabla detallada de todos los mercados analizados"""
        import tkinter as tk
        from tkinter import ttk
        
        detail_popup = tk.Toplevel(self.root)
        detail_popup.title("📊 Detalle de Mercados")
        detail_popup.geometry("700x500")
        detail_popup.configure(bg="#ecf0f1")
        
        header_label = tk.Label(detail_popup, text=f"📊 TODOS LOS MERCADOS - {resultado['partido']}", 
                               bg="#34495e", fg="white", font=('Segoe UI', 11, 'bold'), pady=10)
        header_label.pack(fill='x')
        
        tree_frame = tk.Frame(detail_popup, bg="#ecf0f1")
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ('Mercado', 'Cuota', 'Confianza', 'VE', 'Stake')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        tree.heading('Mercado', text='Mercado')
        tree.heading('Cuota', text='Cuota')
        tree.heading('Confianza', text='Confianza %')
        tree.heading('VE', text='Edge %')
        tree.heading('Stake', text='Stake')
        
        tree.column('Mercado', width=250)
        tree.column('Cuota', width=80)
        tree.column('Confianza', width=100)
        tree.column('VE', width=120)
        tree.column('Stake', width=80)
        
        for i, mercado in enumerate(resultado['todos_mercados']):
            edge_pct = round(mercado['valor_esperado'] * 100, 1)
            tree.insert('', 'end', values=(
                mercado['descripcion'],
                f"{mercado['cuota']:.2f}",
                f"{mercado['confianza']:.1f}%",
                f"{edge_pct}%",
                f"{mercado['stake_recomendado']}u"
            ))
        
        tree.pack(fill='both', expand=True)
        
        close_btn = tk.Button(detail_popup, text="❌ Cerrar", bg="#e74c3c", fg="white",
                             font=('Segoe UI', 9), relief='flat', cursor='hand2',
                             command=detail_popup.destroy)
        close_btn.pack(pady=10)
    
    def guardar_analisis_manual(self, resultado):
        """Guarda el análisis manual en el historial con source=manual"""
        try:
            from ia_bets import guardar_prediccion_historica
            from datetime import datetime
            
            mejor = resultado['mejor_pick']
            prediccion_data = {
                "partido": resultado['partido'],
                "liga": resultado['liga'],
                "prediccion": mejor['prediccion'],
                "cuota": mejor['cuota'],
                "stake_recomendado": mejor['stake_recomendado'],
                "valor_esperado": mejor['valor_esperado'],
                "confianza": mejor['confianza'],
                "source": "manual"
            }
            
            fecha = datetime.now().strftime('%Y-%m-%d')
            guardar_prediccion_historica(prediccion_data, fecha)
            
            import tkinter.messagebox as messagebox
            messagebox.showinfo("Guardado", f"Análisis guardado en historial:\n{mejor['prediccion']}")
            
            print(f"💾 GUARDADO MANUAL: {resultado['partido']} - {mejor['prediccion']}")
            
        except Exception as e:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Error", f"Error guardando análisis: {str(e)}")

    def reproducir_sonido_exito(self):
        """Reproducir sonido MP3 cuando se envía exitosamente a Telegram"""
        try:
            pygame.mixer.init()
            
            archivos_sonido = ['sonido_exito.mp3', 'success.mp3', 'notification.mp3', 'alert.mp3']
            
            for archivo in archivos_sonido:
                if os.path.exists(archivo):
                    pygame.mixer.music.load(archivo)
                    pygame.mixer.music.play()
                    return
            
            print("No se encontró archivo de sonido MP3. Archivos buscados:", archivos_sonido)
            
        except Exception as e:
            print(f"Error reproduciendo sonido: {e}")

    def enviar_predicciones_seleccionadas(self):
        """Enviar predicciones y/o partidos seleccionados a Telegram"""
        predicciones_seleccionadas = []
        partidos_seleccionados = []
        
        for i, var_checkbox in enumerate(self.checkboxes_predicciones):
            if var_checkbox.get():
                predicciones_seleccionadas.append(self.predicciones_actuales[i])
        
        for i, var_checkbox in enumerate(self.checkboxes_partidos):
            if var_checkbox.get():
                partidos_seleccionados.append(self.partidos_actuales[i])
        
        if not predicciones_seleccionadas and not partidos_seleccionados:
            messagebox.showwarning("Sin selección", "Selecciona al menos un pronóstico o partido para enviar.")
            return
        
        fecha = self.entry_fecha.get()
        mensaje_completo = ""
        
        try:
            if predicciones_seleccionadas:
                try:
                    from daily_counter import get_next_pronostico_numbers
                    counter_numbers = get_next_pronostico_numbers(len(predicciones_seleccionadas))
                except ImportError:
                    counter_numbers = list(range(1, len(predicciones_seleccionadas) + 1))
                
                mensaje_predicciones = generar_mensaje_ia(predicciones_seleccionadas, fecha, counter_numbers)
                mensaje_completo += mensaje_predicciones
                
                for pred in predicciones_seleccionadas:
                    pred['sent_to_telegram'] = True
                    pred['fecha_envio_telegram'] = datetime.now().isoformat()
                    guardar_prediccion_historica(pred, fecha)
                
                with open("pronosticos_seleccionados.json", "w", encoding="utf-8") as f:
                    json.dump({"fecha": fecha, "predicciones": predicciones_seleccionadas}, f, ensure_ascii=False, indent=4)
                
                with open("pronosticos_seleccionados.txt", "a", encoding="utf-8") as f:
                    f.write(f"\n=== PRONÓSTICOS SELECCIONADOS {fecha} ===\n")
                    for pred in predicciones_seleccionadas:
                        f.write(f"{pred['partido']} | {pred['prediccion']} | {pred['cuota']} | {pred['razon']}\n")
                    f.write("\n")
            
            if partidos_seleccionados:
                if mensaje_completo:
                    mensaje_completo += "\n\n"
                
                mensaje_partidos = f"⚽ PARTIDOS SELECCIONADOS ({fecha})\n\n"
                
                partidos_por_liga = {}
                for partido in partidos_seleccionados:
                    liga = partido["liga"]
                    if liga not in partidos_por_liga:
                        partidos_por_liga[liga] = []
                    
                    info = f"🕒 {partido['hora']} - {partido['local']} vs {partido['visitante']}\n"
                    info += f"🏦 Casa: {partido['cuotas']['casa']} | 💰 Cuotas -> Local: {partido['cuotas']['local']}, Empate: {partido['cuotas']['empate']}, Visitante: {partido['cuotas']['visitante']}\n\n"
                    partidos_por_liga[liga].append(info)
                
                for liga in sorted(partidos_por_liga.keys()):
                    mensaje_partidos += f"🔷 {liga}\n"
                    for info in partidos_por_liga[liga]:
                        mensaje_partidos += info
                
                mensaje_completo += mensaje_partidos
                
                with open('partidos_seleccionados.json', 'w', encoding='utf-8') as f:
                    json.dump(partidos_seleccionados, f, indent=2, ensure_ascii=False)
                
                with open('partidos_seleccionados.txt', 'w', encoding='utf-8') as f:
                    f.write(mensaje_partidos)
            
            resultado = enviar_telegram_masivo(mensaje_completo, only_premium=True)
            if resultado["exito"]:
                self.reproducir_sonido_exito()
                
                total_items = len(predicciones_seleccionadas) + len(partidos_seleccionados)
                audiencia = resultado.get('audiencia', 'usuarios')
                mensaje_resultado = f"✅ Se han enviado {total_items} elemento(s) seleccionado(s) a Telegram.\n\n"
                mensaje_resultado += f"📊 Estadísticas de envío:\n"
                mensaje_resultado += f"• Audiencia: Usuarios {audiencia}\n"
                mensaje_resultado += f"• Total usuarios {audiencia}: {resultado['total_usuarios']}\n"
                mensaje_resultado += f"• Enviados exitosos: {resultado['enviados_exitosos']}\n"
                if resultado.get('usuarios_bloqueados', 0) > 0:
                    mensaje_resultado += f"• Usuarios que bloquearon el bot: {resultado['usuarios_bloqueados']}\n"
                if resultado.get('errores', 0) > 0:
                    mensaje_resultado += f"• Errores: {resultado['errores']}\n"
                
                messagebox.showinfo("Enviado", mensaje_resultado)
                
                for var_checkbox in self.checkboxes_predicciones:
                    var_checkbox.set(False)
                for var_checkbox in self.checkboxes_partidos:
                    var_checkbox.set(False)
            else:
                if resultado.get('total_usuarios', 0) == 0 and resultado.get('audiencia') == 'premium activos':
                    messagebox.showinfo("Sin usuarios premium", 
                                      "⚠️ No hay usuarios con membresía activa.\n\n"
                                      "Los pronósticos solo se envían a usuarios premium.\n"
                                      "Otorga acceso premium a usuarios desde el menú '👥 Users'.")
                else:
                    error_msg = "No se pudieron enviar los elementos a Telegram."
                    if resultado.get('detalles_errores'):
                        error_msg += f"\n\nErrores:\n" + "\n".join(resultado['detalles_errores'][:3])
                    messagebox.showerror("Error", error_msg)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error enviando elementos seleccionados: {e}")

    def enviar_alerta(self):
        """Enviar alerta de pronóstico a usuarios premium"""
        mensaje_alerta = """📢 ¡Alerta de pronostico! 📢
Nuestro sistema ha detectado una oportunidad con valor.  
En unos momentos compartiremos nuestra apuesta recomendada. ⚽💰"""
        
        try:
            resultado = enviar_telegram_masivo(mensaje_alerta, only_premium=True)
            if resultado["exito"]:
                audiencia = resultado.get('audiencia', 'usuarios')
                mensaje_resultado = f"✅ La alerta se ha enviado a Telegram correctamente.\n\n"
                mensaje_resultado += f"📊 Estadísticas de envío:\n"
                mensaje_resultado += f"• Audiencia: Usuarios {audiencia}\n"
                mensaje_resultado += f"• Total usuarios {audiencia}: {resultado['total_usuarios']}\n"
                mensaje_resultado += f"• Enviados exitosos: {resultado['enviados_exitosos']}\n"
                if resultado.get('usuarios_bloqueados', 0) > 0:
                    mensaje_resultado += f"• Usuarios que bloquearon el bot: {resultado['usuarios_bloqueados']}\n"
                if resultado.get('errores', 0) > 0:
                    mensaje_resultado += f"• Errores: {resultado['errores']}\n"
                messagebox.showinfo("Alerta Enviada", mensaje_resultado)
            else:
                if resultado.get('total_usuarios', 0) == 0 and resultado.get('audiencia') == 'premium activos':
                    messagebox.showinfo("Sin usuarios premium", 
                                      "⚠️ No hay usuarios con membresía activa.\n\n"
                                      "Las alertas solo se envían a usuarios premium.\n"
                                      "Otorga acceso premium a usuarios desde el menú '👥 Users'.")
                else:
                    error_msg = "No se pudo enviar la alerta a Telegram. Revisa la conexión."
                    if resultado.get('detalles_errores'):
                        error_msg += f"\n\nErrores:\n" + "\n".join(resultado['detalles_errores'][:3])
                    messagebox.showerror("Error", error_msg)
        except Exception as e:
            messagebox.showerror("Error", f"Error enviando alerta a Telegram: {e}")
    
    def enviar_promocion(self):
        """Enviar promoción a usuarios sin membresía activa"""
        mensaje_promocion = """🎁 ¡OFERTA ESPECIAL! 🎁

💎 Únete a BetGeniuX Premium y accede a:
• Pronósticos exclusivos con análisis detallado
• Estadísticas avanzadas de partidos
• Alertas en tiempo real
• Soporte prioritario

💰 Solo $12 USD por semana
📈 Mejora tus resultados con nuestros expertos

🔥 ¡No te pierdas las mejores oportunidades!
Activa tu membresía ahora y empieza a ganar. ⚽💰"""
        
        try:
            resultado = enviar_telegram_masivo(mensaje_promocion, only_premium=False, exclude_premium=True)
            if resultado["exito"]:
                audiencia = resultado.get('audiencia', 'usuarios')
                mensaje_resultado = f"✅ La promoción se ha enviado correctamente.\n\n"
                mensaje_resultado += f"📊 Estadísticas de envío:\n"
                mensaje_resultado += f"• Audiencia: {audiencia}\n"
                mensaje_resultado += f"• Total usuarios: {resultado['total_usuarios']}\n"
                mensaje_resultado += f"• Enviados exitosos: {resultado['enviados_exitosos']}\n"
                if resultado.get('usuarios_bloqueados', 0) > 0:
                    mensaje_resultado += f"• Usuarios que bloquearon el bot: {resultado['usuarios_bloqueados']}\n"
                if resultado.get('errores', 0) > 0:
                    mensaje_resultado += f"• Errores: {resultado['errores']}\n"
                messagebox.showinfo("Promoción Enviada", mensaje_resultado)
            else:
                if resultado.get('total_usuarios', 0) == 0:
                    messagebox.showinfo("Sin usuarios", 
                                      "⚠️ No hay usuarios sin membresía activa.\n\n"
                                      "Todos los usuarios registrados ya tienen membresía premium.")
                else:
                    error_msg = "No se pudo enviar la promoción. Revisa la conexión."
                    if resultado.get('detalles_errores'):
                        error_msg += f"\n\nErrores:\n" + "\n".join(resultado['detalles_errores'][:3])
                    messagebox.showerror("Error", error_msg)
        except Exception as e:
            messagebox.showerror("Error", f"Error enviando promoción: {e}")


    def limpiar_cache_api(self):
        """Limpiar cache de API para forzar datos frescos"""
        try:
            from api_cache import APICache
            cache = APICache()
            cleared = cache.clear_expired()
            messagebox.showinfo("Cache Limpiado", f"Se limpiaron {cleared} entradas de cache expiradas")
        except Exception as e:
            messagebox.showerror("Error", f"Error limpiando cache: {e}")

    def cleanup_cache_periodically(self):
        """Limpiar cache automáticamente cada hora"""
        try:
            from api_cache import APICache
            cache = APICache()
            cache.clear_expired()
            self.root.after(3600000, self.cleanup_cache_periodically)
        except:
            pass

    def abrir_track_record(self):
        """Abre ventana de track record mejorada con filtros y tabla estructurada"""
        try:
            from track_record import TrackRecordManager
            import os
            from datetime import datetime, timedelta
            
            api_key = os.getenv('FOOTYSTATS_API_KEY')
            if not api_key:
                cwd = os.getcwd()
                script_dir = Path(__file__).resolve().parent
                env_in_cwd = Path(cwd) / ".env"
                env_in_script = script_dir / ".env"
                
                error_msg = f"FOOTYSTATS_API_KEY no encontrada en .env\n\n"
                error_msg += f"Directorio actual (CWD): {cwd}\n"
                error_msg += f"Directorio del script: {script_dir}\n"
                error_msg += f".env en CWD existe: {env_in_cwd.exists()}\n"
                error_msg += f".env en script existe: {env_in_script.exists()}\n\n"
                error_msg += "Asegúrate de que el archivo .env está en la raíz del proyecto\n"
                error_msg += "y contiene: FOOTYSTATS_API_KEY=tu_api_key"
                
                messagebox.showerror("Error", error_msg)
                return
            tracker = TrackRecordManager(api_key)
            
            ventana_track = tk.Toplevel(self.root)
            ventana_track.title("📊 Track Record Mejorado - SergioBets IA")
            ventana_track.geometry("1400x800")
            ventana_track.configure(bg="#2c3e50")
            
            frame_principal = tk.Frame(ventana_track, bg="#2c3e50")
            frame_principal.pack(fill='both', expand=True, padx=10, pady=10)
            
            titulo = tk.Label(frame_principal, text="📊 TRACK RECORD DE PREDICCIONES", 
                             bg="#2c3e50", fg="white", font=('Segoe UI', 16, 'bold'))
            titulo.pack(pady=(0, 20))
            
            frame_filtros = tk.Frame(frame_principal, bg="#2c3e50")
            frame_filtros.pack(fill='x', pady=(0, 10))
            
            frame_fechas = tk.Frame(frame_principal, bg="#2c3e50")
            frame_fechas.pack(fill='x', pady=(0, 10))
            
            frame_acciones = tk.Frame(frame_principal, bg="#2c3e50")
            frame_acciones.pack(fill='x', pady=(0, 10))
            
            filtro_actual = tk.StringVar(value="historico")
            fecha_inicio = tk.StringVar()
            fecha_fin = tk.StringVar()
            
            hoy = datetime.now()
            hace_mes = hoy - timedelta(days=30)
            fecha_inicio.set(hace_mes.strftime('%Y-%m-%d'))
            fecha_fin.set(hoy.strftime('%Y-%m-%d'))
            
            columns = ('fecha', 'liga', 'equipos', 'tipo_apuesta', 'cuota', 'resultado', 'estado')
            tree = ttk.Treeview(frame_principal, columns=columns, show='headings', height=20)
            
            tree.heading('fecha', text='Fecha')
            tree.heading('liga', text='Liga')
            tree.heading('equipos', text='Equipos')
            tree.heading('tipo_apuesta', text='Tipo de Apuesta')
            tree.heading('cuota', text='Cuota')
            tree.heading('resultado', text='Resultado Final')
            tree.heading('estado', text='Estado')
            
            tree.column('fecha', width=100)
            tree.column('liga', width=150)
            tree.column('equipos', width=200)
            tree.column('tipo_apuesta', width=180)
            tree.column('cuota', width=80)
            tree.column('resultado', width=120)
            tree.column('estado', width=100)
            
            scrollbar = ttk.Scrollbar(frame_principal, orient='vertical', command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            tree.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
            def mostrar_bets_por_categoria(categoria):
                """Mostrar apuestas por categoría con interfaz scrollable mejorada"""
                try:
                    historial = cargar_json('historial_predicciones.json') or []
                except:
                    historial = []
                
                for widget in frame_principal.winfo_children():
                    if widget not in [frame_filtros, frame_fechas, frame_acciones]:
                        widget.destroy()
                
                historial = [p for p in historial if p.get('sent_to_telegram', False)]
                
                if categoria == "pendientes":
                    bets_filtrados = [p for p in historial if p.get("resultado_real") is None or p.get("acierto") is None]
                    titulo = "⏳ APUESTAS PENDIENTES"
                    color_titulo = "#f39c12"
                elif categoria == "acertados":
                    bets_filtrados = [p for p in historial if p.get("acierto") == True]
                    titulo = "✅ APUESTAS ACERTADAS"
                    color_titulo = "#27ae60"
                elif categoria == "fallados":
                    bets_filtrados = [p for p in historial if p.get("acierto") == False]
                    titulo = "❌ APUESTAS FALLADAS"
                    color_titulo = "#e74c3c"
                else:
                    return
                
                canvas = tk.Canvas(frame_principal, bg="#2c3e50", highlightthickness=0)
                scrollbar = ttk.Scrollbar(frame_principal, orient="vertical", command=canvas.yview)
                scrollable_frame = tk.Frame(canvas, bg="#2c3e50")
                
                scrollable_frame.bind(
                    "<Configure>",
                    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
                )
                
                canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
                canvas.configure(yscrollcommand=scrollbar.set)
                
                titulo_label = tk.Label(scrollable_frame, text=f"{titulo} ({len(bets_filtrados)} apuestas)", 
                                       bg="#2c3e50", fg=color_titulo, font=('Segoe UI', 14, 'bold'))
                titulo_label.pack(pady=(10, 20))
                
                def eliminar_prediccion_individual(bet_to_delete):
                    """Eliminar una predicción individual del historial"""
                    respuesta = messagebox.askyesno("Confirmar eliminación", 
                        f"¿Estás seguro de que quieres eliminar esta predicción?\n\n" +
                        f"Partido: {bet_to_delete.get('partido', 'N/A')}\n" +
                        f"Predicción: {bet_to_delete.get('prediccion', 'N/A')}")
                    
                    if respuesta:
                        try:
                            historial_actual = cargar_json('historial_predicciones.json') or []
                            historial_filtrado = []
                            bet_removed = False
                            for p in historial_actual:
                                if (p.get('partido') == bet_to_delete.get('partido') and
                                    p.get('prediccion') == bet_to_delete.get('prediccion') and
                                    p.get('fecha') == bet_to_delete.get('fecha') and
                                    p.get('cuota') == bet_to_delete.get('cuota') and
                                    not bet_removed):
                                    bet_removed = True
                                    continue
                                historial_filtrado.append(p)
                            
                            with open('historial_predicciones.json', 'w', encoding='utf-8') as f:
                                json.dump(historial_filtrado, f, indent=2, ensure_ascii=False)
                            
                            messagebox.showinfo("Éxito", "Predicción eliminada correctamente")
                            mostrar_bets_por_categoria(categoria)  # Refresh the display
                        except Exception as e:
                            messagebox.showerror("Error", f"Error eliminando predicción: {e}")
                
                def editar_prediccion_individual(bet_to_edit):
                    """Editar una predicción individual para marcarla como ganada"""
                    respuesta = messagebox.askyesno("Confirmar edición manual", 
                        f"¿Estás seguro de que quieres marcar esta predicción como GANADA?\n\n" +
                        f"Partido: {bet_to_edit.get('partido', 'N/A')}\n" +
                        f"Predicción: {bet_to_edit.get('prediccion', 'N/A')}\n" +
                        f"Cuota: {bet_to_edit.get('cuota', 'N/A')}\n\n" +
                        f"Esta acción marcará la predicción como acertada manualmente.")
                    
                    if respuesta:
                        try:
                            from datetime import datetime
                            historial_actual = cargar_json('historial_predicciones.json') or []
                            
                            for prediccion in historial_actual:
                                if (prediccion.get('partido') == bet_to_edit.get('partido') and 
                                   prediccion.get('prediccion') == bet_to_edit.get('prediccion') and
                                   prediccion.get('fecha') == bet_to_edit.get('fecha') and
                                   prediccion.get('cuota') == bet_to_edit.get('cuota')):
                                    
                                    prediccion['acierto'] = True
                                    prediccion['actualizacion_manual'] = True
                                    prediccion['fecha_actualizacion'] = datetime.now().isoformat()
                                    
                                    stake = float(prediccion.get('stake', 0))
                                    cuota = float(prediccion.get('cuota', 1))
                                    ganancia = stake * cuota
                                    prediccion['ganancia'] = ganancia
                                    
                                    break
                            
                            with open('historial_predicciones.json', 'w', encoding='utf-8') as f:
                                json.dump(historial_actual, f, indent=2, ensure_ascii=False)
                            
                            messagebox.showinfo("Éxito", "Predicción marcada como ganada correctamente")
                            mostrar_bets_por_categoria(categoria)
                            
                        except Exception as e:
                            messagebox.showerror("Error", f"Error editando predicción: {e}")
                
                if not bets_filtrados:
                    if categoria == "pendientes":
                        no_bets_label = tk.Label(scrollable_frame, text="No hay apuestas pendientes enviadas a Telegram", 
                                                bg="#2c3e50", fg="#7f8c8d", font=('Segoe UI', 12))
                    elif categoria == "acertados":
                        no_bets_label = tk.Label(scrollable_frame, text="No hay apuestas acertadas enviadas a Telegram", 
                                                bg="#2c3e50", fg="#7f8c8d", font=('Segoe UI', 12))
                    else:
                        no_bets_label = tk.Label(scrollable_frame, text="No hay apuestas falladas enviadas a Telegram", 
                                                bg="#2c3e50", fg="#7f8c8d", font=('Segoe UI', 12))
                    no_bets_label.pack(pady=20)
                else:
                    for i, bet in enumerate(bets_filtrados):
                        bet_frame = tk.Frame(scrollable_frame, bg="white", relief='ridge', bd=1)
                        bet_frame.pack(fill='x', pady=5, padx=10)
                        
                        header_frame = tk.Frame(bet_frame, bg="white")
                        header_frame.pack(fill='x', padx=10, pady=(5, 0))
                        
                        partido_text = f"⚽ {bet.get('partido', 'N/A')}"
                        partido_label = tk.Label(header_frame, text=partido_text, bg="white", 
                                               font=('Segoe UI', 11, 'bold'), anchor='w')
                        partido_label.pack(side='left', fill='x', expand=True)
                        
                        if categoria == "fallados":
                            edit_btn = tk.Button(header_frame, text="✏️", 
                                               command=lambda b=bet: editar_prediccion_individual(b),
                                               bg="#f39c12", fg="white", font=('Segoe UI', 8, 'bold'), 
                                               padx=5, pady=2)
                            edit_btn.pack(side='right', padx=(5, 0))
                        
                        delete_btn = tk.Button(header_frame, text="🗑️", 
                                             command=lambda b=bet: eliminar_prediccion_individual(b),
                                             bg="#e74c3c", fg="white", font=('Segoe UI', 8, 'bold'), 
                                             padx=5, pady=2)
                        delete_btn.pack(side='right', padx=(5, 0))
                        
                        prediccion_text = f"🎯 {bet.get('prediccion', 'N/A')} | 💰 {bet.get('cuota', 'N/A')} | 💵 ${bet.get('stake', 'N/A')}"
                        prediccion_label = tk.Label(bet_frame, text=prediccion_text, bg="white", 
                                                  font=('Segoe UI', 10), anchor='w')
                        prediccion_label.pack(fill='x', padx=10)
                        
                        fecha_text = f"📅 {bet.get('fecha', 'N/A')}"
                        if bet.get('fecha_actualizacion'):
                            fecha_text += f" | 🔄 Actualizado: {bet.get('fecha_actualizacion', '')[:10]}"
                        fecha_label = tk.Label(bet_frame, text=fecha_text, bg="white", 
                                             font=('Segoe UI', 9), fg="#7f8c8d", anchor='w')
                        fecha_label.pack(fill='x', padx=10)
                        
                        if bet.get("resultado_real"):
                            resultado = bet["resultado_real"]
                            if categoria == "acertados":
                                ganancia_text = f"💰 Ganancia: ${bet.get('ganancia', 0):.2f}"
                                ganancia_label = tk.Label(bet_frame, text=ganancia_text, bg="white", 
                                                        font=('Segoe UI', 10, 'bold'), fg="#27ae60", anchor='w')
                                ganancia_label.pack(fill='x', padx=10, pady=(0, 5))
                            elif categoria == "fallados":
                                perdida_text = f"💸 Pérdida: ${bet.get('ganancia', 0):.2f}"
                                perdida_label = tk.Label(bet_frame, text=perdida_text, bg="white", 
                                                       font=('Segoe UI', 10, 'bold'), fg="#e74c3c", anchor='w')
                                perdida_label.pack(fill='x', padx=10, pady=(0, 5))
                            
                            if 'corner' in bet.get('prediccion', '').lower():
                                corners_text = f"🚩 Corners: {resultado.get('total_corners', 'N/A')} total"
                            else:
                                corners_text = f"⚽ Resultado: {resultado.get('home_score', 0)}-{resultado.get('away_score', 0)}"
                            
                            resultado_label = tk.Label(bet_frame, text=corners_text, bg="white", 
                                                     font=('Segoe UI', 9), fg="#34495e", anchor='w')
                            resultado_label.pack(fill='x', padx=10, pady=(0, 5))
                
                canvas.pack(side="left", fill="both", expand=True)
                scrollbar.pack(side="right", fill="y")
            
            def cargar_datos_filtrados():
                """Carga datos según el filtro actual - mantener para compatibilidad"""
                filtro = filtro_actual.get()
                if filtro in ["pendientes", "acertados", "fallados"]:
                    mostrar_bets_por_categoria(filtro)
                else:
                    for item in tree.get_children():
                        tree.delete(item)
                    
                    try:
                        historial = cargar_json('historial_predicciones.json') or []
                        
                        historial = [p for p in historial if p.get('sent_to_telegram', False)]
                        
                        if not historial:
                            tk.Label(frame_principal, text="No hay predicciones enviadas a Telegram", 
                                   font=('Segoe UI', 12), fg="#7f8c8d", bg="#2c3e50").pack(pady=20)
                        
                        datos_filtrados = []
                        
                        for prediccion in historial:
                            if filtro == "por_fecha":
                                fecha_pred = prediccion.get('fecha', '')
                                if fecha_pred < fecha_inicio.get() or fecha_pred > fecha_fin.get():
                                    continue
                            
                            resultado_real = prediccion.get('resultado_real')
                            acierto = prediccion.get('acierto')
                            
                            if resultado_real is None:
                                estado = "⏳ Pendiente"
                                resultado_final = "-"
                            elif acierto:
                                estado = "✅ Ganada"
                                resultado_final = f"{resultado_real.get('home_score', 0)}-{resultado_real.get('away_score', 0)}"
                            else:
                                estado = "❌ Perdida"
                                resultado_final = f"{resultado_real.get('home_score', 0)}-{resultado_real.get('away_score', 0)}"
                            
                            datos_filtrados.append((
                                prediccion.get('fecha', ''),
                                prediccion.get('liga', ''),
                                prediccion.get('partido', ''),
                                prediccion.get('prediccion', ''),
                                f"{prediccion.get('cuota', 0):.2f}",
                                resultado_final,
                                estado
                            ))
                        
                        datos_filtrados.sort(key=lambda x: x[0], reverse=True)
                        
                        for i, datos in enumerate(datos_filtrados):
                            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                            tree.insert('', 'end', values=datos, tags=(tag,))
                        
                        tree.tag_configure('evenrow', background='#f8f9fa')
                        tree.tag_configure('oddrow', background='white')
                        
                        
                    except Exception as e:
                        messagebox.showerror("Error", f"Error cargando datos: {e}")
            
            
            def filtrar_pendientes():
                filtro_actual.set("pendientes")
                mostrar_bets_por_categoria("pendientes")
            
            def filtrar_acertados():
                filtro_actual.set("acertados")
                mostrar_bets_por_categoria("acertados")
            
            def filtrar_fallados():
                filtro_actual.set("fallados")
                mostrar_bets_por_categoria("fallados")
            
            def filtrar_historico():
                filtro_actual.set("historico")
                cargar_datos_filtrados()
            
            def filtrar_por_fecha():
                filtro_actual.set("por_fecha")
                cargar_datos_filtrados()
            
            def mostrar_resumen():
                """Abre ventana con resumen detallado"""
                ventana_resumen = tk.Toplevel(ventana_track)
                ventana_resumen.title("📊 Resumen Detallado")
                ventana_resumen.geometry("600x500")
                ventana_resumen.configure(bg="#f8f9fa")
                
                try:
                    reporte = tracker.generar_reporte_detallado()
                    text_widget = ScrolledText(ventana_resumen, wrap=tk.WORD, 
                                             font=('Consolas', 10), bg="white")
                    text_widget.pack(fill='both', expand=True, padx=10, pady=10)
                    text_widget.insert('1.0', reporte)
                    text_widget.config(state='disabled')
                except Exception as e:
                    tk.Label(ventana_resumen, text=f"Error generando reporte: {e}").pack()
            
            def actualizar_resultados():
                """Actualizar resultados desde la API de forma rápida y silenciosa"""
                import threading
                
                def update_in_thread():
                    try:
                        from_date = fecha_inicio.get() if fecha_inicio.get() else None
                        to_date = fecha_fin.get() if fecha_fin.get() else None
                        resultado = tracker.actualizar_historial_con_resultados(
                            max_matches=50, 
                            timeout_per_match=15,
                            from_date=from_date,
                            to_date=to_date
                        )
                        
                        def update_gui():
                            try:
                                filtro = filtro_actual.get()
                                if filtro in ["pendientes", "acertados", "fallados"]:
                                    mostrar_bets_por_categoria(filtro)
                                else:
                                    cargar_datos_filtrados()
                                
                                actualizaciones = resultado.get('actualizaciones', 0)
                                timeouts = resultado.get('timeouts', 0)
                                restantes = resultado.get('matches_restantes', 0)
                                
                                if actualizaciones > 0:
                                    text = f"✅ {actualizaciones} actualizadas"
                                    if restantes > 0:
                                        text += f" ({restantes} pendientes)"
                                    btn_actualizar.config(text=text)
                                elif timeouts > 0:
                                    btn_actualizar.config(text=f"⏰ {timeouts} timeouts")
                                elif restantes > 0:
                                    btn_actualizar.config(text=f"⏳ {restantes} pendientes")
                                else:
                                    btn_actualizar.config(text="✅ Sin cambios")
                                
                                ventana_track.after(3000, lambda: btn_actualizar.config(text="🔄 Actualizar Resultados"))
                                
                            except Exception as e:
                                btn_actualizar.config(text="❌ Error GUI")
                                ventana_track.after(2000, lambda: btn_actualizar.config(text="🔄 Actualizar Resultados"))
                            finally:
                                btn_actualizar.config(state='normal')
                        
                        ventana_track.after(0, update_gui)
                        
                    except Exception as e:
                        def show_error():
                            btn_actualizar.config(text="❌ Error API", state='normal')
                            ventana_track.after(2000, lambda: btn_actualizar.config(text="🔄 Actualizar Resultados"))
                        
                        ventana_track.after(0, show_error)
                
                btn_actualizar.config(state='disabled', text="🔄 Actualizando...")
                thread = threading.Thread(target=update_in_thread, daemon=True)
                thread.start()
            
            def actualizar_automatico():
                """Actualiza resultados automáticamente cada 4 horas"""
                import threading
                
                def update_in_background():
                    try:
                        from_date = fecha_inicio.get() if fecha_inicio.get() else None
                        to_date = fecha_fin.get() if fecha_fin.get() else None
                        resultado = tracker.actualizar_historial_con_resultados(
                            max_matches=50, 
                            timeout_per_match=15,
                            from_date=from_date,
                            to_date=to_date
                        )
                        if resultado.get('actualizaciones', 0) > 0:
                            ventana_track.after(0, cargar_datos_filtrados)
                            print(f"✅ Auto-actualización: {resultado.get('actualizaciones', 0)} predicciones actualizadas")
                    except Exception as e:
                        print(f"❌ Error en auto-actualización: {e}")
                
                def schedule_next_update():
                    """Programa la próxima actualización en 4 horas"""
                    thread = threading.Thread(target=update_in_background, daemon=True)
                    thread.start()
                    ventana_track.after(14400000, schedule_next_update)
                
                thread = threading.Thread(target=update_in_background, daemon=True)
                thread.start()
                ventana_track.after(14400000, schedule_next_update)
            
            def limpiar_historial():
                """Limpia todo el historial"""
                respuesta = messagebox.askyesno("Confirmar", 
                    "¿Estás seguro de que quieres limpiar todo el historial?\n\n" +
                    "Esta acción no se puede deshacer.")
                
                if respuesta:
                    try:
                        with open('historial_predicciones.json', 'w', encoding='utf-8') as f:
                            f.write('[]')
                        messagebox.showinfo("Éxito", "Historial limpiado correctamente")
                        cargar_datos_filtrados()
                    except Exception as e:
                        messagebox.showerror("Error", f"Error limpiando historial: {e}")
            
            btn_pendientes = tk.Button(frame_filtros, text="📌 PENDIENTES", 
                                      command=filtrar_pendientes, bg="#f39c12", fg="white",
                                      font=('Segoe UI', 10, 'bold'), padx=10, pady=5)
            btn_pendientes.pack(side='left', padx=(0, 5))
            
            btn_acertados = tk.Button(frame_filtros, text="✅ ACERTADOS", 
                                     command=filtrar_acertados, bg="#27ae60", fg="white",
                                     font=('Segoe UI', 10, 'bold'), padx=10, pady=5)
            btn_acertados.pack(side='left', padx=5)
            
            btn_fallados = tk.Button(frame_filtros, text="❌ FALLADOS", 
                                    command=filtrar_fallados, bg="#e74c3c", fg="white",
                                    font=('Segoe UI', 10, 'bold'), padx=10, pady=5)
            btn_fallados.pack(side='left', padx=5)
            
            btn_historico = tk.Button(frame_filtros, text="📅 HISTÓRICO", 
                                     command=filtrar_historico, bg="#3498db", fg="white",
                                     font=('Segoe UI', 10, 'bold'), padx=10, pady=5)
            btn_historico.pack(side='left', padx=5)
            
            
            tk.Label(frame_fechas, text="🗓️ Filtro por fechas:", 
                    bg="#2c3e50", fg="white", font=('Segoe UI', 10, 'bold')).pack(side='left')
            
            tk.Label(frame_fechas, text="Desde:", bg="#2c3e50", fg="white").pack(side='left', padx=(10, 5))
            entry_fecha_inicio = DateEntry(frame_fechas, width=12, background="darkblue", 
                                          foreground="white", borderwidth=2, 
                                          date_pattern='yyyy-MM-dd', textvariable=fecha_inicio)
            entry_fecha_inicio.pack(side='left', padx=5)
            
            tk.Label(frame_fechas, text="Hasta:", bg="#2c3e50", fg="white").pack(side='left', padx=(10, 5))
            entry_fecha_fin = DateEntry(frame_fechas, width=12, background="darkblue", 
                                       foreground="white", borderwidth=2, 
                                       date_pattern='yyyy-MM-dd', textvariable=fecha_fin)
            entry_fecha_fin.pack(side='left', padx=5)
            
            btn_filtrar_fecha = tk.Button(frame_fechas, text="🗓️ FILTRAR", 
                                         command=filtrar_por_fecha, bg="#34495e", fg="white",
                                         font=('Segoe UI', 10, 'bold'), padx=10, pady=5)
            btn_filtrar_fecha.pack(side='left', padx=(10, 0))
            
            btn_actualizar = tk.Button(frame_acciones, text="🔄 Actualizar Resultados", 
                                      command=actualizar_resultados, bg="#3498db", fg="white",
                                      font=('Segoe UI', 10, 'bold'), padx=15, pady=5)
            btn_actualizar.pack(side='left', padx=(0, 10))
            
            btn_limpiar = tk.Button(frame_acciones, text="🧹 Limpiar Historial", 
                                   command=limpiar_historial, bg="#e74c3c", fg="white",
                                   font=('Segoe UI', 10, 'bold'), padx=15, pady=5)
            btn_limpiar.pack(side='left', padx=(0, 10))
            
            cargar_datos_filtrados()
            
            actualizar_automatico()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error abriendo track record: {e}")

    def abrir_usuarios(self):
        """Abrir ventana de gestión de usuarios VIP"""
        try:
            import tkinter as tk
            from tkinter import messagebox, simpledialog, ttk
            
            try:
                from access_manager import access_manager
                if not access_manager or not hasattr(access_manager, 'listar_usuarios'):
                    messagebox.showerror("Error", "Sistema de usuarios no está configurado correctamente.")
                    return
            except ImportError:
                messagebox.showerror("Error", "Módulo access_manager no encontrado.\nEsta funcionalidad no está disponible.")
                return
            except Exception as e:
                messagebox.showerror("Error", f"Error cargando sistema de usuarios: {e}")
                return
            
            ventana_usuarios = tk.Toplevel(self.root)
            ventana_usuarios.title("👥 Gestión de Usuarios VIP")
            ventana_usuarios.geometry("1100x700")
            ventana_usuarios.configure(bg="#2c3e50")
            
            ventana_usuarios.grid_rowconfigure(1, weight=1)
            ventana_usuarios.grid_columnconfigure(0, weight=1)
            
            frame_header = tk.Frame(ventana_usuarios, bg="#2c3e50")
            frame_header.grid(row=0, column=0, sticky='ew', padx=10, pady=(10, 0))
            
            tk.Label(frame_header, text="👥 GESTIÓN DE USUARIOS VIP", 
                    bg="#2c3e50", fg="white", font=('Segoe UI', 16, 'bold')).pack(pady=(0, 10))
            
            frame_stats = tk.Frame(frame_header, bg="#34495e", relief='raised', bd=2)
            frame_stats.pack(fill='x', pady=(0, 10))
            
            stats_label = tk.Label(frame_stats, text="📊 Cargando estadísticas...", 
                                  bg="#34495e", fg="white", font=('Segoe UI', 12))
            stats_label.pack(pady=10)
            
            frame_table = tk.Frame(ventana_usuarios, bg="#2c3e50")
            frame_table.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)
            frame_table.grid_rowconfigure(0, weight=1)
            frame_table.grid_columnconfigure(0, weight=1)
            
            style = ttk.Style()
            style.theme_use('clam')
            style.configure("Treeview", 
                          background="white",
                          foreground="black",
                          rowheight=30,
                          fieldbackground="white",
                          font=('Segoe UI', 10))
            style.configure("Treeview.Heading",
                          background="#34495e",
                          foreground="white",
                          font=('Segoe UI', 11, 'bold'),
                          relief='raised')
            style.map('Treeview', background=[('selected', '#3498db')])
            
            columns = ('id', 'usuario', 'nombre', 'premium', 'expira')
            tree = ttk.Treeview(frame_table, columns=columns, show='headings', selectmode='browse')
            
            tree.heading('id', text='ID', anchor='center')
            tree.heading('usuario', text='Usuario', anchor='w')
            tree.heading('nombre', text='Nombre', anchor='w')
            tree.heading('premium', text='Premium', anchor='center')
            tree.heading('expira', text='Expira', anchor='center')
            
            tree.column('id', width=120, minwidth=100, anchor='center')
            tree.column('usuario', width=200, minwidth=150, anchor='w')
            tree.column('nombre', width=200, minwidth=150, anchor='w')
            tree.column('premium', width=100, minwidth=80, anchor='center')
            tree.column('expira', width=180, minwidth=150, anchor='center')
            
            tree.tag_configure('odd', background='#f0f0f0')
            tree.tag_configure('even', background='white')
            
            scrollbar_y = ttk.Scrollbar(frame_table, orient='vertical', command=tree.yview)
            scrollbar_x = ttk.Scrollbar(frame_table, orient='horizontal', command=tree.xview)
            tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
            
            tree.grid(row=0, column=0, sticky='nsew')
            scrollbar_y.grid(row=0, column=1, sticky='ns')
            scrollbar_x.grid(row=1, column=0, sticky='ew')
            
            sort_reverse = {}
            
            def sort_column(col):
                data = [(tree.set(child, col), child) for child in tree.get_children('')]
                
                if col == 'expira':
                    def sort_key(item):
                        val = item[0]
                        if val == 'N/A' or val == 'Error fecha':
                            return ('9999-99-99 99:99', item[1])
                        return (val, item[1])
                    data.sort(key=sort_key, reverse=sort_reverse.get(col, False))
                elif col == 'premium':
                    data.sort(key=lambda x: (0 if '✅' in x[0] else 1, x[1]), reverse=sort_reverse.get(col, False))
                else:
                    data.sort(reverse=sort_reverse.get(col, False))
                
                for index, (val, child) in enumerate(data):
                    tree.move(child, '', index)
                    tree.item(child, tags=('even',) if index % 2 == 0 else ('odd',))
                
                sort_reverse[col] = not sort_reverse.get(col, False)
            
            for col in columns:
                tree.heading(col, command=lambda c=col: sort_column(c))
            
            frame_botones = tk.Frame(ventana_usuarios, bg="#2c3e50")
            frame_botones.grid(row=2, column=0, sticky='ew', padx=10, pady=(0, 10))
            
            def actualizar_estadisticas():
                try:
                    stats = access_manager.obtener_estadisticas()
                    if stats and isinstance(stats, dict):
                        total = stats.get('total_usuarios', 0)
                        premium = stats.get('usuarios_premium', 0)
                        gratuitos = stats.get('usuarios_gratuitos', 0)
                        porcentaje = stats.get('porcentaje_premium', 0)
                        
                        stats_text = f"📊 Total: {total} | 👑 Premium: {premium} | 🆓 Gratuitos: {gratuitos} | 📈 Premium: {porcentaje:.1f}%"
                        stats_label.config(text=stats_text)
                    else:
                        stats_label.config(text="📊 Estadísticas no disponibles")
                except AttributeError as e:
                    stats_label.config(text="❌ Error: Módulo access_manager no configurado")
                    print(f"AttributeError en actualizar_estadisticas: {e}")
                except TypeError as e:
                    stats_label.config(text="❌ Error: Datos de estadísticas inválidos")
                    print(f"TypeError en actualizar_estadisticas: {e}")
                except Exception as e:
                    stats_label.config(text=f"❌ Error cargando estadísticas: {e}")
                    print(f"Error en actualizar_estadisticas: {e}")
            
            def refrescar_usuarios():
                try:
                    usuarios = access_manager.listar_usuarios()
                    
                    for item in tree.get_children():
                        tree.delete(item)
                    
                    if usuarios and isinstance(usuarios, (list, tuple)) and len(usuarios) > 0:
                        for index, usuario in enumerate(usuarios):
                            if usuario and isinstance(usuario, dict):
                                user_id = str(usuario.get('user_id', 'N/A'))
                                username = usuario.get('username', 'N/A') if usuario.get('username') else 'N/A'
                                first_name = usuario.get('first_name', 'N/A') if usuario.get('first_name') else 'N/A'
                                premium = "✅ SÍ" if usuario.get('premium', False) else "❌ NO"
                                
                                expira = "N/A"
                                if usuario.get('fecha_expiracion'):
                                    try:
                                        from datetime import datetime
                                        fecha_exp = datetime.fromisoformat(usuario['fecha_expiracion'])
                                        expira = fecha_exp.strftime('%Y-%m-%d %H:%M')
                                    except:
                                        expira = "Error fecha"
                                
                                tag = 'even' if index % 2 == 0 else 'odd'
                                tree.insert('', 'end', values=(user_id, username, first_name, premium, expira), tags=(tag,))
                    
                    actualizar_estadisticas()
                except AttributeError as e:
                    messagebox.showerror("Error", f"Error: Módulo access_manager no configurado - {e}")
                    print(f"AttributeError en refrescar_usuarios: {e}")
                except TypeError as e:
                    messagebox.showerror("Error", f"Error: Datos de usuarios inválidos - {e}")
                    print(f"TypeError en refrescar_usuarios: {e}")
                except Exception as e:
                    messagebox.showerror("Error", f"Error cargando usuarios: {e}")
                    print(f"Error en refrescar_usuarios: {e}")
                    import traceback
                    print(f"Traceback: {traceback.format_exc()}")
            
            def otorgar_acceso():
                user_id = simpledialog.askstring("Otorgar Acceso", "Ingresa el ID del usuario:")
                if not user_id:
                    return
                
                user_id = user_id.strip()
                if not user_id:
                    messagebox.showerror("Error", "❌ El ID del usuario no puede estar vacío")
                    return
                
                dias = simpledialog.askinteger("Días de Acceso", "¿Cuántos días deseas otorgar de acceso premium?", 
                                              minvalue=1, maxvalue=365)
                if not dias:
                    return
                
                try:
                    if access_manager.otorgar_acceso(user_id, dias):
                        mensaje_confirmacion = access_manager.generar_mensaje_confirmacion_premium(user_id)
                        
                        try:
                            from telegram_utils import enviar_telegram
                            
                            chat_id = user_id
                            if user_id.isdigit() or (user_id.startswith('-') and user_id[1:].isdigit()):
                                chat_id = int(user_id)
                            
                            exito_envio = enviar_telegram(chat_id=chat_id, mensaje=mensaje_confirmacion)
                            
                            if exito_envio:
                                messagebox.showinfo("Éxito", f"✅ Acceso premium otorgado y mensaje de confirmación enviado al usuario {user_id}")
                            else:
                                messagebox.showwarning("Parcial", f"✅ Acceso premium otorgado pero NO se pudo enviar el mensaje de confirmación.\n\n⚠️ Posibles causas:\n• El usuario no ha iniciado el bot en Telegram\n• El usuario bloqueó el bot\n• El ID del usuario es incorrecto\n\nRevisa la consola para más detalles del error.")
                        except Exception as telegram_error:
                            messagebox.showwarning("Parcial", f"✅ Acceso premium otorgado pero error enviando mensaje: {telegram_error}")
                        
                        refrescar_usuarios()
                    else:
                        messagebox.showerror("Error", "❌ Usuario no encontrado")
                except Exception as e:
                    messagebox.showerror("Error", f"Error otorgando acceso: {e}")
            
            def banear_usuario():
                user_id = simpledialog.askstring("Banear Usuario", "Ingresa el ID del usuario a banear:")
                if not user_id:
                    return
                
                confirmar = messagebox.askyesno("Confirmar Baneo", 
                    f"¿Estás seguro de banear al usuario {user_id}?\n\nEsto removerá su acceso premium inmediatamente.")
                
                if confirmar:
                    try:
                        if access_manager.banear_usuario(user_id):
                            messagebox.showinfo("Éxito", "✅ Usuario baneado correctamente")
                            refrescar_usuarios()
                        else:
                            messagebox.showerror("Error", "❌ Usuario no encontrado")
                    except Exception as e:
                        messagebox.showerror("Error", f"Error baneando usuario: {e}")
            
            def limpiar_expirados():
                try:
                    count = access_manager.limpiar_usuarios_expirados()
                    messagebox.showinfo("Limpieza Completada", f"🧹 {count} usuarios con acceso expirado limpiados")
                    refrescar_usuarios()
                except Exception as e:
                    messagebox.showerror("Error", f"Error limpiando usuarios: {e}")
            
            tk.Button(frame_botones, text="🔄 Refrescar", command=refrescar_usuarios,
                     bg="#3498db", fg="white", font=('Segoe UI', 10, 'bold'),
                     padx=15, pady=5).pack(side='left', padx=(0, 5))
            
            tk.Button(frame_botones, text="👑 OTORGAR ACCESO", command=otorgar_acceso,
                     bg="#27ae60", fg="white", font=('Segoe UI', 10, 'bold'),
                     padx=15, pady=5).pack(side='left', padx=5)
            
            tk.Button(frame_botones, text="🚫 BANEAR", command=banear_usuario,
                     bg="#e74c3c", fg="white", font=('Segoe UI', 10, 'bold'),
                     padx=15, pady=5).pack(side='left', padx=5)
            
            tk.Button(frame_botones, text="🧹 Limpiar Expirados", command=limpiar_expirados,
                     bg="#f39c12", fg="white", font=('Segoe UI', 10, 'bold'),
                     padx=15, pady=5).pack(side='left', padx=5)
            
            refrescar_usuarios()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error abriendo gestión de usuarios: {e}")
            import traceback
            print(f"Error detallado en abrir_usuarios: {traceback.format_exc()}")

    def run(self):
        """Ejecutar aplicación principal con GUI y servicios backend"""
        print("🎯 SergioBets - Sistema Completo con GUI y Pagos")
        print("=" * 60)
        
        if not self.check_dependencies():
            print("❌ Faltan dependencias. Abortando.")
            return False
        
        if not self.start_webhook_server():
            print("❌ No se pudo iniciar servidor webhook")
            return False
        
        ngrok_success = self.start_ngrok_tunnel()
        if not ngrok_success:
            print("⚠️ No se pudo iniciar túnel ngrok - continuando sin ngrok")
            logger.warning("Ngrok tunnel failed to start - continuing without ngrok")
            self.ngrok_url = "http://localhost:5000"  # Fallback to localhost
        
        if not self.start_telegram_bot():
            print("❌ No se pudo iniciar bot de Telegram")
            self.stop_all_services()
            return False
        
        print("\n" + "=" * 60)
        print("🎉 ¡SergioBets iniciado correctamente!")
        if ngrok_success and self.ngrok_url and "ngrok" in self.ngrok_url:
            print(f"🌐 URL pública: {self.ngrok_url}")
            print(f"📡 Webhook: {self.ngrok_url}/webhook/nowpayments")
            print(f"🔧 API: {self.ngrok_url}/api/create_payment")
        else:
            print("🌐 URL local: http://localhost:5000")
            print("📡 Webhook: http://localhost:5000/webhook/nowpayments")
            print("🔧 API: http://localhost:5000/api/create_payment")
            print("⚠️ Ngrok no disponible - usando localhost")
        print("=" * 60)
        
        print("\n📋 Próximos pasos:")
        if ngrok_success and self.ngrok_url and "ngrok" in self.ngrok_url:
            print("1. Configura esta URL en NOWPayments dashboard")
            print("2. El bot de Telegram ya está activo")
            print("3. ¡El sistema está listo para recibir pagos!")
        else:
            print("1. Configura ngrok para obtener URL pública")
            print("2. El bot de Telegram ya está activo")
            print("3. Usa localhost para pruebas locales")
        print("\n🤖 El bot de Telegram está ejecutándose en segundo plano")
        print("🌐 El servidor webhook está activo en puerto 5000")
        if ngrok_success and self.ngrok_url and "ngrok" in self.ngrok_url:
            print("🔗 El túnel ngrok está conectado")
        else:
            print("⚠️ El túnel ngrok no está disponible")
        print("\n🎉 Iniciando GUI de SergioBets...")
        
        try:
            self.setup_gui()
            print("✅ GUI iniciada correctamente")
            
            monitor_thread = threading.Thread(target=self.monitor_services, daemon=True)
            monitor_thread.start()
            
            self.root.mainloop()
            
        except Exception as e:
            print(f"❌ Error en GUI: {e}")
            logger.error(f"GUI error: {e}")
        
        logger.info("Stopping all services...")
        self.stop_all_services()
        print("✅ SergioBets detenido correctamente")
        logger.info("✅ SergioBets stopped successfully")
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
