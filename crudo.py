import tkinter as tk
from footystats_api import obtener_partidos_del_dia
from tkinter import ttk, messagebox
from datetime import date, timedelta
from json_storage import guardar_json, cargar_json
from tkinter.scrolledtext import ScrolledText
import threading
import requests
import json
import os
import pygame
from telegram_utils import enviar_telegram, enviar_telegram_masivo
from telegram_bot_listener import iniciar_bot_en_hilo
from tkcalendar import DateEntry
from ia_bets import filtrar_apuestas_inteligentes, generar_mensaje_ia, simular_datos_prueba
from league_utils import detectar_liga_por_imagen

# CONFIG TELEGRAM
TELEGRAM_TOKEN = '8487580276:AAE9aa9dx3Vbbuq9OsKr_d-26mkNQ6csc0c'
TELEGRAM_CHAT_ID = '7659029315'


def cargar_partidos_reales(fecha):
    try:
        datos_api = obtener_partidos_del_dia(fecha)
        partidos = []

        if not datos_api:
            print(f"⚠️ No se obtuvieron datos de la API para {fecha}. Usando datos simulados.")
            return simular_datos_prueba()

        for partido in datos_api:
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
                    "visitante": str(partido.get("odds_ft_2", "4.00"))
                }
            })

        return partidos
    except Exception as e:
        print(f"❌ Error cargando partidos reales: {e}")
        print("🔄 Usando datos simulados como respaldo.")
        return simular_datos_prueba()

progreso_data = {"deposito": 100.0, "meta": 300.0, "saldo_actual": 100.0}
mensaje_telegram = ""
predicciones_actuales = []
checkboxes_predicciones = []
partidos_actuales = []
checkboxes_partidos = []



def guardar_datos_json(fecha):
    guardar_json("partidos.json", cargar_partidos_reales(fecha))
    guardar_json("progreso.json", progreso_data)


def buscar_en_hilo():
    threading.Thread(target=buscar).start()


def buscar(opcion_numero=1):
    global mensaje_telegram
    fecha = entry_fecha.get()
    output.delete('1.0', tk.END)

    ligas_disponibles.clear()
    
    from ia_bets import limpiar_cache_predicciones
    if opcion_numero == 1:
        limpiar_cache_predicciones()

    try:
        partidos = cargar_partidos_reales(fecha)
        
        for partido in partidos:
            liga = partido["liga"]
            ligas_disponibles.add(liga)

        actualizar_ligas()

        liga_filtrada = combo_ligas.get()
        if liga_filtrada not in ['Todas'] + sorted(list(ligas_disponibles)):
            combo_ligas.set('Todas')
            liga_filtrada = 'Todas'

        if liga_filtrada == 'Todas':
            partidos_filtrados = partidos
        else:
            partidos_filtrados = [p for p in partidos if p["liga"] == liga_filtrada]
        
        predicciones_ia = filtrar_apuestas_inteligentes(partidos_filtrados, opcion_numero)
        
        config = cargar_configuracion()
        odds_min = config.get("odds_min", 1.30)
        odds_max = config.get("odds_max", 1.60)
        output.insert(tk.END, f"🎯 Rango activo: {odds_min}–{odds_max}\n\n")
        
        titulo_extra = ""
        if opcion_numero == 2:
            titulo_extra = " - ALTERNATIVAS (2das OPCIONES)"
        
        mostrar_predicciones_con_checkboxes(predicciones_ia, liga_filtrada, titulo_extra)
        mostrar_partidos_con_checkboxes(partidos_filtrados, liga_filtrada, fecha)

        mensaje_telegram = generar_mensaje_ia(predicciones_ia, fecha)
        if liga_filtrada == 'Todas':
            mensaje_telegram += f"\n\n⚽ TODOS LOS PARTIDOS ({fecha})\n\n"
        else:
            mensaje_telegram += f"\n\n⚽ PARTIDOS - {liga_filtrada} ({fecha})\n\n"

        for liga in sorted(set(p["liga"] for p in partidos_filtrados)):
            if liga_filtrada != 'Todas' and liga_filtrada != liga:
                continue
            mensaje_telegram += f"🔷 {liga}\n"
            
            liga_partidos = [p for p in partidos_filtrados if p["liga"] == liga]
            for partido in liga_partidos:
                mensaje_telegram += f"🕒 {partido['hora']} - {partido['local']} vs {partido['visitante']}\n"
                mensaje_telegram += f"🏦 Casa: {partido['cuotas']['casa']} | 💰 Cuotas -> Local: {partido['cuotas']['local']}, Empate: {partido['cuotas']['empate']}, Visitante: {partido['cuotas']['visitante']}\n\n"

        guardar_datos_json(fecha)
        
    except Exception as e:
        error_msg = f"❌ Error al buscar partidos: {e}"
        output.insert(tk.END, error_msg)
        print(error_msg)
        messagebox.showerror("Error", f"Error al cargar partidos: {e}")

def actualizar_ligas():
    ligas = sorted(ligas_disponibles)
    combo_ligas['values'] = ['Todas'] + ligas
    if combo_ligas.get() not in combo_ligas['values']:
        combo_ligas.set('Todas')

def on_liga_changed(event=None):
    """Callback cuando se cambia la selección de liga"""
    if ligas_disponibles:  # Solo actualizar si hay datos cargados
        buscar()

def limpiar_frame_predicciones():
    """Limpiar el frame de predicciones y checkboxes"""
    for widget in frame_predicciones.winfo_children():
        widget.destroy()
    checkboxes_predicciones.clear()
    predicciones_actuales.clear()

def limpiar_frame_partidos():
    """Limpiar el frame de partidos y checkboxes"""
    for widget in frame_partidos.winfo_children():
        widget.destroy()
    checkboxes_partidos.clear()
    partidos_actuales.clear()

