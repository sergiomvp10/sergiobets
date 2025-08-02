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
from tkcalendar import DateEntry  # Importamos DateEntry de la librería tkcalendar

# CONFIG TELEGRAM
TELEGRAM_TOKEN = '7069280342:AAEeDTrSpvZliMXlqcwUv16O5_KkfCqzZ8A'
TELEGRAM_CHAT_ID = '7659029315'


def cargar_partidos_reales(fecha):
    datos_api = obtener_partidos_del_dia(fecha)
    partidos = []

    for partido in datos_api:
        partidos.append({
            "hora": partido.get("time", "00:00"),
            "liga": partido.get("league_name", "Desconocida"),
            "local": partido.get("home_name", "Equipo Local"),
            "visitante": partido.get("away_name", "Equipo Visitante"),
            "cuotas": {
                "casa": "FootyStats",
                "local": str(partido.get("odds_ft_home_team_win", "1.00")),
                "empate": str(partido.get("odds_ft_draw", "1.00")),
                "visitante": str(partido.get("odds_ft_away_team_win", "1.00"))
            }
        })

    return partidos

progreso_data = {"deposito": 100, "meta": 300, "saldo_actual": 100}
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

    mensaje_telegram = f"⚽ MATCHES OF THE DAY ({fecha})\n\n"

    for liga in sorted(partidos_por_liga.keys()):
        if liga_filtrada != 'Todas' and liga_filtrada != liga:
            continue
        output.insert(tk.END, f"🔷 {liga}\n")
        mensaje_telegram += f"🔷 {liga}\n"
        for info in partidos_por_liga[liga]:
            output.insert(tk.END, info)
            mensaje_telegram += info

    guardar_datos_json(fecha)

def actualizar_ligas():
    ligas = sorted(ligas_disponibles)
    combo_ligas['values'] = ['Todas'] + ligas
    if combo_ligas.get() not in combo_ligas['values']:
        combo_ligas.set('Todas')

def enviar_alerta():
    if mensaje_telegram:
        enviar_telegram(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, mensaje_telegram)
        messagebox.showinfo("Enviado", "El mensaje se ha enviado a Telegram.")
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
        fecha = date.today().strftime('%Y-%m-%d')

        mensaje = (
            f"⚡️ APUESTA GRATUITA {fecha} ⚡️\n\n"
            f"🏆 {liga}\n"
            f"{local} 🆚 {visitante}\n\n"
            f"💥 {pronostico}\n\n"
            f"💰 Cuota: {cuota} | Stake {stake} ♻️ | {hora} ⏰"
        )

        try:
            with open("ultimo_pick.json", "w", encoding="utf-8") as f:
                json.dump({"mensaje": mensaje}, f, ensure_ascii=False, indent=4)

            with open("registro_pronosticos.txt", "a", encoding="utf-8") as f:
                f.write(f"{fecha} | Partido: {local} vs {visitante} | Pronóstico: {pronostico} | Cuota: {cuota}\n")

            enviar_telegram(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, mensaje)
            messagebox.showinfo("Enviado", "El pronóstico se ha enviado a Telegram.")
            ventana.destroy()
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
        ("⏰ Hora", "")
    ]

    entries = []
    for texto, valor in campos:
        ttk.Label(ventana, text=texto).pack(pady=2)
        entry = ttk.Entry(ventana)
        entry.insert(0, valor)
        entry.pack()
        entries.append(entry)

    entry_liga, entry_local, entry_visitante, entry_pronostico, entry_cuota, entry_stake, entry_hora = entries

    ttk.Button(ventana, text="📤 Enviar Pronóstico", command=enviar_pick).pack(pady=15)


# --- Interfaz ---
root = tk.Tk()
root.title("🧐 SergioBets v.1 – Cuotas de Partidos (Reales)")
root.geometry("800x600")
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

btn_buscar = ttk.Button(frame_top, text="🔍 Buscar", command=buscar_en_hilo)
btn_buscar.pack(side=tk.LEFT, padx=5)

btn_progreso = ttk.Button(frame_top, text="📊 Progreso", command=abrir_progreso)
btn_progreso.pack(side=tk.LEFT, padx=5)

btn_enviar = ttk.Button(frame_top, text="📢 Enviar a Telegram", command=enviar_alerta)
btn_enviar.pack(side=tk.LEFT, padx=5)

btn_pronostico = ttk.Button(frame_top, text="📌 Enviar Pronóstico", command=abrir_pronostico)
btn_pronostico.pack(side=tk.LEFT, padx=5)

output = ScrolledText(root, wrap=tk.WORD, width=95, height=28, font=('Segoe UI', 10))
output.pack(pady=10, padx=10)

ligas_disponibles = set()

root.mainloop()
