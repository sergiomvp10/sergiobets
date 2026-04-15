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
from datetime import date, timedelta, datetime, timezone
from dotenv import load_dotenv, find_dotenv

# Zona horaria de Bogota, Colombia (UTC-5)
TZ_BOGOTA = timezone(timedelta(hours=-5))

def hora_bogota():
    """Retorna la hora actual en zona horaria de Bogota, Colombia"""
    return datetime.now(TZ_BOGOTA)

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
        self.vsb = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview, style='Slim.Vertical.TScrollbar')
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
    """Gestiona temas claro y oscuro con paleta profesional tipo dashboard"""
    def __init__(self, root):
        from tkinter import font as tkfont
        self.root = root
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.base_font = tkfont.nametofont('TkDefaultFont')
        self.base_font.configure(family='Segoe UI', size=10)
        self.heading_font = tkfont.Font(family='Segoe UI', size=11, weight='bold')
        self.title_font = tkfont.Font(family='Segoe UI', size=14, weight='bold')

        self.sidebar_colors = dict(
            bg="#0F172A", hover="#1E293B", active="#1E3A5F",
            text="#94A3B8", active_text="#FFFFFF", logo="#FFFFFF",
            accent="#3B82F6", divider="#1E293B"
        )

        self.light = dict(
            bg="#F1F5F9", surface="#FFFFFF", fg="#0F172A", muted="#64748B",
            primary="#2563EB", primary_hover="#1D4ED8", accent="#10B981",
            border="#E2E8F0", button_bg="#2563EB", button_fg="#FFFFFF",
            entry_bg="#FFFFFF", entry_fg="#0F172A", output_bg="#F0F9FF",
            secondary_bg="#F8FAFC", sb_trough="#E2E8F0", sb_thumb="#94A3B8",
            header_bg="#FFFFFF", card_bg="#FFFFFF", card_border="#E2E8F0",
            stats_bg="#FFFFFF", tab_active="#2563EB", tab_inactive="#F8FAFC",
            tab_text="#64748B", tab_active_text="#FFFFFF",
            bottom_bg="#FFFFFF", odds_bg="#EEF2FF", odds_fg="#3B5998",
            confidence_high="#10B981", confidence_mid="#F59E0B", confidence_low="#EF4444",
            ev_pos="#10B981", ev_neg="#EF4444",
            badge_high_bg="#DCFCE7", badge_high_fg="#166534",
            badge_mid_bg="#FEF9C3", badge_mid_fg="#854D0E",
            badge_low_bg="#FEE2E2", badge_low_fg="#991B1B"
        )

        self.dark = dict(
            bg="#0B1220", surface="#111827", fg="#E2E8F0", muted="#94A3B8",
            primary="#3B82F6", primary_hover="#2563EB", accent="#22C55E",
            border="#1E293B", button_bg="#3B82F6", button_fg="#FFFFFF",
            entry_bg="#1E293B", entry_fg="#E2E8F0", output_bg="#1E293B",
            secondary_bg="#0F172A", sb_trough="#1E293B", sb_thumb="#475569",
            header_bg="#111827", card_bg="#111827", card_border="#1E293B",
            stats_bg="#111827", tab_active="#3B82F6", tab_inactive="#0F172A",
            tab_text="#94A3B8", tab_active_text="#FFFFFF",
            bottom_bg="#111827", odds_bg="#1E293B", odds_fg="#94A3B8",
            confidence_high="#10B981", confidence_mid="#F59E0B", confidence_low="#EF4444",
            ev_pos="#22C55E", ev_neg="#EF4444",
            badge_high_bg="#064E3B", badge_high_fg="#6EE7B7",
            badge_mid_bg="#713F12", badge_mid_fg="#FDE68A",
            badge_low_bg="#7F1D1D", badge_low_fg="#FCA5A5"
        )

        self.current_mode = 'dark'

    def apply(self, mode='dark'):
        """Aplica el tema especificado"""
        self.current_mode = mode
        p = self.light if mode == 'light' else self.dark

        self.root.configure(bg=p['bg'])

        self.style.configure('TFrame', background=p['bg'])
        self.style.configure('Surface.TFrame', background=p['surface'], relief='flat')
        self.style.configure('Toolbar.TFrame', background=p['surface'], relief='flat')
        self.style.configure('Card.TFrame', background=p['card_bg'], relief='flat')
        self.style.configure('Header.TFrame', background=p['primary'], relief='flat')

        self.style.configure('TLabel', background=p['surface'], foreground=p['fg'], font=('Segoe UI', 10))
        self.style.configure('Muted.TLabel', background=p['surface'], foreground=p['muted'])
        self.style.configure('Title.TLabel', background=p['surface'], foreground=p['fg'], font=('Segoe UI', 14, 'bold'))
        self.style.configure('ItemTitle.TLabel', background=p['card_bg'], foreground=p['fg'], font=('Segoe UI', 11, 'bold'))
        self.style.configure('ItemSub.TLabel', background=p['card_bg'], foreground=p['muted'], font=('Segoe UI', 10))
        self.style.configure('Header.TLabel', background=p['primary'], foreground=p['button_fg'], font=('Segoe UI', 12, 'bold'))

        self.style.configure('TButton', background=p['button_bg'], foreground=p['button_fg'],
                             borderwidth=0, padding=(12, 8), font=('Segoe UI', 10, 'bold'))
        self.style.map('TButton',
                       background=[('active', p['primary_hover']), ('pressed', p['primary_hover'])],
                       foreground=[('disabled', p['muted'])])

        self.style.configure('Secondary.TButton', background=p['secondary_bg'], foreground=p['fg'],
                             borderwidth=1, padding=(10, 6), font=('Segoe UI', 10))
        self.style.map('Secondary.TButton',
                       background=[('active', p['surface']), ('pressed', p['surface'])])

        self.style.configure('TEntry', fieldbackground=p['entry_bg'], foreground=p['entry_fg'],
                             borderwidth=1, relief='solid')
        self.style.configure('TCombobox', fieldbackground=p['entry_bg'], foreground=p['entry_fg'],
                             background=p['surface'], borderwidth=1, arrowcolor=p['fg'])
        self.style.map('TCombobox',
                       fieldbackground=[('readonly', p['entry_bg'])],
                       selectbackground=[('readonly', p['primary'])],
                       selectforeground=[('readonly', p['button_fg'])])

        self.style.configure('TNotebook', background=p['bg'], borderwidth=0, tabmargins=(6, 6, 6, 0))
        self.style.configure('TNotebook.Tab', padding=(16, 10), background=p['secondary_bg'],
                             foreground=p['fg'], borderwidth=0, font=('Segoe UI', 10, 'bold'))
        self.style.map('TNotebook.Tab',
                       background=[('selected', p['primary'])],
                       foreground=[('selected', p['button_fg'])],
                       expand=[('selected', (1, 1, 1, 0))])

        self.style.configure('Toggle.TCheckbutton', background=p['surface'], foreground=p['fg'],
                             font=('Segoe UI', 10))
        self.style.map('Toggle.TCheckbutton', background=[('active', p['surface'])])

        self.style.configure('Card.TCheckbutton', background=p['card_bg'], foreground=p['fg'])
        self.style.map('Card.TCheckbutton', background=[('active', p['card_bg'])])

        self.style.configure('TSeparator', background=p['border'])

        self.style.layout('Slim.Vertical.TScrollbar',
            [('Vertical.Scrollbar.trough', {
                'children': [('Vertical.Scrollbar.thumb', {'expand': 1, 'sticky': 'nswe'})],
                'sticky': 'ns'})])
        self.style.layout('Slim.Horizontal.TScrollbar',
            [('Horizontal.Scrollbar.trough', {
                'children': [('Horizontal.Scrollbar.thumb', {'expand': 1, 'sticky': 'nswe'})],
                'sticky': 'we'})])

        for orient in ('Vertical', 'Horizontal'):
            self.style.configure(f'Slim.{orient}.TScrollbar', width=8, relief='flat',
                background=p['sb_thumb'], darkcolor=p['sb_thumb'], lightcolor=p['sb_thumb'],
                troughcolor=p['sb_trough'], bordercolor=p['sb_trough'],
                arrowcolor=p['sb_thumb'], gripcount=0)
            self.style.map(f'Slim.{orient}.TScrollbar',
                background=[('active', p['sb_thumb']), ('pressed', p['sb_thumb'])])

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
        self._custom_alert_messages = self._load_custom_alerts()
    
    def signal_handler(self, signum, frame):
        """Manejar señales de interrupción"""
        if not hasattr(self, '_stopping'):
            self._stopping = True
            logger.info("🛑 Signal received, stopping SergioBets...")
            print("\n🛑 Deteniendo SergioBets...")
            self.running = False
            self.stop_all_services()
            sys.exit(0)
    
    def _load_custom_alerts(self):
        """Load custom alert messages from JSON file"""
        try:
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'custom_alerts.json')
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _save_custom_alerts(self):
        """Save custom alert messages to JSON file"""
        try:
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'custom_alerts.json')
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self._custom_alert_messages, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving custom alerts: {e}")

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
        """Setup the Tkinter GUI interface with professional sidebar layout"""
        import tkinter as tk
        from tkinter import ttk, messagebox
        from tkcalendar import DateEntry

        self.root = tk.Tk()
        self.root.title("SergioBets PRO")
        self.root.geometry("1400x800")
        self.root.minsize(1100, 700)
        try:
            self.root.state('zoomed')
        except:
            pass

        self.theme = ThemeManager(self.root)
        self.dark_mode_var = tk.BooleanVar(value=True)
        palette = self.theme.apply('dark')

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)

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
        self._sidebar_btns = {}
        self._active_nav = "pronosticos"
        self._content_tab_btns = {}
        self._active_tab = "picks"
        self._stats_labels = {}
        self._palette = palette

        # ── SIDEBAR ──────────────────────────────────────────────
        sb = self.theme.sidebar_colors
        sidebar = tk.Frame(self.root, bg=sb['bg'], width=200)
        sidebar.grid(row=0, column=0, sticky='ns')
        sidebar.grid_propagate(False)
        self._sidebar = sidebar

        # Logo
        logo_f = tk.Frame(sidebar, bg=sb['bg'])
        logo_f.pack(fill='x', padx=16, pady=(20, 28))
        tk.Label(logo_f, text="⚽", bg=sb['bg'], fg=sb['accent'],
                 font=('Segoe UI', 16)).pack(side='left')
        tk.Label(logo_f, text="SergioBets", bg=sb['bg'], fg=sb['logo'],
                 font=('Segoe UI', 13, 'bold')).pack(side='left', padx=(6, 0))
        tk.Label(logo_f, text=" PRO", bg=sb['accent'], fg='#FFFFFF',
                 font=('Segoe UI', 7, 'bold'), padx=4, pady=1).pack(side='left', padx=(4, 0))

        # Navigation items
        nav_items = [
            ("dashboard",    "📊", "Dashboard"),
            ("pronosticos",  "🎯", "Pronosticos"),
            ("partidos",     "⚽", "Partidos"),
            ("alertas",      "🔔", "Alertas"),
            ("tracking",     "📈", "Tracking"),
            ("rendimiento",  "💹", "Rendimiento"),
            ("usuarios",     "👥", "Usuarios"),
            ("ajustes",      "⚙️", "Ajustes"),
        ]
        for nav_id, icon, label in nav_items:
            bf = tk.Frame(sidebar, bg=sb['bg'], cursor='hand2')
            bf.pack(fill='x', padx=8, pady=1)
            ind = tk.Frame(bf, bg=sb['bg'], width=3)
            ind.pack(side='left', fill='y')
            ic = tk.Label(bf, text=icon, bg=sb['bg'], fg=sb['text'],
                          font=('Segoe UI', 12), padx=8, pady=8)
            ic.pack(side='left')
            tx = tk.Label(bf, text=label, bg=sb['bg'], fg=sb['text'],
                          font=('Segoe UI', 10), pady=8, anchor='w')
            tx.pack(side='left', fill='x', expand=True)
            self._sidebar_btns[nav_id] = {'frame': bf, 'ind': ind, 'icon': ic, 'text': tx}
            for w in (bf, ic, tx):
                w.bind('<Button-1>', lambda e, nid=nav_id: self._on_nav_click(nid))
                w.bind('<Enter>', lambda e, nid=nav_id: self._on_nav_hover(nid, True))
                w.bind('<Leave>', lambda e, nid=nav_id: self._on_nav_hover(nid, False))

        self._set_active_nav('dashboard')

        # ── CONTENT AREA ─────────────────────────────────────────
        content = tk.Frame(self.root, bg=palette['bg'])
        content.grid(row=0, column=1, sticky='nsew')
        for r in range(6):
            content.grid_rowconfigure(r, weight=(1 if r == 4 else 0))
        content.grid_columnconfigure(0, weight=1)
        self._content = content

        # ── Header bar ───────────────────────────────────────────
        header = tk.Frame(content, bg=palette['header_bg'], height=48)
        header.grid(row=0, column=0, sticky='ew')
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)
        self._header = header

        st_f = tk.Frame(header, bg=palette['header_bg'])
        st_f.grid(row=0, column=0, sticky='w', padx=20, pady=10)
        self._status_dot = tk.Label(st_f, text="●", bg=palette['header_bg'],
                                    fg="#22C55E", font=('Segoe UI', 10))
        self._status_dot.pack(side='left')
        self._status_lbl = tk.Label(st_f, text="Datos actualizados",
                                    bg=palette['header_bg'], fg=palette['muted'],
                                    font=('Segoe UI', 9))
        self._status_lbl.pack(side='left', padx=(4, 0))

        hdr_icons = tk.Frame(header, bg=palette['header_bg'])
        hdr_icons.grid(row=0, column=0, sticky='e', padx=20, pady=10)
        # Live Colombia clock
        self._clock_lbl = tk.Label(hdr_icons, text="", bg=palette['header_bg'],
                                    fg=palette['fg'], font=('Segoe UI', 10, 'bold'))
        self._clock_lbl.pack(side='left', padx=(0, 12))
        clock_flag = tk.Label(hdr_icons, text="🇨🇴", bg=palette['header_bg'],
                              font=('Segoe UI', 12))
        clock_flag.pack(side='left', padx=(0, 16))
        for ic_txt in ("🔍", "🔔", "💬"):
            tk.Label(hdr_icons, text=ic_txt, bg=palette['header_bg'],
                     fg=palette['muted'], font=('Segoe UI', 14), padx=6).pack(side='left')

        # ── Filter bar ───────────────────────────────────────────
        fbar = tk.Frame(content, bg=palette['header_bg'], padx=20, pady=10)
        fbar.grid(row=1, column=0, sticky='ew')
        self._filter_bar = fbar

        tk.Label(fbar, text="Fecha", bg=palette['header_bg'], fg=palette['muted'],
                 font=('Segoe UI', 9)).pack(side='left', padx=(0, 4))
        self.entry_fecha = DateEntry(fbar, width=12, background="#2563EB",
                                     foreground="white", borderwidth=0,
                                     date_pattern='yyyy-MM-dd',
                                     showothermonthdays=False, showweeknumbers=False)
        self.entry_fecha.pack(side='left', padx=(0, 16))

        tk.Label(fbar, text="Liga", bg=palette['header_bg'], fg=palette['muted'],
                 font=('Segoe UI', 9)).pack(side='left', padx=(0, 4))
        self.combo_ligas = ttk.Combobox(fbar, state='readonly', width=18)
        self.combo_ligas.pack(side='left', padx=(0, 16))
        self.combo_ligas.set('Todas')
        self.combo_ligas.bind('<<ComboboxSelected>>', self.on_liga_changed)

        self._corners_lbl = tk.Label(fbar, text="Corners", bg=palette['header_bg'], fg=palette['muted'],
                 font=('Segoe UI', 9))
        self._corners_lbl.pack(side='left', padx=(0, 4))
        self._combo_corners = ttk.Combobox(fbar, state='readonly', width=12,
                                           values=['Todos', 'Over 8.5', 'Over 9.5', 'Over 10.5'])
        self._combo_corners.pack(side='left', padx=(0, 16))
        self._combo_corners.set('Todos')

        self._conf_lbl = tk.Label(fbar, text="Confianza", bg=palette['header_bg'], fg=palette['muted'],
                 font=('Segoe UI', 9))
        self._conf_lbl.pack(side='left', padx=(0, 4))
        self._combo_conf = ttk.Combobox(fbar, state='readonly', width=14,
                                        values=['Todas', 'Alta (>80%)', 'Media (60-80%)', 'Baja (<60%)'])
        self._combo_conf.pack(side='left', padx=(0, 16))
        self._combo_conf.set('Todas')

        gen_btn = tk.Button(fbar, text="Generar Pronosticos", bg=palette['primary'],
                            fg='#FFFFFF', font=('Segoe UI', 10, 'bold'), relief='flat',
                            cursor='hand2', padx=16, pady=4, bd=0,
                            activebackground=palette['primary_hover'],
                            activeforeground='#FFFFFF', command=self.buscar_en_hilo)
        gen_btn.pack(side='right')
        self._gen_btn = gen_btn

        # ── Stats row ────────────────────────────────────────────
        stats_row = tk.Frame(content, bg=palette['bg'], padx=20, pady=12)
        stats_row.grid(row=2, column=0, sticky='ew')
        for c in range(3):
            stats_row.grid_columnconfigure(c, weight=1, uniform='stat')
        self._stats_row = stats_row

        stats_def = [
            ("pred_hoy",  "🎯", "Pronosticos generados hoy", "0"),
            ("partidos",  "⚽", "Partidos analizados",       "0"),
            ("confianza", "📊", "Promedio de confianza",     "0%"),
        ]
        for col, (sid, icon, label, val) in enumerate(stats_def):
            card = tk.Frame(stats_row, bg=palette['stats_bg'], padx=20, pady=14,
                            highlightbackground=palette['card_border'], highlightthickness=1)
            card.grid(row=0, column=col, sticky='ew', padx=6)
            tk.Label(card, text=icon, bg=palette['stats_bg'],
                     fg=palette['fg'], font=('Segoe UI', 14)).pack(anchor='w')
            v_lbl = tk.Label(card, text=val, bg=palette['stats_bg'],
                             fg=palette['fg'], font=('Segoe UI', 24, 'bold'))
            v_lbl.pack(anchor='w', pady=(4, 0))
            n_lbl = tk.Label(card, text=label, bg=palette['stats_bg'],
                             fg=palette['muted'], font=('Segoe UI', 9))
            n_lbl.pack(anchor='w')
            self._stats_labels[sid] = {'card': card, 'value': v_lbl, 'name': n_lbl}

        # ── Scrollable content ───────────────────────────────────
        scroll_container = tk.Frame(content, bg=palette['bg'])
        scroll_container.grid(row=4, column=0, sticky='nsew', padx=20)
        scroll_container.grid_rowconfigure(0, weight=1)
        scroll_container.grid_columnconfigure(0, weight=1)
        self._scroll_container = scroll_container

        self.sf_predicciones = ScrollableFrame(scroll_container, bg=palette['bg'])
        self.sf_predicciones.inner.grid_columnconfigure(0, weight=1)

        self.sf_partidos = ScrollableFrame(scroll_container, bg=palette['bg'])
        self.sf_partidos.inner.grid_columnconfigure(0, weight=1)

        self.frame_predicciones = self.sf_predicciones.inner
        self.frame_partidos = self.sf_partidos.inner
        self._current_main_mode = 'pronosticos'  # Track which mode is active

        # ── Bottom bar (Pick Destacado only) ─────────────────────
        bottom = tk.Frame(content, bg=palette['bottom_bg'], height=72,
                          highlightbackground=palette['border'], highlightthickness=1)
        bottom.grid(row=5, column=0, sticky='ew')
        bottom.grid_propagate(False)
        bottom.grid_columnconfigure(0, weight=1)
        self._bottom_bar = bottom

        bl = tk.Frame(bottom, bg=palette['bottom_bg'])
        bl.grid(row=0, column=0, sticky='ew', padx=20, pady=12)
        tk.Label(bl, text="⭐ PICK DESTACADO", bg=palette['bottom_bg'],
                 fg=palette['primary'], font=('Segoe UI', 13, 'bold')).pack(side='left')
        self._pick_dest_lbl = tk.Label(bl, text="  Sin picks cargados",
                                       bg=palette['bottom_bg'], fg=palette['muted'],
                                       font=('Segoe UI', 12))
        self._pick_dest_lbl.pack(side='left', padx=(12, 0))

        # ── Settings page (hidden) ───────────────────────────────
        self._settings_frame = tk.Frame(content, bg=palette['bg'])
        self._build_settings_content(palette)

        # ── Tracking page (hidden) ────────────────────────────────
        self._tracking_frame = tk.Frame(content, bg=palette['bg'])
        self._tracking_loaded = False

        # ── Usuarios page (hidden) ────────────────────────────────
        self._usuarios_frame = tk.Frame(content, bg=palette['bg'])
        self._usuarios_loaded = False

        # ── Alertas page (hidden) ─────────────────────────────────
        self._alertas_frame = tk.Frame(content, bg=palette['bg'])
        self._build_alertas_content(palette)

        # ── Dashboard page (hidden) ──────────────────────────────────
        self._dashboard_frame = tk.Frame(content, bg=palette['bg'])
        self._dashboard_loaded = False

        # ── Rendimiento page (hidden) ────────────────────────────────
        self._rendimiento_frame = tk.Frame(content, bg=palette['bg'])
        self._rendimiento_loaded = False

        # Legacy references for backward compatibility
        self.notebook = None
        self.tab_ajustes = self._settings_frame
        self.tab_principal = scroll_container

        # Start live Colombia clock
        self._update_clock()

        # Show dashboard view by default
        self._show_dashboard_page()

        print("✅ GUI setup completed with professional theme")
    
    # ── Sidebar / theme / tab helpers ────────────────────────────

    def _set_active_nav(self, nav_id):
        """Highlight the active sidebar navigation item"""
        sb = self.theme.sidebar_colors
        for nid, parts in self._sidebar_btns.items():
            is_act = (nid == nav_id)
            bg = sb['active'] if is_act else sb['bg']
            fg = sb['active_text'] if is_act else sb['text']
            ind_bg = sb['accent'] if is_act else sb['bg']
            for w in (parts['frame'], parts['icon'], parts['text']):
                w.configure(bg=bg)
            parts['ind'].configure(bg=ind_bg)
            parts['icon'].configure(fg=fg)
            parts['text'].configure(fg=fg)
        self._active_nav = nav_id

    def _on_nav_hover(self, nav_id, entering):
        """Handle sidebar hover effect"""
        if nav_id == self._active_nav:
            return
        sb = self.theme.sidebar_colors
        bg = sb['hover'] if entering else sb['bg']
        parts = self._sidebar_btns[nav_id]
        for w in (parts['frame'], parts['icon'], parts['text']):
            w.configure(bg=bg)

    def _on_nav_click(self, nav_id):
        """Handle sidebar navigation click"""
        if nav_id == "dashboard":
            self._show_dashboard_page()
            self._set_active_nav(nav_id)
        elif nav_id == "pronosticos":
            self._show_main_content('pronosticos')
            self._set_active_nav(nav_id)
        elif nav_id == "partidos":
            self._show_main_content('partidos')
            self._set_active_nav(nav_id)
        elif nav_id == "alertas":
            self._show_alertas_page()
            self._set_active_nav(nav_id)
        elif nav_id == "tracking":
            self._show_tracking_page()
            self._set_active_nav(nav_id)
        elif nav_id == "rendimiento":
            self._show_rendimiento_page()
            self._set_active_nav(nav_id)
        elif nav_id == "usuarios":
            self._show_usuarios_page()
            self._set_active_nav(nav_id)
        elif nav_id == "ajustes":
            self._show_settings_page()
            self._set_active_nav(nav_id)

    def _hide_all_pages(self):
        """Hide all content pages"""
        self._scroll_container.grid_forget()
        self._filter_bar.grid_forget()
        self._stats_row.grid_forget()
        if hasattr(self, '_tabs_frame'):
            self._tabs_frame.grid_forget()
        self._bottom_bar.grid_forget()
        self._settings_frame.grid_forget()
        self._tracking_frame.grid_forget()
        self._usuarios_frame.grid_forget()
        self._alertas_frame.grid_forget()
        self._dashboard_frame.grid_forget()
        self._rendimiento_frame.grid_forget()

    def _show_main_content(self, mode='pronosticos'):
        """Show the main predictions/matches content based on sidebar selection"""
        self._hide_all_pages()
        if mode == 'pronosticos':
            self._bottom_bar.grid(row=5, column=0, sticky='ew')
        else:
            self._bottom_bar.grid_forget()
        self._current_main_mode = mode
        self._scroll_container.grid(row=4, column=0, sticky='nsew', padx=20)
        self._filter_bar.grid(row=1, column=0, sticky='ew')
        # Update button text and show/hide elements based on mode
        if mode == 'partidos':
            self._gen_btn.configure(text="Ver Partidos")
            # Hide stats, tabs, corners and confianza filters for Partidos
            self._stats_row.grid_forget()
            if hasattr(self, '_tabs_frame'):
                self._tabs_frame.grid_forget()
            self._corners_lbl.pack_forget()
            self._combo_corners.pack_forget()
            self._conf_lbl.pack_forget()
            self._combo_conf.pack_forget()
        else:
            self._gen_btn.configure(text="Generar Pronosticos")
            self._stats_row.grid(row=2, column=0, sticky='ew')
            if hasattr(self, '_tabs_frame'):
                self._tabs_frame.grid(row=3, column=0, sticky='ew', pady=(0, 6))
            # Restore corners and confianza filters
            self._corners_lbl.pack(side='left', padx=(0, 4))
            self._combo_corners.pack(side='left', padx=(0, 16))
            self._conf_lbl.pack(side='left', padx=(0, 4))
            self._combo_conf.pack(side='left', padx=(0, 16))
        # Show/hide scroll frames based on mode
        self.sf_predicciones.grid_forget()
        self.sf_partidos.grid_forget()
        if mode == 'pronosticos':
            self.sf_predicciones.grid(row=0, column=0, sticky='nsew')
        elif mode == 'partidos':
            self.sf_partidos.grid(row=0, column=0, sticky='nsew')
        else:  # dashboard - show both
            self._scroll_container.grid_rowconfigure(1, weight=1)
            self.sf_predicciones.grid(row=0, column=0, sticky='nsew', pady=(0, 4))
            self.sf_partidos.grid(row=1, column=0, sticky='nsew', pady=(4, 0))

    def _show_settings_page(self):
        """Show the settings page in the content area"""
        self._hide_all_pages()
        self._bottom_bar.grid_forget()
        self._settings_frame.grid(row=1, column=0, rowspan=5, sticky='nsew', padx=20, pady=20)

    def _show_tracking_page(self):
        """Show the tracking page inline in the content area"""
        self._hide_all_pages()
        self._bottom_bar.grid_forget()
        if not self._tracking_loaded:
            self._build_tracking_content(self._palette)
            self._tracking_loaded = True
        self._tracking_frame.grid(row=1, column=0, rowspan=5, sticky='nsew', padx=20, pady=20)
        # Always reload data from file to reflect any deletions or changes
        self._track_filter_click(self._track_filtro.get())
        # Auto-update pending results in background
        self._track_auto_update()

    def _show_usuarios_page(self):
        """Show the usuarios page inline in the content area"""
        self._hide_all_pages()
        self._bottom_bar.grid_forget()
        if not self._usuarios_loaded:
            self._build_usuarios_content(self._palette)
            self._usuarios_loaded = True
        self._usuarios_frame.grid(row=1, column=0, rowspan=5, sticky='nsew', padx=20, pady=20)
        self._refresh_usuarios_inline()

    def _show_alertas_page(self):
        """Show the alertas page inline in the content area"""
        self._hide_all_pages()
        self._bottom_bar.grid_forget()
        self._alertas_frame.grid(row=1, column=0, rowspan=5, sticky='nsew', padx=20, pady=20)

    def _show_dashboard_page(self):
        """Show the dashboard page with owner metrics"""
        self._hide_all_pages()
        self._bottom_bar.grid(row=5, column=0, sticky='ew')
        if not self._dashboard_loaded:
            self._build_dashboard_content(self._palette)
            self._dashboard_loaded = True
        self._refresh_dashboard_data()
        self._dashboard_frame.grid(row=1, column=0, rowspan=4, sticky='nsew', padx=20, pady=20)

    def _show_rendimiento_page(self):
        """Show the rendimiento (performance) page inline in the content area"""
        self._hide_all_pages()
        self._bottom_bar.grid_forget()
        if not self._rendimiento_loaded:
            self._build_rendimiento_content(self._palette)
            self._rendimiento_loaded = True
        self._refresh_rendimiento_data()
        self._rendimiento_frame.grid(row=1, column=0, rowspan=5, sticky='nsew', padx=20, pady=20)

    def _build_rendimiento_content(self, p):
        """Build the full-page rendimiento (performance) module"""
        import tkinter as tk

        self._rendimiento_frame.grid_rowconfigure(2, weight=1)
        self._rendimiento_frame.grid_columnconfigure(0, weight=1)

        # Title row with export button
        title_f = tk.Frame(self._rendimiento_frame, bg=p['bg'])
        title_f.grid(row=0, column=0, sticky='ew', pady=(0, 16))
        tk.Label(title_f, text="Rendimiento Semanal",
                 bg=p['bg'], fg=p['fg'],
                 font=('Segoe UI', 16, 'bold')).pack(side='left')

        # Export PDF button
        export_btn = tk.Button(title_f, text="Exportar PDF",
                                bg='#3B82F6', fg='#FFFFFF',
                                font=('Segoe UI', 10, 'bold'),
                                relief='flat', cursor='hand2', padx=16, pady=6,
                                command=self._export_rendimiento_pdf)
        export_btn.pack(side='right')

        # Summary KPI row
        kpi_row = tk.Frame(self._rendimiento_frame, bg=p['bg'])
        kpi_row.grid(row=1, column=0, sticky='ew', pady=(0, 16))
        for c in range(5):
            kpi_row.grid_columnconfigure(c, weight=1, uniform='rend_kpi')

        rend_kpis = [
            ("rend_profit",    "Profit Semanal",     "$0 COP",   "#10B981"),
            ("rend_win_days",  "Dias Positivos",     "0",        "#10B981"),
            ("rend_loss_days", "Dias Negativos",     "0",        "#EF4444"),
            ("rend_bets",      "Apuestas Resueltas", "0",        "#3B82F6"),
            ("rend_win_rate",  "Tasa de Acierto",    "0%",       "#F59E0B"),
        ]
        self._rend_kpi_labels = {}
        for col, (kid, label, val, accent) in enumerate(rend_kpis):
            card = tk.Frame(kpi_row, bg=p['card_bg'], padx=16, pady=12,
                            highlightbackground=accent, highlightthickness=2)
            card.grid(row=0, column=col, sticky='ew', padx=4)
            tk.Label(card, text=label, bg=p['card_bg'], fg=p['muted'],
                     font=('Segoe UI', 9)).pack(anchor='w')
            v_lbl = tk.Label(card, text=val, bg=p['card_bg'],
                             fg=accent, font=('Segoe UI', 20, 'bold'))
            v_lbl.pack(anchor='w', pady=(4, 0))
            self._rend_kpi_labels[kid] = v_lbl

        # Chart card (full width, expands)
        chart_card = tk.Frame(self._rendimiento_frame, bg=p['card_bg'], padx=24, pady=20,
                               highlightbackground=p['card_border'], highlightthickness=1)
        chart_card.grid(row=2, column=0, sticky='nsew', pady=(0, 16))
        chart_card.grid_rowconfigure(1, weight=1)
        chart_card.grid_columnconfigure(0, weight=1)

        # Chart header with legend
        chart_header = tk.Frame(chart_card, bg=p['card_bg'])
        chart_header.pack(fill='x', pady=(0, 8))
        tk.Label(chart_header, text="Profit / Loss Diario",
                 bg=p['card_bg'], fg=p['fg'],
                 font=('Segoe UI', 12, 'bold')).pack(side='left')

        # Legend on the right
        legend_f = tk.Frame(chart_header, bg=p['card_bg'])
        legend_f.pack(side='right')
        for color, text in [('#10B981', 'Dia Rentable'), ('#EF4444', 'Dia con Perdida'), ('#3B82F6', 'Acumulado')]:
            dot = tk.Frame(legend_f, bg=color, width=10, height=10)
            dot.pack(side='left', padx=(12, 4))
            dot.pack_propagate(False)
            tk.Label(legend_f, text=text, bg=p['card_bg'], fg=p['muted'],
                     font=('Segoe UI', 8)).pack(side='left')

        # Summary text
        self._rend_chart_summary = tk.Label(chart_card, text="",
                                             bg=p['card_bg'], fg=p['muted'],
                                             font=('Segoe UI', 9, 'italic'))
        self._rend_chart_summary.pack(anchor='w', pady=(0, 8))

        # Full-size canvas for the chart
        self._rend_chart_canvas = tk.Canvas(chart_card, bg=p['card_bg'],
                                             highlightthickness=0, bd=0)
        self._rend_chart_canvas.pack(fill='both', expand=True)

        # Daily breakdown table below chart (compact)
        breakdown_card = tk.Frame(self._rendimiento_frame, bg=p['card_bg'], padx=16, pady=8,
                                   highlightbackground=p['card_border'], highlightthickness=1)
        breakdown_card.grid(row=3, column=0, sticky='ew', pady=(0, 4))

        tk.Label(breakdown_card, text="Detalle por Dia",
                 bg=p['card_bg'], fg=p['fg'],
                 font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 4))

        # Table container using grid for perfect alignment
        table_container = tk.Frame(breakdown_card, bg=p['card_bg'])
        table_container.pack(fill='x')
        col_weights = [2, 1, 1, 1, 2]
        for c, w in enumerate(col_weights):
            table_container.grid_columnconfigure(c, weight=w, uniform='rend_col')

        # Table header row
        col_headers = [
            ("Dia", 'w'),
            ("Apuestas", 'center'),
            ("Ganadas", 'center'),
            ("Perdidas", 'center'),
            ("Profit/Loss", 'e'),
        ]
        for c, (text, anc) in enumerate(col_headers):
            tk.Label(table_container, text=text, bg=p['card_bg'], fg=p['muted'],
                     font=('Segoe UI', 8, 'bold'), anchor=anc).grid(
                row=0, column=c, sticky='ew', padx=6, pady=(0, 3))

        # Separator
        sep = tk.Frame(table_container, bg=p['card_border'], height=1)
        sep.grid(row=1, column=0, columnspan=5, sticky='ew', pady=(0, 2))

        # Store table container and starting row for body
        self._rend_table_container = table_container
        self._rend_table_body_start_row = 2

    def _refresh_rendimiento_data(self):
        """Refresh the rendimiento page with real data"""
        import tkinter as tk
        STAKE = 10000  # $10,000 COP per bet

        try:
            historial = cargar_json('historial_predicciones.json') or []
        except Exception:
            historial = []

        enviados = [pr for pr in historial if pr.get('sent_to_telegram', False)]
        p = self._palette

        # Calculate daily P/L for last 7 days
        hoy = hora_bogota().date()
        dias_nombres = ['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab', 'Dom']
        daily_pl = []
        day_labels = []
        day_details = []  # (total_bets, wins, losses, pl)

        for i in range(6, -1, -1):
            d = hoy - timedelta(days=i)
            d_str = d.strftime('%Y-%m-%d')
            dia_nombre = dias_nombres[d.weekday()]
            day_labels.append(f"{dia_nombre} {d.day}")

            day_bets = [pr for pr in enviados
                        if pr.get('fecha', '') == d_str and pr.get('acierto') is not None]
            wins = sum(1 for b in day_bets if b.get('acierto') is True)
            losses = sum(1 for b in day_bets if b.get('acierto') is False)
            pl = 0
            for bet in day_bets:
                cuota = float(bet.get('cuota', 1))
                if bet.get('acierto') is True:
                    pl += STAKE * cuota - STAKE
                else:
                    pl -= STAKE
            daily_pl.append(pl)
            day_details.append((len(day_bets), wins, losses, pl))

        # Cumulative profit
        cumulative = []
        acc = 0
        for v in daily_pl:
            acc += v
            cumulative.append(acc)

        # Update KPIs
        total_profit = sum(daily_pl)
        win_days = sum(1 for v in daily_pl if v > 0)
        loss_days = sum(1 for v in daily_pl if v < 0)
        total_bets = sum(d[0] for d in day_details)
        total_wins = sum(d[1] for d in day_details)
        win_rate = (total_wins / total_bets * 100) if total_bets > 0 else 0

        if hasattr(self, '_rend_kpi_labels'):
            sign = '+' if total_profit >= 0 else ''
            profit_color = "#10B981" if total_profit >= 0 else "#EF4444"
            self._rend_kpi_labels['rend_profit'].config(
                text=f"{sign}${total_profit:,.0f}", fg=profit_color)
            self._rend_kpi_labels['rend_win_days'].config(text=str(win_days))
            self._rend_kpi_labels['rend_loss_days'].config(text=str(loss_days))
            self._rend_kpi_labels['rend_bets'].config(text=str(total_bets))
            self._rend_kpi_labels['rend_win_rate'].config(text=f"{win_rate:.1f}%")

        # Summary text
        sign = '+' if total_profit >= 0 else ''
        summary_text = (f"Semana: {sign}${total_profit:,.0f} COP  |  "
                        f"{win_days} dias +  |  {loss_days} dias -  |  "
                        f"{total_bets} apuestas resueltas")
        if hasattr(self, '_rend_chart_summary'):
            self._rend_chart_summary.config(text=summary_text)

        # Draw the chart (full page version)
        self._draw_rendimiento_chart(daily_pl, cumulative, day_labels)

        # Update breakdown table
        if hasattr(self, '_rend_table_container'):
            # Remove old body rows (keep header row=0 and separator row=1)
            start = self._rend_table_body_start_row
            for w in self._rend_table_container.grid_slaves():
                info = w.grid_info()
                if int(info.get('row', 0)) >= start:
                    w.destroy()

            for i, (label, (n_bets, wins, losses, pl)) in enumerate(zip(day_labels, day_details)):
                r = start + i
                sign = '+' if pl >= 0 else ''
                pl_color = "#10B981" if pl > 0 else ("#EF4444" if pl < 0 else p['muted'])
                row_bg = p['card_bg']

                # Alternating subtle stripe for readability
                if i % 2 == 1:
                    # Slightly different shade
                    try:
                        base = p['card_bg'].lstrip('#')
                        r_c, g_c, b_c = int(base[:2], 16), int(base[2:4], 16), int(base[4:6], 16)
                        row_bg = f"#{min(r_c+8,255):02x}{min(g_c+8,255):02x}{min(b_c+8,255):02x}"
                    except Exception:
                        row_bg = p['card_bg']

                tk.Label(self._rend_table_container, text=label, bg=row_bg, fg=p['fg'],
                         font=('Segoe UI', 9), anchor='w').grid(
                    row=r, column=0, sticky='ew', padx=6, pady=1)
                tk.Label(self._rend_table_container, text=str(n_bets), bg=row_bg, fg=p['fg'],
                         font=('Segoe UI', 9), anchor='center').grid(
                    row=r, column=1, sticky='ew', padx=6, pady=1)
                tk.Label(self._rend_table_container, text=str(wins), bg=row_bg, fg="#10B981",
                         font=('Segoe UI', 9), anchor='center').grid(
                    row=r, column=2, sticky='ew', padx=6, pady=1)
                tk.Label(self._rend_table_container, text=str(losses), bg=row_bg, fg="#EF4444",
                         font=('Segoe UI', 9), anchor='center').grid(
                    row=r, column=3, sticky='ew', padx=6, pady=1)
                tk.Label(self._rend_table_container, text=f"{sign}${pl:,.0f} COP", bg=row_bg, fg=pl_color,
                         font=('Segoe UI', 9, 'bold'), anchor='e').grid(
                    row=r, column=4, sticky='ew', padx=6, pady=1)

            # Summary total row
            total_row = start + len(day_details)
            total_pl = sum(d[3] for d in day_details)
            total_bets_sum = sum(d[0] for d in day_details)
            total_wins_sum = sum(d[1] for d in day_details)
            total_losses_sum = sum(d[2] for d in day_details)
            t_sign = '+' if total_pl >= 0 else ''
            t_color = "#10B981" if total_pl > 0 else ("#EF4444" if total_pl < 0 else p['muted'])

            # Separator before total
            sep2 = tk.Frame(self._rend_table_container, bg=p['card_border'], height=1)
            sep2.grid(row=total_row, column=0, columnspan=5, sticky='ew', pady=(2, 2))

            total_row += 1
            tk.Label(self._rend_table_container, text="TOTAL", bg=p['card_bg'], fg=p['fg'],
                     font=('Segoe UI', 9, 'bold'), anchor='w').grid(
                row=total_row, column=0, sticky='ew', padx=6, pady=1)
            tk.Label(self._rend_table_container, text=str(total_bets_sum), bg=p['card_bg'], fg=p['fg'],
                     font=('Segoe UI', 9, 'bold'), anchor='center').grid(
                row=total_row, column=1, sticky='ew', padx=6, pady=1)
            tk.Label(self._rend_table_container, text=str(total_wins_sum), bg=p['card_bg'], fg="#10B981",
                     font=('Segoe UI', 9, 'bold'), anchor='center').grid(
                row=total_row, column=2, sticky='ew', padx=6, pady=1)
            tk.Label(self._rend_table_container, text=str(total_losses_sum), bg=p['card_bg'], fg="#EF4444",
                     font=('Segoe UI', 9, 'bold'), anchor='center').grid(
                row=total_row, column=3, sticky='ew', padx=6, pady=1)
            tk.Label(self._rend_table_container, text=f"{t_sign}${total_pl:,.0f} COP", bg=p['card_bg'], fg=t_color,
                     font=('Segoe UI', 9, 'bold'), anchor='e').grid(
                row=total_row, column=4, sticky='ew', padx=6, pady=1)

    def _draw_rendimiento_chart(self, daily_pl, cumulative, day_labels):
        """Draw the full-page weekly bar chart on the rendimiento canvas"""
        if not hasattr(self, '_rend_chart_canvas'):
            return

        STAKE = 10000
        canvas = self._rend_chart_canvas
        canvas.delete('all')
        canvas.update_idletasks()
        p = self._palette

        cw = canvas.winfo_width()
        ch = canvas.winfo_height()
        if cw < 100:
            cw = 800
        if ch < 100:
            ch = 300

        # Chart dimensions
        margin_left = 90
        margin_right = 30
        margin_top = 25
        margin_bottom = 45
        chart_w = cw - margin_left - margin_right
        chart_h = ch - margin_top - margin_bottom

        if chart_w < 80 or chart_h < 80:
            return

        # Find max absolute value for scale
        all_values = daily_pl + cumulative
        max_abs = max(abs(v) for v in all_values) if any(v != 0 for v in all_values) else STAKE
        max_abs = max(max_abs, STAKE)
        # Add 15% padding to the scale
        max_abs = max_abs * 1.15

        # Y-axis: zero line position
        y_zero = margin_top + chart_h / 2
        y_scale = (chart_h / 2) / max_abs

        # Draw grid lines and Y labels
        grid_color = '#334155'
        for frac in [-1, -0.5, 0, 0.5, 1]:
            y = y_zero - frac * (chart_h / 2)
            val = frac * max_abs
            canvas.create_line(margin_left, y, cw - margin_right, y,
                               fill=grid_color, dash=(2, 4) if frac != 0 else ())
            sign_char = '+' if val > 0 else ''
            label = f"{sign_char}${val:,.0f}" if val != 0 else "$0"
            canvas.create_text(margin_left - 10, y, text=label,
                               fill=p['muted'], font=('Segoe UI', 8), anchor='e')

        # Zero line (thicker)
        canvas.create_line(margin_left, y_zero, cw - margin_right, y_zero,
                           fill='#475569', width=1, dash=(4, 2))

        # Bar width
        n_bars = 7
        bar_area = chart_w / n_bars
        bar_w = bar_area * 0.5
        gap = (bar_area - bar_w) / 2

        # Draw bars (without value labels yet)
        bar_positions = []
        for i, (pl, label) in enumerate(zip(daily_pl, day_labels)):
            x1 = margin_left + i * bar_area + gap
            x2 = x1 + bar_w

            if pl >= 0:
                y_top = y_zero - pl * y_scale
                y_bot = y_zero
                color = '#10B981'
            else:
                y_top = y_zero
                y_bot = y_zero - pl * y_scale
                color = '#EF4444'

            if pl != 0:
                canvas.create_rectangle(x1, y_top, x2, y_bot, fill=color, outline='', width=0)

            bar_positions.append((x1, x2, y_top, y_bot, pl))

            # Day label
            canvas.create_text((x1 + x2) / 2, ch - margin_bottom + 18,
                               text=label, fill=p['muted'], font=('Segoe UI', 9))

        # Draw cumulative profit line BEFORE value labels
        points = []
        for i, cum_val in enumerate(cumulative):
            x = margin_left + i * bar_area + bar_area / 2
            y = y_zero - cum_val * y_scale
            points.append((x, y))

        if len(points) >= 2:
            for j in range(len(points) - 1):
                canvas.create_line(points[j][0], points[j][1],
                                   points[j + 1][0], points[j + 1][1],
                                   fill='#3B82F6', width=2.5, smooth=True)
            for px, py in points:
                canvas.create_oval(px - 5, py - 5, px + 5, py + 5,
                                   fill='#3B82F6', outline='#1E293B', width=2)

        # Draw value labels ON TOP of everything (so blue line doesn't cover them)
        for x1, x2, y_top, y_bot, pl in bar_positions:
            if pl != 0:
                sign_char = '+' if pl > 0 else ''
                val_text = f"{sign_char}${pl:,.0f}"
                val_y = y_top - 14 if pl >= 0 else y_bot + 14
                # Background rectangle for readability
                tx = (x1 + x2) / 2
                canvas.create_rectangle(tx - 40, val_y - 8, tx + 40, val_y + 8,
                                        fill=p['card_bg'], outline='')
                canvas.create_text(tx, val_y, text=val_text,
                                   fill='#F8FAFC', font=('Segoe UI', 9, 'bold'))

    def _export_rendimiento_pdf(self):
        """Export the rendimiento report as a PDF file"""
        import tkinter as tk
        from tkinter import filedialog, messagebox
        STAKE = 10000

        try:
            historial = cargar_json('historial_predicciones.json') or []
        except Exception:
            historial = []

        enviados = [pr for pr in historial if pr.get('sent_to_telegram', False)]

        # Calculate weekly data
        hoy = hora_bogota().date()
        dias_nombres = ['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab', 'Dom']
        daily_data = []

        for i in range(6, -1, -1):
            d = hoy - timedelta(days=i)
            d_str = d.strftime('%Y-%m-%d')
            dia_nombre = dias_nombres[d.weekday()]

            day_bets = [pr for pr in enviados
                        if pr.get('fecha', '') == d_str and pr.get('acierto') is not None]
            wins = sum(1 for b in day_bets if b.get('acierto') is True)
            losses = sum(1 for b in day_bets if b.get('acierto') is False)
            pl = 0
            for bet in day_bets:
                cuota = float(bet.get('cuota', 1))
                if bet.get('acierto') is True:
                    pl += STAKE * cuota - STAKE
                else:
                    pl -= STAKE
            daily_data.append((f"{dia_nombre} {d.day}/{d.month}", len(day_bets), wins, losses, pl))

        # Global stats
        resueltos = [pr for pr in enviados if pr.get('acierto') is not None]
        acertados = [pr for pr in resueltos if pr.get('acierto') is True]
        fallados = [pr for pr in resueltos if pr.get('acierto') is False]
        tasa_acierto = (len(acertados) / len(resueltos) * 100) if resueltos else 0
        total_profit = sum(d[4] for d in daily_data)
        total_bets = sum(d[1] for d in daily_data)
        win_days = sum(1 for d in daily_data if d[4] > 0)
        loss_days = sum(1 for d in daily_data if d[4] < 0)

        # Ask user where to save
        filepath = filedialog.asksaveasfilename(
            defaultextension='.pdf',
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"Rendimiento_BetGeniuX_{hoy.strftime('%Y-%m-%d')}.pdf",
            title="Guardar Reporte PDF"
        )
        if not filepath:
            return

        try:
            # Generate PDF using basic text-based approach (no external libraries)
            # Using a simple PDF structure
            lines = []
            lines.append("%PDF-1.4")
            objects = []

            # Object 1: Catalog
            objects.append("1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj")
            # Object 2: Pages
            objects.append("2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj")
            # Object 3: Page
            objects.append("3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> >>\nendobj")

            # Build content stream
            content_lines = []
            content_lines.append("BT")

            # Title
            y = 740
            content_lines.append(f"/F2 22 Tf")
            content_lines.append(f"50 {y} Td")
            content_lines.append(f"(Reporte de Rendimiento - BetGeniuX) Tj")

            # Date
            y -= 28
            content_lines.append(f"/F1 11 Tf")
            content_lines.append(f"0 -28 Td")
            content_lines.append(f"(Generado: {hora_bogota().strftime('%Y-%m-%d %I:%M %p')} \\(Hora Colombia\\)) Tj")

            # Separator
            y -= 20
            content_lines.append(f"0 -20 Td")
            content_lines.append(f"(________________________________________________________) Tj")

            # KPI Summary
            y -= 35
            content_lines.append(f"/F2 14 Tf")
            content_lines.append(f"0 -35 Td")
            content_lines.append(f"(Resumen Semanal) Tj")

            y -= 22
            content_lines.append(f"/F1 11 Tf")
            sign = '+' if total_profit >= 0 else ''
            content_lines.append(f"0 -22 Td")
            content_lines.append(f"(Profit Semanal: {sign}${total_profit:,.0f} COP) Tj")

            y -= 18
            content_lines.append(f"0 -18 Td")
            content_lines.append(f"(Dias Positivos: {win_days}  |  Dias Negativos: {loss_days}) Tj")

            y -= 18
            content_lines.append(f"0 -18 Td")
            content_lines.append(f"(Apuestas Resueltas \\(semana\\): {total_bets}) Tj")

            y -= 18
            content_lines.append(f"0 -18 Td")
            content_lines.append(f"(Tasa de Acierto Global: {tasa_acierto:.1f}% \\({len(acertados)} de {len(resueltos)} resueltas\\)) Tj")

            y -= 18
            content_lines.append(f"0 -18 Td")
            content_lines.append(f"(Stake por apuesta: $10,000 COP) Tj")

            # Separator
            y -= 25
            content_lines.append(f"0 -25 Td")
            content_lines.append(f"(________________________________________________________) Tj")

            # Daily breakdown
            y -= 30
            content_lines.append(f"/F2 14 Tf")
            content_lines.append(f"0 -30 Td")
            content_lines.append(f"(Detalle por Dia) Tj")

            y -= 22
            content_lines.append(f"/F2 10 Tf")
            content_lines.append(f"0 -22 Td")
            content_lines.append(f"(Dia                  Apuestas    Ganadas    Perdidas    Profit/Loss) Tj")

            content_lines.append(f"/F1 10 Tf")
            cumulative = 0
            for dia, n_bets, wins, losses, pl in daily_data:
                cumulative += pl
                y -= 18
                sign_pl = '+' if pl >= 0 else ''
                line = f"{dia:<20s} {n_bets:>5d}       {wins:>5d}       {losses:>5d}       {sign_pl}${pl:,.0f} COP"
                # Escape parentheses for PDF
                line = line.replace('(', '\\(').replace(')', '\\)')
                content_lines.append(f"0 -18 Td")
                content_lines.append(f"({line}) Tj")

            # Cumulative total
            y -= 25
            content_lines.append(f"/F2 11 Tf")
            content_lines.append(f"0 -25 Td")
            sign_cum = '+' if cumulative >= 0 else ''
            content_lines.append(f"(TOTAL ACUMULADO: {sign_cum}${cumulative:,.0f} COP) Tj")

            # Separator
            y -= 25
            content_lines.append(f"0 -25 Td")
            content_lines.append(f"(________________________________________________________) Tj")

            # Bet detail list (last 10)
            y -= 30
            content_lines.append(f"/F2 14 Tf")
            content_lines.append(f"0 -30 Td")
            content_lines.append(f"(Ultimas 10 Apuestas Resueltas) Tj")

            recent_resolved = [pr for pr in reversed(enviados) if pr.get('acierto') is not None][:10]
            content_lines.append(f"/F1 9 Tf")
            for pr in recent_resolved:
                y -= 16
                if y < 60:
                    break
                partido = pr.get('partido', 'N/A')[:30]
                pred = pr.get('prediccion', '')[:20]
                cuota = pr.get('cuota', 0)
                resultado = 'Ganada' if pr.get('acierto') else 'Perdida'
                pl_val = STAKE * float(cuota) - STAKE if pr.get('acierto') else -STAKE
                sign_v = '+' if pl_val >= 0 else ''
                line = f"{partido} | {pred} @{cuota} = {resultado} ({sign_v}${pl_val:,.0f})"
                line = line.replace('(', '\\(').replace(')', '\\)')
                content_lines.append(f"0 -16 Td")
                content_lines.append(f"({line}) Tj")

            # Footer
            content_lines.append(f"0 -{max(y - 30, 16)} Td")
            content_lines.append(f"/F1 8 Tf")
            content_lines.append(f"(Reporte generado por BetGeniuX - Datos de historial_predicciones.json) Tj")

            content_lines.append("ET")
            content_stream = "\n".join(content_lines)

            # Object 4: Content stream
            objects.append(f"4 0 obj\n<< /Length {len(content_stream)} >>\nstream\n{content_stream}\nendstream\nendobj")
            # Object 5: Font Helvetica
            objects.append("5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj")
            # Object 6: Font Helvetica-Bold
            objects.append("6 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>\nendobj")

            # Write PDF
            pdf_content = "%PDF-1.4\n"
            offsets = []
            for obj in objects:
                offsets.append(len(pdf_content))
                pdf_content += obj + "\n"

            xref_start = len(pdf_content)
            pdf_content += "xref\n"
            pdf_content += f"0 {len(objects) + 1}\n"
            pdf_content += "0000000000 65535 f \n"
            for off in offsets:
                pdf_content += f"{off:010d} 00000 n \n"
            pdf_content += "trailer\n"
            pdf_content += f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            pdf_content += "startxref\n"
            pdf_content += f"{xref_start}\n"
            pdf_content += "%%EOF"

            with open(filepath, 'w') as f:
                f.write(pdf_content)

            messagebox.showinfo("Reporte Exportado",
                                f"Reporte PDF guardado exitosamente en:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el PDF:\n{str(e)}")

    def _build_dashboard_content(self, p):
        """Build the owner dashboard with detailed metrics and KPIs"""
        import tkinter as tk

        self._dashboard_frame.grid_rowconfigure(4, weight=1)
        self._dashboard_frame.grid_columnconfigure(0, weight=1)

        # Title
        title_f = tk.Frame(self._dashboard_frame, bg=p['bg'])
        title_f.grid(row=0, column=0, sticky='ew', pady=(0, 16))
        tk.Label(title_f, text="📊  Panel de Control",
                 bg=p['bg'], fg=p['fg'],
                 font=('Segoe UI', 16, 'bold')).pack(anchor='w')
        tk.Label(title_f, text="Resumen ejecutivo del sistema BetGeniuX",
                 bg=p['bg'], fg=p['muted'],
                 font=('Segoe UI', 10)).pack(anchor='w', pady=(4, 0))

        # ── Top KPI cards row ────────────────────────────────
        kpi_row = tk.Frame(self._dashboard_frame, bg=p['bg'])
        kpi_row.grid(row=1, column=0, sticky='ew', pady=(0, 16))
        for c in range(4):
            kpi_row.grid_columnconfigure(c, weight=1, uniform='kpi')

        kpi_defs = [
            ("usuarios_activos", "⭐", "Usuarios Premium", "0", "#3B82F6"),
            ("pronosticos_hoy",  "🎯", "Pronosticos Hoy",  "0", "#10B981"),
            ("tasa_acierto",     "📈", "Tasa de Acierto",  "0%", "#F59E0B"),
            ("roi_global",       "💰", "ROI Global",        "0%", "#8B5CF6"),
        ]
        self._dash_kpi_labels = {}
        for col, (kid, icon, label, val, accent) in enumerate(kpi_defs):
            card = tk.Frame(kpi_row, bg=p['card_bg'], padx=20, pady=16,
                            highlightbackground=accent, highlightthickness=2)
            card.grid(row=0, column=col, sticky='ew', padx=6)

            top_row = tk.Frame(card, bg=p['card_bg'])
            top_row.pack(fill='x')
            tk.Label(top_row, text=icon, bg=p['card_bg'], fg=p['fg'],
                     font=('Segoe UI', 16)).pack(side='left')
            tk.Label(top_row, text=label, bg=p['card_bg'], fg=p['muted'],
                     font=('Segoe UI', 9)).pack(side='right')

            v_lbl = tk.Label(card, text=val, bg=p['card_bg'],
                             fg=accent, font=('Segoe UI', 28, 'bold'))
            v_lbl.pack(anchor='w', pady=(8, 0))

            self._dash_kpi_labels[kid] = v_lbl

        # ── Second row: Rendimiento + Distribucion ───────────
        mid_row = tk.Frame(self._dashboard_frame, bg=p['bg'])
        mid_row.grid(row=2, column=0, sticky='ew', pady=(0, 16))
        mid_row.grid_columnconfigure(0, weight=3)
        mid_row.grid_columnconfigure(1, weight=2)

        # Performance card
        perf_card = tk.Frame(mid_row, bg=p['card_bg'], padx=24, pady=20,
                              highlightbackground=p['card_border'], highlightthickness=1)
        perf_card.grid(row=0, column=0, sticky='nsew', padx=(0, 8))

        tk.Label(perf_card, text="Rendimiento de Predicciones",
                 bg=p['card_bg'], fg=p['fg'],
                 font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(0, 16))

        perf_items = [
            ("total_enviados",    "Total Enviados a Telegram"),
            ("total_acertados",   "Acertadas"),
            ("total_fallados",    "Falladas"),
            ("total_pendientes",  "Pendientes de Resultado"),
            ("promedio_cuota",    "Promedio Cuota"),
            ("mejor_racha",       "Mejor Racha Actual"),
        ]
        self._dash_perf_labels = {}
        for pid, plabel in perf_items:
            row = tk.Frame(perf_card, bg=p['card_bg'])
            row.pack(fill='x', pady=3)
            tk.Label(row, text=plabel, bg=p['card_bg'], fg=p['muted'],
                     font=('Segoe UI', 10)).pack(side='left')
            val_l = tk.Label(row, text="0", bg=p['card_bg'], fg=p['fg'],
                             font=('Segoe UI', 10, 'bold'))
            val_l.pack(side='right')
            self._dash_perf_labels[pid] = val_l

        # Distribution / status card
        status_card = tk.Frame(mid_row, bg=p['card_bg'], padx=24, pady=20,
                                highlightbackground=p['card_border'], highlightthickness=1)
        status_card.grid(row=0, column=1, sticky='nsew', padx=(8, 0))

        tk.Label(status_card, text="Estado del Sistema",
                 bg=p['card_bg'], fg=p['fg'],
                 font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(0, 16))

        status_items = [
            ("estado_bot",        "Bot Telegram"),
            ("usuarios_premium",  "Usuarios Premium"),
            ("usuarios_free",     "Usuarios Free"),
            ("ligas_cubiertas",   "Ligas Cubiertas"),
            ("ultima_prediccion", "Ultima Prediccion"),
            ("uptime_sistema",    "Estado del Sistema"),
        ]
        self._dash_status_labels = {}
        for sid, slabel in status_items:
            row = tk.Frame(status_card, bg=p['card_bg'])
            row.pack(fill='x', pady=3)
            tk.Label(row, text=slabel, bg=p['card_bg'], fg=p['muted'],
                     font=('Segoe UI', 10)).pack(side='left')
            val_l = tk.Label(row, text="--", bg=p['card_bg'], fg=p['fg'],
                             font=('Segoe UI', 10, 'bold'))
            val_l.pack(side='right')
            self._dash_status_labels[sid] = val_l

        # ── Third row: Recent activity (wider, full width) ──────────────
        recent_card = tk.Frame(self._dashboard_frame, bg=p['card_bg'], padx=24, pady=20,
                                highlightbackground=p['card_border'], highlightthickness=1)
        recent_card.grid(row=3, column=0, sticky='ew', pady=(0, 16))

        tk.Label(recent_card, text="Actividad Reciente",
                 bg=p['card_bg'], fg=p['fg'],
                 font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(0, 12))

        # Clipping container for smooth horizontal scroll animation
        self._dash_activity_clip = tk.Frame(recent_card, bg=p['card_bg'], height=160)
        self._dash_activity_clip.pack(fill='x')
        self._dash_activity_clip.pack_propagate(False)

        self._dash_activity_canvas = tk.Canvas(self._dash_activity_clip, bg=p['card_bg'],
                                                highlightthickness=0, bd=0)
        self._dash_activity_canvas.pack(fill='both', expand=True)

        self._dash_activity_frame = tk.Frame(self._dash_activity_canvas, bg=p['card_bg'])
        self._dash_activity_canvas.create_window((0, 0), window=self._dash_activity_frame,
                                                  anchor='nw', tags='content')

        # Animation state
        self._dash_scroll_offset = 0
        self._dash_scroll_running = False
        self._dash_scroll_items = []
        self._dash_scroll_item_height = 28
        self._dash_scroll_pause_count = 0

        # ── Spacer for scrollable area ───────────────────────
        spacer = tk.Frame(self._dashboard_frame, bg=p['bg'])
        spacer.grid(row=4, column=0, sticky='nsew')

    def _refresh_dashboard_data(self):
        """Load real data into dashboard metrics"""
        try:
            historial = cargar_json('historial_predicciones.json') or []
        except Exception:
            historial = []

        enviados = [pr for pr in historial if pr.get('sent_to_telegram', False)]
        acertados = [pr for pr in enviados if pr.get('acierto') is True]
        fallados = [pr for pr in enviados if pr.get('acierto') is False]
        pendientes = [pr for pr in enviados if pr.get('acierto') is None]

        # Today's predictions
        hoy_str = hora_bogota().strftime('%Y-%m-%d')
        pred_hoy = [pr for pr in enviados if pr.get('fecha', '') == hoy_str]

        # Accuracy
        resueltos = len(acertados) + len(fallados)
        tasa = (len(acertados) / resueltos * 100) if resueltos > 0 else 0

        # ROI calculation
        total_stake = 0
        total_retorno = 0
        for pr in enviados:
            stake = float(pr.get('stake', pr.get('stake_recomendado', 1)))
            cuota = float(pr.get('cuota', 1))
            total_stake += stake
            if pr.get('acierto') is True:
                total_retorno += stake * cuota
            elif pr.get('acierto') is False:
                total_retorno += 0  # lost
            else:
                total_retorno += stake  # pending = neutral
        roi = ((total_retorno - total_stake) / total_stake * 100) if total_stake > 0 else 0

        # Average odds
        cuotas = [float(pr.get('cuota', 0)) for pr in enviados if pr.get('cuota')]
        avg_cuota = sum(cuotas) / len(cuotas) if cuotas else 0

        # Win streak
        racha = 0
        for pr in reversed(enviados):
            if pr.get('acierto') is True:
                racha += 1
            elif pr.get('acierto') is False:
                break

        # Users
        usuarios_premium = 0
        usuarios_free = 0
        try:
            from access_manager import access_manager
            if access_manager and hasattr(access_manager, 'listar_usuarios'):
                usuarios = access_manager.listar_usuarios()
                if usuarios and isinstance(usuarios, (list, tuple)):
                    for u in usuarios:
                        if isinstance(u, dict):
                            if u.get('premium') or u.get('is_premium'):
                                usuarios_premium += 1
                            else:
                                usuarios_free += 1
                        elif isinstance(u, (list, tuple)) and len(u) >= 4:
                            if u[3]:
                                usuarios_premium += 1
                            else:
                                usuarios_free += 1
        except Exception:
            pass
        total_usuarios = usuarios_premium + usuarios_free

        # Leagues covered
        ligas = set()
        for pr in enviados:
            liga = pr.get('liga', '')
            if liga:
                ligas.add(liga)

        # Last prediction time
        ultima = "--"
        if enviados:
            last = enviados[-1]
            ultima = last.get('fecha', last.get('fecha_envio_telegram', '--'))
            if len(ultima) > 10:
                ultima = ultima[:16].replace('T', ' ')

        # Update KPI cards
        p = self._palette
        if hasattr(self, '_dash_kpi_labels'):
            self._dash_kpi_labels['usuarios_activos'].config(text=str(usuarios_premium))
            self._dash_kpi_labels['pronosticos_hoy'].config(text=str(len(pred_hoy)))
            self._dash_kpi_labels['tasa_acierto'].config(text=f"{tasa:.1f}%")
            roi_color = "#10B981" if roi >= 0 else "#EF4444"
            self._dash_kpi_labels['roi_global'].config(text=f"{roi:+.1f}%", fg=roi_color)

        # Update performance labels
        if hasattr(self, '_dash_perf_labels'):
            self._dash_perf_labels['total_enviados'].config(text=str(len(enviados)))
            self._dash_perf_labels['total_acertados'].config(text=str(len(acertados)), fg="#10B981")
            self._dash_perf_labels['total_fallados'].config(text=str(len(fallados)), fg="#EF4444")
            self._dash_perf_labels['total_pendientes'].config(text=str(len(pendientes)), fg="#F59E0B")
            self._dash_perf_labels['promedio_cuota'].config(text=f"{avg_cuota:.2f}" if avg_cuota else "--")
            self._dash_perf_labels['mejor_racha'].config(
                text=f"{racha} seguidas" if racha > 0 else "0",
                fg="#10B981" if racha > 0 else p['fg'])

        # Update status labels
        if hasattr(self, '_dash_status_labels'):
            self._dash_status_labels['estado_bot'].config(text="Activo", fg="#10B981")
            self._dash_status_labels['usuarios_premium'].config(text=str(usuarios_premium))
            self._dash_status_labels['usuarios_free'].config(text=str(usuarios_free))
            self._dash_status_labels['ligas_cubiertas'].config(text=str(len(ligas)))
            self._dash_status_labels['ultima_prediccion'].config(text=ultima)
            self._dash_status_labels['uptime_sistema'].config(text="Operativo", fg="#10B981")

        # Update recent activity with scrolling animation
        if hasattr(self, '_dash_activity_frame'):
            import tkinter as tk
            for w in self._dash_activity_frame.winfo_children():
                w.destroy()

            recent = list(reversed(enviados[-10:])) if enviados else []
            self._dash_scroll_items = recent
            if not recent:
                tk.Label(self._dash_activity_frame,
                         text="Sin actividad reciente. Genera pronosticos para comenzar.",
                         bg=p['card_bg'], fg=p['muted'],
                         font=('Segoe UI', 10)).pack(anchor='w')
            else:
                # Build items twice for seamless loop
                display_items = recent + recent
                for pr in display_items:
                    act_row = tk.Frame(self._dash_activity_frame, bg=p['card_bg'])
                    act_row.pack(fill='x', pady=3)

                    # Status icon
                    if pr.get('acierto') is True:
                        status_icon, status_fg = "✅", "#10B981"
                    elif pr.get('acierto') is False:
                        status_icon, status_fg = "❌", "#EF4444"
                    else:
                        status_icon, status_fg = "⏳", "#F59E0B"

                    tk.Label(act_row, text=status_icon, bg=p['card_bg'], fg=status_fg,
                             font=('Segoe UI', 11)).pack(side='left', padx=(0, 10))
                    partido = pr.get('partido', 'Desconocido')
                    pred_text = pr.get('prediccion', '')
                    cuota_val = pr.get('cuota', '')
                    tk.Label(act_row, text=f"{partido}  |  {pred_text}  @{cuota_val}",
                             bg=p['card_bg'], fg=p['fg'],
                             font=('Segoe UI', 10)).pack(side='left', padx=(0, 20))
                    fecha_val = pr.get('fecha', '')
                    tk.Label(act_row, text=fecha_val, bg=p['card_bg'], fg=p['muted'],
                             font=('Segoe UI', 9)).pack(side='right')

                # Update canvas scroll region after widgets render
                self._dash_activity_frame.update_idletasks()
                self._dash_activity_canvas.config(
                    scrollregion=self._dash_activity_canvas.bbox('all'))

                # Start smooth scroll animation
                self._dash_scroll_offset = 0
                self._dash_scroll_pause_count = 0
                if not self._dash_scroll_running and len(recent) > 4:
                    self._dash_scroll_running = True
                    self._dash_animate_scroll()

    def _dash_animate_scroll(self):
        """Smooth scroll animation for recent activity feed"""
        if not self._dash_scroll_running:
            return
        if not hasattr(self, '_dash_activity_canvas'):
            self._dash_scroll_running = False
            return
        try:
            # Get total height of all items and height of one set
            bbox = self._dash_activity_canvas.bbox('all')
            if not bbox:
                self._dash_scroll_running = False
                return
            total_height = bbox[3] - bbox[1]
            half_height = total_height // 2
            clip_height = self._dash_activity_clip.winfo_height()

            if half_height <= clip_height:
                # Not enough items to scroll
                self._dash_scroll_running = False
                return

            # Calculate item height dynamically
            n_items = len(self._dash_scroll_items)
            if n_items > 0:
                item_h = half_height / n_items
            else:
                self._dash_scroll_running = False
                return

            # Pause briefly at each item boundary for readability
            at_boundary = abs(self._dash_scroll_offset % item_h) < 1.5
            if at_boundary and self._dash_scroll_pause_count < 40:
                self._dash_scroll_pause_count += 1
                self._dash_activity_canvas.after(50, self._dash_animate_scroll)
                return

            self._dash_scroll_pause_count = 0

            # Scroll by 1 pixel
            self._dash_scroll_offset += 1
            self._dash_activity_canvas.yview_moveto(self._dash_scroll_offset / total_height)

            # Reset to beginning seamlessly when we've scrolled through first set
            if self._dash_scroll_offset >= half_height:
                self._dash_scroll_offset = 0
                self._dash_activity_canvas.yview_moveto(0)

            # Schedule next frame (~30fps smooth animation)
            self._dash_activity_canvas.after(33, self._dash_animate_scroll)
        except Exception:
            self._dash_scroll_running = False

    def _on_tab_click(self, tab_id):
        """Handle content tab switching"""
        p = self._palette
        for tid, lbl in self._content_tab_btns.items():
            is_act = (tid == tab_id)
            lbl.configure(
                bg=p['tab_active'] if is_act else p['tab_inactive'],
                fg=p['tab_active_text'] if is_act else p['tab_text'],
                font=('Segoe UI', 10, 'bold' if is_act else 'normal'))
        self._active_tab = tab_id
        if tab_id == "historial":
            self._show_tracking_page()
            self._set_active_nav('tracking')

    def _toggle_theme(self):
        """Toggle between dark and light themes"""
        import tkinter as tk
        new_mode = 'light' if self.dark_mode_var.get() else 'dark'
        self.dark_mode_var.set(new_mode == 'dark')
        palette = self.theme.apply(new_mode)
        self._palette = palette
        self._rebuild_theme(palette)
        if hasattr(self, '_theme_toggle_btn'):
            self._theme_toggle_btn.config(
                text="🌙 Modo Oscuro" if new_mode == 'light' else "☀️ Modo Claro")

    def _update_clock(self):
        """Update the live Colombia clock every second"""
        try:
            now = hora_bogota()
            time_str = now.strftime('%I:%M:%S %p')
            self._clock_lbl.config(text=time_str)
        except Exception:
            pass
        try:
            self.root.after(1000, self._update_clock)
        except Exception:
            pass

    def _rebuild_theme(self, p):
        """Rebuild all custom tk widgets with the new palette"""
        try:
            for frame in (self._content, self._scroll_container,
                          self._tracking_frame, self._usuarios_frame,
                          self._alertas_frame, self._settings_frame):
                frame.configure(bg=p['bg'])
            self._header.configure(bg=p['header_bg'])
            self._filter_bar.configure(bg=p['header_bg'])
            self._bottom_bar.configure(bg=p['bottom_bg'],
                                       highlightbackground=p['border'])
            # Update header children
            for w in self._header.winfo_children():
                w.configure(bg=p['header_bg'])
                for c in w.winfo_children():
                    c.configure(bg=p['header_bg'])
            # Update filter bar labels
            for w in self._filter_bar.winfo_children():
                if isinstance(w, tk.Label):
                    w.configure(bg=p['header_bg'], fg=p['muted'])
            # Update stats
            self._stats_row.configure(bg=p['bg'])
            for sid, parts in self._stats_labels.items():
                parts['card'].configure(bg=p['stats_bg'],
                                        highlightbackground=p['card_border'])
                parts['value'].configure(bg=p['stats_bg'], fg=p['fg'])
                parts['name'].configure(bg=p['stats_bg'], fg=p['muted'])
                for c in parts['card'].winfo_children():
                    c.configure(bg=p['stats_bg'])
            # Update tabs (if they exist)
            if hasattr(self, '_tabs_frame'):
                self._tabs_frame.configure(bg=p['bg'])
            for tid, lbl in self._content_tab_btns.items():
                is_act = (tid == self._active_tab)
                lbl.configure(
                    bg=p['tab_active'] if is_act else p['tab_inactive'],
                    fg=p['tab_active_text'] if is_act else p['tab_text'])
            # Update bottom bar
            for w in self._bottom_bar.winfo_children():
                w.configure(bg=p['bottom_bg'])
                for c in w.winfo_children():
                    if isinstance(c, tk.Label):
                        c.configure(bg=p['bottom_bg'])
            self._gen_btn.configure(bg=p['primary'],
                                    activebackground=p['primary_hover'])
            # ScrollableFrames
            if hasattr(self, 'sf_predicciones') and self.sf_predicciones:
                self.sf_predicciones.update_theme(p['bg'])
            if hasattr(self, 'sf_partidos') and self.sf_partidos:
                self.sf_partidos.update_theme(p['bg'])
        except Exception as e:
            logger.warning(f"Error rebuilding theme: {e}")

    def update_custom_widgets_theme(self, palette):
        """Actualiza widgets personalizados que no usan ttk (legacy compat)"""
        self._rebuild_theme(palette)

    def _update_stats_display(self, num_pred=0, num_partidos=0, avg_conf=0):
        """Update the stats cards with current data"""
        try:
            self._stats_labels['pred_hoy']['value'].config(text=str(num_pred))
            self._stats_labels['partidos']['value'].config(text=str(num_partidos))
            conf_text = f"{avg_conf:.1f}%" if avg_conf else "0%"
            self._stats_labels['confianza']['value'].config(text=conf_text)
        except Exception:
            pass
    
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

    def _build_settings_content(self, p):
        """Build settings content inside self._settings_frame"""
        import tkinter as tk
        from tkinter import ttk

        card = tk.Frame(self._settings_frame, bg=p['card_bg'], padx=40, pady=30,
                        highlightbackground=p['card_border'], highlightthickness=1)
        card.pack(fill='x', pady=(0, 20))

        tk.Label(card, text="⚙️  Configuracion de Filtros de Cuotas",
                 bg=p['card_bg'], fg=p['fg'],
                 font=('Segoe UI', 14, 'bold')).pack(anchor='w', pady=(0, 24))

        config_actual = self.cargar_configuracion()

        row_min = tk.Frame(card, bg=p['card_bg'])
        row_min.pack(fill='x', pady=8)
        tk.Label(row_min, text="Cuota minima:", bg=p['card_bg'], fg=p['fg'],
                 font=('Segoe UI', 11)).pack(side='left')
        self.entry_min_tab = tk.Entry(row_min, font=('Segoe UI', 11), width=12,
                                      bg=p['entry_bg'], fg=p['entry_fg'],
                                      insertbackground=p['fg'], relief='flat',
                                      highlightbackground=p['border'], highlightthickness=1)
        self.entry_min_tab.pack(side='right')
        self.entry_min_tab.insert(0, str(config_actual.get("odds_min", 1.30)))

        row_max = tk.Frame(card, bg=p['card_bg'])
        row_max.pack(fill='x', pady=8)
        tk.Label(row_max, text="Cuota maxima:", bg=p['card_bg'], fg=p['fg'],
                 font=('Segoe UI', 11)).pack(side='left')
        self.entry_max_tab = tk.Entry(row_max, font=('Segoe UI', 11), width=12,
                                      bg=p['entry_bg'], fg=p['entry_fg'],
                                      insertbackground=p['fg'], relief='flat',
                                      highlightbackground=p['border'], highlightthickness=1)
        self.entry_max_tab.pack(side='right')
        self.entry_max_tab.insert(0, str(config_actual.get("odds_max", 1.60)))

        info_text = "Formato: Decimal EU  |  Limite minimo tecnico: 1.01\nSolo se mostraran apuestas en el rango seleccionado"
        tk.Label(card, text=info_text, bg=p['card_bg'], fg=p['muted'],
                 font=('Segoe UI', 9), justify='left').pack(anchor='w', pady=(16, 0))

        btn_f = tk.Frame(card, bg=p['card_bg'])
        btn_f.pack(anchor='w', pady=(20, 0))
        tk.Button(btn_f, text="Guardar Configuracion", bg=p['primary'], fg='#FFFFFF',
                  font=('Segoe UI', 10, 'bold'), relief='flat', cursor='hand2',
                  padx=20, pady=6, bd=0, command=self.guardar_ajustes_tab).pack()

    def setup_settings_tab(self):
        """Legacy wrapper - settings are now built inline"""
        pass

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

    # ── Alertas inline page builder ─────────────────────────────

    def _build_alertas_content(self, p):
        """Build alertas page content with multiple alert types and manual alerts"""
        import tkinter as tk
        from tkinter import ttk

        self._alertas_frame.grid_rowconfigure(2, weight=1)
        self._alertas_frame.grid_columnconfigure(0, weight=1)

        # Title
        title_f = tk.Frame(self._alertas_frame, bg=p['bg'])
        title_f.grid(row=0, column=0, sticky='ew', pady=(0, 16))
        tk.Label(title_f, text="📢  Centro de Alertas y Mensajes",
                 bg=p['bg'], fg=p['fg'],
                 font=('Segoe UI', 16, 'bold')).pack(anchor='w')
        tk.Label(title_f, text="Envia alertas predefinidas o mensajes personalizados a tus usuarios",
                 bg=p['bg'], fg=p['muted'],
                 font=('Segoe UI', 10)).pack(anchor='w', pady=(4, 0))

        # Predefined alert types card
        predef_card = tk.Frame(self._alertas_frame, bg=p['card_bg'], padx=24, pady=20,
                               highlightbackground=p['card_border'], highlightthickness=1)
        predef_card.grid(row=1, column=0, sticky='ew', pady=(0, 16))

        tk.Label(predef_card, text="Alertas Rapidas",
                 bg=p['card_bg'], fg=p['fg'],
                 font=('Segoe UI', 13, 'bold')).pack(anchor='w', pady=(0, 16))

        alerts_grid = tk.Frame(predef_card, bg=p['card_bg'])
        alerts_grid.pack(fill='x')
        for c in range(3):
            alerts_grid.grid_columnconfigure(c, weight=1, uniform='alert')

        alert_types = [
            ("Alerta de Pronostico", "#3B82F6",
             "Alerta de pronostico!\nNuestro sistema ha detectado una oportunidad con valor.\nEn unos momentos compartiremos nuestra apuesta recomendada.",
             True),
            ("Promocion Premium", "#10B981",
             "OFERTA ESPECIAL!\n\nUnete a BetGeniuX Premium y accede a:\n• Pronosticos exclusivos con analisis detallado\n• Estadisticas avanzadas de partidos\n• Alertas en tiempo real\n• Soporte prioritario\n\nSolo $12 USD por semana\nMejora tus resultados con nuestros expertos\n\nNo te pierdas las mejores oportunidades!\nActiva tu membresia ahora y empieza a ganar.",
             False),
            ("Jornada en Vivo", "#F59E0B",
             "JORNADA EN VIVO!\n\nLos partidos de hoy ya estan en juego.\nRevisa nuestros pronosticos actualizados y no te pierdas ninguna oportunidad.\n\nAnalisis en tiempo real disponible.\nBuena suerte!",
             True),
            ("Alta Confianza", "#EF4444",
             "PICK DE ALTA CONFIANZA!\n\nNuestro modelo ha identificado una apuesta con confianza superior al 85%.\n\nRevisa el pick destacado en la app.\nSolo para miembros Premium.",
             True),
            ("Resumen Diario", "#8B5CF6",
             "RESUMEN DEL DIA\n\nAqui tienes el resumen de los pronosticos de hoy.\n\nRevisa los resultados en la seccion de Tracking.\nSigue mejorando con BetGeniuX.",
             True),
            ("Ultimo Momento", "#DC2626",
             "ULTIMO MOMENTO!\n\nInformacion importante sobre los partidos de hoy.\nRevisa las actualizaciones en la app.\n\nCambios de alineacion o condiciones que pueden afectar los pronosticos.",
             True),
        ]

        for idx, (title, color, default_msg, premium_only) in enumerate(alert_types):
            row_idx = idx // 3
            col_idx = idx % 3
            msg = self._custom_alert_messages.get(title, default_msg)
            btn_f = tk.Frame(alerts_grid, bg=p['secondary_bg'], padx=16, pady=12,
                             highlightbackground=p['card_border'], highlightthickness=1,
                             cursor='hand2')
            btn_f.grid(row=row_idx, column=col_idx, sticky='ew', padx=4, pady=4)
            tk.Label(btn_f, text=title, bg=p['secondary_bg'],
                     fg=p['fg'], font=('Segoe UI', 10, 'bold')).pack(anchor='w')
            audience_text = "Solo Premium" if premium_only else "No Premium"
            tk.Label(btn_f, text=audience_text, bg=p['secondary_bg'], fg=p['muted'],
                     font=('Segoe UI', 8)).pack(anchor='w', pady=(2, 0))
            send_btn = tk.Button(btn_f, text="Enviar", bg=color, fg='#FFFFFF',
                                 font=('Segoe UI', 9, 'bold'), relief='flat',
                                 cursor='hand2', padx=12, pady=3, bd=0,
                                 command=lambda m=msg, po=premium_only: self._enviar_alerta_tipo(m, po))
            send_btn.pack(anchor='w', pady=(8, 0))
            # Double-click to edit message
            for widget in [btn_f] + btn_f.winfo_children():
                widget.bind('<Double-Button-1>',
                            lambda e, t=title, m=msg, po=premium_only, c=color: self._abrir_editor_alerta(t, m, po, c))

        # Manual alert card
        manual_card = tk.Frame(self._alertas_frame, bg=p['card_bg'], padx=24, pady=20,
                               highlightbackground=p['card_border'], highlightthickness=1)
        manual_card.grid(row=2, column=0, sticky='nsew', pady=(0, 10))
        manual_card.grid_rowconfigure(2, weight=1)
        manual_card.grid_columnconfigure(0, weight=1)

        tk.Label(manual_card, text="Mensaje Personalizado",
                 bg=p['card_bg'], fg=p['fg'],
                 font=('Segoe UI', 13, 'bold')).grid(row=0, column=0, sticky='w', pady=(0, 8))

        tk.Label(manual_card, text="Escribe un mensaje personalizado para enviar a tus usuarios:",
                 bg=p['card_bg'], fg=p['muted'],
                 font=('Segoe UI', 9)).grid(row=1, column=0, sticky='w', pady=(0, 8))

        self._alerta_manual_text = tk.Text(manual_card, font=('Segoe UI', 11),
                                           bg=p['entry_bg'], fg=p['entry_fg'],
                                           insertbackground=p['fg'], relief='flat',
                                           highlightbackground=p['border'], highlightthickness=1,
                                           wrap='word', height=6)
        self._alerta_manual_text.grid(row=2, column=0, sticky='nsew', pady=(0, 12))

        btns_row = tk.Frame(manual_card, bg=p['card_bg'])
        btns_row.grid(row=3, column=0, sticky='w')

        # Audience selection
        self._alerta_audience = tk.StringVar(value='premium')
        tk.Label(btns_row, text="Enviar a:", bg=p['card_bg'], fg=p['muted'],
                 font=('Segoe UI', 9)).pack(side='left', padx=(0, 8))
        for val, text in [('premium', 'Solo Premium'), ('todos', 'Todos'), ('no_premium', 'No Premium')]:
            tk.Radiobutton(btns_row, text=text, variable=self._alerta_audience, value=val,
                           bg=p['card_bg'], fg=p['fg'], selectcolor=p['entry_bg'],
                           activebackground=p['card_bg'], activeforeground=p['fg'],
                           font=('Segoe UI', 9)).pack(side='left', padx=(0, 12))

        tk.Button(btns_row, text="📤 Enviar Mensaje", bg=p['primary'], fg='#FFFFFF',
                  font=('Segoe UI', 10, 'bold'), relief='flat', cursor='hand2',
                  padx=16, pady=6, bd=0,
                  command=self._enviar_alerta_manual).pack(side='right', padx=(20, 0))

    def _abrir_editor_alerta(self, titulo, mensaje, premium_only, color):
        """Open a centered popup to edit and send an alert message"""
        import tkinter as tk
        from tkinter import messagebox
        p = self._palette

        popup = tk.Toplevel(self.root)
        popup.title(f"Editar: {titulo}")
        popup.configure(bg=p['bg'])
        popup.resizable(True, True)

        # Size and center
        w, h = 620, 540
        popup.geometry(f"{w}x{h}")
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() - w) // 2
        y = (popup.winfo_screenheight() - h) // 2
        popup.geometry(f"{w}x{h}+{x}+{y}")
        popup.transient(self.root)
        popup.grab_set()

        # Header
        header = tk.Frame(popup, bg=color, height=50)
        header.pack(fill='x', side='top')
        header.pack_propagate(False)
        tk.Label(header, text=titulo, bg=color, fg='#FFFFFF',
                 font=('Segoe UI', 14, 'bold')).pack(expand=True)

        # Buttons (pack at bottom FIRST so they are always visible)
        btn_row = tk.Frame(popup, bg=p['bg'], pady=12)
        btn_row.pack(fill='x', side='bottom', padx=24)

        # Audience (pack above buttons)
        audience_var = tk.StringVar(value='premium' if premium_only else 'no_premium')
        aud_row = tk.Frame(popup, bg=p['bg'])
        aud_row.pack(fill='x', side='bottom', padx=24, pady=(8, 0))
        tk.Label(aud_row, text="Enviar a:", bg=p['bg'], fg=p['muted'],
                 font=('Segoe UI', 9)).pack(side='left', padx=(0, 8))
        for val, text in [('premium', 'Solo Premium'), ('todos', 'Todos'), ('no_premium', 'No Premium')]:
            tk.Radiobutton(aud_row, text=text, variable=audience_var, value=val,
                           bg=p['bg'], fg=p['fg'], selectcolor=p['entry_bg'],
                           activebackground=p['bg'], activeforeground=p['fg'],
                           font=('Segoe UI', 9)).pack(side='left', padx=(0, 12))

        # Body (fills remaining space in the middle)
        body = tk.Frame(popup, bg=p['bg'], padx=24, pady=16)
        body.pack(fill='both', expand=True)
        body.grid_rowconfigure(1, weight=1)
        body.grid_columnconfigure(0, weight=1)

        tk.Label(body, text="Edita el mensaje antes de enviar:",
                 bg=p['bg'], fg=p['muted'],
                 font=('Segoe UI', 10)).grid(row=0, column=0, sticky='w', pady=(0, 8))

        text_widget = tk.Text(body, font=('Segoe UI', 11),
                              bg=p['entry_bg'], fg=p['entry_fg'],
                              insertbackground=p['fg'], relief='flat',
                              highlightbackground=p['border'], highlightthickness=1,
                              wrap='word')
        text_widget.grid(row=1, column=0, sticky='nsew')
        text_widget.insert('1.0', mensaje)

        def enviar():
            msg_editado = text_widget.get('1.0', 'end').strip()
            if not msg_editado:
                messagebox.showwarning("Vacio", "El mensaje no puede estar vacio.")
                return
            aud = audience_var.get()
            try:
                if aud == 'premium':
                    resultado = enviar_telegram_masivo(msg_editado, only_premium=True)
                elif aud == 'no_premium':
                    resultado = enviar_telegram_masivo(msg_editado, only_premium=False, exclude_premium=True)
                else:
                    resultado = enviar_telegram_masivo(msg_editado, only_premium=False)
                if resultado["exito"]:
                    audiencia = resultado.get('audiencia', 'usuarios')
                    info = f"Audiencia: {audiencia}\n"
                    info += f"Total: {resultado['total_usuarios']}\n"
                    info += f"Enviados: {resultado['enviados_exitosos']}"
                    messagebox.showinfo("Alerta Enviada", info)
                    popup.destroy()
                else:
                    if resultado.get('total_usuarios', 0) == 0:
                        messagebox.showinfo("Sin usuarios", "No hay usuarios en la audiencia seleccionada.")
                    else:
                        messagebox.showerror("Error", "No se pudo enviar la alerta.")
            except Exception as e:
                messagebox.showerror("Error", f"Error enviando alerta: {e}")

        def guardar():
            msg_editado = text_widget.get('1.0', 'end').strip()
            if not msg_editado:
                messagebox.showwarning("Vacio", "El mensaje no puede estar vacio.")
                return
            self._custom_alert_messages[titulo] = msg_editado
            self._save_custom_alerts()
            messagebox.showinfo("Guardado", f"Mensaje de '{titulo}' guardado correctamente.")
            popup.destroy()
            # Rebuild alertas page to reflect saved message
            if hasattr(self, '_alertas_frame'):
                for w in self._alertas_frame.winfo_children():
                    w.destroy()
                self._build_alertas_content(self._palette)

        tk.Button(btn_row, text="Cancelar", bg=p['secondary_bg'], fg=p['fg'],
                  font=('Segoe UI', 10), relief='flat', cursor='hand2',
                  padx=16, pady=6, bd=0,
                  command=popup.destroy).pack(side='left')
        tk.Button(btn_row, text="Guardar", bg='#6B7280', fg='#FFFFFF',
                  font=('Segoe UI', 10, 'bold'), relief='flat', cursor='hand2',
                  padx=16, pady=6, bd=0,
                  command=guardar).pack(side='left', padx=(12, 0))
        tk.Button(btn_row, text="Enviar Mensaje", bg=color, fg='#FFFFFF',
                  font=('Segoe UI', 10, 'bold'), relief='flat', cursor='hand2',
                  padx=16, pady=6, bd=0,
                  command=enviar).pack(side='right')

    def _enviar_alerta_tipo(self, mensaje, premium_only):
        """Send a predefined alert type"""
        from tkinter import messagebox
        try:
            if premium_only:
                resultado = enviar_telegram_masivo(mensaje, only_premium=True)
            else:
                resultado = enviar_telegram_masivo(mensaje, only_premium=False, exclude_premium=True)
            if resultado["exito"]:
                audiencia = resultado.get('audiencia', 'usuarios')
                msg = f"✅ Alerta enviada correctamente.\n\n"
                msg += f"📊 Audiencia: {audiencia}\n"
                msg += f"• Total: {resultado['total_usuarios']}\n"
                msg += f"• Enviados: {resultado['enviados_exitosos']}"
                messagebox.showinfo("Alerta Enviada", msg)
            else:
                if resultado.get('total_usuarios', 0) == 0:
                    messagebox.showinfo("Sin usuarios",
                                        "⚠️ No hay usuarios en la audiencia seleccionada.")
                else:
                    messagebox.showerror("Error", "No se pudo enviar la alerta.")
        except Exception as e:
            messagebox.showerror("Error", f"Error enviando alerta: {e}")

    def _enviar_alerta_manual(self):
        """Send a manual custom alert"""
        from tkinter import messagebox
        mensaje = self._alerta_manual_text.get('1.0', 'end').strip()
        if not mensaje:
            messagebox.showwarning("Vacio", "Escribe un mensaje antes de enviar.")
            return
        audience = self._alerta_audience.get()
        try:
            if audience == 'premium':
                resultado = enviar_telegram_masivo(mensaje, only_premium=True)
            elif audience == 'no_premium':
                resultado = enviar_telegram_masivo(mensaje, only_premium=False, exclude_premium=True)
            else:
                resultado = enviar_telegram_masivo(mensaje, only_premium=False)
            if resultado["exito"]:
                audiencia = resultado.get('audiencia', 'usuarios')
                msg = f"✅ Mensaje enviado correctamente.\n\n"
                msg += f"📊 Audiencia: {audiencia}\n"
                msg += f"• Total: {resultado['total_usuarios']}\n"
                msg += f"• Enviados: {resultado['enviados_exitosos']}"
                messagebox.showinfo("Mensaje Enviado", msg)
                self._alerta_manual_text.delete('1.0', 'end')
            else:
                if resultado.get('total_usuarios', 0) == 0:
                    messagebox.showinfo("Sin usuarios",
                                        "⚠️ No hay usuarios en la audiencia seleccionada.")
                else:
                    messagebox.showerror("Error", "No se pudo enviar el mensaje.")
        except Exception as e:
            messagebox.showerror("Error", f"Error enviando mensaje: {e}")

    # ── Tracking inline page builder ────────────────────────────

    def _build_tracking_content(self, p):
        """Build tracking/track record page inline"""
        import tkinter as tk
        from tkinter import ttk, messagebox

        self._tracking_frame.grid_rowconfigure(4, weight=1)
        self._tracking_frame.grid_columnconfigure(0, weight=1)

        # Title
        tk.Label(self._tracking_frame, text="📊  Track Record de Predicciones",
                 bg=p['bg'], fg=p['fg'],
                 font=('Segoe UI', 16, 'bold')).grid(row=0, column=0, sticky='w', pady=(0, 12))

        # Row 1: Filter buttons
        filter_row = tk.Frame(self._tracking_frame, bg=p['bg'])
        filter_row.grid(row=1, column=0, sticky='ew', pady=(0, 8))

        self._track_filtro = tk.StringVar(value="historico")

        btn_color = p['secondary_bg']
        btn_fg = p['fg']
        track_filter_btns = [
            ("⏳ Pendientes", "pendientes"),
            ("✅ Acertados", "acertados"),
            ("❌ Fallados", "fallados"),
            ("📅 Historico", "historico"),
        ]
        self._track_filter_btn_refs = []
        for text, filt in track_filter_btns:
            btn = tk.Button(filter_row, text=text, bg=btn_color, fg=btn_fg,
                            font=('Segoe UI', 9, 'bold'), relief='flat',
                            cursor='hand2', padx=14, pady=5, bd=0,
                            command=lambda f=filt: self._track_filter_click(f))
            btn.pack(side='left', padx=(0, 6))
            self._track_filter_btn_refs.append(btn)

        # Row 2: Date filters
        date_row = tk.Frame(self._tracking_frame, bg=p['bg'])
        date_row.grid(row=2, column=0, sticky='ew', pady=(0, 8))

        tk.Label(date_row, text="Desde:", bg=p['bg'], fg=p['muted'],
                 font=('Segoe UI', 9)).pack(side='left', padx=(0, 4))
        self._track_fecha_inicio = DateEntry(date_row, width=12, background="#2563EB",
                                              foreground="white", borderwidth=0,
                                              date_pattern='yyyy-MM-dd')
        self._track_fecha_inicio.pack(side='left', padx=(0, 12))

        tk.Label(date_row, text="Hasta:", bg=p['bg'], fg=p['muted'],
                 font=('Segoe UI', 9)).pack(side='left', padx=(0, 4))
        self._track_fecha_fin = DateEntry(date_row, width=12, background="#2563EB",
                                           foreground="white", borderwidth=0,
                                           date_pattern='yyyy-MM-dd')
        self._track_fecha_fin.pack(side='left', padx=(0, 12))

        tk.Button(date_row, text="🔍 Filtrar por Fecha", bg=btn_color, fg=btn_fg,
                  font=('Segoe UI', 9, 'bold'), relief='flat', cursor='hand2', padx=12, pady=4, bd=0,
                  command=lambda: self._track_filter_click("por_fecha")).pack(side='left')

        # Row 3: Action buttons
        action_row = tk.Frame(self._tracking_frame, bg=p['bg'])
        action_row.grid(row=3, column=0, sticky='ew', pady=(0, 10))

        self._track_btn_actualizar = tk.Button(action_row, text="🔄 Actualizar Resultados",
                                               bg=btn_color, fg=btn_fg,
                                               font=('Segoe UI', 9, 'bold'), relief='flat',
                                               cursor='hand2', padx=14, pady=5, bd=0,
                                               command=self._track_actualizar_resultados)
        self._track_btn_actualizar.pack(side='left', padx=(0, 6))

        tk.Button(action_row, text="🧹 Limpiar Historial", bg=btn_color, fg=btn_fg,
                  font=('Segoe UI', 9, 'bold'), relief='flat', cursor='hand2',
                  padx=14, pady=5, bd=0,
                  command=self._track_limpiar_historial).pack(side='left', padx=(0, 6))

        tk.Button(action_row, text="🗑️ Eliminar Seleccionados", bg=btn_color, fg=btn_fg,
                  font=('Segoe UI', 9, 'bold'), relief='flat', cursor='hand2',
                  padx=14, pady=5, bd=0,
                  command=self._track_delete_selected).pack(side='left')

        # Storage for bet checkboxes
        self._track_check_vars = []

        # Content area - scrollable frame for bets
        self._track_content = ScrollableFrame(self._tracking_frame, bg=p['bg'])
        self._track_content.grid(row=4, column=0, sticky='nsew')
        self._track_content.inner.grid_columnconfigure(0, weight=1)
        self._track_inner = self._track_content.inner

        # Load initial data
        self._track_filter_click("historico")

    def _track_filter_click(self, filtro):
        """Handle track record filter button click"""
        import tkinter as tk
        self._track_filtro.set(filtro)
        p = self._palette

        # Clear content
        for w in self._track_inner.winfo_children():
            w.destroy()

        try:
            historial = cargar_json('historial_predicciones.json') or []
        except Exception:
            historial = []

        historial = [pr for pr in historial if pr.get('sent_to_telegram', False)]

        # Sort by date descending (most recent first)
        historial.sort(key=lambda x: x.get('fecha', ''), reverse=True)

        if filtro == "pendientes":
            bets = [pr for pr in historial if pr.get("resultado_real") is None or pr.get("acierto") is None]
            titulo = "⏳ Apuestas Pendientes"
        elif filtro == "acertados":
            bets = [pr for pr in historial if pr.get("acierto") is True]
            titulo = "✅ Apuestas Acertadas"
        elif filtro == "fallados":
            bets = [pr for pr in historial if pr.get("acierto") is False]
            titulo = "❌ Apuestas Falladas"
        elif filtro == "por_fecha":
            f_ini = self._track_fecha_inicio.get()
            f_fin = self._track_fecha_fin.get()
            bets = [pr for pr in historial
                    if f_ini <= pr.get('fecha', '') <= f_fin]
            titulo = f"📅 Historial ({f_ini} a {f_fin})"
        else:
            bets = historial
            titulo = "📅 Historial Completo"

        tk.Label(self._track_inner, text=f"{titulo}  ({len(bets)} apuestas)",
                 bg=p['bg'], fg=p['fg'],
                 font=('Segoe UI', 13, 'bold')).grid(row=0, column=0, sticky='w', pady=(0, 10))

        if not bets:
            tk.Label(self._track_inner, text="No hay apuestas en esta categoria",
                     bg=p['bg'], fg=p['muted'],
                     font=('Segoe UI', 11)).grid(row=1, column=0, sticky='w', pady=10)
            return

        self._track_check_vars = []
        for i, bet in enumerate(bets):
            card = tk.Frame(self._track_inner, bg=p['card_bg'], padx=12, pady=10,
                            highlightbackground=p['card_border'], highlightthickness=1)
            card.grid(row=i + 1, column=0, sticky='ew', pady=3)
            card.grid_columnconfigure(2, weight=1)

            # Checkbox for selection (toggle button for reliable dark-theme support)
            var = tk.BooleanVar(value=False)
            self._track_check_vars.append((var, bet))
            chk_btn = tk.Button(card, text="☐", bg=p['card_bg'], fg=p['muted'],
                                font=('Segoe UI', 14), relief='flat', cursor='hand2',
                                bd=0, highlightthickness=0, width=2, padx=0)
            def make_toggle(v=var, b=chk_btn, palette=p):
                def toggle():
                    v.set(not v.get())
                    if v.get():
                        b.config(text="☑", fg=palette['primary'])
                    else:
                        b.config(text="☐", fg=palette['muted'])
                return toggle
            chk_btn.config(command=make_toggle())
            chk_btn.grid(row=0, column=0, rowspan=3, sticky='ns', padx=(0, 4))

            # Team/match name
            partido_text = bet.get('partido', 'N/A')
            tk.Label(card, text=partido_text, bg=p['card_bg'], fg=p['fg'],
                     font=('Segoe UI', 11, 'bold'), anchor='w').grid(
                row=0, column=1, columnspan=2, sticky='w')

            # Prediction + odds + stake
            pred_text = f"{bet.get('prediccion', 'N/A')}  |  Cuota: {bet.get('cuota', 'N/A')}  |  Stake: ${bet.get('stake', 'N/A')}"
            tk.Label(card, text=pred_text, bg=p['card_bg'], fg=p['muted'],
                     font=('Segoe UI', 9), anchor='w').grid(
                row=1, column=1, columnspan=2, sticky='w', pady=(2, 0))

            # Date
            fecha_text = f"📅 {bet.get('fecha', 'N/A')}"
            if bet.get('fecha_actualizacion'):
                fecha_text += f"  |  Actualizado: {bet.get('fecha_actualizacion', '')[:10]}"
            tk.Label(card, text=fecha_text, bg=p['card_bg'], fg=p['muted'],
                     font=('Segoe UI', 8), anchor='w').grid(
                row=2, column=1, columnspan=2, sticky='w', pady=(2, 0))

            # Result badge on right
            right = tk.Frame(card, bg=p['card_bg'])
            right.grid(row=0, column=3, rowspan=3, sticky='e', padx=(12, 0))

            resultado_real = bet.get('resultado_real')
            acierto = bet.get('acierto')
            if resultado_real is None:
                badge_bg, badge_fg = p['badge_mid_bg'], p['badge_mid_fg']
                badge_text = "⏳ Pendiente"
            elif acierto:
                badge_bg, badge_fg = p['badge_high_bg'], p['badge_high_fg']
                ganancia = bet.get('ganancia', 0)
                badge_text = f"✅ +${ganancia:.2f}" if isinstance(ganancia, (int, float)) else "✅ Ganada"
            else:
                badge_bg, badge_fg = p['badge_low_bg'], p['badge_low_fg']
                badge_text = "❌ Perdida"

            tk.Label(right, text=badge_text, bg=badge_bg, fg=badge_fg,
                     font=('Segoe UI', 9, 'bold'), padx=8, pady=2).pack(anchor='e')

    def _track_delete_selected(self):
        """Delete selected bets from track record"""
        from tkinter import messagebox
        selected = [(var, bet) for var, bet in self._track_check_vars if var.get()]
        if not selected:
            messagebox.showinfo("Info", "No hay predicciones seleccionadas para eliminar.")
            return
        n = len(selected)
        respuesta = messagebox.askyesno("Confirmar",
            f"¿Eliminar {n} prediccion{'es' if n > 1 else ''} seleccionada{'s' if n > 1 else ''}?")
        if respuesta:
            try:
                historial = cargar_json('historial_predicciones.json') or []
                bets_to_remove = [bet for _, bet in selected]
                new_hist = []
                removed_set = set()
                for pr in historial:
                    should_remove = False
                    for idx, bet in enumerate(bets_to_remove):
                        if idx not in removed_set:
                            if (pr.get('partido') == bet.get('partido')
                                    and pr.get('prediccion') == bet.get('prediccion')
                                    and pr.get('fecha') == bet.get('fecha')
                                    and pr.get('cuota') == bet.get('cuota')):
                                should_remove = True
                                removed_set.add(idx)
                                break
                    if not should_remove:
                        new_hist.append(pr)
                with open('historial_predicciones.json', 'w', encoding='utf-8') as f:
                    json.dump(new_hist, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Exito", f"{len(removed_set)} prediccion{'es' if len(removed_set) > 1 else ''} eliminada{'s' if len(removed_set) > 1 else ''}")
                self._track_filter_click(self._track_filtro.get())
            except Exception as e:
                messagebox.showerror("Error", f"Error eliminando: {e}")

    def _track_auto_update(self):
        """Auto-update pending results when entering Tracking page"""
        try:
            historial = cargar_json('historial_predicciones.json') or []
            pending = [p for p in historial if p.get('resultado_real') is None and p.get('sent_to_telegram', False)]
            if pending:
                self._track_actualizar_resultados(silent=True)
        except Exception:
            pass

    def _track_actualizar_resultados(self, silent=False):
        """Update track record results from API"""
        from tkinter import messagebox
        try:
            api_key = os.getenv('FOOTYSTATS_API_KEY')
            if not api_key:
                if not silent:
                    messagebox.showerror("Error", "FOOTYSTATS_API_KEY no encontrada en .env")
                return
            # Prevent multiple simultaneous updates
            if hasattr(self, '_track_updating') and self._track_updating:
                return
            self._track_updating = True
            tracker = TrackRecordManager(api_key)
            self._track_btn_actualizar.config(state='disabled', text="🔄 Actualizando...")

            def update_thread():
                try:
                    resultado = tracker.actualizar_historial_con_resultados(
                        max_matches=50, timeout_per_match=10)

                    def on_done():
                        try:
                            self._track_updating = False
                            acts = resultado.get('actualizaciones', 0)
                            errs = resultado.get('errores', 0)
                            if acts > 0:
                                self._track_btn_actualizar.config(text=f"✅ {acts} actualizadas")
                            elif errs > 0:
                                self._track_btn_actualizar.config(text=f"⚠️ {errs} sin resultado")
                            else:
                                self._track_btn_actualizar.config(text="✅ Todo al dia")
                            self.root.after(3000, lambda: self._track_btn_actualizar.config(
                                text="🔄 Actualizar Resultados", state='normal'))
                            self._track_filter_click(self._track_filtro.get())
                        except Exception:
                            self._track_updating = False
                            self._track_btn_actualizar.config(text="🔄 Actualizar Resultados", state='normal')

                    self.root.after(0, on_done)
                except Exception as e:
                    def on_error():
                        self._track_updating = False
                        self._track_btn_actualizar.config(text="❌ Error", state='normal')
                        self.root.after(2000, lambda: self._track_btn_actualizar.config(
                            text="🔄 Actualizar Resultados"))
                    self.root.after(0, on_error)

            threading.Thread(target=update_thread, daemon=True).start()
        except Exception as e:
            self._track_updating = False
            if not silent:
                messagebox.showerror("Error", f"Error: {e}")

    def _track_limpiar_historial(self):
        """Clear all track record history"""
        from tkinter import messagebox
        respuesta = messagebox.askyesno("Confirmar",
            "¿Limpiar todo el historial?\n\nEsta accion no se puede deshacer.")
        if respuesta:
            try:
                with open('historial_predicciones.json', 'w', encoding='utf-8') as f:
                    f.write('[]')
                messagebox.showinfo("Exito", "Historial limpiado")
                self._track_filter_click(self._track_filtro.get())
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")

    # ── Usuarios inline page builder ────────────────────────────

    def _build_usuarios_content(self, p):
        """Build usuarios management page inline - professional dark theme"""
        import tkinter as tk

        self._usuarios_frame.grid_rowconfigure(3, weight=1)
        self._usuarios_frame.grid_columnconfigure(0, weight=1)

        # Title row
        title_f = tk.Frame(self._usuarios_frame, bg=p['bg'])
        title_f.grid(row=0, column=0, sticky='ew', pady=(0, 16))
        tk.Label(title_f, text="Gestion de Usuarios",
                 bg=p['bg'], fg=p['fg'],
                 font=('Segoe UI', 16, 'bold')).pack(side='left')

        # KPI cards row
        kpi_row = tk.Frame(self._usuarios_frame, bg=p['bg'])
        kpi_row.grid(row=1, column=0, sticky='ew', pady=(0, 16))
        for c in range(5):
            kpi_row.grid_columnconfigure(c, weight=1, uniform='usr_kpi')

        usr_kpis = [
            ("usr_total",      "Total Usuarios",     "0",   "#3B82F6"),
            ("usr_premium",    "Premium Activos",    "0",   "#10B981"),
            ("usr_gratuitos",  "Gratuitos",          "0",   "#64748B"),
            ("usr_pct",        "Tasa Premium",       "0%",  "#F59E0B"),
            ("usr_recientes",  "Registros (7d)",     "0",   "#8B5CF6"),
        ]
        self._usr_kpi_labels = {}
        for col, (kid, label, val, accent) in enumerate(usr_kpis):
            card = tk.Frame(kpi_row, bg=p['card_bg'], padx=12, pady=10,
                            highlightbackground=accent, highlightthickness=2)
            card.grid(row=0, column=col, sticky='ew', padx=4)
            tk.Label(card, text=label, bg=p['card_bg'], fg=p['muted'],
                     font=('Segoe UI', 8)).pack(anchor='w')
            v_lbl = tk.Label(card, text=val, bg=p['card_bg'], fg=accent,
                             font=('Segoe UI', 16, 'bold'))
            v_lbl.pack(anchor='w')
            self._usr_kpi_labels[kid] = v_lbl

        # Action buttons row (above table)
        btns_f = tk.Frame(self._usuarios_frame, bg=p['bg'])
        btns_f.grid(row=2, column=0, sticky='ew', pady=(0, 8))

        btn_style = {'font': ('Segoe UI', 9, 'bold'), 'relief': 'flat',
                     'cursor': 'hand2', 'padx': 14, 'pady': 5, 'bd': 0}

        tk.Button(btns_f, text="Refrescar", bg=p['primary'], fg='#FFFFFF',
                  command=self._refresh_usuarios_inline, **btn_style).pack(side='left', padx=(0, 6))
        tk.Button(btns_f, text="Otorgar Acceso", bg='#10B981', fg='#FFFFFF',
                  command=self._usuarios_otorgar_acceso, **btn_style).pack(side='left', padx=(0, 6))
        tk.Button(btns_f, text="Banear", bg='#EF4444', fg='#FFFFFF',
                  command=self._usuarios_banear, **btn_style).pack(side='left', padx=(0, 6))
        tk.Button(btns_f, text="Limpiar Expirados", bg='#F59E0B', fg='#FFFFFF',
                  command=self._usuarios_limpiar_expirados, **btn_style).pack(side='left', padx=(0, 6))
        tk.Button(btns_f, text="Eliminar Seleccionados", bg='#7C3AED', fg='#FFFFFF',
                  command=self._usuarios_eliminar_seleccionados, **btn_style).pack(side='left')

        # Seleccionar todos checkbox
        self._usr_select_all_var = tk.BooleanVar(value=False)
        sel_all_cb = tk.Checkbutton(btns_f, text="Todos", variable=self._usr_select_all_var,
                                     bg=p['bg'], fg=p['fg'], selectcolor=p['card_bg'],
                                     activebackground=p['bg'], activeforeground=p['fg'],
                                     font=('Segoe UI', 9),
                                     command=self._usuarios_toggle_select_all)
        sel_all_cb.pack(side='right', padx=(12, 0))

        # Column layout: percentage-based widths
        # [checkbox, ID, Usuario, Nombre, Premium, Registro, Expira]
        self._usr_col_pcts = [0.03, 0.10, 0.18, 0.18, 0.08, 0.13, 0.30]

        # Table card — single container, pack layout (no grid gaps)
        table_card = tk.Frame(self._usuarios_frame, bg=p['card_bg'],
                               highlightbackground=p['card_border'], highlightthickness=1)
        table_card.grid(row=3, column=0, sticky='nsew')

        # Table header — use place for exact column positioning
        hdr_bg = '#1E293B' if p['bg'] == '#0F172A' else '#E2E8F0'
        hdr_fg = '#94A3B8' if p['bg'] == '#0F172A' else '#475569'
        header_row = tk.Frame(table_card, bg=hdr_bg, height=32)
        header_row.pack(fill='x')
        header_row.pack_propagate(False)

        col_headers = ["", "ID", "Usuario", "Nombre", "Premium", "Registro", "Expira"]
        anchors = ['center', 'center', 'w', 'w', 'center', 'center', 'center']
        rx = 0.0
        for text, anc, pct in zip(col_headers, anchors, self._usr_col_pcts):
            lbl = tk.Label(header_row, text=text, bg=hdr_bg, fg=hdr_fg,
                           font=('Segoe UI', 9, 'bold'), anchor=anc)
            lbl.place(relx=rx, rely=0, relwidth=pct, relheight=1.0)
            rx += pct

        # Scrollable body — canvas + scrollbar in a frame
        body_bg = p['card_bg']
        body_outer = tk.Frame(table_card, bg=body_bg)
        body_outer.pack(fill='both', expand=True)

        canvas = tk.Canvas(body_outer, bg=body_bg, highlightthickness=0, bd=0)
        canvas.pack(side='left', fill='both', expand=True)

        sb_y = tk.Scrollbar(body_outer, orient='vertical', command=canvas.yview)
        sb_y.pack(side='right', fill='y')
        canvas.configure(yscrollcommand=sb_y.set)

        self._usr_table_inner = tk.Frame(canvas, bg=body_bg)
        canvas.create_window((0, 0), window=self._usr_table_inner, anchor='nw', tags='inner')

        def _on_configure(e):
            canvas.configure(scrollregion=canvas.bbox('all'))
        self._usr_table_inner.bind('<Configure>', _on_configure)

        def _on_canvas_configure(e):
            canvas.itemconfig('inner', width=e.width)
        canvas.bind('<Configure>', _on_canvas_configure)

        # Mouse wheel scroll
        def _on_mousewheel(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), 'units')
        def _on_mousewheel_linux(e):
            if e.num == 4:
                canvas.yview_scroll(-1, 'units')
            elif e.num == 5:
                canvas.yview_scroll(1, 'units')
        canvas.bind('<MouseWheel>', _on_mousewheel)
        canvas.bind('<Button-4>', _on_mousewheel_linux)
        canvas.bind('<Button-5>', _on_mousewheel_linux)

        self._usr_table_canvas = canvas
        self._usr_checkboxes = {}
        self._usr_check_vars = {}

    def _refresh_usuarios_inline(self):
        """Refresh the inline usuarios table with dark themed rows"""
        import tkinter as tk
        try:
            from access_manager import access_manager
            if not access_manager or not hasattr(access_manager, 'listar_usuarios'):
                return
        except (ImportError, Exception):
            return

        p = self._palette

        try:
            usuarios = access_manager.listar_usuarios()

            # Clear existing rows
            for w in self._usr_table_inner.winfo_children():
                w.destroy()
            self._usr_check_vars.clear()
            self._usr_checkboxes.clear()
            self._usr_select_all_var.set(False)

            # Dark alternating stripes — both dark
            stripe_a = p['card_bg']
            stripe_b = '#162032' if p['bg'] == '#0F172A' else '#F1F5F9'
            row_height = 30
            pcts = self._usr_col_pcts
            anchors = ['center', 'center', 'w', 'w', 'center', 'center', 'center']

            if usuarios and isinstance(usuarios, (list, tuple)):
                for idx, usuario in enumerate(usuarios):
                    if not usuario or not isinstance(usuario, dict):
                        continue

                    user_id = str(usuario.get('user_id', 'N/A'))
                    username = usuario.get('username', 'N/A') or 'N/A'
                    first_name = usuario.get('first_name', 'N/A') or 'N/A'
                    is_premium = usuario.get('premium', False)
                    premium_text = "SI" if is_premium else "NO"
                    premium_fg = '#10B981' if is_premium else '#EF4444'

                    registro = '-'
                    if usuario.get('fecha_registro'):
                        try:
                            fecha_reg = datetime.fromisoformat(usuario['fecha_registro'])
                            registro = fecha_reg.strftime('%d/%m/%Y')
                        except Exception:
                            registro = '-'

                    expira = '-'
                    if usuario.get('fecha_expiracion'):
                        try:
                            fecha_exp = datetime.fromisoformat(usuario['fecha_expiracion'])
                            expira = fecha_exp.strftime('%d/%m/%Y %I:%M %p')
                        except Exception:
                            expira = '-'

                    row_bg = stripe_a if idx % 2 == 0 else stripe_b

                    # Row frame — pack fills width, fixed height, place for cols
                    row_f = tk.Frame(self._usr_table_inner, bg=row_bg, height=row_height)
                    row_f.pack(fill='x')
                    row_f.pack_propagate(False)

                    # Checkbox
                    var = tk.BooleanVar(value=False)
                    self._usr_check_vars[user_id] = var
                    cb = tk.Checkbutton(row_f, variable=var, text='',
                                         bg=row_bg, fg=p['fg'],
                                         activebackground=row_bg, activeforeground=p['fg'],
                                         selectcolor=row_bg, highlightthickness=0,
                                         bd=0, relief='flat', overrelief='flat',
                                         onvalue=True, offvalue=False)
                    cb.place(relx=0, rely=0, relwidth=pcts[0], relheight=1.0)
                    self._usr_checkboxes[user_id] = cb

                    # Data cells via place — exact same relx as header
                    cell_data = [
                        (user_id,      p['muted'], ('Segoe UI', 9)),
                        (username,     p['fg'],    ('Segoe UI', 9)),
                        (first_name,   p['fg'],    ('Segoe UI', 9)),
                        (premium_text, premium_fg, ('Segoe UI', 9, 'bold')),
                        (registro,     p['muted'], ('Segoe UI', 9)),
                        (expira,       p['fg'],    ('Segoe UI', 9)),
                    ]
                    rx = pcts[0]  # start after checkbox
                    for ci, (txt, fg, fnt) in enumerate(cell_data):
                        anc = anchors[ci + 1]
                        tk.Label(row_f, text=txt, bg=row_bg, fg=fg,
                                 font=fnt, anchor=anc, padx=4).place(
                            relx=rx, rely=0, relwidth=pcts[ci + 1], relheight=1.0)
                        rx += pcts[ci + 1]

            # Update KPI cards
            try:
                stats = access_manager.obtener_estadisticas()
                if stats and isinstance(stats, dict):
                    self._usr_kpi_labels['usr_total'].config(text=str(stats.get('total_usuarios', 0)))
                    self._usr_kpi_labels['usr_premium'].config(text=str(stats.get('usuarios_premium', 0)))
                    self._usr_kpi_labels['usr_gratuitos'].config(text=str(stats.get('usuarios_gratuitos', 0)))
                    self._usr_kpi_labels['usr_pct'].config(text=f"{stats.get('porcentaje_premium', 0):.1f}%")

                    # Count recent registrations (last 7 days)
                    recientes = 0
                    hoy = hora_bogota().date()
                    for u in usuarios:
                        if u.get('fecha_registro'):
                            try:
                                fr = datetime.fromisoformat(u['fecha_registro']).date()
                                if (hoy - fr).days <= 7:
                                    recientes += 1
                            except Exception:
                                pass
                    self._usr_kpi_labels['usr_recientes'].config(text=str(recientes))
            except Exception:
                pass

        except Exception:
            pass

    def _usuarios_toggle_select_all(self):
        """Toggle all checkboxes in the usuarios table"""
        val = self._usr_select_all_var.get()
        for var in self._usr_check_vars.values():
            var.set(val)

    def _usuarios_eliminar_seleccionados(self):
        """Delete selected users from the system"""
        from tkinter import messagebox
        try:
            from access_manager import access_manager
        except Exception:
            messagebox.showerror("Error", "Modulo access_manager no disponible")
            return

        selected_ids = [uid for uid, var in self._usr_check_vars.items() if var.get()]
        if not selected_ids:
            messagebox.showwarning("Seleccion", "Selecciona al menos un usuario para eliminar")
            return

        confirm = messagebox.askyesno("Confirmar eliminacion",
            f"Eliminar {len(selected_ids)} usuario(s)?\n\nEsta accion no se puede deshacer.")
        if confirm:
            try:
                count = access_manager.eliminar_usuarios_multiple(selected_ids)
                messagebox.showinfo("Eliminados", f"{count} usuario(s) eliminados")
                self._refresh_usuarios_inline()
            except Exception as e:
                messagebox.showerror("Error", f"Error eliminando usuarios: {e}")

    def _usuarios_otorgar_acceso(self):
        """Grant premium access to a user"""
        from tkinter import messagebox, simpledialog
        try:
            from access_manager import access_manager
        except Exception:
            messagebox.showerror("Error", "Modulo access_manager no disponible")
            return

        user_id = simpledialog.askstring("Otorgar Acceso", "Ingresa el ID del usuario:")
        if not user_id or not user_id.strip():
            return
        user_id = user_id.strip()
        dias = simpledialog.askinteger("Dias de Acceso",
                                        "¿Cuantos dias de acceso premium?",
                                        minvalue=1, maxvalue=365)
        if not dias:
            return
        try:
            if access_manager.otorgar_acceso(user_id, dias):
                try:
                    msg_conf = access_manager.generar_mensaje_confirmacion_premium(user_id)
                    chat_id = int(user_id) if user_id.lstrip('-').isdigit() else user_id
                    enviar_telegram(chat_id=chat_id, mensaje=msg_conf)
                except Exception:
                    pass
                messagebox.showinfo("Exito", f"✅ Acceso premium otorgado a {user_id} por {dias} dias")
                self._refresh_usuarios_inline()
            else:
                messagebox.showerror("Error", "❌ Usuario no encontrado")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")

    def _usuarios_banear(self):
        """Ban a user"""
        from tkinter import messagebox, simpledialog
        try:
            from access_manager import access_manager
        except Exception:
            messagebox.showerror("Error", "Modulo access_manager no disponible")
            return

        user_id = simpledialog.askstring("Banear Usuario", "Ingresa el ID del usuario a banear:")
        if not user_id:
            return
        confirm = messagebox.askyesno("Confirmar",
                                       f"¿Banear al usuario {user_id}?\nSe removera su acceso premium.")
        if confirm:
            try:
                if access_manager.banear_usuario(user_id):
                    messagebox.showinfo("Exito", "✅ Usuario baneado")
                    self._refresh_usuarios_inline()
                else:
                    messagebox.showerror("Error", "❌ Usuario no encontrado")
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")

    def _usuarios_limpiar_expirados(self):
        """Clean expired users"""
        from tkinter import messagebox
        try:
            from access_manager import access_manager
            count = access_manager.limpiar_usuarios_expirados()
            messagebox.showinfo("Limpieza", f"🧹 {count} usuarios expirados limpiados")
            self._refresh_usuarios_inline()
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")

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
        """Mostrar predicciones como tarjetas profesionales estilo dashboard"""
        self.limpiar_frame_predicciones()
        p = self._palette

        if not predicciones:
            return

        # Update stats
        confianzas = [pred.get('confianza', 0) for pred in predicciones if pred.get('confianza')]
        avg_conf = sum(confianzas) / len(confianzas) if confianzas else 0
        self._update_stats_display(num_pred=len(predicciones), avg_conf=avg_conf)

        # Update pick destacado in bottom bar
        if predicciones:
            best = predicciones[0]
            self._pick_dest_lbl.config(
                text=f"  {best['partido']}  -  {best['prediccion']}  @{best['cuota']}",
                fg=p['fg'])

        for i, pred in enumerate(predicciones, 1):
            self.predicciones_actuales.append(pred)

            card = tk.Frame(self.frame_predicciones, bg=p['card_bg'], padx=16, pady=14,
                            highlightbackground=p['card_border'], highlightthickness=1)
            card.grid(row=i, column=0, sticky='ew', pady=4)
            card.grid_columnconfigure(1, weight=1)

            # Checkbox
            var_cb = tk.BooleanVar()
            self.checkboxes_predicciones.append(var_cb)
            chk = ttk.Checkbutton(card, variable=var_cb, style='Card.TCheckbutton')
            chk.grid(row=0, column=0, rowspan=3, padx=(0, 12), sticky='n')

            # Team names + prediction type
            title_text = pred.get('partido', '')
            tk.Label(card, text=title_text, bg=p['card_bg'], fg=p['fg'],
                     font=('Segoe UI', 12, 'bold'), anchor='w').grid(
                row=0, column=1, sticky='w')

            pred_type = pred.get('prediccion', '')
            hora = pred.get('hora', '')
            sub_line = f"{pred_type}  -  {hora}"
            tk.Label(card, text=sub_line, bg=p['card_bg'], fg=p['muted'],
                     font=('Segoe UI', 9), anchor='w').grid(
                row=1, column=1, sticky='w', pady=(2, 0))

            # Reason
            razon = pred.get('razon', '')
            tk.Label(card, text=razon, bg=p['card_bg'], fg=p['muted'],
                     font=('Segoe UI', 9), anchor='w', wraplength=500,
                     justify='left').grid(row=2, column=1, sticky='w', pady=(4, 0))

            # Right side: confidence badge + odds + EV
            right = tk.Frame(card, bg=p['card_bg'])
            right.grid(row=0, column=2, rowspan=3, padx=(16, 0), sticky='e')

            # Confidence badge
            conf = pred.get('confianza', 0)
            if conf >= 80:
                badge_bg, badge_fg = p['badge_high_bg'], p['badge_high_fg']
            elif conf >= 60:
                badge_bg, badge_fg = p['badge_mid_bg'], p['badge_mid_fg']
            else:
                badge_bg, badge_fg = p['badge_low_bg'], p['badge_low_fg']

            conf_badge = tk.Label(right, text=f"  {conf}%  ", bg=badge_bg, fg=badge_fg,
                                  font=('Segoe UI', 11, 'bold'), padx=8, pady=2)
            conf_badge.pack(anchor='e')

            # Odds
            cuota = pred.get('cuota', '0')
            tk.Label(right, text=str(cuota), bg=p['card_bg'], fg=p['fg'],
                     font=('Segoe UI', 16, 'bold')).pack(anchor='e', pady=(4, 0))

            # EV
            ve = pred.get('valor_esperado', 0)
            ve_text = f"+{ve:.1%}" if isinstance(ve, (int, float)) and ve > 0 else f"{ve}"
            ve_fg = p['ev_pos'] if isinstance(ve, (int, float)) and ve > 0 else p['ev_neg']
            tk.Label(right, text=ve_text, bg=p['card_bg'], fg=ve_fg,
                     font=('Segoe UI', 9, 'bold')).pack(anchor='e')

            # Action buttons
            btns = tk.Frame(card, bg=p['card_bg'])
            btns.grid(row=0, column=3, rowspan=3, padx=(12, 0), sticky='e')
            tk.Button(btns, text="Ver Analisis", bg=p['secondary_bg'], fg=p['fg'],
                      font=('Segoe UI', 9), relief='flat', cursor='hand2', bd=0,
                      padx=10, pady=4).pack(pady=(0, 4))
            tk.Button(btns, text="Enviar", bg=p['primary'], fg='#FFFFFF',
                      font=('Segoe UI', 9, 'bold'), relief='flat', cursor='hand2',
                      bd=0, padx=10, pady=4,
                      command=lambda v=var_cb: (v.set(True), self.enviar_predicciones_seleccionadas())).pack()

            # Liga tag at bottom
            liga = pred.get('liga', '')
            if liga:
                tk.Label(card, text=liga, bg=p['card_border'], fg=p['muted'],
                         font=('Segoe UI', 8), padx=6, pady=1).grid(
                    row=3, column=1, sticky='w', pady=(6, 0))

    def mostrar_partidos_con_checkboxes(self, partidos_filtrados, liga_filtrada, fecha):
        """Mostrar partidos como tarjetas profesionales estilo dashboard"""
        self.limpiar_frame_partidos()
        p = self._palette

        if not partidos_filtrados:
            return

        # Update partidos stat
        try:
            self._stats_labels['partidos']['value'].config(text=str(len(partidos_filtrados)))
        except Exception:
            pass

        for i, partido in enumerate(partidos_filtrados, 1):
            self.partidos_actuales.append(partido)

            card = tk.Frame(self.frame_partidos, bg=p['card_bg'], padx=16, pady=14,
                            highlightbackground=p['card_border'], highlightthickness=1)
            card.grid(row=i, column=0, sticky='ew', pady=4)
            card.grid_columnconfigure(1, weight=1)

            # Checkbox
            var_cb = tk.BooleanVar()
            self.checkboxes_partidos.append(var_cb)
            chk = ttk.Checkbutton(card, variable=var_cb, style='Card.TCheckbutton')
            chk.grid(row=0, column=0, rowspan=2, padx=(0, 12), sticky='n')

            # Team names
            teams_text = f"{partido['local']}  vs  {partido['visitante']}"
            tk.Label(card, text=teams_text, bg=p['card_bg'], fg=p['fg'],
                     font=('Segoe UI', 12, 'bold'), anchor='w').grid(
                row=0, column=1, sticky='w')

            # Liga + hora
            hora = partido.get('hora', '')
            liga = partido.get('liga', '')
            sub_line = f"{liga}  |  {hora}"
            tk.Label(card, text=sub_line, bg=p['card_bg'], fg=p['muted'],
                     font=('Segoe UI', 9), anchor='w').grid(
                row=1, column=1, sticky='w', pady=(2, 0))

            # Odds display
            odds_f = tk.Frame(card, bg=p['card_bg'])
            odds_f.grid(row=0, column=2, rowspan=2, padx=(16, 0), sticky='e')

            cuotas = partido.get('cuotas', {})
            for label, key in [("1", 'local'), ("X", 'empate'), ("2", 'visitante')]:
                val = cuotas.get(key, '-')
                of = tk.Frame(odds_f, bg=p['odds_bg'], width=52, height=44,
                              highlightbackground=p['card_border'], highlightthickness=1)
                of.pack(side='left', padx=2)
                of.pack_propagate(False)
                tk.Label(of, text=label, bg=p['odds_bg'], fg=p['muted'],
                         font=('Segoe UI', 8)).pack(pady=(2, 0))
                tk.Label(of, text=str(val), bg=p['odds_bg'], fg=p['odds_fg'],
                         font=('Segoe UI', 10, 'bold')).pack()

            # Analyze button
            tk.Button(card, text="Analizar", bg=p['secondary_bg'], fg=p['fg'],
                      font=('Segoe UI', 9), relief='flat', cursor='hand2', bd=0,
                      padx=12, pady=4,
                      command=lambda pt=partido: self.analizar_partido_individual(pt)).grid(
                row=0, column=3, rowspan=2, padx=(12, 0), sticky='e')

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
            
            fecha = hora_bogota().strftime('%Y-%m-%d')
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
            
            fecha = hora_bogota().strftime('%Y-%m-%d')
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
            
            fecha = hora_bogota().strftime('%Y-%m-%d')
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
                    pred['fecha_envio_telegram'] = hora_bogota().isoformat()
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
            
            hoy = hora_bogota()
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
            
            scrollbar = ttk.Scrollbar(frame_principal, orient='vertical', command=tree.yview, style='Slim.Vertical.TScrollbar')
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
                scrollbar = ttk.Scrollbar(frame_principal, orient="vertical", command=canvas.yview, style='Slim.Vertical.TScrollbar')
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
                                    prediccion['fecha_actualizacion'] = hora_bogota().isoformat()
                                    
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
            
            scrollbar_y = ttk.Scrollbar(frame_table, orient='vertical', command=tree.yview, style='Slim.Vertical.TScrollbar')
            scrollbar_x = ttk.Scrollbar(frame_table, orient='horizontal', command=tree.xview, style='Slim.Horizontal.TScrollbar')
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
                                        expira = fecha_exp.strftime('%Y-%m-%d %I:%M %p')
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