def mostrar_predicciones_con_checkboxes(predicciones, liga_filtrada, titulo_extra=""):
    """Mostrar predicciones con checkboxes para selección"""
    limpiar_frame_predicciones()
    
    if not predicciones:
        return
    
    titulo_frame = tk.Frame(frame_predicciones, bg="#34495e")
    titulo_frame.pack(fill='x', pady=2)
    
    titulo_text = "🤖 PREDICCIONES IA - SELECCIONA PICKS PARA ENVIAR"
    if liga_filtrada != 'Todas':
        titulo_text += f" - {liga_filtrada}"
    titulo_text += titulo_extra
    
    titulo_label = tk.Label(titulo_frame, text=titulo_text, bg="#34495e", fg="white", 
                           font=('Segoe UI', 10, 'bold'), pady=5)
    titulo_label.pack()
    
    for i, pred in enumerate(predicciones):
        predicciones_actuales.append(pred)
        
        pred_frame = tk.Frame(frame_predicciones, bg="#ecf0f1", relief='ridge', bd=1)
        pred_frame.pack(fill='x', pady=2, padx=5)
        
        var_checkbox = tk.BooleanVar()
        checkboxes_predicciones.append(var_checkbox)
        
        checkbox_frame = tk.Frame(pred_frame, bg="#ecf0f1")
        checkbox_frame.pack(fill='x', padx=5, pady=3)
        
        checkbox = tk.Checkbutton(checkbox_frame, variable=var_checkbox, bg="#ecf0f1")
        checkbox.pack(side=tk.LEFT)
        
        pred_text = f"🎯 PICK #{i+1}: {pred['prediccion']} | ⚽ {pred['partido']} | 💰 {pred['cuota']} | ⏰ {pred['hora']}"
        pred_label = tk.Label(checkbox_frame, text=pred_text, bg="#ecf0f1", 
                             font=('Segoe UI', 9), anchor='w')
        pred_label.pack(side=tk.LEFT, fill='x', expand=True, padx=5)
        
        justif_label = tk.Label(pred_frame, text=f"📝 {pred['razon']}", bg="#ecf0f1", 
                               font=('Segoe UI', 8), fg="#7f8c8d", anchor='w')
        justif_label.pack(fill='x', padx=25, pady=(0,3))

def mostrar_partidos_con_checkboxes(partidos_filtrados, liga_filtrada, fecha):
    """Mostrar partidos con checkboxes para selección - diseño unificado con Predicciones IA"""
    limpiar_frame_partidos()
    
    if not partidos_filtrados:
        return
    
    titulo_frame = tk.Frame(frame_partidos, bg="#34495e")
    titulo_frame.pack(fill='x', pady=2)
    
    titulo_text = f"🗓️ PARTIDOS PROGRAMADOS PARA LA JORNADA DEL: {fecha}"
    if liga_filtrada != 'Todas':
        titulo_text += f" - {liga_filtrada}"
    
    titulo_label = tk.Label(titulo_frame, text=titulo_text, bg="#34495e", fg="white", 
                           font=('Segoe UI', 10, 'bold'), pady=5)
    titulo_label.pack()
    
    for i, partido in enumerate(partidos_filtrados):
        partidos_actuales.append(partido)
        
        partido_frame = tk.Frame(frame_partidos, bg="#B2F0E8", relief='ridge', bd=1)
        partido_frame.pack(fill='x', pady=2, padx=5)
        
        var_checkbox = tk.BooleanVar()
        checkboxes_partidos.append(var_checkbox)
        
        # Frame del checkbox con el mismo layout que predicciones
        checkbox_frame = tk.Frame(partido_frame, bg="#B2F0E8")
        checkbox_frame.pack(fill='x', padx=5, pady=3)
        
        checkbox = tk.Checkbutton(checkbox_frame, variable=var_checkbox, bg="#B2F0E8")
        checkbox.pack(side=tk.LEFT)
        
        # Texto principal con el mismo formato que predicciones
        partido_text = f"⚽ PARTIDO #{i+1}: {partido['local']} vs {partido['visitante']} | ⏰ {partido['hora']} | 💰 {partido['cuotas']['local']}-{partido['cuotas']['empate']}-{partido['cuotas']['visitante']}"
        partido_label = tk.Label(checkbox_frame, text=partido_text, bg="#B2F0E8", 
                               font=('Segoe UI', 9), anchor='w')
        partido_label.pack(side=tk.LEFT, fill='x', expand=True, padx=5)
        
        # Información adicional con el mismo estilo que predicciones
        casa_label = tk.Label(partido_frame, text=f"🏠 Casa: {partido['cuotas']['casa']} | 🏆 Liga: {partido['liga']}", bg="#B2F0E8", 
                             font=('Segoe UI', 8), fg="#7f8c8d", anchor='w')
        casa_label.pack(fill='x', padx=25, pady=(0,3))

def reproducir_sonido_exito():
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

def enviar_predicciones_seleccionadas():
    """Enviar predicciones y/o partidos seleccionados a Telegram"""
    predicciones_seleccionadas = []
    partidos_seleccionados = []
    
    for i, var_checkbox in enumerate(checkboxes_predicciones):
        if var_checkbox.get():
            predicciones_seleccionadas.append(predicciones_actuales[i])
    
    for i, var_checkbox in enumerate(checkboxes_partidos):
        if var_checkbox.get():
            partidos_seleccionados.append(partidos_actuales[i])
    
    if not predicciones_seleccionadas and not partidos_seleccionados:
        messagebox.showwarning("Sin selección", "Selecciona al menos un pronóstico o partido para enviar.")
        return
    
    fecha = entry_fecha.get()
    mensaje_completo = ""
    
    try:
        if predicciones_seleccionadas:
            mensaje_predicciones = generar_mensaje_ia(predicciones_seleccionadas, fecha)
            mensaje_completo += mensaje_predicciones
            
            for pred in predicciones_seleccionadas:
                from ia_bets import guardar_prediccion_historica
                guardar_prediccion_historica(pred, fecha)
            
            with open("picks_seleccionados.json", "w", encoding="utf-8") as f:
                json.dump({"fecha": fecha, "predicciones": predicciones_seleccionadas}, f, ensure_ascii=False, indent=4)
            
            with open("picks_seleccionados.txt", "a", encoding="utf-8") as f:
                f.write(f"\n=== PICKS SELECCIONADOS {fecha} ===\n")
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
        
        resultado = enviar_telegram_masivo(mensaje_completo, TELEGRAM_TOKEN)
        if resultado["exito"]:
            reproducir_sonido_exito()
            
            total_items = len(predicciones_seleccionadas) + len(partidos_seleccionados)
            mensaje_resultado = f"✅ Se han enviado {total_items} elemento(s) seleccionado(s) a Telegram.\n\n"
            mensaje_resultado += f"📊 Estadísticas de envío:\n"
            mensaje_resultado += f"• Usuarios registrados: {resultado['total_usuarios']}\n"
            mensaje_resultado += f"• Enviados exitosos: {resultado['enviados_exitosos']}\n"
            if resultado.get('usuarios_bloqueados', 0) > 0:
                mensaje_resultado += f"• Usuarios que bloquearon el bot: {resultado['usuarios_bloqueados']}\n"
            if resultado.get('errores', 0) > 0:
                mensaje_resultado += f"• Errores: {resultado['errores']}\n"
            
            messagebox.showinfo("Enviado", mensaje_resultado)
            
            for var_checkbox in checkboxes_predicciones:
                var_checkbox.set(False)
            for var_checkbox in checkboxes_partidos:
                var_checkbox.set(False)
        else:
            error_msg = "No se pudieron enviar los elementos a Telegram."
            if resultado.get('detalles_errores'):
                error_msg += f"\n\nErrores:\n" + "\n".join(resultado['detalles_errores'][:3])
            messagebox.showerror("Error", error_msg)
            
    except Exception as e:
        messagebox.showerror("Error", f"Error enviando elementos seleccionados: {e}")




