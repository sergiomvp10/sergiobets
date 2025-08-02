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
    
    def obtener_resultado_partido(self, fecha: str, equipo_local: str, equipo_visitante: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene el resultado de un partido específico de la API
        """
        try:
            endpoint = f"{self.base_url}/todays-matches"
            params = {
                "key": self.api_key,
                "date": fecha,
                "timezone": "America/Bogota"
            }
            
            response = requests.get(endpoint, params=params)
            if response.status_code != 200:
                print(f"Error API: {response.status_code}")
                return None
            
            data = response.json()
            partidos = data.get("data", [])
            
            for partido in partidos:
                home_name = partido.get("home_name", "").lower()
                away_name = partido.get("away_name", "").lower()
                
                if (equipo_local.lower() in home_name or home_name in equipo_local.lower()) and \
                   (equipo_visitante.lower() in away_name or away_name in equipo_visitante.lower()):
                    
                    status = partido.get("status", "").lower().strip()
                    
                    if status in VALID_MATCH_STATUSES:
                        return {
                            "match_id": partido.get("id"),
                            "status": status,
                            "home_score": partido.get("home_goals", 0),
                            "away_score": partido.get("away_goals", 0),
                            "total_goals": partido.get("home_goals", 0) + partido.get("away_goals", 0),
                            "corners_home": partido.get("home_corners", 0),
                            "corners_away": partido.get("away_corners", 0),
                            "total_corners": partido.get("home_corners", 0) + partido.get("away_corners", 0),
                            "cards_home": partido.get("home_cards", 0),
                            "cards_away": partido.get("away_cards", 0),
                            "total_cards": partido.get("home_cards", 0) + partido.get("away_cards", 0),
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
    
    def validar_prediccion(self, prediccion: Dict[str, Any], resultado: Dict[str, Any]) -> Tuple[bool, float]:
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
                umbral = float(tipo_prediccion.split("más de ")[1].split(" corners")[0])
                acierto = resultado["total_corners"] > umbral
                
            elif "más de" in tipo_prediccion and "tarjetas" in tipo_prediccion:
                umbral = float(tipo_prediccion.split("más de ")[1].split(" tarjetas")[0])
                acierto = resultado["total_cards"] > umbral
                
            elif "btts" in tipo_prediccion or "ambos equipos marcan" in tipo_prediccion:
                acierto = resultado["home_score"] > 0 and resultado["away_score"] > 0
                
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

    def actualizar_historial_con_resultados(self) -> Dict[str, Any]:
        """
        Actualiza el historial de predicciones con los resultados reales
        Optimizado para procesar matches únicos y evitar crashes por exceso de API calls
        """
        try:
            import time
            
            correccion_result = self.corregir_datos_historicos()
            
            historial = cargar_json(self.historial_file) or []
            actualizaciones = 0
            errores = 0
            partidos_incompletos = 0
            
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
            
            print(f"Procesando {len(matches_unicos)} matches únicos para {len(predicciones_pendientes)} predicciones...")
            
            for i, (key, match_data) in enumerate(matches_unicos.items()):
                try:
                    print(f"Procesando {i+1}/{len(matches_unicos)}: {match_data['partido']}")
                    
                    if i > 0:
                        time.sleep(2)
                    
                    resultado = self.obtener_resultado_partido(
                        match_data["fecha"],
                        match_data["equipo_local"],
                        match_data["equipo_visitante"]
                    )
                    
                    if resultado:
                        for prediccion in match_data["predicciones"]:
                            try:
                                acierto, ganancia = self.validar_prediccion(prediccion, resultado)
                                
                                prediccion["resultado_real"] = resultado
                                prediccion["ganancia"] = ganancia
                                prediccion["acierto"] = acierto
                                prediccion["fecha_actualizacion"] = datetime.now().isoformat()
                                
                                actualizaciones += 1
                                
                            except Exception as e:
                                print(f"    ❌ Error validando predicción {prediccion.get('prediccion', 'Unknown')}: {e}")
                                errores += 1
                        
                        print(f"  ✅ Match actualizado: {len(match_data['predicciones'])} predicciones procesadas")
                    else:
                        partidos_incompletos += 1
                        errores += len(match_data["predicciones"])
                        print(f"  ⏳ Match incompleto: {len(match_data['predicciones'])} predicciones pendientes")
                        
                except Exception as e:
                    print(f"  ❌ Error procesando match {match_data['partido']}: {e}")
                    errores += len(match_data["predicciones"])
                    continue
            
            guardar_json(self.historial_file, historial)
            
            print(f"Proceso completado: {actualizaciones} predicciones actualizadas, {partidos_incompletos} matches incompletos")
            
            return {
                "actualizaciones": actualizaciones,
                "errores": errores,
                "partidos_incompletos": partidos_incompletos,
                "correcciones_historicas": correccion_result.get("correcciones", 0),
                "total_procesadas": len(predicciones_pendientes),
                "matches_procesados": len(matches_unicos)
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
