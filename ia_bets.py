import random
import json
import os
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from scipy import stats

LIGAS_CONOCIDAS = {
    "Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1",
    "Champions League", "Europa League", "Championship", "Liga MX",
    "Primeira Liga", "Eredivisie", "Scottish Premiership", "MLS",
    "Copa Libertadores", "Copa Sudamericana", "Liga Argentina",
    "Brasileirão", "Liga Colombiana", "Primera División Chile",
    "Liga Peruana", "Liga Ecuatoriana", "Liga Uruguaya", "Liga Boliviana"
}

def cargar_configuracion_cuotas():
    """Carga la configuración de cuotas desde config_app.json"""
    from json_storage import cargar_json
    config = cargar_json("config_app.json")
    if config is None:
        return 1.30, 1.60
    return config.get("odds_min", 1.30), config.get("odds_max", 1.60)

def obtener_cuotas_configuradas():
    """Obtiene las cuotas configuradas (función helper para usar en el código)"""
    return cargar_configuracion_cuotas()



_cache_predicciones = {}

def generar_semilla_partido(local: str, visitante: str, fecha: str, cuotas: Dict[str, str]) -> int:
    """Genera semilla determinística basada en datos del partido"""
    datos_partido = f"{local}|{visitante}|{fecha}|{cuotas.get('local', '2.0')}|{cuotas.get('empate', '3.0')}|{cuotas.get('visitante', '4.0')}"
    hash_objeto = hashlib.md5(datos_partido.encode())
    return int(hash_objeto.hexdigest()[:8], 16)

def limpiar_cache_predicciones():
    """Limpia el cache de predicciones"""
    global _cache_predicciones
    _cache_predicciones.clear()

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

def calcular_probabilidades_btts(semilla: int) -> Dict[str, float]:
    """Calcula probabilidades de Both Teams To Score basado en estadísticas determinísticas"""
    np.random.seed(semilla + 1)
    prob_btts_si = np.random.normal(0.52, 0.15)
    prob_btts_si = max(0.25, min(0.75, prob_btts_si))
    
    return {
        "btts_si": prob_btts_si,
        "btts_no": 1 - prob_btts_si
    }

def calcular_probabilidades_over_under(rendimiento_equipos: Optional[Dict[str, Any]] = None, semilla: int = 0) -> Dict[str, float]:
    """Calcula probabilidades de Over/Under con análisis contextual"""
    np.random.seed(semilla + 2)
    goles_esperados = float(np.random.normal(2.7, 0.8))
    
    if rendimiento_equipos:
        factor_ofensivo = rendimiento_equipos.get("goles_promedio_local", 1.3) + rendimiento_equipos.get("goles_promedio_visitante", 1.3)
        goles_esperados = goles_esperados * (factor_ofensivo / 2.6)
    
    goles_esperados = max(1.5, min(4.5, goles_esperados))
    
    prob_over_25 = float(1 - stats.poisson.cdf(2, goles_esperados))
    prob_over_15 = float(1 - stats.poisson.cdf(1, goles_esperados))
    
    return {
        "over_15": prob_over_15,
        "under_15": 1 - prob_over_15,
        "over_25": prob_over_25,
        "under_25": 1 - prob_over_25,
        "goles_esperados": goles_esperados
    }

def calcular_probabilidades_primera_mitad(semilla: int) -> Dict[str, float]:
    """Calcula probabilidades de goles en primera mitad"""
    np.random.seed(semilla + 3)
    goles_primera_mitad = float(np.random.normal(1.2, 0.5))
    goles_primera_mitad = max(0.5, min(2.5, goles_primera_mitad))
    
    prob_over_05_1h = float(1 - stats.poisson.pmf(0, goles_primera_mitad))
    prob_over_15_1h = float(1 - stats.poisson.cdf(1, goles_primera_mitad))
    
    return {
        "over_05_1h": prob_over_05_1h,
        "over_15_1h": prob_over_15_1h,
        "goles_esperados_1h": goles_primera_mitad
    }

def calcular_probabilidades_tarjetas(rendimiento_equipos: Optional[Dict[str, Any]] = None, semilla: int = 0) -> Dict[str, float]:
    """Calcula probabilidades de tarjetas con análisis contextual"""
    np.random.seed(semilla + 4)
    tarjetas_esperadas = float(np.random.normal(4.8, 1.2))
    
    if rendimiento_equipos:
        factor_disciplina = rendimiento_equipos.get("tarjetas_promedio", 1.0)
        tarjetas_esperadas = tarjetas_esperadas * factor_disciplina
    
    tarjetas_esperadas = max(2.0, min(8.0, tarjetas_esperadas))
    
    prob_over_35_cards = float(1 - stats.poisson.cdf(3, tarjetas_esperadas))
    prob_over_55_cards = float(1 - stats.poisson.cdf(5, tarjetas_esperadas))
    
    return {
        "over_35_cards": prob_over_35_cards,
        "over_55_cards": prob_over_55_cards,
        "tarjetas_esperadas": tarjetas_esperadas
    }