def enviar_alerta():
    if mensaje_telegram:
        try:
            resultado = enviar_telegram_masivo(mensaje_telegram, TELEGRAM_TOKEN)
            if resultado["exito"]:
                mensaje_resultado = f"✅ El mensaje se ha enviado a Telegram correctamente.\n\n"
                mensaje_resultado += f"📊 Estadísticas de envío:\n"
                mensaje_resultado += f"• Usuarios registrados: {resultado['total_usuarios']}\n"
                mensaje_resultado += f"• Enviados exitosos: {resultado['enviados_exitosos']}\n"
                if resultado.get('usuarios_bloqueados', 0) > 0:
                    mensaje_resultado += f"• Usuarios que bloquearon el bot: {resultado['usuarios_bloqueados']}\n"
                if resultado.get('errores', 0) > 0:
                    mensaje_resultado += f"• Errores: {resultado['errores']}\n"
                messagebox.showinfo("Enviado", mensaje_resultado)
            else:
                error_msg = "No se pudo enviar el mensaje a Telegram. Revisa la conexión."
                if resultado.get('detalles_errores'):
                    error_msg += f"\n\nErrores:\n" + "\n".join(resultado['detalles_errores'][:3])
                messagebox.showerror("Error", error_msg)
        except Exception as e:
            messagebox.showerror("Error", f"Error enviando a Telegram: {e}")
    else:
        messagebox.showwarning("Sin datos", "Debes buscar primero los partidos antes de enviar a Telegram.")


def abrir_progreso():
    def guardar_datos():
        try:
            deposito = float(entry_deposito.get())
            meta = float(entry_meta.get())
            saldo = float(entry_saldo.get())

            progreso_data["deposito"] = deposito
            progreso_data["meta"] = meta
            progreso_data["saldo_actual"] = saldo

            actualizar_barra()
            guardar_datos_json(entry_fecha.get())
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingresa valores numéricos válidos.")

    def actualizar_barra():
        progreso = (progreso_data["saldo_actual"] - progreso_data["deposito"]) / (progreso_data["meta"] - progreso_data["deposito"]) * 100
        progreso = max(0, min(progreso, 100))
        barra['value'] = progreso
        label_resultado.config(text=f"📈 Progreso: {progreso:.2f}%")

    ventana = tk.Toplevel(root)
    ventana.title("📊 Progreso del Usuario")
    ventana.geometry("400x300")
    ventana.configure(bg="#f1f3f4")

    ttk.Label(ventana, text="💵 Depósito inicial:").pack(pady=5)
    entry_deposito = ttk.Entry(ventana)
    entry_deposito.insert(0, str(progreso_data["deposito"]))
    entry_deposito.pack()

    ttk.Label(ventana, text="🎯 Meta objetivo:").pack(pady=5)
    entry_meta = ttk.Entry(ventana)
    entry_meta.insert(0, str(progreso_data["meta"]))
    entry_meta.pack()

    ttk.Label(ventana, text="📊 Saldo actual:").pack(pady=5)
    entry_saldo = ttk.Entry(ventana)
    entry_saldo.insert(0, str(progreso_data["saldo_actual"]))
    entry_saldo.pack()

    ttk.Button(ventana, text="✅ Guardar y calcular", command=guardar_datos).pack(pady=10)

    barra = ttk.Progressbar(ventana, length=300, mode='determinate')
    barra.pack(pady=10)

    label_resultado = ttk.Label(ventana, text="")
    label_resultado.pack()

    actualizar_barra()


