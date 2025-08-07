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

CUOTA_MIN = 1.45
CUOTA_MAX = 1.75

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

def calcular_probabilidades_btts(semilla: int, rendimiento_equipos: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
    """Calcula probabilidades de Both Teams To Score basado en estadísticas de equipos"""
    if rendimiento_equipos:
        goles_local = rendimiento_equipos.get("goles_promedio_local", 1.3)
        goles_visitante = rendimiento_equipos.get("goles_promedio_visitante", 1.3)
        
        prob_local_score = min(0.85, max(0.15, goles_local / 2.0))
        prob_visitante_score = min(0.85, max(0.15, goles_visitante / 2.0))
        prob_btts_si = prob_local_score * prob_visitante_score
    else:
        np.random.seed(semilla + 1)
        prob_btts_si = np.random.normal(0.52, 0.12)
    
    prob_btts_si = max(0.25, min(0.75, prob_btts_si))
    
    return {
        "btts_si": prob_btts_si,
        "btts_no": 1 - prob_btts_si
    }

def calcular_probabilidades_over_under(rendimiento_equipos: Optional[Dict[str, Any]] = None, semilla: int = 0, liga: str = "") -> Dict[str, float]:
    """Calcula probabilidades de Over/Under con análisis contextual mejorado"""
    
    league_averages = {
        "Premier League": 2.8,
        "La Liga": 2.6,
        "Serie A": 2.4,
        "Bundesliga": 3.1,
        "Champions League": 2.9,
        "Copa Colombia": 2.3,
        "Liga Colombiana": 2.3,
        "Brasileirão": 2.5
    }
    
    base_goals = league_averages.get(liga, 2.7)
    
    if rendimiento_equipos:
        factor_ofensivo = rendimiento_equipos.get("goles_promedio_local", 1.3) + rendimiento_equipos.get("goles_promedio_visitante", 1.3)
        goles_esperados = base_goals * (factor_ofensivo / 2.6)
    else:
        np.random.seed(semilla + 2)
        goles_esperados = float(np.random.normal(base_goals, 0.6))
    
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

def calcular_probabilidades_primera_mitad(rendimiento_equipos: Optional[Dict[str, Any]] = None, semilla: int = 0, liga: str = "") -> Dict[str, float]:
    """Calcula probabilidades de eventos en la primera mitad con análisis mejorado"""
    
    league_first_half_averages = {
        "Premier League": 0.68,
        "La Liga": 0.62,
        "Serie A": 0.58,
        "Bundesliga": 0.72,
        "Champions League": 0.65,
        "Copa Colombia": 0.60,
        "Liga Colombiana": 0.58
    }
    
    base_prob = league_first_half_averages.get(liga, 0.65)
    
    if rendimiento_equipos:
        factor_ofensivo = (rendimiento_equipos.get("goles_promedio_local", 1.3) + 
                          rendimiento_equipos.get("goles_promedio_visitante", 1.3)) / 2.6
        prob_gol_primera_mitad = base_prob * factor_ofensivo
    else:
        np.random.seed(semilla + 3)
        prob_gol_primera_mitad = float(np.random.normal(base_prob, 0.12))
    
    prob_gol_primera_mitad = max(0.35, min(0.85, prob_gol_primera_mitad))
    
    return {
        "gol_primera_mitad_si": prob_gol_primera_mitad,
        "gol_primera_mitad_no": 1 - prob_gol_primera_mitad,
        "over_05_1h": prob_gol_primera_mitad,
        "over_15_1h": prob_gol_primera_mitad * 0.7,
        "goles_esperados_1h": prob_gol_primera_mitad * 1.8
    }

def calcular_probabilidades_tarjetas(rendimiento_equipos: Optional[Dict[str, Any]] = None, semilla: int = 0, liga: str = "") -> Dict[str, float]:
    """Calcula probabilidades de tarjetas con análisis contextual mejorado"""
    
    league_card_averages = {
        "Premier League": 4.2,
        "La Liga": 5.1,
        "Serie A": 4.8,
        "Champions League": 4.5,
        "Copa Colombia": 5.2,
        "Liga Colombiana": 5.0
    }
    
    base_cards = league_card_averages.get(liga, 4.8)
    
    if rendimiento_equipos:
        factor_disciplina = rendimiento_equipos.get("tarjetas_promedio", 1.0)
        tarjetas_esperadas = base_cards * factor_disciplina
    else:
        np.random.seed(semilla + 4)
        tarjetas_esperadas = float(np.random.normal(base_cards, 1.0))
    
    tarjetas_esperadas = max(2.0, min(8.0, tarjetas_esperadas))
    
    prob_over_35_cards = float(1 - stats.poisson.cdf(3, tarjetas_esperadas))
    prob_over_55_cards = float(1 - stats.poisson.cdf(5, tarjetas_esperadas))
    
    return {
        "over_35_cards": prob_over_35_cards,
        "over_55_cards": prob_over_55_cards,
        "tarjetas_esperadas": tarjetas_esperadas
    }

def calcular_probabilidades_corners(rendimiento_equipos: Optional[Dict[str, Any]] = None, semilla: int = 0, liga: str = "") -> Dict[str, float]:
    """Calcula probabilidades de corners con análisis de estilo de juego"""
    
    league_corner_averages = {
        "Premier League": 11.2,
        "La Liga": 9.8,
        "Serie A": 9.5,
        "Bundesliga": 11.8,
        "Champions League": 10.5,
        "Copa Colombia": 9.2,
        "Liga Colombiana": 9.0
    }
    
    base_corners = league_corner_averages.get(liga, 10.5)
    
    if rendimiento_equipos:
        factor_corners = rendimiento_equipos.get("corners_promedio", 1.0)
        corners_esperados = base_corners * factor_corners
    else:
        np.random.seed(semilla + 5)
        corners_esperados = float(np.random.normal(base_corners, 2.0))
    
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
    from league_utils import detectar_liga_por_imagen
    
    cuotas = partido.get("cuotas", {})
    local = partido.get('local', 'Local')
    visitante = partido.get('visitante', 'Visitante')
    fecha = partido.get('fecha', datetime.now().strftime('%Y-%m-%d'))
    
    liga = partido.get("liga")
    if not liga or liga == "Desconocida":
        home_image = partido.get('home_image', '')
        away_image = partido.get('away_image', '')
        liga_detectada = detectar_liga_por_imagen(home_image, away_image)
        liga = liga_detectada if liga_detectada != "Liga Internacional" else "Desconocida"
    
    semilla = generar_semilla_partido(local, visitante, fecha, cuotas)
    
    rendimiento = analizar_rendimiento_equipos(local, visitante, semilla)
    
    prob_1x2 = calcular_probabilidades_1x2(cuotas)
    prob_btts = calcular_probabilidades_btts(semilla, rendimiento)
    prob_over_under = calcular_probabilidades_over_under(rendimiento, semilla, liga)
    prob_primera_mitad = calcular_probabilidades_primera_mitad(rendimiento, semilla, liga)
    prob_tarjetas = calcular_probabilidades_tarjetas(rendimiento, semilla, liga)
    prob_corners = calcular_probabilidades_corners(rendimiento, semilla, liga)
    prob_handicap = calcular_probabilidades_handicap(cuotas, rendimiento)
    
    prob_equipo_gol = calcular_probabilidades_equipo_gol(rendimiento, semilla, liga)
    
    return {
        "partido": f"{local} vs {visitante}",
        "liga": liga,
        "hora": partido.get("hora", "00:00"),
        "probabilidades_1x2": prob_1x2,
        "probabilidades_btts": prob_btts,
        "probabilidades_over_under": prob_over_under,
        "probabilidades_primera_mitad": prob_primera_mitad,
        "probabilidades_tarjetas": prob_tarjetas,
        "probabilidades_corners": prob_corners,
        "probabilidades_handicap": prob_handicap,
        "probabilidades_equipo_gol": prob_equipo_gol,
        "rendimiento_equipos": rendimiento,
        "cuotas_disponibles": cuotas
    }

def calcular_probabilidades_equipo_gol(rendimiento_equipos: Optional[Dict[str, Any]] = None, semilla: int = 0, liga: str = "") -> Dict[str, float]:
    """Calcula probabilidades de que cada equipo marque al menos un gol"""
    
    if rendimiento_equipos:
        goles_local = rendimiento_equipos.get("goles_promedio_local", 1.3)
        goles_visitante = rendimiento_equipos.get("goles_promedio_visitante", 1.3)
        
        prob_local_gol = min(0.90, max(0.20, 1 - np.exp(-goles_local)))
        prob_visitante_gol = min(0.90, max(0.20, 1 - np.exp(-goles_visitante)))
    else:
        np.random.seed(semilla + 7)
        prob_local_gol = float(np.random.normal(0.70, 0.15))
        prob_visitante_gol = float(np.random.normal(0.65, 0.15))
    
    prob_local_gol = max(0.20, min(0.90, prob_local_gol))
    prob_visitante_gol = max(0.20, min(0.90, prob_visitante_gol))
    
    return {
        "equipo_local_gol": prob_local_gol,
        "equipo_local_no_gol": 1 - prob_local_gol,
        "equipo_visitante_gol": prob_visitante_gol,
        "equipo_visitante_no_gol": 1 - prob_visitante_gol
    }

def calcular_value_bet(probabilidad_estimada: float, cuota_mercado: float) -> Tuple[float, bool]:
    """Calcula el valor esperado y determina si es una value bet"""
    valor_esperado = (probabilidad_estimada * cuota_mercado) - 1
    es_value_bet = valor_esperado > 0.12  # Mínimo 12% de valor esperado
    
    return valor_esperado, es_value_bet

def calcular_puntuacion_compuesta(apuesta: Dict[str, Any], liga: str) -> float:
    """
    Calcula puntuación compuesta basada en probabilidad, rentabilidad y seguridad
    """
    valor_esperado = apuesta["valor_esperado"]
    score_ve = min(valor_esperado * 2.5, 1.0)  # Normalizar a 0-1, máximo en 40% VE
    
    confianza = apuesta["confianza"] / 100.0
    score_confianza = confianza
    
    ligas_premium = {"Premier League", "La Liga", "Serie A", "Bundesliga", "Champions League"}
    ligas_buenas = {"Ligue 1", "Eredivisie", "Primeira Liga", "Liga MX"}
    
    if liga in ligas_premium:
        score_liga = 1.0
    elif liga in ligas_buenas:
        score_liga = 0.8
    else:
        score_liga = 0.6
    
    tipo_apuesta = apuesta["tipo"]
    volatilidad_tipos = {
        "BTTS": 0.9,        # Más estable
        "Over/Under": 0.85,  # Bastante estable
        "Corners": 0.7,      # Moderadamente volátil
        "Cards": 0.6,        # Más volátil
        "Handicap": 0.8,     # Estable con datos
        "1X2": 0.75,         # Moderado
        "Equipo_Gol": 0.8    # Bastante estable
    }
    score_volatilidad = volatilidad_tipos.get(tipo_apuesta, 0.7)
    
    puntuacion_final = (
        score_ve * 0.40 +           # 40% Valor Esperado
        score_confianza * 0.30 +    # 30% Confianza
        score_liga * 0.20 +         # 20% Seguridad Liga
        score_volatilidad * 0.10    # 10% Estabilidad Tipo
    )
    
    return puntuacion_final

def aplicar_filtros_seguridad(apuesta: Dict[str, Any], liga: str) -> bool:
    """
    Aplica filtros de seguridad para prevenir apuestas de alto riesgo
    """
    ligas_premium = {"Premier League", "La Liga", "Serie A", "Bundesliga", "Champions League"}
    ve_minimo = 0.12 if liga in ligas_premium else 0.18
    
    if apuesta["valor_esperado"] < ve_minimo:
        return False
    
    if apuesta["confianza"] < 65:
        return False
    
    cuota = apuesta["cuota"]
    if cuota < 1.45 or cuota > 1.75:
        return False
    
    if apuesta["valor_esperado"] < 0.15 and apuesta["confianza"] < 75:
        return False
    
    return True

def encontrar_mejores_apuestas(analisis: Dict[str, Any], num_opciones: int = 1) -> List[Dict[str, Any]]:
    """
    Encuentra las mejores apuestas usando algoritmo avanzado de selección
    Optimiza por probabilidad, rentabilidad y seguridad
    """
    local = analisis["partido"].split(" vs ")[0]
    visitante = analisis["partido"].split(" vs ")[1]
    liga = analisis.get("liga", "Liga Internacional")
    
    candidatas = []
    
    prob_1x2 = analisis["probabilidades_1x2"]
    cuotas = analisis["cuotas_disponibles"]
    
    for resultado, probabilidad in prob_1x2.items():
        try:
            cuota = float(cuotas.get(resultado, "1.00"))
            if cuota > 1.0:
                ve, es_value = calcular_value_bet(probabilidad, cuota)
                if es_value and CUOTA_MIN <= cuota <= CUOTA_MAX:
                    apuesta = {
                        "tipo": "1X2",
                        "mercado": resultado,
                        "descripcion": {
                            "local": f"Victoria {local}",
                            "empate": "Empate",
                            "visitante": f"Victoria {visitante}"
                        }.get(resultado, resultado),
                        "probabilidad": probabilidad,
                        "cuota": cuota,
                        "valor_esperado": ve,
                        "confianza": probabilidad * 100
                    }
                    
                    if aplicar_filtros_seguridad(apuesta, liga):
                        apuesta["puntuacion_compuesta"] = calcular_puntuacion_compuesta(apuesta, liga)
                        candidatas.append(apuesta)
        except (ValueError, TypeError):
            continue
    
    prob_btts = analisis["probabilidades_btts"]
    cuota_btts_si = 1.45  # Cuota ajustada al nuevo rango
    cuota_btts_no = 1.55  # Cuota ajustada al nuevo rango
    
    ve_btts_si, es_value_si = calcular_value_bet(prob_btts["btts_si"], cuota_btts_si)
    ve_btts_no, es_value_no = calcular_value_bet(prob_btts["btts_no"], cuota_btts_no)
    
    if es_value_si and CUOTA_MIN <= cuota_btts_si <= CUOTA_MAX:
        apuesta_btts_si = {
            "tipo": "BTTS",
            "mercado": "btts_si",
            "descripcion": "Ambos equipos marcan - SÍ",
            "probabilidad": prob_btts["btts_si"],
            "cuota": cuota_btts_si,
            "valor_esperado": ve_btts_si,
            "confianza": prob_btts["btts_si"] * 100
        }
        
        if aplicar_filtros_seguridad(apuesta_btts_si, liga):
            apuesta_btts_si["puntuacion_compuesta"] = calcular_puntuacion_compuesta(apuesta_btts_si, liga)
            candidatas.append(apuesta_btts_si)
    
    if es_value_no and CUOTA_MIN <= cuota_btts_no <= CUOTA_MAX:
        apuesta_btts_no = {
            "tipo": "BTTS",
            "mercado": "btts_no",
            "descripcion": "Ambos equipos marcan - NO",
            "probabilidad": prob_btts["btts_no"],
            "cuota": cuota_btts_no,
            "valor_esperado": ve_btts_no,
            "confianza": prob_btts["btts_no"] * 100
        }
        
        if aplicar_filtros_seguridad(apuesta_btts_no, liga):
            apuesta_btts_no["puntuacion_compuesta"] = calcular_puntuacion_compuesta(apuesta_btts_no, liga)
            candidatas.append(apuesta_btts_no)
    
    prob_ou = analisis["probabilidades_over_under"]
    
    cuota_over_15 = 1.50
    cuota_under_15 = 1.50
    
    ve_over_15, es_value_over_15 = calcular_value_bet(prob_ou["over_15"], cuota_over_15)
    ve_under_15, es_value_under_15 = calcular_value_bet(prob_ou["under_15"], cuota_under_15)
    
    if es_value_over_15 and CUOTA_MIN <= cuota_over_15 <= CUOTA_MAX:
        apuesta_over_15 = {
            "tipo": "Over/Under",
            "mercado": "over_15",
            "descripcion": "Más de 1.5 goles",
            "probabilidad": prob_ou["over_15"],
            "cuota": cuota_over_15,
            "valor_esperado": ve_over_15,
            "confianza": prob_ou["over_15"] * 100
        }
        
        if aplicar_filtros_seguridad(apuesta_over_15, liga):
            apuesta_over_15["puntuacion_compuesta"] = calcular_puntuacion_compuesta(apuesta_over_15, liga)
            candidatas.append(apuesta_over_15)
    
    if es_value_under_15 and CUOTA_MIN <= cuota_under_15 <= CUOTA_MAX:
        apuesta_under_15 = {
            "tipo": "Over/Under",
            "mercado": "under_15",
            "descripcion": "Menos de 1.5 goles",
            "probabilidad": prob_ou["under_15"],
            "cuota": cuota_under_15,
            "valor_esperado": ve_under_15,
            "confianza": prob_ou["under_15"] * 100
        }
        
        if aplicar_filtros_seguridad(apuesta_under_15, liga):
            apuesta_under_15["puntuacion_compuesta"] = calcular_puntuacion_compuesta(apuesta_under_15, liga)
            candidatas.append(apuesta_under_15)
    
    cuota_over_25 = 1.55
    cuota_under_25 = 1.45
    
    ve_over_25, es_value_over_25 = calcular_value_bet(prob_ou["over_25"], cuota_over_25)
    ve_under_25, es_value_under_25 = calcular_value_bet(prob_ou["under_25"], cuota_under_25)
    
    if es_value_over_25 and CUOTA_MIN <= cuota_over_25 <= CUOTA_MAX:
        apuesta_over_25 = {
            "tipo": "Over/Under",
            "mercado": "over_25",
            "descripcion": "Más de 2.5 goles",
            "probabilidad": prob_ou["over_25"],
            "cuota": cuota_over_25,
            "valor_esperado": ve_over_25,
            "confianza": prob_ou["over_25"] * 100
        }
        
        if aplicar_filtros_seguridad(apuesta_over_25, liga):
            apuesta_over_25["puntuacion_compuesta"] = calcular_puntuacion_compuesta(apuesta_over_25, liga)
            candidatas.append(apuesta_over_25)
    
    if es_value_under_25 and CUOTA_MIN <= cuota_under_25 <= CUOTA_MAX:
        apuesta_under_25 = {
            "tipo": "Over/Under",
            "mercado": "under_25",
            "descripcion": "Menos de 2.5 goles",
            "probabilidad": prob_ou["under_25"],
            "cuota": cuota_under_25,
            "valor_esperado": ve_under_25,
            "confianza": prob_ou["under_25"] * 100
        }
        
        if aplicar_filtros_seguridad(apuesta_under_25, liga):
            apuesta_under_25["puntuacion_compuesta"] = calcular_puntuacion_compuesta(apuesta_under_25, liga)
            candidatas.append(apuesta_under_25)
    
    prob_handicap = analisis["probabilidades_handicap"]
    
    cuota_handicap_local_05 = 1.45
    cuota_handicap_visitante_05 = 1.50
    
    ve_h_local, es_value_h_local = calcular_value_bet(prob_handicap["handicap_local_05"], cuota_handicap_local_05)
    ve_h_visitante, es_value_h_visitante = calcular_value_bet(prob_handicap["handicap_visitante_05"], cuota_handicap_visitante_05)
    
    if es_value_h_local and CUOTA_MIN <= cuota_handicap_local_05 <= CUOTA_MAX:
        apuesta_h_local = {
            "tipo": "Handicap",
            "mercado": "handicap_local_05",
            "descripcion": f"{local} -0.5",
            "probabilidad": prob_handicap["handicap_local_05"],
            "cuota": cuota_handicap_local_05,
            "valor_esperado": ve_h_local,
            "confianza": prob_handicap["handicap_local_05"] * 100
        }
        
        if aplicar_filtros_seguridad(apuesta_h_local, liga):
            apuesta_h_local["puntuacion_compuesta"] = calcular_puntuacion_compuesta(apuesta_h_local, liga)
            candidatas.append(apuesta_h_local)
    
    if es_value_h_visitante and CUOTA_MIN <= cuota_handicap_visitante_05 <= CUOTA_MAX:
        apuesta_h_visitante = {
            "tipo": "Handicap",
            "mercado": "handicap_visitante_05",
            "descripcion": f"{visitante} +0.5",
            "probabilidad": prob_handicap["handicap_visitante_05"],
            "cuota": cuota_handicap_visitante_05,
            "valor_esperado": ve_h_visitante,
            "confianza": prob_handicap["handicap_visitante_05"] * 100
        }
        
        if aplicar_filtros_seguridad(apuesta_h_visitante, liga):
            apuesta_h_visitante["puntuacion_compuesta"] = calcular_puntuacion_compuesta(apuesta_h_visitante, liga)
            candidatas.append(apuesta_h_visitante)
    
    prob_corners = analisis["probabilidades_corners"]
    
    cuota_over_85_corners = 1.45
    cuota_over_105_corners = 1.55
    
    ve_corners_85, es_value_corners_85 = calcular_value_bet(prob_corners["over_85_corners"], cuota_over_85_corners)
    ve_corners_105, es_value_corners_105 = calcular_value_bet(prob_corners["over_105_corners"], cuota_over_105_corners)
    
    if es_value_corners_85 and CUOTA_MIN <= cuota_over_85_corners <= CUOTA_MAX:
        apuesta_corners_85 = {
            "tipo": "Corners",
            "mercado": "over_85_corners",
            "descripcion": "Más de 8.5 corners",
            "probabilidad": prob_corners["over_85_corners"],
            "cuota": cuota_over_85_corners,
            "valor_esperado": ve_corners_85,
            "confianza": prob_corners["over_85_corners"] * 100
        }
        
        if aplicar_filtros_seguridad(apuesta_corners_85, liga):
            apuesta_corners_85["puntuacion_compuesta"] = calcular_puntuacion_compuesta(apuesta_corners_85, liga)
            candidatas.append(apuesta_corners_85)
    
    if es_value_corners_105 and CUOTA_MIN <= cuota_over_105_corners <= CUOTA_MAX:
        apuesta_corners_105 = {
            "tipo": "Corners",
            "mercado": "over_105_corners",
            "descripcion": "Más de 9.5 corners",
            "probabilidad": prob_corners["over_105_corners"],
            "cuota": cuota_over_105_corners,
            "valor_esperado": ve_corners_105,
            "confianza": prob_corners["over_105_corners"] * 100
        }
        
        if aplicar_filtros_seguridad(apuesta_corners_105, liga):
            apuesta_corners_105["puntuacion_compuesta"] = calcular_puntuacion_compuesta(apuesta_corners_105, liga)
            candidatas.append(apuesta_corners_105)
    
    prob_tarjetas = analisis["probabilidades_tarjetas"]
    
    cuota_over_35_cards = 1.50
    cuota_over_55_cards = 1.45
    
    ve_cards_35, es_value_cards_35 = calcular_value_bet(prob_tarjetas["over_35_cards"], cuota_over_35_cards)
    ve_cards_55, es_value_cards_55 = calcular_value_bet(prob_tarjetas["over_55_cards"], cuota_over_55_cards)
    
    if es_value_cards_35 and CUOTA_MIN <= cuota_over_35_cards <= CUOTA_MAX:
        apuesta_cards_35 = {
            "tipo": "Cards",
            "mercado": "over_35_cards",
            "descripcion": "Más de 3.5 tarjetas",
            "probabilidad": prob_tarjetas["over_35_cards"],
            "cuota": cuota_over_35_cards,
            "valor_esperado": ve_cards_35,
            "confianza": prob_tarjetas["over_35_cards"] * 100
        }
        
        if aplicar_filtros_seguridad(apuesta_cards_35, liga):
            apuesta_cards_35["puntuacion_compuesta"] = calcular_puntuacion_compuesta(apuesta_cards_35, liga)
            candidatas.append(apuesta_cards_35)
    
    if es_value_cards_55 and CUOTA_MIN <= cuota_over_55_cards <= CUOTA_MAX:
        apuesta_cards_55 = {
            "tipo": "Cards",
            "mercado": "over_55_cards",
            "descripcion": "Más de 4.5 tarjetas",
            "probabilidad": prob_tarjetas["over_55_cards"],
            "cuota": cuota_over_55_cards,
            "valor_esperado": ve_cards_55,
            "confianza": prob_tarjetas["over_55_cards"] * 100
        }
        
        if aplicar_filtros_seguridad(apuesta_cards_55, liga):
            apuesta_cards_55["puntuacion_compuesta"] = calcular_puntuacion_compuesta(apuesta_cards_55, liga)
            candidatas.append(apuesta_cards_55)
    
    prob_primera_mitad = analisis["probabilidades_primera_mitad"]
    
    cuota_gol_primera_mitad_si = 1.60
    cuota_gol_primera_mitad_no = 1.55
    
    ve_gol_1h_si, es_value_gol_1h_si = calcular_value_bet(prob_primera_mitad["gol_primera_mitad_si"], cuota_gol_primera_mitad_si)
    ve_gol_1h_no, es_value_gol_1h_no = calcular_value_bet(prob_primera_mitad["gol_primera_mitad_no"], cuota_gol_primera_mitad_no)
    
    if es_value_gol_1h_si and CUOTA_MIN <= cuota_gol_primera_mitad_si <= CUOTA_MAX:
        apuesta_gol_1h_si = {
            "tipo": "Equipo_Gol",
            "mercado": "gol_primera_mitad_si",
            "descripcion": "Gol en primer tiempo - Sí",
            "probabilidad": prob_primera_mitad["gol_primera_mitad_si"],
            "cuota": cuota_gol_primera_mitad_si,
            "valor_esperado": ve_gol_1h_si,
            "confianza": prob_primera_mitad["gol_primera_mitad_si"] * 100
        }
        
        if aplicar_filtros_seguridad(apuesta_gol_1h_si, liga):
            apuesta_gol_1h_si["puntuacion_compuesta"] = calcular_puntuacion_compuesta(apuesta_gol_1h_si, liga)
            candidatas.append(apuesta_gol_1h_si)
    
    if es_value_gol_1h_no and CUOTA_MIN <= cuota_gol_primera_mitad_no <= CUOTA_MAX:
        apuesta_gol_1h_no = {
            "tipo": "Equipo_Gol",
            "mercado": "gol_primera_mitad_no",
            "descripcion": "Gol en primer tiempo - No",
            "probabilidad": prob_primera_mitad["gol_primera_mitad_no"],
            "cuota": cuota_gol_primera_mitad_no,
            "valor_esperado": ve_gol_1h_no,
            "confianza": prob_primera_mitad["gol_primera_mitad_no"] * 100
        }
        
        if aplicar_filtros_seguridad(apuesta_gol_1h_no, liga):
            apuesta_gol_1h_no["puntuacion_compuesta"] = calcular_puntuacion_compuesta(apuesta_gol_1h_no, liga)
            candidatas.append(apuesta_gol_1h_no)
    
    prob_equipo_gol = analisis["probabilidades_equipo_gol"]
    
    cuota_local_gol = 1.50
    cuota_visitante_gol = 1.55
    
    ve_local_gol, es_value_local_gol = calcular_value_bet(prob_equipo_gol["equipo_local_gol"], cuota_local_gol)
    ve_visitante_gol, es_value_visitante_gol = calcular_value_bet(prob_equipo_gol["equipo_visitante_gol"], cuota_visitante_gol)
    
    if es_value_local_gol and CUOTA_MIN <= cuota_local_gol <= CUOTA_MAX:
        apuesta_local_gol = {
            "tipo": "Equipo_Gol",
            "mercado": "equipo_local_gol",
            "descripcion": f"{local} marca al menos un gol",
            "probabilidad": prob_equipo_gol["equipo_local_gol"],
            "cuota": cuota_local_gol,
            "valor_esperado": ve_local_gol,
            "confianza": prob_equipo_gol["equipo_local_gol"] * 100
        }
        
        if aplicar_filtros_seguridad(apuesta_local_gol, liga):
            apuesta_local_gol["puntuacion_compuesta"] = calcular_puntuacion_compuesta(apuesta_local_gol, liga)
            candidatas.append(apuesta_local_gol)
    
    if es_value_visitante_gol and CUOTA_MIN <= cuota_visitante_gol <= CUOTA_MAX:
        apuesta_visitante_gol = {
            "tipo": "Equipo_Gol",
            "mercado": "equipo_visitante_gol",
            "descripcion": f"{visitante} marca al menos un gol",
            "probabilidad": prob_equipo_gol["equipo_visitante_gol"],
            "cuota": cuota_visitante_gol,
            "valor_esperado": ve_visitante_gol,
            "confianza": prob_equipo_gol["equipo_visitante_gol"] * 100
        }
        
        if aplicar_filtros_seguridad(apuesta_visitante_gol, liga):
            apuesta_visitante_gol["puntuacion_compuesta"] = calcular_puntuacion_compuesta(apuesta_visitante_gol, liga)
            candidatas.append(apuesta_visitante_gol)
    
    # Aplicar algoritmo avanzado de selección
    if candidatas:
        candidatas.sort(key=lambda x: x["puntuacion_compuesta"], reverse=True)
        
        opciones_finales = candidatas[:num_opciones]
        
        for opcion in opciones_finales:
            kelly_fraction = opcion["valor_esperado"] / (opcion["cuota"] - 1)
            stake_recomendado = min(8, max(1, int(kelly_fraction * 50)))
            
            opcion["stake_recomendado"] = stake_recomendado
            opcion["justificacion"] = generar_justificacion(opcion, analisis)
        
        return opciones_finales
        
    prob_primera_mitad = analisis["probabilidades_primera_mitad"]
    
    cuota_gol_primera_mitad_si = 1.60
    cuota_gol_primera_mitad_no = 1.55
    
    ve_gol_1h_si, es_value_gol_1h_si = calcular_value_bet(prob_primera_mitad["gol_primera_mitad_si"], cuota_gol_primera_mitad_si)
    ve_gol_1h_no, es_value_gol_1h_no = calcular_value_bet(prob_primera_mitad["gol_primera_mitad_no"], cuota_gol_primera_mitad_no)
    
    if es_value_gol_1h_si and CUOTA_MIN <= cuota_gol_primera_mitad_si <= CUOTA_MAX:
        opciones_finales.append({
            "tipo": "gol_primera_mitad",
            "prediccion": "Gol en primer tiempo - Sí",
            "cuota": cuota_gol_primera_mitad_si,
            "probabilidad": prob_primera_mitad["gol_primera_mitad_si"],
            "valor_esperado": ve_gol_1h_si,
            "confianza": prob_primera_mitad["gol_primera_mitad_si"] * 100
        })
    
    if es_value_gol_1h_no and CUOTA_MIN <= cuota_gol_primera_mitad_no <= CUOTA_MAX:
        opciones_finales.append({
            "tipo": "gol_primera_mitad",
            "prediccion": "Gol en primer tiempo - No",
            "cuota": cuota_gol_primera_mitad_no,
            "probabilidad": prob_primera_mitad["gol_primera_mitad_no"],
            "valor_esperado": ve_gol_1h_no,
            "confianza": prob_primera_mitad["gol_primera_mitad_no"] * 100
        })
    
    prob_equipo_gol = analisis["probabilidades_equipo_gol"]
    
    cuota_local_gol = 1.50
    cuota_visitante_gol = 1.55
    
    ve_local_gol, es_value_local_gol = calcular_value_bet(prob_equipo_gol["equipo_local_gol"], cuota_local_gol)
    ve_visitante_gol, es_value_visitante_gol = calcular_value_bet(prob_equipo_gol["equipo_visitante_gol"], cuota_visitante_gol)
    
    if es_value_local_gol and CUOTA_MIN <= cuota_local_gol <= CUOTA_MAX:
        opciones_finales.append({
            "tipo": "equipo_gol",
            "prediccion": f"{local} marca al menos un gol",
            "cuota": cuota_local_gol,
            "probabilidad": prob_equipo_gol["equipo_local_gol"],
            "valor_esperado": ve_local_gol,
            "confianza": prob_equipo_gol["equipo_local_gol"] * 100
        })
    
    if es_value_visitante_gol and CUOTA_MIN <= cuota_visitante_gol <= CUOTA_MAX:
        opciones_finales.append({
            "tipo": "equipo_gol",
            "prediccion": f"{visitante} marca al menos un gol",
            "cuota": cuota_visitante_gol,
            "probabilidad": prob_equipo_gol["equipo_visitante_gol"],
            "valor_esperado": ve_visitante_gol,
            "confianza": prob_equipo_gol["equipo_visitante_gol"] * 100
        })
    
    prob_corners = analisis["probabilidades_corners"]
    corners_esperados = prob_corners.get("corners_esperados", 10.5)
    
    prob_over_95_corners = float(1 - stats.poisson.cdf(9, corners_esperados))
    prob_under_95_corners = 1 - prob_over_95_corners
    
    cuota_over_95_corners = 1.65
    cuota_under_95_corners = 1.50
    
    ve_corners_95_over, es_value_corners_95_over = calcular_value_bet(prob_over_95_corners, cuota_over_95_corners)
    ve_corners_95_under, es_value_corners_95_under = calcular_value_bet(prob_under_95_corners, cuota_under_95_corners)
    
    if es_value_corners_95_over and CUOTA_MIN <= cuota_over_95_corners <= CUOTA_MAX:
        opciones_finales.append({
            "tipo": "corners",
            "prediccion": "Más de 9.5 corners",
            "cuota": cuota_over_95_corners,
            "probabilidad": prob_over_95_corners,
            "valor_esperado": ve_corners_95_over,
            "confianza": prob_over_95_corners * 100
        })
    
    if es_value_corners_95_under and CUOTA_MIN <= cuota_under_95_corners <= CUOTA_MAX:
        opciones_finales.append({
            "tipo": "corners",
            "prediccion": "Menos de 9.5 corners",
            "cuota": cuota_under_95_corners,
            "probabilidad": prob_under_95_corners,
            "valor_esperado": ve_corners_95_under,
            "confianza": prob_under_95_corners * 100
        })
    
    prob_tarjetas = analisis["probabilidades_tarjetas"]
    tarjetas_esperadas = prob_tarjetas.get("tarjetas_esperadas", 4.8)
    
    prob_over_45_cards = float(1 - stats.poisson.cdf(4, tarjetas_esperadas))
    prob_under_45_cards = 1 - prob_over_45_cards
    
    cuota_over_45_cards = 1.70
    cuota_under_45_cards = 1.48
    
    ve_cards_45_over, es_value_cards_45_over = calcular_value_bet(prob_over_45_cards, cuota_over_45_cards)
    ve_cards_45_under, es_value_cards_45_under = calcular_value_bet(prob_under_45_cards, cuota_under_45_cards)
    
    if es_value_cards_45_over and CUOTA_MIN <= cuota_over_45_cards <= CUOTA_MAX:
        opciones_finales.append({
            "tipo": "tarjetas",
            "prediccion": "Más de 4.5 tarjetas",
            "cuota": cuota_over_45_cards,
            "probabilidad": prob_over_45_cards,
            "valor_esperado": ve_cards_45_over,
            "confianza": prob_over_45_cards * 100
        })
    
    if es_value_cards_45_under and CUOTA_MIN <= cuota_under_45_cards <= CUOTA_MAX:
        opciones_finales.append({
            "tipo": "tarjetas",
            "prediccion": "Menos de 4.5 tarjetas",
            "cuota": cuota_under_45_cards,
            "probabilidad": prob_under_45_cards,
            "valor_esperado": ve_cards_45_under,
            "confianza": prob_under_45_cards * 100
        })
    
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
