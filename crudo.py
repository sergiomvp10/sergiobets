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
from telegram_utils import enviar_telegram
from tkcalendar import DateEntry
from ia_bets import filtrar_apuestas_inteligentes, generar_mensaje_ia, simular_datos_prueba
from league_utils import detectar_liga_por_imagen

# CONFIG TELEGRAM
TELEGRAM_TOKEN = '7069280342:AAEeDTrSpvZliMXlqcwUv16O5_KkfCqzZ8A'
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



def guardar_datos_json(fecha):
    guardar_json("partidos.json", cargar_partidos_reales(fecha))
    guardar_json("progreso.json", progreso_data)


def buscar_en_hilo():
    threading.Thread(target=buscar).start()


def buscar():
    global mensaje_telegram
    fecha = entry_fecha.get()
    output.delete('1.0', tk.END)
    output.insert(tk.END, f"📅 Partidos programados para la jornada del: {fecha}\n\n")

    ligas_disponibles.clear()
    partidos_por_liga = {}

    try:
        partidos = cargar_partidos_reales(fecha)
        
        for partido in partidos:
            liga = partido["liga"]
            ligas_disponibles.add(liga)

            info = f"🕒 {partido['hora']} - {partido['local']} vs {partido['visitante']}\n"
            info += f"🏦 Casa: {partido['cuotas']['casa']} | 💰 Cuotas -> Local: {partido['cuotas']['local']}, Empate: {partido['cuotas']['empate']}, Visitante: {partido['cuotas']['visitante']}\n\n"

            if liga not in partidos_por_liga:
                partidos_por_liga[liga] = []
            partidos_por_liga[liga].append(info)

        actualizar_ligas()

        liga_filtrada = combo_ligas.get()
        if liga_filtrada not in ['Todas'] + sorted(list(ligas_disponibles)):
            combo_ligas.set('Todas')
            liga_filtrada = 'Todas'

        if liga_filtrada == 'Todas':
            partidos_filtrados = partidos
        else:
            partidos_filtrados = [p for p in partidos if p["liga"] == liga_filtrada]
        
        predicciones_ia = filtrar_apuestas_inteligentes(partidos_filtrados)
        
        mostrar_predicciones_con_checkboxes(predicciones_ia, liga_filtrada)

        mensaje_telegram = generar_mensaje_ia(predicciones_ia, fecha)
        if liga_filtrada == 'Todas':
            mensaje_telegram += f"\n\n⚽ TODOS LOS PARTIDOS ({fecha})\n\n"
        else:
            mensaje_telegram += f"\n\n⚽ PARTIDOS - {liga_filtrada} ({fecha})\n\n"

        for liga in sorted(partidos_por_liga.keys()):
            if liga_filtrada != 'Todas' and liga_filtrada != liga:
                continue
            output.insert(tk.END, f"🔷 {liga}\n")
            mensaje_telegram += f"🔷 {liga}\n"
            for info in partidos_por_liga[liga]:
                output.insert(tk.END, info)
                mensaje_telegram += info

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

def mostrar_predicciones_con_checkboxes(predicciones, liga_filtrada):
    """Mostrar predicciones con checkboxes para selección"""
    limpiar_frame_predicciones()
    
    if not predicciones:
        return
    
    titulo_frame = tk.Frame(frame_predicciones, bg="#34495e")
    titulo_frame.pack(fill='x', pady=2)
    
    titulo_text = "🤖 PREDICCIONES IA - SELECCIONA PICKS PARA ENVIAR"
    if liga_filtrada != 'Todas':
        titulo_text += f" - {liga_filtrada}"
    
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