def abrir_track_record():
    """Abre ventana de track record de predicciones con UI organizada"""
    try:
        from track_record import TrackRecordManager
        import os
        
        api_key = "ba2674c1de1595d6af7c099be1bcef8c915f9324f0c1f0f5ac926106d199dafd"
        tracker = TrackRecordManager(api_key)
        
        ventana_track = tk.Toplevel(root)
        ventana_track.title("📊 Track Record - BetGeniuX IA")
        ventana_track.geometry("900x700")
        ventana_track.configure(bg="#2c3e50")
        
        frame_principal = tk.Frame(ventana_track, bg="#2c3e50")
        frame_principal.pack(fill='both', expand=True, padx=20, pady=20)
        
        titulo = tk.Label(frame_principal, text="📊 TRACK RECORD DE PREDICCIONES", 
                         bg="#2c3e50", fg="white", font=('Segoe UI', 16, 'bold'))
        titulo.pack(pady=(0, 20))
        
        frame_acciones = tk.Frame(frame_principal, bg="#2c3e50")
        frame_acciones.pack(fill='x', pady=(0, 10))
        
        frame_visualizacion = tk.Frame(frame_principal, bg="#2c3e50")
        frame_visualizacion.pack(fill='x', pady=(0, 20))
        
        vista_actual = tk.StringVar(value="general")
        
        def actualizar_resultados():
            btn_actualizar.config(state='disabled', text="🔄 Procesando...")
            ventana_track.update()
            
            try:
                import time
                start_time = time.time()
                resultado = tracker.actualizar_historial_con_resultados()
                end_time = time.time()
                
                if "error" in resultado:
                    messagebox.showerror("Error", f"Error actualizando: {resultado['error']}")
                else:
                    mensaje = f"✅ Actualización completada en {end_time - start_time:.1f}s\n\n"
                    mensaje += f"📊 Predicciones actualizadas: {resultado['actualizaciones']}\n"
                    mensaje += f"🎯 Matches únicos procesados: {resultado.get('matches_procesados', 0)}\n"
                    mensaje += f"❌ Errores: {resultado['errores']}\n"
                    mensaje += f"⏳ Partidos incompletos: {resultado.get('partidos_incompletos', 0)}\n"
                    mensaje += f"🔧 Correcciones históricas: {resultado.get('correcciones_historicas', 0)}\n"
                    mensaje += f"📈 Total procesadas: {resultado['total_procesadas']}"
                    messagebox.showinfo("Actualización Completada", mensaje)
                    mostrar_vista_actual()
            finally:
                btn_actualizar.config(state='normal', text="🔄 Actualizar Resultados")
        
        def limpiar_historial():
            respuesta = messagebox.askyesno("Confirmar", 
                "¿Estás seguro de que quieres limpiar todo el historial de predicciones?\n\n" +
                "Esta acción no se puede deshacer.")
            
            if respuesta:
                try:
                    if os.path.exists('historial_predicciones.json'):
                        with open('historial_predicciones.json', 'w', encoding='utf-8') as f:
                            f.write('[]')
                        messagebox.showinfo("Éxito", "Historial limpiado correctamente")
                        mostrar_vista_actual()
                    else:
                        messagebox.showinfo("Info", "No hay historial para limpiar")
                except Exception as e:
                    messagebox.showerror("Error", f"Error limpiando historial: {e}")
        
        def mostrar_metricas_generales():
            vista_actual.set("general")
            mostrar_vista_actual()
        
        def mostrar_metricas_financieras():
            vista_actual.set("financieras")
            mostrar_vista_actual()
        
        def mostrar_rendimiento_tipos():
            vista_actual.set("tipos")
            mostrar_vista_actual()
        
        def mostrar_vista_actual():
            metricas = tracker.calcular_metricas_rendimiento()
            
            for widget in frame_resultados.winfo_children():
                widget.destroy()
            
            if "error" in metricas:
                error_label = tk.Label(frame_resultados, text=f"❌ {metricas['error']}", 
                                     bg="#ecf0f1", fg="red", font=('Segoe UI', 12))
                error_label.pack(pady=10)
                return
            
            if "mensaje" in metricas:
                mensaje_label = tk.Label(frame_resultados, text=f"ℹ️ {metricas['mensaje']}", 
                                       bg="#ecf0f1", fg="blue", font=('Segoe UI', 12))
                mensaje_label.pack(pady=10)
                return
            
            vista = vista_actual.get()
            
            if vista == "general":
                contenido = f"""
📈 MÉTRICAS GENERALES

• Total predicciones: {metricas['total_predicciones']}
• Predicciones resueltas: {metricas['predicciones_resueltas']}
• Aciertos: {metricas['aciertos']}
• Fallos: {metricas['predicciones_resueltas'] - metricas['aciertos']}
• Tasa de acierto: {metricas['tasa_acierto']:.1f}%

📊 ESTADO DEL SISTEMA:
• Predicciones pendientes: {metricas['total_predicciones'] - metricas['predicciones_resueltas']}
• Eficiencia de procesamiento: {(metricas['predicciones_resueltas'] / metricas['total_predicciones'] * 100):.1f}%
"""
            
            elif vista == "financieras":
                contenido = f"""
💰 MÉTRICAS FINANCIERAS

• Total apostado: ${metricas['total_apostado']:.2f}
• Ganancia total: ${metricas['total_ganancia']:.2f}
• Ganancia neta: ${metricas['total_ganancia'] - metricas['total_apostado']:.2f}
• ROI: {metricas['roi']:.2f}%
• Valor esperado promedio: {metricas['valor_esperado_promedio']:.3f}

📈 ANÁLISIS FINANCIERO:
• Stake promedio: ${metricas['total_apostado'] / max(metricas['predicciones_resueltas'], 1):.2f}
• Ganancia por predicción: ${metricas['total_ganancia'] / max(metricas['predicciones_resueltas'], 1):.2f}
"""
            
            elif vista == "tipos":
                contenido = "🎯 RENDIMIENTO POR TIPO DE APUESTA\n\n"
                
                if metricas.get('tipos_apuesta'):
                    for tipo, datos in metricas['tipos_apuesta'].items():
                        roi_tipo = ((datos['ganancia'] - datos['total'] * (datos['ganancia'] / max(datos['total'], 1))) / max(datos['total'], 1)) * 100
                        contenido += f"• {tipo}:\n"
                        contenido += f"  - Predicciones: {datos['total']}\n"
                        contenido += f"  - Aciertos: {datos['aciertos']} ({datos['win_rate']:.1f}%)\n"
                        contenido += f"  - Ganancia: ${datos['ganancia']:.2f}\n"
                        contenido += f"  - ROI: {roi_tipo:.1f}%\n\n"
                else:
                    contenido += "No hay datos de tipos de apuesta disponibles."
            
            metricas_label = tk.Label(frame_resultados, text=contenido, 
                                    bg="#ecf0f1", fg="#2c3e50", font=('Segoe UI', 11),
                                    justify='left', anchor='nw', padx=20, pady=20)
            metricas_label.pack(fill='both', expand=True, padx=10, pady=10)
        
        btn_actualizar = tk.Button(frame_acciones, text="🔄 Actualizar Resultados", 
                                  command=actualizar_resultados, bg="#3498db", fg="white",
                                  font=('Segoe UI', 10, 'bold'), padx=15, pady=5)
        btn_actualizar.pack(side='left', padx=(0, 10))
        
        btn_limpiar = tk.Button(frame_acciones, text="🧹 Limpiar Historial", 
                               command=limpiar_historial, bg="#e74c3c", fg="white",
                               font=('Segoe UI', 10, 'bold'), padx=15, pady=5)
        btn_limpiar.pack(side='left', padx=(0, 10))
        
        btn_general = tk.Button(frame_visualizacion, text="📈 Métricas Generales", 
                               command=mostrar_metricas_generales, bg="#27ae60", fg="white",
                               font=('Segoe UI', 10, 'bold'), padx=15, pady=5)
        btn_general.pack(side='left', padx=(0, 10))
        
        btn_financieras = tk.Button(frame_visualizacion, text="💰 Métricas Financieras", 
                                   command=mostrar_metricas_financieras, bg="#f39c12", fg="white",
                                   font=('Segoe UI', 10, 'bold'), padx=15, pady=5)
        btn_financieras.pack(side='left', padx=(0, 10))
        
        btn_tipos = tk.Button(frame_visualizacion, text="🎯 Rendimiento por Tipo", 
                             command=mostrar_rendimiento_tipos, bg="#9b59b6", fg="white",
                             font=('Segoe UI', 10, 'bold'), padx=15, pady=5)
        btn_tipos.pack(side='left')
        
        frame_categorias = tk.Frame(frame_principal, bg="#2c3e50")
        frame_categorias.pack(fill='x', pady=(10, 20))
        
        def mostrar_bets_por_categoria(categoria):
            try:
                with open('historial_predicciones.json', 'r', encoding='utf-8') as f:
                    historial = json.load(f)
            except:
                historial = []
            
            for widget in frame_resultados.winfo_children():
                widget.destroy()
            
            if categoria == "pendiente":
                bets_filtrados = [p for p in historial if p.get("resultado_real") is None or p.get("acierto") is None]
                titulo = "⏳ APUESTAS PENDIENTES"
                color_titulo = "#f39c12"
            elif categoria == "acertado":
                bets_filtrados = [p for p in historial if p.get("acierto") == True]
                titulo = "✅ APUESTAS ACERTADAS"
                color_titulo = "#27ae60"
            elif categoria == "fallado":
                bets_filtrados = [p for p in historial if p.get("acierto") == False]
                titulo = "❌ APUESTAS FALLADAS"
                color_titulo = "#e74c3c"
            else:
                return
            
            canvas = tk.Canvas(frame_resultados, bg="#ecf0f1")
            scrollbar = ttk.Scrollbar(frame_resultados, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg="#ecf0f1")
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            titulo_label = tk.Label(scrollable_frame, text=titulo, 
                                   bg="#ecf0f1", fg=color_titulo, font=('Segoe UI', 14, 'bold'))
            titulo_label.pack(pady=(10, 20))
            
            if not bets_filtrados:
                no_bets_label = tk.Label(scrollable_frame, text=f"No hay apuestas en esta categoría", 
                                        bg="#ecf0f1", fg="#7f8c8d", font=('Segoe UI', 12))
                no_bets_label.pack(pady=20)
            else:
                for i, bet in enumerate(bets_filtrados):
                    bet_frame = tk.Frame(scrollable_frame, bg="white", relief='ridge', bd=1)
                    bet_frame.pack(fill='x', pady=5, padx=10)
                    
                    partido_text = f"⚽ {bet.get('partido', 'N/A')}"
                    partido_label = tk.Label(bet_frame, text=partido_text, bg="white", 
                                           font=('Segoe UI', 11, 'bold'), anchor='w')
                    partido_label.pack(fill='x', padx=10, pady=(5, 0))
                    
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
                        if categoria == "acertado":
                            ganancia_text = f"💰 Ganancia: ${bet.get('ganancia', 0):.2f}"
                            ganancia_label = tk.Label(bet_frame, text=ganancia_text, bg="white", 
                                                    font=('Segoe UI', 10, 'bold'), fg="#27ae60", anchor='w')
                            ganancia_label.pack(fill='x', padx=10, pady=(0, 5))
                        elif categoria == "fallado":
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
            
            count_text = f" ({len(bets_filtrados)} apuestas)"
            titulo_label.config(text=titulo + count_text)
        
        btn_pendientes = tk.Button(frame_categorias, text="⏳ Pendientes", 
                                  command=lambda: mostrar_bets_por_categoria("pendiente"), 
                                  bg="#f39c12", fg="white", font=('Segoe UI', 10, 'bold'), padx=15, pady=5)
        btn_pendientes.pack(side='left', padx=(0, 10))
        
        btn_acertados = tk.Button(frame_categorias, text="✅ Acertados", 
                                 command=lambda: mostrar_bets_por_categoria("acertado"), 
                                 bg="#27ae60", fg="white", font=('Segoe UI', 10, 'bold'), padx=15, pady=5)
        btn_acertados.pack(side='left', padx=(0, 10))
        
        btn_fallados = tk.Button(frame_categorias, text="❌ Fallados", 
                                command=lambda: mostrar_bets_por_categoria("fallado"), 
                                bg="#e74c3c", fg="white", font=('Segoe UI', 10, 'bold'), padx=15, pady=5)
        btn_fallados.pack(side='left')
        
        frame_resultados = tk.Frame(frame_principal, bg="#ecf0f1", relief='ridge', bd=2)
        frame_resultados.pack(fill='both', expand=True)
        
        mostrar_vista_actual()
        
    except Exception as e:
        messagebox.showerror("Error", f"Error abriendo track record: {e}")

