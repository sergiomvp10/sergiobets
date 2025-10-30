#!/usr/bin/env python3
"""
Track Record Module for BetGeniuX
Compares predictions against actual match results and calculates performance metrics
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from json_storage import cargar_json, guardar_json
from json_optimizer import JSONOptimizer
from error_handler import safe_file_operation

VALID_MATCH_STATUSES = ["complete", "completed", "finished", "ft", "full-time", "full time", "ended", "played", "match finished", "match_finished"]
INVALID_MATCH_STATUSES = ["not started", "not_started", "scheduled", "in play", "in_play", "live", "halftime", "half-time", "postponed", "cancelled", "suspended", "abandoned"]

class TrackRecordManager:
    """Manages prediction tracking and performance analysis"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.football-data-api.com"):
        self.api_key = api_key
        self.base_url = base_url
        from pathlib import Path
        self.historial_file = str(Path(__file__).resolve().parent / "historial_predicciones.json")
        print(f"📁 Track Record usando archivo: {self.historial_file}")
    
    def _normalize_team_name(self, name: str) -> str:
        """
        Normalize team name by removing accents, punctuation, and extra spaces
        """
        import unicodedata
        import re
        
        name = unicodedata.normalize('NFD', name)
        name = ''.join(char for char in name if unicodedata.category(char) != 'Mn')
        
        name = name.lower()
        
        name = re.sub(r'[^\w\s]', ' ', name)
        name = ' '.join(name.split())
        
        return name
    
    def _get_team_tokens(self, name: str) -> set:
        """
        Get significant tokens from team name (words with 3+ characters)
        """
        normalized = self._normalize_team_name(name)
        tokens = {token for token in normalized.split() if len(token) >= 3}
        return tokens
    
    def _teams_match(self, pred_team: str, api_team: str, threshold: float = 0.5) -> bool:
        """
        Check if two team names match using token overlap
        """
        pred_tokens = self._get_team_tokens(pred_team)
        api_tokens = self._get_team_tokens(api_team)
        
        if not pred_tokens or not api_tokens:
            return False
        
        intersection = len(pred_tokens & api_tokens)
        union = len(pred_tokens | api_tokens)
        
        if union == 0:
            return False
        
        similarity = intersection / union
        return similarity >= threshold
    
    def _try_flexible_team_matching(self, equipo_local: str, equipo_visitante: str, fecha: str, timeout: int = 8) -> Optional[Dict[str, Any]]:
        """
        Intenta encontrar un partido donde al menos uno de los equipos coincida.
        Útil cuando el oponente cambió pero necesitamos el resultado del equipo principal.
        """
        try:
            endpoint = f"{self.base_url}/todays-matches"
            
            dates_to_try = [fecha]
            try:
                fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
                for days_offset in [-1, 1, -2, 2, -3, 3]:
                    dates_to_try.append((fecha_obj + timedelta(days=days_offset)).strftime('%Y-%m-%d'))
            except:
                pass
            
            for date_to_try in dates_to_try:
                params = {
                    "key": self.api_key,
                    "date": date_to_try,
                    "timezone": "America/Bogota"
                }
                
                try:
                    response = requests.get(endpoint, params=params, timeout=timeout)
                    if response.status_code != 200:
                        continue
                    
                    data = response.json()
                    partidos = data.get("data", [])
                    
                    for partido in partidos:
                        home_name = partido.get("home_name", "")
                        away_name = partido.get("away_name", "")
                        
                        local_match_home = self._teams_match(equipo_local, home_name)
                        local_match_away = self._teams_match(equipo_local, away_name)
                        visitante_match_home = self._teams_match(equipo_visitante, home_name)
                        visitante_match_away = self._teams_match(equipo_visitante, away_name)
                        
                        if local_match_home or local_match_away or visitante_match_home or visitante_match_away:
                            status = partido.get("status", "").lower().strip()
                            
                            if status in VALID_MATCH_STATUSES:
                                home_goals = partido.get("homeGoalCount") or partido.get("home_goals", 0)
                                away_goals = partido.get("awayGoalCount") or partido.get("away_goals", 0)
                                
                                team_a_corners = partido.get("team_a_corners", -1)
                                team_b_corners = partido.get("team_b_corners", -1)
                                total_corner_count = partido.get("totalCornerCount", -1)
                                
                                if total_corner_count == -1 and team_a_corners != -1 and team_b_corners != -1:
                                    total_corner_count = team_a_corners + team_b_corners
                                
                                print(f"  ✅ Flexible match found: predicted {equipo_local} vs {equipo_visitante}, found {home_name} vs {away_name} on {date_to_try}")
                                
                                return {
                                    "match_id": partido.get("id"),
                                    "status": status,
                                    "home_score": home_goals,
                                    "away_score": away_goals,
                                    "total_goals": home_goals + away_goals,
                                    "corners_home": team_a_corners if team_a_corners != -1 else 0,
                                    "corners_away": team_b_corners if team_b_corners != -1 else 0,
                                    "total_corners": total_corner_count if total_corner_count != -1 else 0,
                                    "cards_home": partido.get("home_cards", 0),
                                    "cards_away": partido.get("away_cards", 0),
                                    "total_cards": partido.get("home_cards", 0) + partido.get("away_cards", 0),
                                    "corner_data_available": total_corner_count != -1,
                                    "resultado_1x2": self._determinar_resultado_1x2(home_goals, away_goals),
                                    "flexible_match": True,
                                    "actual_home": home_name,
                                    "actual_away": away_name
                                }
                except:
                    continue
            
            print(f"  ❌ No flexible match found for {equipo_local} or {equipo_visitante}")
            return None
            
        except Exception as e:
            print(f"Error in flexible matching: {e}")
            return None

    def obtener_resultado_partido(self, fecha: str, equipo_local: str, equipo_visitante: str, timeout: int = 8) -> Optional[Dict[str, Any]]:
        """
        Obtiene el resultado de un partido específico de la API con timeout
        """
        try:
            endpoint = f"{self.base_url}/todays-matches"
            
            dates_to_try = [fecha]
            
            try:
                fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
                dates_to_try.extend([
                    (fecha_obj - timedelta(days=1)).strftime('%Y-%m-%d'),
                    (fecha_obj + timedelta(days=1)).strftime('%Y-%m-%d'),
                    (fecha_obj - timedelta(days=2)).strftime('%Y-%m-%d'),
                    (fecha_obj + timedelta(days=2)).strftime('%Y-%m-%d')
                ])
            except:
                pass
            
            for date_to_try in dates_to_try:
                params = {
                    "key": self.api_key,
                    "date": date_to_try,
                    "timezone": "America/Bogota"
                }
                
                print(f"API call: {endpoint} with date={date_to_try}")
                response = requests.get(endpoint, params=params, timeout=timeout)
                if response.status_code != 200:
                    print(f"Error API for {date_to_try}: {response.status_code}")
                    continue
                
                data = response.json()
                partidos = data.get("data", [])
                print(f"API returned {len(partidos)} matches for {date_to_try}")
                
                for i, partido in enumerate(partidos[:3]):
                    print(f"  Match {i+1}: {partido.get('home_name')} vs {partido.get('away_name')}")
                
                for partido in partidos:
                    home_name = partido.get("home_name", "")
                    away_name = partido.get("away_name", "")
                    
                    local_match = self._teams_match(equipo_local, home_name)
                    visitante_match = self._teams_match(equipo_visitante, away_name)
                    
                    if local_match and visitante_match:
                        
                        status = partido.get("status", "").lower().strip()
                        print(f"Found match: {partido.get('home_name')} vs {partido.get('away_name')} on {date_to_try} - Status: {status}")
                        
                        if status in VALID_MATCH_STATUSES:
                            home_goals = partido.get("homeGoalCount") or partido.get("home_goals", 0)
                            away_goals = partido.get("awayGoalCount") or partido.get("away_goals", 0)
                            
                            team_a_corners = partido.get("team_a_corners", -1)
                            team_b_corners = partido.get("team_b_corners", -1)
                            total_corner_count = partido.get("totalCornerCount", -1)
                            
                            if total_corner_count == -1 and team_a_corners != -1 and team_b_corners != -1:
                                total_corner_count = team_a_corners + team_b_corners
                            
                            return {
                                "match_id": partido.get("id"),
                                "status": status,
                                "home_score": home_goals,
                                "away_score": away_goals,
                                "total_goals": home_goals + away_goals,
                                "corners_home": team_a_corners if team_a_corners != -1 else 0,
                                "corners_away": team_b_corners if team_b_corners != -1 else 0,
                                "total_corners": total_corner_count if total_corner_count != -1 else 0,
                                "cards_home": partido.get("home_cards", 0),
                                "cards_away": partido.get("away_cards", 0),
                                "total_cards": partido.get("home_cards", 0) + partido.get("away_cards", 0),
                                "corner_data_available": total_corner_count != -1,
                                "resultado_1x2": self._determinar_resultado_1x2(home_goals, away_goals)
                            }
                        elif status in INVALID_MATCH_STATUSES:
                            print(f"Skipping incomplete match: {partido.get('home_name')} vs {partido.get('away_name')} - Status: {status}")
                            return None
                        else:
                            print(f"Unknown match status: {status} for {partido.get('home_name')} vs {partido.get('away_name')}")
                            return None
            
            print(f"No exact match found for {equipo_local} vs {equipo_visitante}, trying flexible matching...")
            return self._try_flexible_team_matching(equipo_local, equipo_visitante, fecha, timeout)
            
        except requests.exceptions.Timeout:
            print(f"Timeout obteniendo resultado del partido {equipo_local} vs {equipo_visitante}")
            return None
        except Exception as e:
            print(f"Error obteniendo resultado: {e}")
            return None
    
    def _determinar_resultado_1x2(self, goles_local: int, goles_visitante: int) -> str:
        """Determina el resultado 1X2 basado en los goles"""
        if goles_local > goles_visitante:
            return "1"
        elif goles_local < goles_visitante:
            return "2"
        else:
            return "X"
    
    def validar_prediccion(self, prediccion: Dict[str, Any], resultado: Dict[str, Any]) -> Tuple[Optional[bool], Optional[float]]:
        """
        Valida si una predicción fue correcta y calcula la ganancia
        """
        tipo_prediccion = prediccion["prediccion"].lower()
        stake = prediccion["stake"]
        cuota = prediccion["cuota"]
        
        acierto = False
        
        try:
            if "más de" in tipo_prediccion and "goles" in tipo_prediccion:
                umbral = float(tipo_prediccion.split("más de ")[1].split(" goles")[0])
                acierto = resultado["total_goals"] > umbral
                
            elif "más de" in tipo_prediccion and "corners" in tipo_prediccion:
                total_corners = resultado.get("total_corners", 0)
                if not resultado.get("corner_data_available", True) or total_corners <= 0:
                    return None, None
                umbral = float(tipo_prediccion.split("más de ")[1].split(" corners")[0])
                acierto = total_corners > umbral
                print(f"    🏁 Corner bet validation: {total_corners} corners vs {umbral} threshold = {'WIN' if acierto else 'LOSS'}")
                
            elif "menos de" in tipo_prediccion and "corners" in tipo_prediccion:
                total_corners = resultado.get("total_corners", 0)
                if not resultado.get("corner_data_available", True) or total_corners <= 0:
                    return None, None
                umbral = float(tipo_prediccion.split("menos de ")[1].split(" corners")[0])
                acierto = total_corners < umbral
                print(f"    🏁 Corner bet validation: {total_corners} corners vs {umbral} threshold = {'WIN' if acierto else 'LOSS'}")
                
            elif "más de" in tipo_prediccion and "tarjetas" in tipo_prediccion:
                umbral = float(tipo_prediccion.split("más de ")[1].split(" tarjetas")[0])
                acierto = resultado["total_cards"] > umbral
                
            elif "btts" in tipo_prediccion or "ambos equipos marcan" in tipo_prediccion:
                acierto = resultado["home_score"] > 0 and resultado["away_score"] > 0
                
            elif "+0.5" in tipo_prediccion or "-0.5" in tipo_prediccion:
                if "+0.5" in tipo_prediccion:
                    team_name = tipo_prediccion.split(" +0.5")[0].strip()
                    partido_parts = prediccion.get("partido", "").split(" vs ")
                    if len(partido_parts) == 2:
                        away_team = partido_parts[1].strip()
                        if team_name.lower() in away_team.lower():
                            acierto = resultado["resultado_1x2"] in ["X", "2"]
                        else:
                            acierto = resultado["resultado_1x2"] in ["1", "X"]
                    else:
                        acierto = False
                elif "-0.5" in tipo_prediccion:
                    team_name = tipo_prediccion.split(" -0.5")[0].strip()
                    partido_parts = prediccion.get("partido", "").split(" vs ")
                    if len(partido_parts) == 2:
                        away_team = partido_parts[1].strip()
                        if team_name.lower() in away_team.lower():
                            acierto = resultado["resultado_1x2"] == "2"
                        else:
                            acierto = resultado["resultado_1x2"] == "1"
                    else:
                        acierto = False
                        
            elif any(x in tipo_prediccion for x in ["1", "x", "2", "local", "empate", "visitante"]):
                if "local" in tipo_prediccion or "1" in tipo_prediccion:
                    acierto = resultado["resultado_1x2"] == "1"
                elif "empate" in tipo_prediccion or "x" in tipo_prediccion:
                    acierto = resultado["resultado_1x2"] == "X"
                elif "visitante" in tipo_prediccion or "2" in tipo_prediccion:
                    acierto = resultado["resultado_1x2"] == "2"
            
            if acierto:
                ganancia = stake * (cuota - 1)
            else:
                ganancia = -stake
                
            return acierto, ganancia
            
        except Exception as e:
            print(f"Error validando predicción: {e}")
            return False, -stake
    
    def corregir_datos_historicos(self) -> Dict[str, Any]:
        """
        Corrige predicciones que fueron marcadas incorrectamente debido a partidos incompletos
        """
        try:
            historial = cargar_json(self.historial_file) or []
            correcciones = 0
            predicciones_corregidas = []
            
            for prediccion in historial:
                resultado_real = prediccion.get("resultado_real")
                
                if resultado_real is not None:
                    status = resultado_real.get("status", "").lower().strip()
                    
                    if status not in VALID_MATCH_STATUSES:
                        predicciones_corregidas.append({
                            "partido": prediccion.get("partido", "unknown"),
                            "fecha": prediccion.get("fecha", "unknown"),
                            "status_anterior": status,
                            "acierto_anterior": prediccion.get("acierto"),
                            "ganancia_anterior": prediccion.get("ganancia", 0)
                        })
                        
                        prediccion["resultado_real"] = None
                        prediccion["ganancia"] = None
                        prediccion["acierto"] = None
                        if "fecha_actualizacion" in prediccion:
                            del prediccion["fecha_actualizacion"]
                        
                        correcciones += 1
            
            if correcciones > 0:
                guardar_json(self.historial_file, historial)
                print(f"Corregidas {correcciones} predicciones con estados de partido inválidos")
                
                for correccion in predicciones_corregidas:
                    print(f"  - {correccion['partido']} ({correccion['fecha']}) - Status: {correccion['status_anterior']} - Era: {'Win' if correccion['acierto_anterior'] else 'Loss'}")
            
            return {
                "correcciones": correcciones,
                "predicciones_corregidas": predicciones_corregidas,
                "total_predicciones": len(historial)
            }
            
        except Exception as e:
            print(f"Error corrigiendo datos históricos: {e}")
            return {"error": str(e)}

    @safe_file_operation(default_return={"actualizados": 0, "errores": 0})
    def actualizar_historial_con_resultados(self, max_matches=50, timeout_per_match=8, from_date=None, to_date=None) -> Dict[str, Any]:
        """
        Actualiza el historial de predicciones con los resultados reales
        Optimizado para evitar colgados con límites y timeouts
        """
        try:
            import time
            
            correccion_result = self.corregir_datos_historicos()
            
            historial = cargar_json(self.historial_file) or []
            actualizaciones = 0
            errores = 0
            partidos_incompletos = 0
            timeouts = 0
            
            predicciones_pendientes = [p for p in historial if p.get("resultado_real") is None]
            
            if from_date or to_date:
                original_count = len(predicciones_pendientes)
                if from_date and to_date:
                    predicciones_pendientes = [p for p in predicciones_pendientes 
                                              if from_date <= p.get("fecha", "") <= to_date]
                    print(f"🔍 Filtrando por rango de fechas: {from_date} a {to_date}")
                    print(f"   Predicciones en rango: {len(predicciones_pendientes)} de {original_count}")
                elif from_date:
                    predicciones_pendientes = [p for p in predicciones_pendientes 
                                              if p.get("fecha", "") >= from_date]
                    print(f"🔍 Filtrando desde: {from_date}")
                    print(f"   Predicciones filtradas: {len(predicciones_pendientes)} de {original_count}")
                elif to_date:
                    predicciones_pendientes = [p for p in predicciones_pendientes 
                                              if p.get("fecha", "") <= to_date]
                    print(f"🔍 Filtrando hasta: {to_date}")
                    print(f"   Predicciones filtradas: {len(predicciones_pendientes)} de {original_count}")
            
            if not predicciones_pendientes:
                print("✅ No hay predicciones pendientes para actualizar")
                return {
                    "actualizaciones": 0,
                    "errores": 0,
                    "partidos_incompletos": 0,
                    "correcciones_historicas": correccion_result.get("correcciones", 0),
                    "total_procesadas": 0,
                    "matches_procesados": 0,
                    "matches_restantes": 0
                }
            
            if from_date or to_date:
                print(f"🎯 Actualizando {len(predicciones_pendientes)} predicciones pendientes en el rango de fechas seleccionado")
            else:
                print(f"🎯 Actualizando {len(predicciones_pendientes)} predicciones pendientes (todas las fechas)")
            
            matches_unicos = {}
            for prediccion in predicciones_pendientes:
                partido = prediccion["partido"]
                fecha = prediccion["fecha"]
                key = f"{fecha}|{partido}"
                
                if key not in matches_unicos:
                    if " vs " in partido:
                        parts = partido.split(" vs ")
                        equipo_local = parts[0].strip()
                        equipo_visitante = parts[1].strip()
                    else:
                        print(f"⚠️ Formato de partido inválido: {partido}")
                        continue
                        
                    matches_unicos[key] = {
                        "fecha": fecha,
                        "partido": partido,
                        "equipo_local": equipo_local,
                        "equipo_visitante": equipo_visitante,
                        "predicciones": []
                    }
                matches_unicos[key]["predicciones"].append(prediccion)
            
            def prioridad_match(item):
                key, match_data = item
                fecha = match_data["fecha"]
                
                try:
                    from datetime import datetime
                    fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
                    today = datetime.now()
                    days_diff = abs((today - fecha_obj).days)
                    return days_diff
                except:
                    return 999
            
            print(f"🔄 Priorizando partidos por proximidad a hoy (más recientes primero)...")
            
            priority_matches = []
            other_matches = []
            
            confirmed_api_dates = ["2025-08-04", "2025-08-05", "2025-08-06"]  # Dates known to have API data
            
            for key, match_data in matches_unicos.items():
                partido = match_data["partido"].lower()
                fecha = match_data["fecha"]
                
                if " vs " in partido:
                    teams = partido.split(" vs ")
                    equipo_local = teams[0].strip() if len(teams) > 0 else ""
                    equipo_visitante = teams[1].strip() if len(teams) > 1 else ""
                else:
                    equipo_local = ""
                    equipo_visitante = ""
                
                has_confirmed_api_data = (
                    (("athletic" in equipo_local and "club" in equipo_local) and 
                     ("atlético" in equipo_visitante and "go" in equipo_visitante)) or
                    ("cuiabá" in equipo_local and ("volta" in equipo_visitante or "redonda" in equipo_visitante)) or
                    (("universidad" in equipo_local and "chile" in equipo_local) and "cobresal" in equipo_visitante) or
                    ("athletic club" in partido and "atlético go" in partido) or
                    ("cuiabá" in partido and "volta redonda" in partido) or
                    ("universidad chile" in partido and "cobresal" in partido)
                )
                
                # Also prioritize recent dates that are more likely to have API data
                recent_dates = ["2025-08-04", "2025-08-05", "2025-08-06", "2025-08-03"]
                is_recent_date = fecha in recent_dates
                
                if has_confirmed_api_data or is_recent_date:
                    priority_matches.append((key, match_data))
                    if has_confirmed_api_data:
                        print(f"   🎯 PRIORITY: {match_data['partido']} (confirmed API match)")
                    elif is_recent_date:
                        print(f"   📅 PRIORITY: {match_data['partido']} (recent date: {fecha})")
                else:
                    other_matches.append((key, match_data))
            
            confirmed_api_matches = []
            other_priority_matches = []
            
            api_team_indicators = [
                ("athletic club", "criciúma"),  # Athletic Club vs Criciúma
                ("universidad chile", "audax italiano"),  # Universidad Chile vs Audax Italiano  
                ("o'higgins", "cobresal"),  # O'Higgins vs Cobresal
                ("atlético pr", "cuiabá"),  # Atlético PR vs Cuiabá
                ("atlético go", "ferroviária")  # Atlético GO vs Ferroviária
            ]
            
            for item in priority_matches:
                key, match_data = item
                partido = match_data["partido"].lower()
                fecha = match_data["fecha"]
                
                is_api_match = False
                for team1, team2 in api_team_indicators:
                    if (team1 in partido and team2 in partido) or (team2 in partido and team1 in partido):
                        is_api_match = True
                        break
                
                if is_api_match:
                    confirmed_api_matches.append(item)
                else:
                    other_priority_matches.append(item)
            
            confirmed_api_matches.sort(key=lambda x: x[1]["partido"])
            
            other_priority_matches_sorted = sorted(other_priority_matches, key=prioridad_match)
            other_matches_sorted = sorted(other_matches, key=prioridad_match)
            
            matches_ordenados = confirmed_api_matches + other_priority_matches_sorted + other_matches_sorted
            
            print(f"🎯 FORCED PRIORITIZATION (targeting actual pending matches):")
            print(f"   ✅ Matches with API team names (processed FIRST): {len(confirmed_api_matches)}")
            print(f"   📋 Other priority matches: {len(other_priority_matches_sorted)}")
            print(f"   📋 Standard matches: {len(other_matches_sorted)}")
            
            if confirmed_api_matches:
                print(f"   🔥 PROCESSING THESE FIRST:")
                for item in confirmed_api_matches[:5]:
                    key, match_data = item
                    print(f"     🎯 {match_data['partido']} ({match_data['fecha']})")
            else:
                print(f"   ⚠️ NO API TEAM MATCHES FOUND - will process in standard order")
            matches_to_process = matches_ordenados[:max_matches]
            
            print(f"📊 Priorización universal completada:")
            print(f"   🎯 Matches prioritarios (con datos API): {len(priority_matches)}")
            print(f"   📋 Matches estándar: {len(other_matches)}")
            print(f"   🔄 Procesando {len(matches_to_process)} matches (priorizando los que tienen datos)")
            
            if priority_matches:
                print(f"📊 PROCESANDO PRIMERO:")
                for key, match_data in matches_to_process[:3]:
                    status = "🎯 PRIORITY" if (key, match_data) in priority_matches else "📋 STANDARD"
                    print(f"   {status}: {match_data['partido']} ({match_data['fecha']})")
            else:
                print(f"⚠️ No se encontraron matches prioritarios, procesando en orden estándar")
            
            print(f"Procesando {len(matches_to_process)} matches (máximo {max_matches}) de {len(matches_unicos)} únicos para {len(predicciones_pendientes)} predicciones...")
            
            for i, (key, match_data) in enumerate(matches_to_process):
                try:
                    print(f"Procesando {i+1}/{len(matches_to_process)}: {match_data['partido']}")
                    print(f"  Buscando: {match_data['equipo_local']} vs {match_data['equipo_visitante']} en {match_data['fecha']}")
                    
                    if i > 0:
                        time.sleep(1)
                    
                    try:
                        equipo_local = match_data["equipo_local"]
                        equipo_visitante = match_data["equipo_visitante"]
                        
                        if not equipo_local or not equipo_visitante:
                            partido = match_data["partido"]
                            if " vs " in partido:
                                teams = partido.split(" vs ")
                                equipo_local = teams[0].strip() if len(teams) > 0 else equipo_local
                                equipo_visitante = teams[1].strip() if len(teams) > 1 else equipo_visitante
                        
                        resultado = self.obtener_resultado_partido(
                            match_data["fecha"],
                            equipo_local,
                            equipo_visitante,
                            timeout=timeout_per_match
                        )
                        
                        if resultado:
                            print(f"  ✅ Resultado encontrado: {resultado['home_score']}-{resultado['away_score']} (Status: {resultado['status']})")
                            for prediccion in match_data["predicciones"]:
                                try:
                                    validation_result = self.validar_prediccion(prediccion, resultado)
                                    
                                    if validation_result == (None, None):
                                        print(f"    ⏳ Predicción '{prediccion['prediccion']}': DATA PENDING (corner data not available)")
                                        continue
                                    
                                    acierto, ganancia = validation_result
                                    
                                    prediccion["resultado_real"] = resultado
                                    prediccion["ganancia"] = ganancia
                                    prediccion["acierto"] = acierto
                                    prediccion["fecha_actualizacion"] = datetime.now().isoformat()
                                    
                                    actualizaciones += 1
                                    print(f"    ✅ Predicción '{prediccion['prediccion']}': {'WIN' if acierto else 'LOSS'} (${ganancia:.2f})")
                                    
                                except Exception as e:
                                    print(f"    ❌ Error validando predicción {prediccion.get('prediccion', 'Unknown')}: {e}")
                                    errores += 1
                            
                            print(f"  ✅ Match actualizado: {len(match_data['predicciones'])} predicciones procesadas")
                        else:
                            partidos_incompletos += 1
                            errores += len(match_data["predicciones"])
                            print(f"  ⏳ Match incompleto: {len(match_data['predicciones'])} predicciones pendientes")
                    
                    except Exception as e:
                        if "timeout" in str(e).lower():
                            timeouts += 1
                            print(f"  ⏰ Timeout procesando match {match_data['partido']} (>{timeout_per_match}s)")
                        else:
                            print(f"  ❌ Error procesando match {match_data['partido']}: {e}")
                        errores += len(match_data["predicciones"])
                        continue
                        
                except Exception as e:
                    print(f"  ❌ Error procesando match {match_data['partido']}: {e}")
                    errores += len(match_data["predicciones"])
                    continue
            
            guardar_json(self.historial_file, historial)
            print(f"✅ Guardado en: {self.historial_file}")
            
            remaining_matches = len(matches_unicos) - len(matches_to_process)
            print(f"Proceso completado: {actualizaciones} predicciones actualizadas, {partidos_incompletos} matches incompletos, {timeouts} timeouts")
            if remaining_matches > 0:
                print(f"⏳ {remaining_matches} matches restantes - ejecutar nuevamente para continuar")
            
            return {
                "actualizaciones": actualizaciones,
                "errores": errores,
                "partidos_incompletos": partidos_incompletos,
                "timeouts": timeouts,
                "correcciones_historicas": correccion_result.get("correcciones", 0),
                "total_procesadas": len(predicciones_pendientes),
                "matches_procesados": len(matches_to_process),
                "matches_restantes": remaining_matches
            }
            
        except Exception as e:
            print(f"Error crítico actualizando historial: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}
    
    def calcular_metricas_rendimiento(self) -> Dict[str, Any]:
        """
        Calcula métricas de rendimiento del sistema de predicciones
        """
        try:
            historial = cargar_json(self.historial_file) or []
            
            if not historial:
                return {"error": "No hay historial disponible"}
            
            historial = [p for p in historial if p.get('sent_to_telegram', False)]
            
            if not historial:
                return {"error": "No hay predicciones enviadas a Telegram"}
            
            con_resultado = [p for p in historial if p.get("resultado_real") is not None]
            
            if not con_resultado:
                return {
                    "total_predicciones": len(historial),
                    "predicciones_resueltas": 0,
                    "predicciones_pendientes": len(historial),
                    "aciertos": 0,
                    "tasa_acierto": 0,
                    "total_apostado": 0,
                    "total_ganancia": 0,
                    "roi": 0,
                    "mensaje": "No hay predicciones resueltas aún"
                }
            
            total_predicciones = len(historial)
            predicciones_resueltas = len(con_resultado)
            aciertos = [p for p in con_resultado if p.get("acierto", False)]
            
            total_apostado = sum(p["stake"] for p in con_resultado)
            total_ganancia = sum(p.get("ganancia", 0) for p in con_resultado)
            roi = (total_ganancia / total_apostado * 100) if total_apostado > 0 else 0
            
            tipos_apuesta = {}
            for pred in con_resultado:
                tipo = pred["prediccion"]
                if tipo not in tipos_apuesta:
                    tipos_apuesta[tipo] = {"total": 0, "aciertos": 0, "ganancia": 0}
                
                tipos_apuesta[tipo]["total"] += 1
                if pred.get("acierto", False):
                    tipos_apuesta[tipo]["aciertos"] += 1
                tipos_apuesta[tipo]["ganancia"] += pred.get("ganancia", 0)
            
            for tipo in tipos_apuesta:
                total = tipos_apuesta[tipo]["total"]
                aciertos_tipo = tipos_apuesta[tipo]["aciertos"]
                tipos_apuesta[tipo]["win_rate"] = (aciertos_tipo / total * 100) if total > 0 else 0
            
            predicciones_pendientes = total_predicciones - predicciones_resueltas
            
            predicciones_con_ve = [p for p in historial if "valor_esperado" in p]
            valor_esperado_promedio = 0
            if predicciones_con_ve:
                valor_esperado_promedio = sum(p["valor_esperado"] for p in predicciones_con_ve) / len(predicciones_con_ve)
            
            return {
                "total_predicciones": total_predicciones,
                "predicciones_resueltas": predicciones_resueltas,
                "predicciones_pendientes": predicciones_pendientes,
                "aciertos": len(aciertos),
                "tasa_acierto": len(aciertos) / predicciones_resueltas * 100,
                "total_apostado": total_apostado,
                "total_ganancia": total_ganancia,
                "roi": roi,
                "valor_esperado_promedio": valor_esperado_promedio,
                "tipos_apuesta": tipos_apuesta,
                "fecha_calculo": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error calculando métricas: {e}")
            return {"error": str(e)}
    
    def generar_reporte_detallado(self) -> str:
        """
        Genera un reporte detallado del rendimiento
        """
        metricas = self.calcular_metricas_rendimiento()
        
        if "error" in metricas:
            return f"Error generando reporte: {metricas['error']}"
        
        reporte = f"""
📊 REPORTE DE RENDIMIENTO - BETGENIUX IA
{'='*50}

📈 MÉTRICAS GENERALES:
• Total de predicciones: {metricas['total_predicciones']}
• Predicciones resueltas: {metricas['predicciones_resueltas']}
• Aciertos: {metricas['aciertos']}
• Tasa de acierto: {metricas['tasa_acierto']:.1f}%

💰 MÉTRICAS FINANCIERAS:
• Total apostado: ${metricas['total_apostado']:.2f}
• Ganancia total: ${metricas['total_ganancia']:.2f}
• ROI: {metricas['roi']:.2f}%
• Valor esperado promedio: {metricas['valor_esperado_promedio']:.3f}

🎯 RENDIMIENTO POR TIPO DE APUESTA:
"""
        
        for tipo, datos in metricas.get('tipos_apuesta', {}).items():
            reporte += f"• {tipo}: {datos['aciertos']}/{datos['total']} ({datos['win_rate']:.1f}%) - Ganancia: ${datos['ganancia']:.2f}\n"
        
        reporte += f"\n📅 Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return reporte


def test_track_record():
    """Función de prueba para el sistema de track record"""
    print("=== TESTING TRACK RECORD SYSTEM ===")
    
    api_key = "ba2674c1de1595d6af7c099be1bcef8c915f9324f0c1f0f5ac926106d199dafd"
    
    tracker = TrackRecordManager(api_key)
    
    print("1. Testing metrics calculation...")
    metricas = tracker.calcular_metricas_rendimiento()
    print(f"   Métricas: {metricas}")
    
    print("\n2. Testing detailed report...")
    reporte = tracker.generar_reporte_detallado()
    print(f"   Reporte generado: {len(reporte)} caracteres")
    
    print("\n3. Testing result update (simulation)...")
    resultado_update = tracker.actualizar_historial_con_resultados()
    print(f"   Resultado update: {resultado_update}")
    
    return True


if __name__ == "__main__":
    test_track_record()
