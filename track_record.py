#!/usr/bin/env python3
"""
Track Record Module for SergioBets
Compares predictions against actual match results and calculates performance metrics
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from json_storage import cargar_json, guardar_json

VALID_MATCH_STATUSES = ["complete", "finished", "ft", "full-time", "ended"]
INVALID_MATCH_STATUSES = ["not started", "not_started", "scheduled", "in play", "in_play", "live", "halftime", "half-time", "postponed", "cancelled", "suspended"]

class TrackRecordManager:
    """Manages prediction tracking and performance analysis"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.football-data-api.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.historial_file = "historial_predicciones.json"
    
    def obtener_resultado_partido(self, fecha: str, equipo_local: str, equipo_visitante: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
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
                    (fecha_obj + timedelta(days=1)).strftime('%Y-%m-%d')
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
                    home_name = partido.get("home_name", "").lower()
                    away_name = partido.get("away_name", "").lower()
                    
                    equipo_local_clean = equipo_local.lower().strip()
                    equipo_visitante_clean = equipo_visitante.lower().strip()
                    home_name_clean = home_name.strip()
                    away_name_clean = away_name.strip()
                    
                    local_match = (
                        equipo_local_clean in home_name_clean or 
                        home_name_clean in equipo_local_clean or
                        any(word in home_name_clean for word in equipo_local_clean.split() if len(word) > 3) or
                        (equipo_local_clean.startswith('athletic') and 'athletic' in home_name_clean) or
                        (equipo_local_clean.startswith('atletico') and 'atletico' in home_name_clean)
                    )
                    
                    visitante_match = (
                        equipo_visitante_clean in away_name_clean or 
                        away_name_clean in equipo_visitante_clean or
                        any(word in away_name_clean for word in equipo_visitante_clean.split() if len(word) > 3) or
                        (equipo_visitante_clean.startswith('atletico') and 'atletico' in away_name_clean)
                    )
                    
                    if local_match and visitante_match:
                        
                        status = partido.get("status", "").lower().strip()
                        print(f"Found match: {partido.get('home_name')} vs {partido.get('away_name')} on {date_to_try} - Status: {status}")
                        
                        if status in VALID_MATCH_STATUSES:
                            team_a_corners = partido.get("team_a_corners", -1)
                            team_b_corners = partido.get("team_b_corners", -1)
                            total_corner_count = partido.get("totalCornerCount", -1)
                            
                            if total_corner_count == -1 and team_a_corners != -1 and team_b_corners != -1:
                                total_corner_count = team_a_corners + team_b_corners
                            
                            return {
                                "match_id": partido.get("id"),
                                "status": status,
                                "home_score": partido.get("home_goals", 0),
                                "away_score": partido.get("away_goals", 0),
                                "total_goals": partido.get("home_goals", 0) + partido.get("away_goals", 0),
                                "corners_home": team_a_corners if team_a_corners != -1 else 0,
                                "corners_away": team_b_corners if team_b_corners != -1 else 0,
                                "total_corners": total_corner_count if total_corner_count != -1 else 0,
                                "cards_home": partido.get("home_cards", 0),
                                "cards_away": partido.get("away_cards", 0),
                                "total_cards": partido.get("home_cards", 0) + partido.get("away_cards", 0),
                                "corner_data_available": total_corner_count != -1,
                                "resultado_1x2": self._determinar_resultado_1x2(
                                    partido.get("home_goals", 0), 
                                    partido.get("away_goals", 0)
                                )
                            }
                        elif status in INVALID_MATCH_STATUSES:
                            print(f"Skipping incomplete match: {partido.get('home_name')} vs {partido.get('away_name')} - Status: {status}")
                            return None
                        else:
                            print(f"Unknown match status: {status} for {partido.get('home_name')} vs {partido.get('away_name')}")
                            return None
            
            print(f"No match found for {equipo_local} vs {equipo_visitante} on any date")
            return None
            
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
                if not resultado.get("corner_data_available", True) or resultado.get("total_corners", 0) <= 0:
                    return None, None
                umbral = float(tipo_prediccion.split("más de ")[1].split(" corners")[0])
                acierto = resultado["total_corners"] > umbral
                
            elif "menos de" in tipo_prediccion and "corners" in tipo_prediccion:
                if not resultado.get("corner_data_available", True) or resultado.get("total_corners", 0) <= 0:
                    return None, None
                umbral = float(tipo_prediccion.split("menos de ")[1].split(" corners")[0])
                acierto = resultado["total_corners"] < umbral
                
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

    def actualizar_historial_con_resultados(self, max_matches=10, timeout_per_match=15) -> Dict[str, Any]:
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
            
            if not predicciones_pendientes:
                return {
                    "actualizaciones": 0,
                    "errores": 0,
                    "partidos_incompletos": 0,
                    "correcciones_historicas": correccion_result.get("correcciones", 0),
                    "total_procesadas": 0
                }
            
            matches_unicos = {}
            for prediccion in predicciones_pendientes:
                partido = prediccion["partido"]
                fecha = prediccion["fecha"]
                key = f"{fecha}|{partido}"
                
                if key not in matches_unicos:
                    matches_unicos[key] = {
                        "fecha": fecha,
                        "partido": partido,
                        "equipo_local": partido.split(" vs ")[0].strip(),
                        "equipo_visitante": partido.split(" vs ")[1].strip(),
                        "predicciones": []
                    }
                matches_unicos[key]["predicciones"].append(prediccion)
            
            matches_to_process = list(matches_unicos.items())[:max_matches]
            
            print(f"Procesando {len(matches_to_process)} matches (máximo {max_matches}) de {len(matches_unicos)} únicos para {len(predicciones_pendientes)} predicciones...")
            
            for i, (key, match_data) in enumerate(matches_to_process):
                try:
                    print(f"Procesando {i+1}/{len(matches_to_process)}: {match_data['partido']}")
                    print(f"  Buscando: {match_data['equipo_local']} vs {match_data['equipo_visitante']} en {match_data['fecha']}")
                    
                    if i > 0:
                        time.sleep(1)
                    
                    try:
                        resultado = self.obtener_resultado_partido(
                            match_data["fecha"],
                            match_data["equipo_local"],
                            match_data["equipo_visitante"],
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
            
            con_resultado = [p for p in historial if p.get("resultado_real") is not None]
            
            if not con_resultado:
                return {
                    "total_predicciones": len(historial),
                    "predicciones_resueltas": 0,
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
            
            return {
                "total_predicciones": total_predicciones,
                "predicciones_resueltas": predicciones_resueltas,
                "aciertos": len(aciertos),
                "tasa_acierto": len(aciertos) / predicciones_resueltas * 100,
                "total_apostado": total_apostado,
                "total_ganancia": total_ganancia,
                "roi": roi,
                "valor_esperado_promedio": sum(p["valor_esperado"] for p in historial) / total_predicciones,
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
📊 REPORTE DE RENDIMIENTO - SERGIOBETS IA
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
    
    api_key = "b37303668c4be1b78ac35b9e96460458e72b74749814a7d6f44983ac4b432079"
    
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