def abrir_usuarios():
    """Abrir ventana para mostrar usuarios registrados de Telegram"""
    ventana_usuarios = tk.Toplevel(root)
    ventana_usuarios.title("👥 Usuarios Registrados - BetGeniuX")
    ventana_usuarios.geometry("700x500")
    ventana_usuarios.configure(bg="#f1f3f4")
    
    frame_header = tk.Frame(ventana_usuarios, bg="#f1f3f4")
    frame_header.pack(fill=tk.X, padx=10, pady=10)
    
    usuarios_data = []
    total_usuarios = 0
    
    try:
        if os.path.exists('usuarios.txt'):
            with open('usuarios.txt', 'r', encoding='utf-8') as f:
                for linea in f:
                    if linea.strip() and ' - ' in linea:
                        partes = linea.strip().split(' - ')
                        if len(partes) >= 3:
                            usuarios_data.append({
                                'user_id': partes[0],
                                'username': partes[1],
                                'first_name': partes[2]
                            })
                            total_usuarios += 1
    except Exception as e:
        print(f"Error leyendo usuarios.txt: {e}")
    
    titulo_text = f"👥 Usuarios Registrados en Telegram ({total_usuarios} usuarios)"
    label_titulo = tk.Label(frame_header, text=titulo_text, 
                           font=("Segoe UI", 14, "bold"), bg="#f1f3f4", fg="#333")
    label_titulo.pack()
    
    frame_lista = tk.Frame(ventana_usuarios, bg="#f1f3f4")
    frame_lista.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    from tkinter import scrolledtext
    texto_usuarios = scrolledtext.ScrolledText(frame_lista, 
                                              font=("Courier", 10),
                                              bg="white", 
                                              fg="#333",
                                              wrap=tk.WORD,
                                              state=tk.NORMAL)
    texto_usuarios.pack(fill=tk.BOTH, expand=True)
    
    if usuarios_data:
        texto_usuarios.insert(tk.END, "ID de Usuario       | Username           | Nombre\n")
        texto_usuarios.insert(tk.END, "-" * 65 + "\n")
        
        for usuario in usuarios_data:
            user_id = usuario['user_id'].ljust(16)
            username = usuario['username'].ljust(18)
            first_name = usuario['first_name']
            
            linea = f"{user_id} | {username} | {first_name}\n"
            texto_usuarios.insert(tk.END, linea)
    else:
        texto_usuarios.insert(tk.END, "📭 No hay usuarios registrados aún.\n\n")
        texto_usuarios.insert(tk.END, "Los usuarios se registrarán automáticamente cuando:\n")
        texto_usuarios.insert(tk.END, "• Envíen /start al bot de Telegram\n")
        texto_usuarios.insert(tk.END, "• Envíen cualquier mensaje al bot\n\n")
        texto_usuarios.insert(tk.END, "Asegúrate de que el bot esté ejecutándose:\n")
        texto_usuarios.insert(tk.END, "python run_telegram_bot.py")
    
    texto_usuarios.config(state=tk.DISABLED)
    
    btn_refrescar = ttk.Button(ventana_usuarios, text="🔄 Refrescar Lista", 
                              command=lambda: refrescar_usuarios(texto_usuarios, frame_header))
    btn_refrescar.pack(pady=10)


