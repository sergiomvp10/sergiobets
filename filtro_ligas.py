import requests
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from tkinter.scrolledtext import ScrolledText
import threading

API_KEY = '25a50341bad35456ad3a828704d1bca5'
API_URL_FIXTURES = 'https://v3.football.api-sports.io/fixtures?date={date}'
API_URL_ODDS = 'https://v3.football.api-sports.io/odds?fixture={fixture_id}'

HEADERS = {
    'x-apisports-key': API_KEY
}

def obtener_partidos(fecha):
    try:
        response = requests.get(API_URL_FIXTURES.format(date=fecha), headers=HEADERS)
        data = response.json()['response']
        return data
    except:
        return []

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
    liga_filtrada = combo_ligas.get()
    fecha = entry_fecha.get()
    if not fecha:
        fecha = date.today().isoformat()

    output.delete('1.0', tk.END)
    output.insert(tk.END, "Cargando partidos...\n")
    root.update()

    partidos = obtener_partidos(fecha)
    output.delete('1.0', tk.END)
    ligas_disponibles.clear()

    if not partidos:
        output.insert(tk.END, "No se encontraron partidos o hubo un error en la API.\n")
        return

    for partido in partidos:
        league = partido['league']['name']
        ligas_disponibles.add(league)

        if liga_filtrada != 'Todas' and liga_filtrada != league:
            continue

        home = partido['teams']['home']['name']
        away = partido['teams']['away']['name']
        hora = partido['fixture']['date'][11:16]
        fixture_id = partido['fixture']['id']

        bookmaker, c_local, c_empate, c_visitante = obtener_cuotas(fixture_id)

        output.insert(tk.END, f"🕒 {hora} - {home} vs {away} ({league})\n")
        output.insert(tk.END, f"🏦 Casa: {bookmaker} | 💰 Cuotas -> Local: {c_local}, Empate: {c_empate}, Visitante: {c_visitante}\n\n")

    actualizar_ligas()

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