def enviar_predicciones_seleccionadas():
    """Enviar solo las predicciones seleccionadas a Telegram"""
    predicciones_seleccionadas = []
    
    for i, var_checkbox in enumerate(checkboxes_predicciones):
        if var_checkbox.get():
            predicciones_seleccionadas.append(predicciones_actuales[i])
    
    if not predicciones_seleccionadas:
        messagebox.showwarning("Sin selección", "Selecciona al menos un pronóstico para enviar.")
        return
    
    fecha = entry_fecha.get()
    mensaje = generar_mensaje_ia(predicciones_seleccionadas, fecha)
    
    try:
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
        
        exito = enviar_telegram(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, mensaje)
        if exito:
            messagebox.showinfo("Enviado", f"Se han enviado {len(predicciones_seleccionadas)} pronóstico(s) seleccionado(s) a Telegram.")
            for var_checkbox in checkboxes_predicciones:
                var_checkbox.set(False)
        else:
            messagebox.showerror("Error", "No se pudieron enviar los pronósticos a Telegram.")
            
    except Exception as e:
        messagebox.showerror("Error", f"Error enviando pronósticos seleccionados: {e}")

def enviar_alerta():
    if mensaje_telegram:
        try:
            exito = enviar_telegram(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, mensaje_telegram)
            if exito:
                messagebox.showinfo("Enviado", "El mensaje se ha enviado a Telegram correctamente.")
            else:
                messagebox.showerror("Error", "No se pudo enviar el mensaje a Telegram. Revisa la conexión.")
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


def abrir_usuarios():
    """Abrir ventana para mostrar usuarios registrados de Telegram"""
    ventana_usuarios = tk.Toplevel(root)
    ventana_usuarios.title("👥 Usuarios Registrados - SergioBets")
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

            exito = enviar_telegram(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, mensaje)
            if exito:
                messagebox.showinfo("Enviado", "El pronóstico avanzado se ha enviado correctamente.")
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


# --- Interfaz ---
root = tk.Tk()
root.title("🧐 SergioBets v.1 – Cuotas de Partidos (Reales)")
root.geometry("800x600")
root.minsize(800, 600)
root.state('zoomed')  # Maximizar ventana en Windows
root.configure(bg="#f1f3f4")

style = ttk.Style()
style.configure('TLabel', font=('Segoe UI', 10))
style.configure('TButton', font=('Segoe UI', 10, 'bold'))
style.configure('TCombobox', font=('Segoe UI', 10))

frame_top = tk.Frame(root, bg="#f1f3f4")
frame_top.pack(pady=15)

label_fecha = ttk.Label(frame_top, text="📅 Fecha:")
label_fecha.pack(side=tk.LEFT)

entry_fecha = DateEntry(frame_top, width=12, background="darkblue", foreground="white", borderwidth=2, date_pattern='yyyy-MM-dd')
entry_fecha.pack(side=tk.LEFT, padx=5)

label_liga = ttk.Label(frame_top, text="🏆 Liga:")
label_liga.pack(side=tk.LEFT, padx=10)

combo_ligas = ttk.Combobox(frame_top, state='readonly', width=30)
combo_ligas.pack(side=tk.LEFT)
combo_ligas.set('Todas')
combo_ligas.bind('<<ComboboxSelected>>', on_liga_changed)

btn_buscar = ttk.Button(frame_top, text="🔍 Buscar", command=buscar_en_hilo)
btn_buscar.pack(side=tk.LEFT, padx=5)

btn_progreso = ttk.Button(frame_top, text="📊 Progreso", command=abrir_progreso)
btn_progreso.pack(side=tk.LEFT, padx=5)

btn_enviar = ttk.Button(frame_top, text="📢 Enviar a Telegram", command=enviar_alerta)
btn_enviar.pack(side=tk.LEFT, padx=5)

btn_pronostico = ttk.Button(frame_top, text="📌 Enviar Pronóstico Seleccionado", command=enviar_predicciones_seleccionadas)
btn_pronostico.pack(side=tk.LEFT, padx=5)

btn_usuarios = ttk.Button(frame_top, text="👥 Users", command=abrir_usuarios)
btn_usuarios.pack(side=tk.LEFT, padx=5)

frame_predicciones = tk.Frame(root, bg="#f1f3f4")
frame_predicciones.pack(pady=5, padx=10, fill='x')

output = ScrolledText(root, wrap=tk.WORD, width=95, height=25, font=('Segoe UI', 10))
output.pack(pady=10, padx=10, expand=True, fill='both')

ligas_disponibles = set()

root.mainloop()