def refrescar_usuarios(texto_widget, header_frame):
    """Refrescar la lista de usuarios"""
    usuarios_data = []
    total_usuarios = 0
    
    try:
        if os.path.exists('usuarios.txt'):
            with open('usuarios.txt', 'r', encoding='utf-8') as f:
                for linea in f:
                    if linea.strip() and ' - ' in linea:
                        partes = linea.strip().split(' - ')
                        if len(partes) >= 3:
                            usuarios_data.append({
                                'user_id': partes[0],
                                'username': partes[1],
                                'first_name': partes[2]
                            })
                            total_usuarios += 1
    except Exception as e:
        print(f"Error leyendo usuarios.txt: {e}")
    
    for widget in header_frame.winfo_children():
        if isinstance(widget, tk.Label):
            titulo_text = f"👥 Usuarios Registrados en Telegram ({total_usuarios} usuarios)"
            widget.config(text=titulo_text)
    
    texto_widget.config(state=tk.NORMAL)
    texto_widget.delete(1.0, tk.END)
    
    if usuarios_data:
        texto_widget.insert(tk.END, "ID de Usuario       | Username           | Nombre\n")
        texto_widget.insert(tk.END, "-" * 65 + "\n")
        
        for usuario in usuarios_data:
            user_id = usuario['user_id'].ljust(16)
            username = usuario['username'].ljust(18)
            first_name = usuario['first_name']
            
            linea = f"{user_id} | {username} | {first_name}\n"
            texto_widget.insert(tk.END, linea)
    else:
        texto_widget.insert(tk.END, "📭 No hay usuarios registrados aún.\n\n")
        texto_widget.insert(tk.END, "Los usuarios se registrarán automáticamente cuando:\n")
        texto_widget.insert(tk.END, "• Envíen /start al bot de Telegram\n")
        texto_widget.insert(tk.END, "• Envíen cualquier mensaje al bot\n\n")
        texto_widget.insert(tk.END, "Asegúrate de que el bot esté ejecutándose:\n")
        texto_widget.insert(tk.END, "python run_telegram_bot.py")
    
    texto_widget.config(state=tk.DISABLED)


