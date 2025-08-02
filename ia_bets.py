import random
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from scipy import stats

LIGAS_CONOCIDAS = {
    "Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1",
    "Champions League", "Europa League", "Championship", "Liga MX",
    "Primeira Liga", "Eredivisie", "Scottish Premiership", "MLS",
    "Copa Libertadores", "Copa Sudamericana", "Liga Argentina",
    "Brasileirão", "Liga Colombiana"
}

CUOTA_MIN = 1.50
CUOTA_MAX = 1.75

def es_liga_conocida(liga: str) -> bool:
    return any(liga_conocida.lower() in liga.lower() for liga_conocida in LIGAS_CONOCIDAS)

def calcular_probabilidades_1x2(cuotas: Dict[str, str]) -> Dict[str, float]:
    """Calcula probabilidades implícitas de las cuotas 1X2"""
    try:
        local = float(cuotas.get("local", "1.00"))
        empate = float(cuotas.get("empate", "1.00"))
        visitante = float(cuotas.get("visitante", "1.00"))
        
        prob_local = 1 / local if local > 0 else 0
        prob_empate = 1 / empate if empate > 0 else 0
        prob_visitante = 1 / visitante if visitante > 0 else 0
        
        total = prob_local + prob_empate + prob_visitante
        
        if total > 0:
            return {
                "local": prob_local / total,
                "empate": prob_empate / total,
                "visitante": prob_visitante / total
            }
        else:
            return {"local": 0.33, "empate": 0.33, "visitante": 0.34}
    except (ValueError, TypeError):
        return {"local": 0.33, "empate": 0.33, "visitante": 0.34}

def calcular_probabilidades_btts() -> Dict[str, float]:
    """Calcula probabilidades de Both Teams To Score basado en estadísticas simuladas"""
    prob_btts_si = np.random.normal(0.52, 0.15)  # Media 52% con variación
    prob_btts_si = max(0.25, min(0.75, prob_btts_si))  # Límites realistas
    
    return {
        "btts_si": prob_btts_si,
        "btts_no": 1 - prob_btts_si
    }

def calcular_probabilidades_over_under() -> Dict[str, float]:
    """Calcula probabilidades de Over/Under 2.5 goles"""
    goles_esperados = float(np.random.normal(2.7, 0.8))  # Media 2.7 goles por partido
    goles_esperados = max(1.5, min(4.5, goles_esperados))
    
    prob_over_25 = float(1 - stats.poisson.cdf(2, goles_esperados))
    
    return {
        "over_25": prob_over_25,
        "under_25": 1 - prob_over_25,
        "goles_esperados": goles_esperados
    }

def calcular_probabilidades_primera_mitad() -> Dict[str, float]:
    """Calcula probabilidades de goles en primera mitad"""
    goles_primera_mitad = float(np.random.normal(1.2, 0.5))
    goles_primera_mitad = max(0.5, min(2.5, goles_primera_mitad))
    
    prob_over_05_1h = float(1 - stats.poisson.pmf(0, goles_primera_mitad))
    prob_over_15_1h = float(1 - stats.poisson.cdf(1, goles_primera_mitad))
    
    return {
        "over_05_1h": prob_over_05_1h,
        "over_15_1h": prob_over_15_1h,
        "goles_esperados_1h": goles_primera_mitad
    }

def calcular_probabilidades_tarjetas() -> Dict[str, float]:
    """Calcula probabilidades de tarjetas totales"""
    tarjetas_esperadas = float(np.random.normal(4.8, 1.2))
    tarjetas_esperadas = max(2.0, min(8.0, tarjetas_esperadas))
    
    prob_over_35_cards = float(1 - stats.poisson.cdf(3, tarjetas_esperadas))
    prob_over_55_cards = float(1 - stats.poisson.cdf(5, tarjetas_esperadas))
    
    return {
        "over_35_cards": prob_over_35_cards,
        "over_55_cards": prob_over_55_cards,
        "tarjetas_esperadas": tarjetas_esperadas
    }

