#!/usr/bin/env python3

import json
import requests
from datetime import datetime, timedelta

def debug_track_record_issue():
    """Debug why track record isn't registering predictions correctly"""
    print("=== DEBUGGING TRACK RECORD ISSUE ===")
    
    with open('historial_predicciones.json', 'r', encoding='utf-8') as f:
        historial = json.load(f)
    
    print(f"Total predictions: {len(historial)}")
    
    matches = {}
    for pred in historial:
        key = f"{pred['fecha']}|{pred['partido']}"
        if key not in matches:
            matches[key] = []
        matches[key].append(pred)
    
    print(f"Unique matches: {len(matches)}")
    for key, preds in matches.items():
        fecha, partido = key.split('|')
        print(f"  {partido} ({fecha}): {len(preds)} predictions")
    
    api_key = "ba2674c1de1595d6af7c099be1bcef8c915f9324f0c1f0f5ac926106d199dafd"
    
    for key, preds in matches.items():
        fecha, partido = key.split('|')
        equipo_local = partido.split(" vs ")[0].strip()
        equipo_visitante = partido.split(" vs ")[1].strip()
        
        print(f"\n🔍 Testing API for: {partido} on {fecha}")
        print(f"   Local: '{equipo_local}' | Visitante: '{equipo_visitante}'")
        
        try:
            endpoint = "https://api.football-data-api.com/todays-matches"
            params = {
                "key": api_key,
                "date": fecha,
                "timezone": "America/Bogota"
            }
            
            response = requests.get(endpoint, params=params)
            if response.status_code == 200:
                data = response.json()
                partidos = data.get("data", [])
                print(f"   API returned {len(partidos)} matches for {fecha}")
                
                found = False
                for partido_api in partidos:
                    home_name = partido_api.get("home_name", "").lower()
                    away_name = partido_api.get("away_name", "").lower()
                    status = partido_api.get("status", "")
                    
                    print(f"     API Match: {partido_api.get('home_name')} vs {partido_api.get('away_name')} - Status: {status}")
                    
                    if (equipo_local.lower() in home_name or home_name in equipo_local.lower()) and \
                       (equipo_visitante.lower() in away_name or away_name in equipo_visitante.lower()):
                        found = True
                        print(f"     ✅ MATCH FOUND! Status: {status}")
                        if status.lower() in ["complete", "finished", "ft"]:
                            print(f"     ✅ Match is complete - can be processed")
                        else:
                            print(f"     ⏳ Match not complete yet - Status: {status}")
                        break
                
                if not found:
                    print(f"     ❌ No matching API result found for {partido}")
                    print(f"     🔍 Trying fuzzy search...")
                    for partido_api in partidos:
                        home_name = partido_api.get("home_name", "")
                        away_name = partido_api.get("away_name", "")
                        if equipo_local.lower()[:5] in home_name.lower() or equipo_visitante.lower()[:5] in away_name.lower():
                            print(f"       Possible match: {home_name} vs {away_name}")
            else:
                print(f"   ❌ API Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    debug_track_record_issue()