def abrir_pronostico():
    def enviar_pick():
        liga = entry_liga.get()
        local = entry_local.get()
        visitante = entry_visitante.get()
        pronostico = entry_pronostico.get()
        cuota = entry_cuota.get()
        stake = entry_stake.get()
        hora = entry_hora.get()
        justificacion = entry_justificacion.get()
        fecha = date.today().strftime('%Y-%m-%d')

        mensaje = (
            f"⚡️ PICK AVANZADO IA {fecha} ⚡️\n\n"
            f"🏆 {liga}\n"
            f"{local} 🆚 {visitante}\n\n"
            f"💥 {pronostico}\n"
            f"📝 {justificacion}\n\n"
            f"💰 Cuota: {cuota} | Stake {stake}u | {hora} ⏰\n"
            f"🧠 Análisis probabilístico IA"
        )

        try:
            from ia_bets import guardar_prediccion_historica
            prediccion_data = {
                "partido": f"{local} vs {visitante}",
                "liga": liga,
                "prediccion": pronostico,
                "cuota": float(cuota) if cuota else 0,
                "stake_recomendado": int(stake) if stake else 1,
                "valor_esperado": 0,
                "confianza": 0
            }
            guardar_prediccion_historica(prediccion_data, fecha)

            with open("ultimo_pick.json", "w", encoding="utf-8") as f:
                json.dump({"mensaje": mensaje}, f, ensure_ascii=False, indent=4)

            with open("registro_pronosticos.txt", "a", encoding="utf-8") as f:
                f.write(f"{fecha} | {local} vs {visitante} | {pronostico} | {cuota} | {justificacion}\n")

            resultado = enviar_telegram_masivo(mensaje, TELEGRAM_TOKEN)
            if resultado["exito"]:
                mensaje_resultado = f"✅ El pronóstico avanzado se ha enviado correctamente.\n\n"
                mensaje_resultado += f"📊 Estadísticas de envío:\n"
                mensaje_resultado += f"• Usuarios registrados: {resultado['total_usuarios']}\n"
                mensaje_resultado += f"• Enviados exitosos: {resultado['enviados_exitosos']}\n"
                if resultado.get('usuarios_bloqueados', 0) > 0:
                    mensaje_resultado += f"• Usuarios que bloquearon el bot: {resultado['usuarios_bloqueados']}\n"
                if resultado.get('errores', 0) > 0:
                    mensaje_resultado += f"• Errores: {resultado['errores']}\n"
                messagebox.showinfo("Enviado", mensaje_resultado)
                ventana.destroy()
            else:
                messagebox.showerror("Error", "No se pudo enviar el pronóstico a Telegram.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo enviar el pronóstico: {e}")

    ventana = tk.Toplevel(root)
    ventana.title("📌 Enviar Pronóstico del Día")
    ventana.geometry("400x450")
    ventana.configure(bg="#f1f3f4")

    campos = [
        ("🏆 Liga", ""),
        ("🏠 Local", ""),
        ("🛡️ Visitante", ""),
        ("🔮 Pronóstico", ""),
        ("💰 Cuota", ""),
        ("♻️ Stake", ""),
        ("⏰ Hora", ""),
        ("📝 Justificación", "")
    ]

    entries = []
    for texto, valor in campos:
        ttk.Label(ventana, text=texto).pack(pady=2)
        entry = ttk.Entry(ventana)
        entry.insert(0, valor)
        entry.pack()
        entries.append(entry)

    entry_liga, entry_local, entry_visitante, entry_pronostico, entry_cuota, entry_stake, entry_hora, entry_justificacion = entries

    ttk.Button(ventana, text="📤 Enviar Pronóstico", command=enviar_pick).pack(pady=15)


def cargar_configuracion():
    """Carga la configuración desde config_app.json"""
    config = cargar_json("config_app.json")
    if config is None:
        config = {"odds_min": 1.30, "odds_max": 1.60}
        guardar_json("config_app.json", config)
    return config

def guardar_configuracion(config):
    """Guarda la configuración en config_app.json"""
    guardar_json("config_app.json", config)

def abrir_ajustes():
    """Abrir ventana de ajustes"""
    ventana_ajustes = tk.Toplevel(root)
    ventana_ajustes.title("⚙️ Ajustes - Filtros de Cuotas")
    ventana_ajustes.geometry("400x300")
    ventana_ajustes.configure(bg="#f1f3f4")
    ventana_ajustes.resizable(False, False)
    
    config = cargar_configuracion()
    
    frame_main = tk.Frame(ventana_ajustes, bg="#f1f3f4")
    frame_main.pack(pady=20, padx=20, fill='both', expand=True)
    
    ttk.Label(frame_main, text="⚙️ Configuración de Filtros de Cuotas", font=('Segoe UI', 12, 'bold')).pack(pady=(0, 20))
    
    frame_min = tk.Frame(frame_main, bg="#f1f3f4")
    frame_min.pack(pady=10, fill='x')
    
    ttk.Label(frame_min, text="Cuota mínima:", font=('Segoe UI', 10)).pack(side=tk.LEFT)
    entry_min = tk.Entry(frame_min, font=('Segoe UI', 10), width=10)
    entry_min.pack(side=tk.RIGHT)
    entry_min.insert(0, str(config.get("odds_min", 1.30)))
    
    frame_max = tk.Frame(frame_main, bg="#f1f3f4")
    frame_max.pack(pady=10, fill='x')
    
    ttk.Label(frame_max, text="Cuota máxima:", font=('Segoe UI', 10)).pack(side=tk.LEFT)
    entry_max = tk.Entry(frame_max, font=('Segoe UI', 10), width=10)
    entry_max.pack(side=tk.RIGHT)
    entry_max.insert(0, str(config.get("odds_max", 1.60)))
    
    frame_info = tk.Frame(frame_main, bg="#f1f3f4")
    frame_info.pack(pady=20, fill='x')
    
    info_text = "ℹ️ Formato: Decimal EU\n📊 Límite mínimo técnico: 1.01\n🎯 Solo se mostrarán apuestas en el rango seleccionado"
    ttk.Label(frame_info, text=info_text, font=('Segoe UI', 9), foreground='#666666').pack()
    
    def guardar_ajustes():
        try:
            odds_min = float(entry_min.get())
            odds_max = float(entry_max.get())
            
            if odds_min < 1.01:
                messagebox.showerror("Error", "La cuota mínima debe ser al menos 1.01")
                return
            
            if odds_max < odds_min:
                messagebox.showerror("Error", "La cuota máxima debe ser mayor o igual a la mínima")
                return
            
            nueva_config = {"odds_min": odds_min, "odds_max": odds_max}
            guardar_configuracion(nueva_config)
            
            messagebox.showinfo("Éxito", "Configuración guardada correctamente")
            ventana_ajustes.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Por favor ingresa valores numéricos válidos")
    
    frame_botones = tk.Frame(frame_main, bg="#f1f3f4")
    frame_botones.pack(pady=20)
    
    ttk.Button(frame_botones, text="💾 Guardar", command=guardar_ajustes).pack(side=tk.LEFT, padx=5)
    ttk.Button(frame_botones, text="❌ Cancelar", command=ventana_ajustes.destroy).pack(side=tk.LEFT, padx=5)

# --- Interfaz ---
root = tk.Tk()
root.title("🧐 BetGeniuX v.1 – Cuotas de Partidos (Reales)")
root.geometry("800x600")
root.minsize(800, 600)
root.state('zoomed')  # Maximizar ventana en Windows
root.configure(bg="#f1f3f4")

style = ttk.Style()
style.configure('TLabel', font=('Segoe UI', 10))
style.configure('TButton', font=('Segoe UI', 10, 'bold'))
style.configure('TCombobox', font=('Segoe UI', 10))

notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True, padx=10, pady=10)

tab_principal = tk.Frame(notebook, bg="#f1f3f4")
notebook.add(tab_principal, text="🏠 Principal")