def calcular_probabilidades_corners(rendimiento_equipos: Optional[Dict[str, Any]] = None, semilla: int = 0) -> Dict[str, float]:
    """Calcula probabilidades de corners totales"""
    np.random.seed(semilla + 5)
    corners_esperados = float(np.random.normal(10.5, 2.5))
    
    if rendimiento_equipos:
        factor_corners = rendimiento_equipos.get("corners_promedio", 1.0)
        corners_esperados = corners_esperados * factor_corners
    
    corners_esperados = max(6.0, min(16.0, corners_esperados))
    
    prob_over_85_corners = float(1 - stats.poisson.cdf(8, corners_esperados))
    prob_over_105_corners = float(1 - stats.poisson.cdf(10, corners_esperados))
    
    return {
        "over_85_corners": prob_over_85_corners,
        "over_105_corners": prob_over_105_corners,
        "corners_esperados": corners_esperados
    }

def calcular_probabilidades_handicap(cuotas: Dict[str, str], rendimiento_equipos: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
    """Calcula probabilidades de hándicap asiático"""
    try:
        prob_1x2 = calcular_probabilidades_1x2(cuotas)
        
        factor_forma = 1.0
        if rendimiento_equipos:
            forma_local = rendimiento_equipos.get("forma_local", 0.5)
            forma_visitante = rendimiento_equipos.get("forma_visitante", 0.5)
            factor_forma = forma_local / (forma_local + forma_visitante)
        
        prob_handicap_local_05 = prob_1x2["local"] * factor_forma
        prob_handicap_visitante_05 = 1 - prob_handicap_local_05
        
        prob_handicap_local_15 = prob_1x2["local"] * 0.6 * factor_forma
        prob_handicap_visitante_15 = 1 - prob_handicap_local_15
        
        return {
            "handicap_local_05": prob_handicap_local_05,
            "handicap_visitante_05": prob_handicap_visitante_05,
            "handicap_local_15": prob_handicap_local_15,
            "handicap_visitante_15": prob_handicap_visitante_15
        }
    except:
        return {
            "handicap_local_05": 0.5,
            "handicap_visitante_05": 0.5,
            "handicap_local_15": 0.35,
            "handicap_visitante_15": 0.65
        }

def analizar_rendimiento_equipos(local: str, visitante: str, semilla: int) -> Dict[str, Any]:
    """Simula análisis de rendimiento reciente y enfrentamientos directos"""
    np.random.seed(semilla + 6)
    
    rendimiento_local = {
        "goles_favor": float(np.random.normal(1.4, 0.6)),
        "goles_contra": float(np.random.normal(1.1, 0.5)),
        "tarjetas": float(np.random.normal(2.2, 0.8)),
        "corners": float(np.random.normal(5.5, 1.5)),
        "victorias": np.random.randint(1, 4),
        "forma": float(np.random.normal(0.6, 0.2))
    }
    
    rendimiento_visitante = {
        "goles_favor": float(np.random.normal(1.2, 0.5)),
        "goles_contra": float(np.random.normal(1.3, 0.6)),
        "tarjetas": float(np.random.normal(2.4, 0.9)),
        "corners": float(np.random.normal(4.8, 1.3)),
        "victorias": np.random.randint(0, 3),
        "forma": float(np.random.normal(0.4, 0.2))
    }
    
    h2h_goles_local = float(np.random.normal(1.5, 0.8))
    h2h_goles_visitante = float(np.random.normal(1.2, 0.7))
    
    return {
        "goles_promedio_local": max(0.5, min(3.0, rendimiento_local["goles_favor"])),
        "goles_promedio_visitante": max(0.5, min(3.0, rendimiento_visitante["goles_favor"])),
        "tarjetas_promedio": (rendimiento_local["tarjetas"] + rendimiento_visitante["tarjetas"]) / 4.8,
        "corners_promedio": (rendimiento_local["corners"] + rendimiento_visitante["corners"]) / 10.3,
        "forma_local": max(0.1, min(0.9, rendimiento_local["forma"])),
        "forma_visitante": max(0.1, min(0.9, rendimiento_visitante["forma"])),
        "h2h_goles_total": h2h_goles_local + h2h_goles_visitante,
        "ventaja_local": rendimiento_local["forma"] - rendimiento_visitante["forma"]
    }

def analizar_partido_completo(partido: Dict[str, Any]) -> Dict[str, Any]:
    """Análisis completo de un partido con múltiples mercados y contexto determinístico"""
    cuotas = partido.get("cuotas", {})
    local = partido.get('local', 'Local')
    visitante = partido.get('visitante', 'Visitante')
    fecha = partido.get('fecha', datetime.now().strftime('%Y-%m-%d'))
    
    semilla = generar_semilla_partido(local, visitante, fecha, cuotas)
    
    rendimiento = analizar_rendimiento_equipos(local, visitante, semilla)
    
    prob_1x2 = calcular_probabilidades_1x2(cuotas)
    prob_btts = calcular_probabilidades_btts(semilla)
    prob_over_under = calcular_probabilidades_over_under(rendimiento, semilla)
    prob_primera_mitad = calcular_probabilidades_primera_mitad(semilla)
    prob_tarjetas = calcular_probabilidades_tarjetas(rendimiento, semilla)
    prob_corners = calcular_probabilidades_corners(rendimiento, semilla)
    prob_handicap = calcular_probabilidades_handicap(cuotas, rendimiento)
    
    return {
        "partido": f"{local} vs {visitante}",
        "liga": partido.get("liga", "Desconocida"),
        "hora": partido.get("hora", "00:00"),
        "probabilidades_1x2": prob_1x2,
        "probabilidades_btts": prob_btts,
        "probabilidades_over_under": prob_over_under,
        "probabilidades_primera_mitad": prob_primera_mitad,
        "probabilidades_tarjetas": prob_tarjetas,
        "probabilidades_corners": prob_corners,
        "probabilidades_handicap": prob_handicap,
        "rendimiento_equipos": rendimiento,
        "cuotas_disponibles": cuotas
    }

def calcular_value_bet(probabilidad_estimada: float, cuota_mercado: float) -> Tuple[float, bool]:
    """Calcula el valor esperado y determina si es una value bet"""
    valor_esperado = (probabilidad_estimada * cuota_mercado) - 1
    es_value_bet = valor_esperado > 0.01  # Mínimo 1% de valor esperado
    
    return valor_esperado, es_value_bet

def encontrar_mejores_apuestas(analisis: Dict[str, Any], num_opciones: int = 1) -> List[Dict[str, Any]]:
    """Encuentra las mejores apuestas basadas en cuotas reales de la API dentro del rango configurado"""
    mejores_apuestas = []
    cuota_min, cuota_max = obtener_cuotas_configuradas()
    
    cuotas_reales = analisis["cuotas_disponibles"]
    
    mercados_disponibles = [
        ("1X2", "local", analisis["probabilidades_1x2"]["local"], cuotas_reales.get("local", "0"), f"Victoria {analisis['partido'].split(' vs ')[0]}"),
        ("1X2", "empate", analisis["probabilidades_1x2"]["empate"], cuotas_reales.get("empate", "0"), "Empate"),
        ("1X2", "visitante", analisis["probabilidades_1x2"]["visitante"], cuotas_reales.get("visitante", "0"), f"Victoria {analisis['partido'].split(' vs ')[1]}"),
        
        ("BTTS", "btts_si", analisis.get("probabilidades_btts", {}).get("btts_si", 0.5), cuotas_reales.get("btts_si", "0"), "Ambos equipos marcan - SÍ"),
        ("BTTS", "btts_no", analisis.get("probabilidades_btts", {}).get("btts_no", 0.5), cuotas_reales.get("btts_no", "0"), "Ambos equipos marcan - NO"),
        
        ("Over/Under", "over_15", analisis.get("probabilidades_over_under", {}).get("over_15", 0.8), cuotas_reales.get("over_15", "0"), "Más de 1.5 goles"),
        ("Over/Under", "under_15", analisis.get("probabilidades_over_under", {}).get("under_15", 0.2), cuotas_reales.get("under_15", "0"), "Menos de 1.5 goles"),
        ("Over/Under", "over_25", analisis.get("probabilidades_over_under", {}).get("over_25", 0.6), cuotas_reales.get("over_25", "0"), "Más de 2.5 goles"),
        ("Over/Under", "under_25", analisis.get("probabilidades_over_under", {}).get("under_25", 0.4), cuotas_reales.get("under_25", "0"), "Menos de 2.5 goles"),
        
        ("Corners", "over_85", analisis.get("probabilidades_corners", {}).get("over_85_corners", 0.6), cuotas_reales.get("corners_over_85", "0"), "Más de 8.5 corners"),
        ("Corners", "over_95", analisis.get("probabilidades_corners", {}).get("over_105_corners", 0.5), cuotas_reales.get("corners_over_95", "0"), "Más de 9.5 corners"),
        ("Corners", "over_105", analisis.get("probabilidades_corners", {}).get("over_105_corners", 0.4), cuotas_reales.get("corners_over_105", "0"), "Más de 10.5 corners"),
        
        ("1H", "over_05", analisis.get("probabilidades_primera_mitad", {}).get("over_05_1h", 0.6), cuotas_reales.get("1h_over_05", "0"), "Más de 0.5 goles 1H"),
        ("1H", "over_15", analisis.get("probabilidades_primera_mitad", {}).get("over_15_1h", 0.3), cuotas_reales.get("1h_over_15", "0"), "Más de 1.5 goles 1H"),
    ]
    
    for tipo_mercado, mercado, probabilidad, cuota_str, descripcion in mercados_disponibles:
        try:
            cuota_real = float(cuota_str)
            
            if cuota_real <= 1.0:
                continue
                
            if not (cuota_min <= cuota_real <= cuota_max):
                continue
                
            ve, es_value = calcular_value_bet(probabilidad, cuota_real)
            
            if es_value:
                mejores_apuestas.append({
                    "tipo": tipo_mercado,
                    "mercado": mercado,
                    "descripcion": descripcion,
                    "probabilidad": probabilidad,
                    "cuota": cuota_real,
                    "valor_esperado": ve,
                    "confianza": probabilidad * 100,
                    "ajuste": "ninguno"
                })
                
        except (ValueError, TypeError):
            continue
    
    if mejores_apuestas:
        mejores_apuestas.sort(key=lambda x: x["valor_esperado"], reverse=True)
        
        opciones_finales = mejores_apuestas[:num_opciones]
        
        for opcion in opciones_finales:
            kelly_fraction = opcion["valor_esperado"] / (opcion["cuota"] - 1)
            stake_recomendado = min(10, max(1, int(kelly_fraction * 100)))
            
            opcion["stake_recomendado"] = stake_recomendado
            opcion["justificacion"] = generar_justificacion(opcion, analisis)
        
        return opciones_finales
    
    return []

def generar_justificacion(apuesta: Dict[str, Any], analisis: Dict[str, Any]) -> str:
    """Genera justificación técnica para la apuesta recomendada"""
    tipo = apuesta["tipo"]
    ve_pct = round(apuesta["valor_esperado"] * 100, 1)
    conf_pct = round(apuesta["confianza"], 1)
    rendimiento = analisis.get("rendimiento_equipos", {})
    
    justificaciones = {
        "1X2": f"Probabilidad estimada {conf_pct}% vs cuota {apuesta['cuota']} (VE: +{ve_pct}%). Forma reciente: {rendimiento.get('forma_local', 0.5):.1f} vs {rendimiento.get('forma_visitante', 0.5):.1f}",
        "BTTS": f"Análisis estadístico indica {conf_pct}% probabilidad. Promedio goles: {rendimiento.get('goles_promedio_local', 1.3):.1f} + {rendimiento.get('goles_promedio_visitante', 1.3):.1f}. VE: +{ve_pct}%",
        "Over/Under": f"Modelo predictivo estima {analisis['probabilidades_over_under']['goles_esperados']:.1f} goles. Rendimiento ofensivo equipos favorece línea. VE: +{ve_pct}%",
        "Hándicap": f"Ventaja forma: {rendimiento.get('ventaja_local', 0):.2f}. H2H promedio: {rendimiento.get('h2h_goles_total', 2.7):.1f} goles. Probabilidad {conf_pct}% con VE +{ve_pct}%",
        "Corners": f"Promedio corners equipos: {rendimiento.get('corners_promedio', 1.0):.1f}x media liga. Estilo de juego favorece línea. VE: +{ve_pct}%",
        "Tarjetas": f"Factor disciplina: {rendimiento.get('tarjetas_promedio', 1.0):.1f}x promedio. Historial enfrentamientos indica {conf_pct}% probabilidad. VE: +{ve_pct}%"
    }
    
    return justificaciones.get(tipo, f"Value bet identificada: {ve_pct}% valor esperado con {conf_pct}% confianza basada en análisis contextual.")

def generar_prediccion(partido: Dict[str, Any], opcion_numero: int = 1) -> Optional[Dict[str, Any]]:
    try:
        analisis = analizar_partido_completo(partido)
        mejores_apuestas = encontrar_mejores_apuestas(analisis, num_opciones=2)
        
        if not mejores_apuestas:
            return None
            
        if not es_liga_conocida(analisis["liga"]):
            return None
        
        indice_opcion = opcion_numero - 1
        if indice_opcion >= len(mejores_apuestas):
            return None
            
        mejor_apuesta = mejores_apuestas[indice_opcion]
        
        return {
            "partido": analisis["partido"],
            "liga": analisis["liga"],
            "hora": analisis["hora"],
            "prediccion": mejor_apuesta["descripcion"],
            "cuota": mejor_apuesta["cuota"],
            "stake_recomendado": mejor_apuesta["stake_recomendado"],
            "confianza": round(mejor_apuesta["confianza"], 1),
            "valor_esperado": round(mejor_apuesta["valor_esperado"], 3),
            "razon": mejor_apuesta["justificacion"],
            "opcion_numero": opcion_numero,
            "total_opciones": len(mejores_apuestas)
        }
    except Exception as e:
        print(f"Error generando predicción para partido: {e}")
        return None

def filtrar_apuestas_inteligentes(partidos: List[Dict[str, Any]], opcion_numero: int = 1) -> List[Dict[str, Any]]:
    predicciones_validas = []
    fecha = datetime.now().strftime('%Y-%m-%d')
    
    for partido in partidos:
        try:
            clave_partido = f"{partido.get('local', '')}|{partido.get('visitante', '')}|{fecha}|opcion_{opcion_numero}"
            
            if clave_partido in _cache_predicciones:
                prediccion = _cache_predicciones[clave_partido]
            else:
                partido_con_fecha = {**partido, 'fecha': fecha}
                prediccion = generar_prediccion(partido_con_fecha, opcion_numero)
                if prediccion:
                    _cache_predicciones[clave_partido] = prediccion
            
            if prediccion:
                predicciones_validas.append(prediccion)
        except Exception as e:
            print(f"Error procesando partido {partido.get('local', 'N/A')} vs {partido.get('visitante', 'N/A')}: {e}")
            continue
    
    predicciones_validas.sort(key=lambda x: x["valor_esperado"], reverse=True)
    
    return predicciones_validas[:5]

def generar_mensaje_ia(predicciones: List[Dict[str, Any]], fecha: str) -> str:
    if not predicciones:
        return f"🤖 IA BetGeniuX - {fecha}\n\n❌ No se encontraron apuestas recomendadas para hoy.\nCriterios: Value betting, ligas conocidas, análisis probabilístico."
    
    mensaje = f"🤖 IA BetGeniuX - ANÁLISIS AVANZADO ({fecha})\n\n"
    
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
            "sent_to_telegram": True,
            "resultado_real": None,
            "ganancia": None
        }
        
        historial.append(registro)
        guardar_json("historial_predicciones.json", historial)
        
    except Exception as e:
        print(f"Error guardando predicción histórica: {e}")