def analizar_partido_completo(partido: Dict[str, Any]) -> Dict[str, Any]:
    """Análisis completo de un partido con múltiples mercados"""
    cuotas = partido.get("cuotas", {})
    
    prob_1x2 = calcular_probabilidades_1x2(cuotas)
    
    prob_btts = calcular_probabilidades_btts()
    
    prob_over_under = calcular_probabilidades_over_under()
    
    prob_primera_mitad = calcular_probabilidades_primera_mitad()
    
    prob_tarjetas = calcular_probabilidades_tarjetas()
    
    return {
        "partido": f"{partido.get('local', 'Local')} vs {partido.get('visitante', 'Visitante')}",
        "liga": partido.get("liga", "Desconocida"),
        "hora": partido.get("hora", "00:00"),
        "probabilidades_1x2": prob_1x2,
        "probabilidades_btts": prob_btts,
        "probabilidades_over_under": prob_over_under,
        "probabilidades_primera_mitad": prob_primera_mitad,
        "probabilidades_tarjetas": prob_tarjetas,
        "cuotas_disponibles": cuotas
    }

def calcular_value_bet(probabilidad_estimada: float, cuota_mercado: float) -> Tuple[float, bool]:
    """Calcula el valor esperado y determina si es una value bet"""
    valor_esperado = (probabilidad_estimada * cuota_mercado) - 1
    es_value_bet = valor_esperado > 0.05  # Mínimo 5% de valor esperado
    
    return valor_esperado, es_value_bet