tab_ajustes = tk.Frame(notebook, bg="#f1f3f4")
notebook.add(tab_ajustes, text="⚙️ Ajustes")

frame_top = tk.Frame(tab_principal, bg="#f1f3f4")
frame_top.pack(pady=15)

label_fecha = ttk.Label(frame_top, text="📅 Fecha:")
label_fecha.pack(side=tk.LEFT)

entry_fecha = DateEntry(frame_top, width=12, background="darkblue", foreground="white", borderwidth=2, date_pattern='yyyy-MM-dd', showothermonthdays=False, showweeknumbers=False)
entry_fecha.pack(side=tk.LEFT, padx=5)

label_liga = ttk.Label(frame_top, text="🏆 Liga:")
label_liga.pack(side=tk.LEFT, padx=10)

combo_ligas = ttk.Combobox(frame_top, state='readonly', width=30)
combo_ligas.pack(side=tk.LEFT)
combo_ligas.set('Todas')
combo_ligas.bind('<<ComboboxSelected>>', on_liga_changed)

btn_buscar = ttk.Button(frame_top, text="🔍 Buscar", command=buscar_en_hilo)
btn_buscar.pack(side=tk.LEFT, padx=5)

def regenerar_en_hilo():
    threading.Thread(target=lambda: buscar(opcion_numero=2)).start()

btn_regenerar = ttk.Button(frame_top, text="🔄 Regenerar", command=regenerar_en_hilo)
btn_regenerar.pack(side=tk.LEFT, padx=2)

btn_progreso = ttk.Button(frame_top, text="📊 Progreso", command=abrir_progreso)
btn_progreso.pack(side=tk.LEFT, padx=5)

btn_enviar = ttk.Button(frame_top, text="📢 Enviar a Telegram", command=enviar_alerta)
btn_enviar.pack(side=tk.LEFT, padx=5)

btn_pronostico = ttk.Button(frame_top, text="📌 Enviar Pronóstico Seleccionado", command=enviar_predicciones_seleccionadas)
btn_pronostico.pack(side=tk.LEFT, padx=5)

btn_track_record = ttk.Button(frame_top, text="📊 Track Record", command=abrir_track_record)
btn_track_record.pack(side=tk.LEFT, padx=5)

btn_usuarios = ttk.Button(frame_top, text="👥 Users", command=abrir_usuarios)
btn_usuarios.pack(side=tk.LEFT, padx=5)

frame_predicciones = tk.Frame(tab_principal, bg="#f1f3f4")
frame_predicciones.pack(pady=5, padx=10, fill='x')

frame_partidos = tk.Frame(tab_principal, bg="#f1f3f4")
frame_partidos.pack(pady=5, padx=10, fill='x')

output = ScrolledText(tab_principal, wrap=tk.WORD, width=95, height=25, font=('Arial', 9), bg='#B2F0E8')
output.pack(pady=10, padx=10, expand=True, fill='both')

frame_ajustes_content = tk.Frame(tab_ajustes, bg="#f1f3f4")
frame_ajustes_content.pack(pady=50, padx=50, fill='both', expand=True)

ttk.Label(frame_ajustes_content, text="⚙️ Configuración de Filtros de Cuotas", font=('Segoe UI', 14, 'bold')).pack(pady=(0, 30))

config_actual = cargar_configuracion()

frame_min_tab = tk.Frame(frame_ajustes_content, bg="#f1f3f4")
frame_min_tab.pack(pady=15, fill='x')

ttk.Label(frame_min_tab, text="Cuota mínima:", font=('Segoe UI', 12)).pack(side=tk.LEFT)
entry_min_tab = tk.Entry(frame_min_tab, font=('Segoe UI', 12), width=15)
entry_min_tab.pack(side=tk.RIGHT)
entry_min_tab.insert(0, str(config_actual.get("odds_min", 1.30)))

frame_max_tab = tk.Frame(frame_ajustes_content, bg="#f1f3f4")
frame_max_tab.pack(pady=15, fill='x')

ttk.Label(frame_max_tab, text="Cuota máxima:", font=('Segoe UI', 12)).pack(side=tk.LEFT)
entry_max_tab = tk.Entry(frame_max_tab, font=('Segoe UI', 12), width=15)
entry_max_tab.pack(side=tk.RIGHT)
entry_max_tab.insert(0, str(config_actual.get("odds_max", 1.60)))

frame_info_tab = tk.Frame(frame_ajustes_content, bg="#f1f3f4")
frame_info_tab.pack(pady=30, fill='x')

info_text_tab = "ℹ️ Formato: Decimal EU\n📊 Límite mínimo técnico: 1.01\n🎯 Solo se mostrarán apuestas en el rango seleccionado"
ttk.Label(frame_info_tab, text=info_text_tab, font=('Segoe UI', 10), foreground='#666666').pack()

def guardar_ajustes_tab():
    try:
        odds_min = float(entry_min_tab.get())
        odds_max = float(entry_max_tab.get())
        
        if odds_min < 1.01:
            messagebox.showerror("Error", "La cuota mínima debe ser al menos 1.01")
            return
        
        if odds_max < odds_min:
            messagebox.showerror("Error", "La cuota máxima debe ser mayor o igual a la mínima")
            return
        
        nueva_config = {"odds_min": odds_min, "odds_max": odds_max}
        guardar_configuracion(nueva_config)
        
        messagebox.showinfo("Éxito", "Configuración guardada correctamente")
        
    except ValueError:
        messagebox.showerror("Error", "Por favor ingresa valores numéricos válidos")

frame_boton_tab = tk.Frame(frame_ajustes_content, bg="#f1f3f4")
frame_boton_tab.pack(pady=30)

ttk.Button(frame_boton_tab, text="💾 Guardar", command=guardar_ajustes_tab).pack()

ligas_disponibles = set()

try:
    print("🤖 Iniciando bot de Telegram integrado...")
    hilo_bot = iniciar_bot_en_hilo()
    print("✅ Bot de Telegram iniciado correctamente en segundo plano")
except Exception as e:
    print(f"⚠️ Error iniciando bot de Telegram: {e}")
    print("📱 La aplicación continuará funcionando sin el bot")

root.mainloop()
