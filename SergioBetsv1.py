import requests
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from tkinter.scrolledtext import ScrolledText
import threading
import json

API_KEY = '25a50341bad35456ad3a828704d1bca5'
API_URL_FIXTURES = 'https://v3.football.api-sports.io/fixtures?date={date}'
API_URL_ODDS = 'https://v3.football.api-sports.io/odds?fixture={fixture_id}'

HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'v3.football.api-sports.io'
}

def verificar_api_key():
    try:
        response = requests.get("https://v3.football.api-sports.io/status", headers=HEADERS)
        print("API Key status:", response.status_code)
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print("Error al verificar la API Key:", e)
        return False

def obtener_partidos(fecha):
    try:
        response = requests.get(API_URL_FIXTURES.format(date=fecha), headers=HEADERS)
        print("Fixture response status:", response.status_code)
        if response.status_code != 200:
            return None
        json_response = response.json()
        print("\n📦 Respuesta de la API:\n", json.dumps(json_response, indent=2, ensure_ascii=False))
        data = json_response['response']
        return data
    except Exception as e:
        print("Error al obtener partidos:", e)
        return None

def obtener_cuotas(fixture_id):
    try:
        response = requests.get(API_URL_ODDS.format(fixture_id=fixture_id), headers=HEADERS)
        data = response.json()['response']
        if data and 'bookmakers' in data[0]:
            bookmaker = data[0]['bookmakers'][0]['name']
            bets = data[0]['bookmakers'][0]['bets']

            cuota_local = cuota_empate = cuota_visitante = "N/D"

            for bet in bets:
                if bet['name'] == 'Match Winner':
                    for odd in bet['values']:
                        if odd['value'] == 'Home':
                            cuota_local = odd['odd']
                        elif odd['value'] == 'Draw':
                            cuota_empate = odd['odd']
                        elif odd['value'] == 'Away':
                            cuota_visitante = odd['odd']

            return bookmaker, cuota_local, cuota_empate, cuota_visitante
    except:
        pass
    return None, "N/D", "N/D", "N/D"

def buscar_en_hilo():
    threading.Thread(target=buscar).start()

def buscar():
    if not verificar_api_key():
        messagebox.showerror("Error de API", "Tu API Key es inválida o ha sido bloqueada. Verifica en https://www.api-football.com")
        return

    fecha = entry_fecha.get()
    if not fecha:
        fecha = date.today().isoformat()

    output.delete('1.0', tk.END)
    output.insert(tk.END, "Cargando partidos...\n")
    root.update()

    partidos = obtener_partidos(fecha)
    output.delete('1.0', tk.END)
    ligas_disponibles.clear()

    if partidos is None:
        output.insert(tk.END, "❌ Error al conectarse con la API. Revisa tu conexión o clave.\n")
        return

    if len(partidos) == 0:
        output.insert(tk.END, "🕒 No hay partidos disponibles para esta fecha.\n")
        return

    partidos_por_liga = {}

    for partido in partidos:
        league = partido['league']['name']
        ligas_disponibles.add(league)

        home = partido['teams']['home']['name']
        away = partido['teams']['away']['name']
        hora = partido['fixture']['date'][11:16]
        fixture_id = partido['fixture']['id']

        bookmaker, c_local, c_empate, c_visitante = obtener_cuotas(fixture_id)

        info = f"🕒 {hora} - {home} vs {away}\n"
        info += f"🏦 Casa: {bookmaker} | 💰 Cuotas -> Local: {c_local}, Empate: {c_empate}, Visitante: {c_visitante}\n\n"

        if league not in partidos_por_liga:
            partidos_por_liga[league] = []
        partidos_por_liga[league].append(info)

    actualizar_ligas()

    liga_filtrada = combo_ligas.get()
    if liga_filtrada not in ['Todas'] + sorted(list(ligas_disponibles)):
        combo_ligas.set('Todas')
        liga_filtrada = 'Todas'

    for liga in sorted(partidos_por_liga.keys()):
        if liga_filtrada != 'Todas' and liga_filtrada != liga:
            continue
        output.insert(tk.END, f"🔷 {liga}\n")
        for info in partidos_por_liga[liga]:
            output.insert(tk.END, info)

def actualizar_ligas():
    ligas = sorted(list(ligas_disponibles))
    combo_ligas['values'] = ['Todas'] + ligas
    if combo_ligas.get() not in combo_ligas['values']:
        combo_ligas.set('Todas')

# Interfaz
root = tk.Tk()
root.title("🤖 SergioBets v.1 - Cuotas de Partidos")
root.geometry("800x600")
root.configure(bg="#f1f3f4")

style = ttk.Style()
style.configure('TLabel', font=('Segoe UI', 10))
style.configure('TButton', font=('Segoe UI', 10, 'bold'))
style.configure('TCombobox', font=('Segoe UI', 10))

frame_top = tk.Frame(root, bg="#f1f3f4")
frame_top.pack(pady=15)

label_fecha = ttk.Label(frame_top, text="📅 Fecha (YYYY-MM-DD):")
label_fecha.pack(side=tk.LEFT)
entry_fecha = ttk.Entry(frame_top, width=12)
entry_fecha.pack(side=tk.LEFT, padx=5)
entry_fecha.insert(0, date.today().isoformat())

label_liga = ttk.Label(frame_top, text="🏆 Liga:")
label_liga.pack(side=tk.LEFT, padx=10)
combo_ligas = ttk.Combobox(frame_top, state='readonly', width=30)
combo_ligas.pack(side=tk.LEFT)
combo_ligas.set('Todas')

btn_buscar = ttk.Button(frame_top, text="🔍 Buscar", command=buscar_en_hilo)
btn_buscar.pack(side=tk.LEFT, padx=15)

output = ScrolledText(root, wrap=tk.WORD, width=95, height=28, font=('Segoe UI', 10))
output.pack(pady=10, padx=10)

ligas_disponibles = set()

root.mainloop()