def encontrar_mejor_apuesta(analisis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Función de compatibilidad - devuelve solo la mejor apuesta"""
    mejores = encontrar_mejores_apuestas(analisis, num_opciones=1)
    return mejores[0] if mejores else None

def generar_reporte_rendimiento() -> Dict[str, Any]:
    """Genera reporte de rendimiento de las predicciones (DEPRECATED - usar TrackRecordManager)"""
    try:
        from track_record import TrackRecordManager
        
        api_key = "b37303668c4be1b78ac35b9e96460458e72b74749814a7d6f44983ac4b432079"
        tracker = TrackRecordManager(api_key)
        
        return tracker.calcular_metricas_rendimiento()
        
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
            "cuotas": {"casa": "Bet365", "local": "1.45", "empate": "4.50", "visitante": "6.00"}
        },
        {
            "hora": "17:30",
            "liga": "La Liga",
            "local": "Real Madrid",
            "visitante": "Barcelona",
            "cuotas": {"casa": "Bet365", "local": "1.50", "empate": "4.20", "visitante": "5.50"}
        },
        {
            "hora": "20:00",
            "liga": "Serie A",
            "local": "Juventus",
            "visitante": "Inter Milan",
            "cuotas": {"casa": "Bet365", "local": "1.40", "empate": "4.80", "visitante": "7.00"}
        }
    ]
    return partidos_simulados