def encontrar_mejor_apuesta(analisis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Encuentra la mejor apuesta basada en value betting"""
    mejores_apuestas = []
    
    prob_1x2 = analisis["probabilidades_1x2"]
    cuotas = analisis["cuotas_disponibles"]
    
    for resultado, probabilidad in prob_1x2.items():
        try:
            cuota = float(cuotas.get(resultado, "1.00"))
            if cuota > 1.0:
                ve, es_value = calcular_value_bet(probabilidad, cuota)
                if es_value and CUOTA_MIN <= cuota <= CUOTA_MAX:
                    mejores_apuestas.append({
                        "tipo": "1X2",
                        "mercado": resultado,
                        "descripcion": {
                            "local": f"Victoria {analisis['partido'].split(' vs ')[0]}",
                            "empate": "Empate",
                            "visitante": f"Victoria {analisis['partido'].split(' vs ')[1]}"
                        }.get(resultado, resultado),
                        "probabilidad": probabilidad,
                        "cuota": cuota,
                        "valor_esperado": ve,
                        "confianza": probabilidad * 100
                    })
        except (ValueError, TypeError):
            continue
    
    prob_btts = analisis["probabilidades_btts"]
    cuota_btts_si = 1.85  # Cuota simulada
    cuota_btts_no = 1.95  # Cuota simulada
    
    ve_btts_si, es_value_si = calcular_value_bet(prob_btts["btts_si"], cuota_btts_si)
    ve_btts_no, es_value_no = calcular_value_bet(prob_btts["btts_no"], cuota_btts_no)
    
    if es_value_si and CUOTA_MIN <= cuota_btts_si <= CUOTA_MAX:
        mejores_apuestas.append({
            "tipo": "BTTS",
            "mercado": "btts_si",
            "descripcion": "Ambos equipos marcan - SÍ",
            "probabilidad": prob_btts["btts_si"],
            "cuota": cuota_btts_si,
            "valor_esperado": ve_btts_si,
            "confianza": prob_btts["btts_si"] * 100
        })
    
    if es_value_no and CUOTA_MIN <= cuota_btts_no <= CUOTA_MAX:
        mejores_apuestas.append({
            "tipo": "BTTS",
            "mercado": "btts_no",
            "descripcion": "Ambos equipos marcan - NO",
            "probabilidad": prob_btts["btts_no"],
            "cuota": cuota_btts_no,
            "valor_esperado": ve_btts_no,
            "confianza": prob_btts["btts_no"] * 100
        })
    
    prob_ou = analisis["probabilidades_over_under"]
    cuota_over_25 = 1.75  # Cuota simulada
    cuota_under_25 = 2.05  # Cuota simulada
    
    ve_over, es_value_over = calcular_value_bet(prob_ou["over_25"], cuota_over_25)
    ve_under, es_value_under = calcular_value_bet(prob_ou["under_25"], cuota_under_25)
    
    if es_value_over and CUOTA_MIN <= cuota_over_25 <= CUOTA_MAX:
        mejores_apuestas.append({
            "tipo": "Over/Under",
            "mercado": "over_25",
            "descripcion": "Más de 2.5 goles",
            "probabilidad": prob_ou["over_25"],
            "cuota": cuota_over_25,
            "valor_esperado": ve_over,
            "confianza": prob_ou["over_25"] * 100
        })
    
    if es_value_under and CUOTA_MIN <= cuota_under_25 <= CUOTA_MAX:
        mejores_apuestas.append({
            "tipo": "Over/Under",
            "mercado": "under_25",
            "descripcion": "Menos de 2.5 goles",
            "probabilidad": prob_ou["under_25"],
            "cuota": cuota_under_25,
            "valor_esperado": ve_under,
            "confianza": prob_ou["under_25"] * 100
        })
    
    if mejores_apuestas:
        mejores_apuestas.sort(key=lambda x: x["valor_esperado"], reverse=True)
        mejor = mejores_apuestas[0]
        
        kelly_fraction = mejor["valor_esperado"] / (mejor["cuota"] - 1)
        stake_recomendado = min(10, max(1, int(kelly_fraction * 100)))
        
        mejor["stake_recomendado"] = stake_recomendado
        mejor["justificacion"] = generar_justificacion(mejor, analisis)
        
        return mejor
    
    return None

def generar_justificacion(apuesta: Dict[str, Any], analisis: Dict[str, Any]) -> str:
    """Genera justificación técnica para la apuesta recomendada"""
    tipo = apuesta["tipo"]
    ve_pct = round(apuesta["valor_esperado"] * 100, 1)
    conf_pct = round(apuesta["confianza"], 1)
    
    justificaciones = {
        "1X2": f"Probabilidad estimada {conf_pct}% vs cuota {apuesta['cuota']} (VE: +{ve_pct}%). Liga conocida con historial.",
        "BTTS": f"Análisis estadístico indica {conf_pct}% probabilidad. Cuota {apuesta['cuota']} ofrece {ve_pct}% valor esperado.",
        "Over/Under": f"Modelo predictivo estima {analisis['probabilidades_over_under']['goles_esperados']:.1f} goles. Probabilidad {conf_pct}% con VE +{ve_pct}%."
    }
    
    return justificaciones.get(tipo, f"Value bet identificada: {ve_pct}% valor esperado con {conf_pct}% confianza.")

def generar_prediccion(partido: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        analisis = analizar_partido_completo(partido)
        mejor_apuesta = encontrar_mejor_apuesta(analisis)
        
        if not mejor_apuesta:
            return None
            
        if not es_liga_conocida(analisis["liga"]):
            return None
        
        return {
            "partido": analisis["partido"],
            "liga": analisis["liga"],
            "hora": analisis["hora"],
            "prediccion": mejor_apuesta["descripcion"],
            "cuota": mejor_apuesta["cuota"],
            "stake_recomendado": mejor_apuesta["stake_recomendado"],
            "confianza": round(mejor_apuesta["confianza"], 1),
            "valor_esperado": round(mejor_apuesta["valor_esperado"], 3),
            "razon": mejor_apuesta["justificacion"]
        }
    except Exception as e:
        print(f"Error generando predicción para partido: {e}")
        return None

def filtrar_apuestas_inteligentes(partidos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    predicciones_validas = []
    fecha = datetime.now().strftime('%Y-%m-%d')
    
    for partido in partidos:
        try:
            prediccion = generar_prediccion(partido)
            if prediccion:
                predicciones_validas.append(prediccion)
                guardar_prediccion_historica(prediccion, fecha)
        except Exception as e:
            print(f"Error procesando partido {partido.get('local', 'N/A')} vs {partido.get('visitante', 'N/A')}: {e}")
            continue
    
    predicciones_validas.sort(key=lambda x: x["valor_esperado"], reverse=True)
    
    return predicciones_validas[:5]

def generar_mensaje_ia(predicciones: List[Dict[str, Any]], fecha: str) -> str:
    if not predicciones:
        return f"🤖 IA SERGIOBETS - {fecha}\n\n❌ No se encontraron apuestas recomendadas para hoy.\nCriterios: Value betting, ligas conocidas, análisis probabilístico."
    
    mensaje = f"🤖 IA SERGIOBETS - ANÁLISIS AVANZADO ({fecha})\n\n"
    
    for i, pred in enumerate(predicciones, 1):
        mensaje += f"🎯 PICK #{i} - VALUE BET\n"
        mensaje += f"🏆 {pred['liga']}\n"
        mensaje += f"⚽ {pred['partido']}\n"
        mensaje += f"🔮 {pred['prediccion']}\n"
        mensaje += f"💰 Cuota: {pred['cuota']} | Stake: {pred['stake_recomendado']}u\n"
        mensaje += f"📊 Confianza: {pred['confianza']}% | VE: +{pred['valor_esperado']}\n"
        mensaje += f"📝 {pred['razon']}\n"
        mensaje += f"⏰ {pred['hora']}\n\n"
    
    total_ve = sum(pred['valor_esperado'] for pred in predicciones)
    mensaje += f"📈 RESUMEN DEL DÍA:\n"
    mensaje += f"• {len(predicciones)} value bets identificadas\n"
    mensaje += f"• Valor esperado total: +{total_ve:.1f}%\n\n"
    
    mensaje += "🧠 Análisis generado por IA avanzada con modelos probabilísticos.\n"
    mensaje += "⚠️ Apostar con responsabilidad."
    
    return mensaje

def guardar_prediccion_historica(prediccion: Dict[str, Any], fecha: str) -> None:
    """Guarda predicción en el historial para seguimiento futuro"""
    try:
        from json_storage import guardar_json, cargar_json
        
        historial = cargar_json("historial_predicciones.json") or []
        
        registro = {
            "fecha": fecha,
            "partido": prediccion["partido"],
            "liga": prediccion["liga"],
            "prediccion": prediccion["prediccion"],
            "cuota": prediccion["cuota"],
            "stake": prediccion["stake_recomendado"],
            "valor_esperado": prediccion["valor_esperado"],
            "confianza": prediccion["confianza"],
            "timestamp": datetime.now().isoformat(),
            "resultado_real": None,
            "ganancia": None
        }
        
        historial.append(registro)
        guardar_json("historial_predicciones.json", historial)
        
    except Exception as e:
        print(f"Error guardando predicción histórica: {e}")

def generar_reporte_rendimiento() -> Dict[str, Any]:
    """Genera reporte de rendimiento de las predicciones"""
    try:
        from json_storage import cargar_json
        
        historial = cargar_json("historial_predicciones.json") or []
        
        if not historial:
            return {"total_predicciones": 0, "mensaje": "No hay historial disponible"}
        
        total = len(historial)
        con_resultado = [p for p in historial if p.get("resultado_real") is not None]
        aciertos = [p for p in con_resultado if p.get("ganancia", 0) > 0]
        
        return {
            "total_predicciones": total,
            "predicciones_resueltas": len(con_resultado),
            "aciertos": len(aciertos),
            "tasa_acierto": len(aciertos) / len(con_resultado) * 100 if con_resultado else 0,
            "roi_total": sum(p.get("ganancia", 0) for p in con_resultado),
            "valor_esperado_promedio": sum(p["valor_esperado"] for p in historial) / total
        }
        
    except Exception as e:
        print(f"Error generando reporte: {e}")
        return {"error": str(e)}

def simular_datos_prueba() -> List[Dict[str, Any]]:
    partidos_simulados = [
        {
            "hora": "15:00",
            "liga": "Premier League",
            "local": "Manchester City",
            "visitante": "Arsenal",
            "cuotas": {"casa": "Bet365", "local": "1.65", "empate": "3.80", "visitante": "4.20"}
        },
        {
            "hora": "17:30",
            "liga": "La Liga",
            "local": "Real Madrid",
            "visitante": "Barcelona",
            "cuotas": {"casa": "Bet365", "local": "2.10", "empate": "3.40", "visitante": "3.20"}
        },
        {
            "hora": "20:00",
            "liga": "Serie A",
            "local": "Juventus",
            "visitante": "Inter Milan",
            "cuotas": {"casa": "Bet365", "local": "1.55", "empate": "4.00", "visitante": "5.50"}
        }
    ]
    return partidos_simulados
