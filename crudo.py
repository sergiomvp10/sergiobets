import tkinter as tk
from footystats_api import obtener_partidos_del_dia
from tkinter import ttk, messagebox
from datetime import date, timedelta
from json_storage import guardar_json, cargar_json
from tkinter.scrolledtext import ScrolledText
import threading
import requests
import json
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
        
        if predicciones_ia:
            output.insert(tk.END, "🤖 PREDICCIONES IA - PICKS RECOMENDADOS\n")
            if liga_filtrada != 'Todas':
                output.insert(tk.END, f"🏆 Liga: {liga_filtrada}\n")
            output.insert(tk.END, "=" * 50 + "\n")
            for i, pred in enumerate(predicciones_ia, 1):
                output.insert(tk.END, f"🎯 PICK #{i}: {pred['prediccion']}\n")
                output.insert(tk.END, f"⚽ {pred['partido']} ({pred['liga']})\n")
                output.insert(tk.END, f"💰 Cuota: {pred['cuota']} | Stake: {pred['stake_recomendado']}u | ⏰ {pred['hora']}\n")
                output.insert(tk.END, f"📊 Confianza: {pred['confianza']}% | Valor Esperado: {pred['valor_esperado']}\n")
                output.insert(tk.END, f"📝 Justificación: {pred['razon']}\n\n")
            output.insert(tk.END, "=" * 50 + "\n\n")

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

btn_pronostico = ttk.Button(frame_top, text="📌 Enviar Pronóstico", command=abrir_pronostico)
btn_pronostico.pack(side=tk.LEFT, padx=5)

output = ScrolledText(root, wrap=tk.WORD, width=95, height=28, font=('Segoe UI', 10))
output.pack(pady=10, padx=10, expand=True, fill='both')

ligas_disponibles = set()

root.mainloop()
