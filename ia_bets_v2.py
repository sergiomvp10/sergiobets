"""
ALGORITMO V2 - BetGeniuX Experimental Engine
==============================================
Motor de pronosticos experimental enfocado en RENTABILIDAD MAXIMA.

Filosofia V2:
  "Menos picks, mejor seleccion, cuotas mas altas = mas dinero"

Diferencias clave vs V1:
  1. ELIMINA apuestas defensivas (under goles, under corners, etc.)
  2. PRIORIZA mercados con logica real:
     - Ganador (1X2): solo cuando hay ventaja clara de forma/H2H
     - BTTS SI: equipos goleadores con defensas permeables
     - Over Goles: partidos con historial de muchos goles
     - Corners Over: equipos con estilo ofensivo/presion alta
     - Tarjetas Over: rivales historicos, arbitros estrictos
     - Double Chance: cuando hay valor pero incertidumbre en el exacto
  3. SCORING inteligente por tipo de mercado
  4. CUOTAS altas: min 1.65, rango prioritario 1.75-2.10
  5. MAX 3 picks/dia (configurable)
  6. DIVERSIFICACION: no repetir el mismo tipo de mercado

NO MODIFICA ia_bets.py — archivo completamente independiente.
"""

import json
import os
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from scipy import stats

# ── V2 Configuration ────────────────────────────────────────
V2_ODDS_MIN = 1.65             # Cuota minima absoluta
V2_ODDS_PRIORITY_MIN = 1.75    # Rango prioritario inferior
V2_ODDS_PRIORITY_MAX = 2.10    # Rango prioritario superior
V2_ODDS_MAX = 2.80             # Cuota maxima absoluta
V2_EV_OVERRIDE_THRESHOLD = 0.15  # 15% EV para override fuera del rango
V2_EV_MIN = 0.08              # 8% EV minimo (mas estricto que V1)
V2_MAX_PICKS = 3               # Maximo picks por dia
V2_MAX_SAME_MARKET = 2         # Maximo picks del mismo tipo de mercado

# Mercados PROHIBIDOS en V2 (apuestas defensivas / perezosas)
V2_MERCADOS_PROHIBIDOS = {
    "under_05", "under_15", "under_25", "under_35", "under_45", "under_55",
    "under_85", "under_95", "under_105", "under_115",
    "under_35_cards", "under_45_cards", "under_55_cards",
    "under_05_1h", "under_15_1h", "under_25_1h",
    "under_05_2h", "under_15_2h", "under_25_2h",
    "result_x", "result_x_1h", "result_x_2h",
}

# Umbrales de confianza MINIMA por tipo de mercado
V2_CONFIDENCE_THRESHOLDS = {
    "1X2": 0.48,
    "BTTS": 0.55,
    "Over/Under": 0.52,
    "1H": 0.45,
    "2H": 0.45,
    "DC": 0.62,
    "Corners": 0.50,
    "Tarjetas": 0.50,
    "Handicap": 0.45,
}

# Peso de cada factor en el scoring por tipo de mercado
# [ev_weight, context_weight, prob_weight, range_bonus_weight]
V2_MARKET_WEIGHTS = {
    "1X2":        [0.30, 0.35, 0.20, 0.15],
    "BTTS":       [0.35, 0.30, 0.20, 0.15],
    "Over/Under": [0.30, 0.30, 0.25, 0.15],
    "1H":         [0.35, 0.25, 0.25, 0.15],
    "2H":         [0.35, 0.25, 0.25, 0.15],
    "DC":         [0.25, 0.30, 0.30, 0.15],
    "Corners":    [0.30, 0.35, 0.20, 0.15],
    "Tarjetas":   [0.30, 0.35, 0.20, 0.15],
    "Handicap":   [0.30, 0.30, 0.25, 0.15],
}

# ── Reutilizamos funciones de analisis de ia_bets ───────────
from ia_bets import (
    generar_semilla_partido,
    es_liga_conocida,
    calcular_probabilidades_1x2,
    calcular_probabilidades_btts,
    calcular_probabilidades_over_under,
    calcular_probabilidades_primera_mitad,
    calcular_probabilidades_tarjetas,
    calcular_probabilidades_corners,
    calcular_probabilidades_handicap,
    analizar_rendimiento_equipos,
    analizar_partido_completo,
    _log_to_file,
    LIGAS_CONOCIDAS,
)

_cache_predicciones_v2 = {}


def limpiar_cache_predicciones_v2():
    """Limpia el cache de predicciones V2"""
    global _cache_predicciones_v2
    _cache_predicciones_v2.clear()


def cargar_configuracion_v2():
    """Carga configuracion V2 desde config_app.json (si existe)"""
    try:
        from json_storage import cargar_json
        config = cargar_json("config_app.json")
        if config and "v2_odds_min" in config:
            return {
                "odds_min": config.get("v2_odds_min", V2_ODDS_MIN),
                "odds_pri_min": config.get("v2_odds_priority_min", V2_ODDS_PRIORITY_MIN),
                "odds_pri_max": config.get("v2_odds_priority_max", V2_ODDS_PRIORITY_MAX),
                "odds_max": config.get("v2_odds_max", V2_ODDS_MAX),
                "ev_min": config.get("v2_ev_min", V2_EV_MIN),
                "max_picks": config.get("v2_max_picks", V2_MAX_PICKS),
            }
    except Exception:
        pass
    return {
        "odds_min": V2_ODDS_MIN,
        "odds_pri_min": V2_ODDS_PRIORITY_MIN,
        "odds_pri_max": V2_ODDS_PRIORITY_MAX,
        "odds_max": V2_ODDS_MAX,
        "ev_min": V2_EV_MIN,
        "max_picks": V2_MAX_PICKS,
    }


# ═══════════════════════════════════════════════════════════════
#  ANALISIS CONTEXTUAL POR TIPO DE MERCADO
# ═══════════════════════════════════════════════════════════════

def _analizar_contexto_1x2(analisis: Dict[str, Any], mercado: str) -> float:
    """
    Analisis contextual para Ganador (1X2).
    Factores: forma diferencial, H2H, localia, consistencia.
    """
    rend = analisis.get("rendimiento_equipos", {})
    forma_local = rend.get("forma_local", 0.5)
    forma_visit = rend.get("forma_visitante", 0.5)
    h2h_goles = rend.get("h2h_goles_total", 2.7)

    if mercado == "local":
        forma_diff = forma_local - forma_visit
        localia_bonus = 0.12
        score = 0.5 + (forma_diff * 0.8) + localia_bonus
        if h2h_goles > 2.5:
            score += 0.05
    elif mercado == "visitante":
        forma_diff = forma_visit - forma_local
        penalizacion = -0.08
        score = 0.5 + (forma_diff * 0.8) + penalizacion
        if forma_diff > 0.15:
            score += 0.10
    else:
        return 0.0

    return max(0.0, min(1.0, score))


def _analizar_contexto_btts(analisis: Dict[str, Any]) -> float:
    """
    Analisis contextual para BTTS (Ambos Marcan).
    Factores: goles promedio de ambos, defensas permeables, H2H, goles esperados.
    """
    rend = analisis.get("rendimiento_equipos", {})
    goles_local = rend.get("goles_promedio_local", 1.3)
    goles_visit = rend.get("goles_promedio_visitante", 1.3)
    h2h_goles = rend.get("h2h_goles_total", 2.7)
    ou_data = analisis.get("probabilidades_over_under", {})
    goles_esperados = ou_data.get("goles_esperados", 2.7)

    min_goles = min(goles_local, goles_visit)
    score = 0.0

    if min_goles >= 1.2:
        score += 0.35
    elif min_goles >= 0.9:
        score += 0.20
    else:
        score += 0.05

    if goles_esperados >= 2.8:
        score += 0.25
    elif goles_esperados >= 2.3:
        score += 0.15
    else:
        score += 0.05

    if h2h_goles >= 3.0:
        score += 0.20
    elif h2h_goles >= 2.5:
        score += 0.12
    else:
        score += 0.05

    balance = 1.0 - abs(goles_local - goles_visit) / 2.0
    score += balance * 0.20

    return max(0.0, min(1.0, score))


def _analizar_contexto_over_goles(analisis: Dict[str, Any], linea: float) -> float:
    """
    Analisis contextual para Over Goles.
    Factores: margen sobre linea, potencia ofensiva, H2H, forma.
    """
    rend = analisis.get("rendimiento_equipos", {})
    goles_local = rend.get("goles_promedio_local", 1.3)
    goles_visit = rend.get("goles_promedio_visitante", 1.3)
    h2h_goles = rend.get("h2h_goles_total", 2.7)
    ou_data = analisis.get("probabilidades_over_under", {})
    goles_esperados = ou_data.get("goles_esperados", 2.7)

    margen = goles_esperados - linea
    if margen <= 0:
        return 0.1

    score = 0.0

    if margen >= 1.0:
        score += 0.35
    elif margen >= 0.5:
        score += 0.25
    else:
        score += 0.10

    potencia = goles_local + goles_visit
    if potencia >= 2.8:
        score += 0.25
    elif potencia >= 2.3:
        score += 0.15
    else:
        score += 0.05

    if h2h_goles > linea + 0.5:
        score += 0.20
    elif h2h_goles > linea:
        score += 0.10

    forma_local = rend.get("forma_local", 0.5)
    forma_visit = rend.get("forma_visitante", 0.5)
    if forma_local > 0.55 and forma_visit > 0.45:
        score += 0.20
    elif forma_local > 0.55 or forma_visit > 0.55:
        score += 0.10

    return max(0.0, min(1.0, score))


def _analizar_contexto_corners(analisis: Dict[str, Any], linea: float) -> float:
    """
    Analisis contextual para Corners Over.
    Factores: factor corners, estilo ofensivo, partido disputado, goles esperados.
    """
    rend = analisis.get("rendimiento_equipos", {})
    corners_factor = rend.get("corners_promedio", 1.0)
    forma_local = rend.get("forma_local", 0.5)
    forma_visit = rend.get("forma_visitante", 0.5)
    ou_data = analisis.get("probabilidades_over_under", {})
    goles_esperados = ou_data.get("goles_esperados", 2.7)

    score = 0.0

    if corners_factor >= 1.15:
        score += 0.30
    elif corners_factor >= 1.0:
        score += 0.20
    elif corners_factor >= 0.85:
        score += 0.10
    else:
        score += 0.02

    diff_forma = abs(forma_local - forma_visit)
    if diff_forma < 0.15:
        score += 0.25
    elif diff_forma < 0.25:
        score += 0.15
    else:
        score += 0.05

    if goles_esperados >= 2.8:
        score += 0.20
    elif goles_esperados >= 2.3:
        score += 0.12
    else:
        score += 0.05

    if forma_local > 0.5 and forma_visit > 0.4:
        score += 0.25
    elif forma_local > 0.5 or forma_visit > 0.5:
        score += 0.12

    penalty = max(0, (linea - 8.5) * 0.05)
    score -= penalty

    return max(0.0, min(1.0, score))


def _analizar_contexto_tarjetas(analisis: Dict[str, Any], linea: float) -> float:
    """
    Analisis contextual para Tarjetas Over.
    Factores: disciplina, intensidad, partido disputado, H2H.
    """
    rend = analisis.get("rendimiento_equipos", {})
    tarjetas_factor = rend.get("tarjetas_promedio", 1.0)
    forma_local = rend.get("forma_local", 0.5)
    forma_visit = rend.get("forma_visitante", 0.5)
    h2h_goles = rend.get("h2h_goles_total", 2.7)
    ventaja = rend.get("ventaja_local", 0)

    score = 0.0

    if tarjetas_factor >= 1.2:
        score += 0.30
    elif tarjetas_factor >= 1.0:
        score += 0.20
    elif tarjetas_factor >= 0.8:
        score += 0.10
    else:
        score += 0.02

    diff_forma = abs(forma_local - forma_visit)
    if diff_forma < 0.12:
        score += 0.30
    elif diff_forma < 0.22:
        score += 0.18
    else:
        score += 0.05

    if h2h_goles >= 3.0:
        score += 0.20
    elif h2h_goles >= 2.5:
        score += 0.12
    else:
        score += 0.05

    if abs(ventaja) < 0.15:
        score += 0.20
    elif abs(ventaja) < 0.25:
        score += 0.10

    penalty = max(0, (linea - 3.5) * 0.06)
    score -= penalty

    return max(0.0, min(1.0, score))


def _analizar_contexto_dc(analisis: Dict[str, Any], mercado: str) -> float:
    """
    Analisis contextual para Double Chance (1X, X2, 12).
    Factores: probabilidad combinada, forma, ventaja.
    """
    prob_1x2 = analisis.get("probabilidades_1x2", {})
    rend = analisis.get("rendimiento_equipos", {})
    forma_local = rend.get("forma_local", 0.5)
    forma_visit = rend.get("forma_visitante", 0.5)

    score = 0.0

    if mercado == "1x":
        prob_combinada = prob_1x2.get("local", 0.33) + prob_1x2.get("empate", 0.33)
        if forma_local > forma_visit and forma_local > 0.5:
            score += 0.30
        else:
            score += 0.10
    elif mercado == "x2":
        prob_combinada = prob_1x2.get("empate", 0.33) + prob_1x2.get("visitante", 0.33)
        if forma_visit > forma_local and forma_visit > 0.5:
            score += 0.30
        else:
            score += 0.10
    elif mercado == "12":
        prob_combinada = prob_1x2.get("local", 0.33) + prob_1x2.get("visitante", 0.33)
        if forma_local > 0.5 and forma_visit > 0.45:
            score += 0.25
        else:
            score += 0.10
    else:
        return 0.0

    if prob_combinada >= 0.72:
        score += 0.35
    elif prob_combinada >= 0.62:
        score += 0.25
    else:
        score += 0.10

    ventaja = rend.get("ventaja_local", 0)
    if abs(ventaja) > 0.15:
        score += 0.20
    elif abs(ventaja) > 0.08:
        score += 0.10

    return max(0.0, min(1.0, score))


def _analizar_contexto_handicap(analisis: Dict[str, Any], mercado: str) -> float:
    """Analisis contextual para Handicap Asiatico."""
    rend = analisis.get("rendimiento_equipos", {})
    forma_local = rend.get("forma_local", 0.5)
    forma_visit = rend.get("forma_visitante", 0.5)
    ventaja = rend.get("ventaja_local", 0)
    h2h_goles = rend.get("h2h_goles_total", 2.7)

    score = 0.0
    es_local = "home" in mercado
    es_minus = "minus" in mercado

    if es_local and es_minus:
        if ventaja > 0.20:
            score += 0.40
        elif ventaja > 0.10:
            score += 0.25
        else:
            score += 0.05
    elif not es_local and es_minus:
        if ventaja < -0.20:
            score += 0.35
        elif ventaja < -0.10:
            score += 0.20
        else:
            score += 0.05
    elif es_local and not es_minus:
        if abs(ventaja) < 0.15:
            score += 0.30
        else:
            score += 0.10
    else:
        if abs(ventaja) < 0.15:
            score += 0.30
        else:
            score += 0.10

    if h2h_goles >= 2.8:
        score += 0.25
    else:
        score += 0.10

    forma_fav = forma_local if es_local else forma_visit
    if forma_fav > 0.6:
        score += 0.25
    elif forma_fav > 0.5:
        score += 0.15

    return max(0.0, min(1.0, score))


def _analizar_contexto_1h_2h(analisis: Dict[str, Any], periodo: str, mercado: str) -> float:
    """Analisis contextual para Primera/Segunda Mitad (solo over y ganador)."""
    rend = analisis.get("rendimiento_equipos", {})
    forma_local = rend.get("forma_local", 0.5)
    forma_visit = rend.get("forma_visitante", 0.5)

    if periodo == "1H":
        pm_data = analisis.get("probabilidades_primera_mitad", {})
        goles_esp = pm_data.get("goles_esperados_1h", 1.2)
    else:
        pm_data = analisis.get("probabilidades_segunda_mitad", {})
        goles_esp = pm_data.get("goles_2h_esperados", 1.3)

    score = 0.0

    if "over" in mercado:
        try:
            num = mercado.replace("over_", "").replace("_1h", "").replace("_2h", "")
            linea = float(num) / 10.0 if len(num) <= 2 else float(num)
        except (ValueError, IndexError):
            linea = 0.5

        margen = goles_esp - linea
        if margen > 0.5:
            score += 0.40
        elif margen > 0.2:
            score += 0.25
        else:
            score += 0.08

        if forma_local > 0.5 and forma_visit > 0.4:
            score += 0.30
        else:
            score += 0.10

        if goles_esp >= 1.5:
            score += 0.20
        elif goles_esp >= 1.0:
            score += 0.10

    elif "result_1" in mercado or "result_2" in mercado:
        ventaja = rend.get("ventaja_local", 0)
        if "result_1" in mercado:
            if ventaja > 0.15:
                score += 0.35
            elif ventaja > 0.05:
                score += 0.20
            else:
                score += 0.05
        else:
            if ventaja < -0.15:
                score += 0.35
            elif ventaja < -0.05:
                score += 0.20
            else:
                score += 0.05

        forma_fav = forma_local if "result_1" in mercado else forma_visit
        if forma_fav > 0.6:
            score += 0.30
        elif forma_fav > 0.5:
            score += 0.15

        score += 0.15

    return max(0.0, min(1.0, score))


# ═══════════════════════════════════════════════════════════════
#  MOTOR DE SCORING V2
# ═══════════════════════════════════════════════════════════════

def _obtener_contexto_mercado(analisis: Dict[str, Any], tipo: str, mercado: str) -> float:
    """Router: obtiene el score contextual para cualquier tipo de mercado"""
    if tipo == "1X2":
        return _analizar_contexto_1x2(analisis, mercado)
    elif tipo == "BTTS":
        return _analizar_contexto_btts(analisis)
    elif tipo == "Over/Under":
        try:
            num = mercado.replace("over_", "")
            linea = float(num) / 10.0
        except (ValueError, AttributeError):
            linea = 2.5
        return _analizar_contexto_over_goles(analisis, linea)
    elif tipo == "Corners":
        try:
            num = mercado.replace("over_", "")
            linea = float(num) / 10.0
        except (ValueError, AttributeError):
            linea = 9.5
        return _analizar_contexto_corners(analisis, linea)
    elif tipo == "Tarjetas":
        try:
            num = mercado.replace("over_", "").replace("_cards", "")
            linea = float(num) / 10.0
        except (ValueError, AttributeError):
            linea = 4.5
        return _analizar_contexto_tarjetas(analisis, linea)
    elif tipo == "DC":
        return _analizar_contexto_dc(analisis, mercado)
    elif tipo == "Handicap":
        return _analizar_contexto_handicap(analisis, mercado)
    elif tipo in ("1H", "2H"):
        return _analizar_contexto_1h_2h(analisis, tipo, mercado)
    else:
        return 0.3


def _calcular_score_v2(tipo: str, cuota: float, ev: float, probabilidad: float,
                       contexto: float) -> float:
    """Scoring V2: combina EV, contexto, probabilidad, y bonus de rango."""
    cfg = cargar_configuracion_v2()
    weights = V2_MARKET_WEIGHTS.get(tipo, [0.30, 0.30, 0.25, 0.15])
    w_ev, w_ctx, w_prob, w_range = weights

    ev_score = min(ev / 0.40, 1.0)
    ctx_score = contexto
    prob_score = min(probabilidad / 0.80, 1.0)

    if cfg["odds_pri_min"] <= cuota <= cfg["odds_pri_max"]:
        range_bonus = 1.0
    elif cfg["odds_min"] <= cuota < cfg["odds_pri_min"]:
        range_bonus = 0.5
    elif cfg["odds_pri_max"] < cuota <= cfg["odds_max"]:
        range_bonus = 0.7
    else:
        range_bonus = 0.0

    return (ev_score * w_ev) + (ctx_score * w_ctx) + (prob_score * w_prob) + (range_bonus * w_range)


# ═══════════════════════════════════════════════════════════════
#  MOTOR DE SELECCION V2
# ═══════════════════════════════════════════════════════════════

def encontrar_mejores_apuestas_v2(analisis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Motor V2: Pipeline completo de seleccion de apuestas rentables.
    1. Genera mercados  2. Filtra prohibidos  3. Filtra cuota/EV
    4. Confianza por tipo  5. Scoring contextual  6. Diversifica  7. Top 3
    """
    candidatos = []
    cfg = cargar_configuracion_v2()
    cuotas_reales = analisis["cuotas_disponibles"]
    mercados_disponibles = _construir_mercados(analisis, cuotas_reales)

    for tipo_mercado, mercado, probabilidad, cuota_str, descripcion in mercados_disponibles:
        try:
            cuota_real = float(cuota_str)
            if cuota_real <= 1.0:
                continue

            # FILTRO 1: Mercados prohibidos
            if mercado.lower() in V2_MERCADOS_PROHIBIDOS:
                continue
            desc_lower = descripcion.lower()
            if "menos" in desc_lower or "under" in desc_lower:
                continue
            if "empate" in desc_lower and tipo_mercado in ("1X2", "1H", "2H"):
                continue

            # FILTRO 2: Cuota minima/maxima
            if cuota_real < cfg["odds_min"] or cuota_real > cfg["odds_max"]:
                continue

            # FILTRO 3: EV minimo
            ve = (probabilidad * cuota_real) - 1
            en_rango = cfg["odds_pri_min"] <= cuota_real <= cfg["odds_pri_max"]
            if en_rango:
                if ve < cfg["ev_min"]:
                    continue
            else:
                if ve < V2_EV_OVERRIDE_THRESHOLD:
                    continue

            # FILTRO 4: Confianza minima por tipo
            umbral = V2_CONFIDENCE_THRESHOLDS.get(tipo_mercado, 0.45)
            if probabilidad < umbral:
                continue

            # SCORING contextual
            contexto = _obtener_contexto_mercado(analisis, tipo_mercado, mercado)
            score = _calcular_score_v2(tipo_mercado, cuota_real, ve, probabilidad, contexto)

            candidatos.append({
                "tipo": tipo_mercado,
                "mercado": mercado,
                "descripcion": descripcion,
                "probabilidad": probabilidad,
                "cuota": cuota_real,
                "valor_esperado": ve,
                "edge_percentage": ve * 100,
                "confianza": probabilidad * 100,
                "stake_recomendado": min(10, max(1, int(abs(ve) * 50))),
                "source": "api",
                "score_v2": score,
                "contexto_score": contexto,
                "en_rango_prioritario": en_rango,
                "justificacion": "",
            })

        except (ValueError, TypeError):
            continue

    if not candidatos:
        return []

    candidatos.sort(key=lambda x: x["score_v2"], reverse=True)

    # DIVERSIFICACION: max 2 del mismo tipo
    seleccionados = []
    conteo_tipos = {}
    for c in candidatos:
        tipo = c["tipo"]
        count = conteo_tipos.get(tipo, 0)
        if count >= V2_MAX_SAME_MARKET:
            continue
        seleccionados.append(c)
        conteo_tipos[tipo] = count + 1
        if len(seleccionados) >= cfg["max_picks"]:
            break

    # POST-PROCESO: Kelly stake + justificaciones
    for pick in seleccionados:
        if pick["cuota"] > 1:
            kelly = pick["valor_esperado"] / (pick["cuota"] - 1)
            pick["stake_recomendado"] = min(10, max(1, int(kelly * 100)))
        pick["justificacion"] = _generar_justificacion_v2(pick, analisis)

    return seleccionados


def _construir_mercados(analisis: Dict[str, Any], cuotas_reales: Dict) -> List[tuple]:
    """Construye la lista de mercados V2 (solo ofensivos/rentables)"""
    parts = analisis['partido'].split(' vs ')
    loc = parts[0] if len(parts) > 1 else "Local"
    vis = parts[1] if len(parts) > 1 else "Visitante"

    return [
        # 1X2 (sin empate)
        ("1X2", "local", analisis["probabilidades_1x2"]["local"],
         cuotas_reales.get("local", "0"), f"Victoria {loc}"),
        ("1X2", "visitante", analisis["probabilidades_1x2"]["visitante"],
         cuotas_reales.get("visitante", "0"), f"Victoria {vis}"),
        # BTTS SI
        ("BTTS", "btts_si", analisis.get("probabilidades_btts", {}).get("btts_si", 0.5),
         cuotas_reales.get("btts_si", "0"), "Ambos equipos marcan - SI"),
        # Over Goles
        ("Over/Under", "over_15", analisis.get("probabilidades_over_under", {}).get("over_15", 0.8),
         cuotas_reales.get("over_15", "0"), "Mas de 1.5 goles"),
        ("Over/Under", "over_25", analisis.get("probabilidades_over_under", {}).get("over_25", 0.6),
         cuotas_reales.get("over_25", "0"), "Mas de 2.5 goles"),
        ("Over/Under", "over_35", analisis.get("probabilidades_over_under", {}).get("over_35", 0.4),
         cuotas_reales.get("over_35", "0"), "Mas de 3.5 goles"),
        ("Over/Under", "over_45", analisis.get("probabilidades_over_under", {}).get("over_45", 0.2),
         cuotas_reales.get("over_45", "0"), "Mas de 4.5 goles"),
        # 1H Over + Ganador
        ("1H", "over_05_1h", analisis.get("probabilidades_primera_mitad", {}).get("over_05_1h", 0.6),
         cuotas_reales.get("1h_over_05", "0"), "Mas de 0.5 goles 1H"),
        ("1H", "over_15_1h", analisis.get("probabilidades_primera_mitad", {}).get("over_15_1h", 0.3),
         cuotas_reales.get("1h_over_15", "0"), "Mas de 1.5 goles 1H"),
        ("1H", "result_1_1h", analisis.get("probabilidades_primera_mitad", {}).get("result_1_1h", 0.35),
         cuotas_reales.get("1h_result_1", "0"), f"Victoria {loc} 1H"),
        ("1H", "result_2_1h", analisis.get("probabilidades_primera_mitad", {}).get("result_2_1h", 0.35),
         cuotas_reales.get("1h_result_2", "0"), f"Victoria {vis} 1H"),
        # 2H Over + Ganador
        ("2H", "over_05_2h", analisis.get("probabilidades_segunda_mitad", {}).get("over_05_2h", 0.5),
         cuotas_reales.get("2h_over_05", "0"), "Mas de 0.5 goles 2H"),
        ("2H", "over_15_2h", analisis.get("probabilidades_segunda_mitad", {}).get("over_15_2h", 0.3),
         cuotas_reales.get("2h_over_15", "0"), "Mas de 1.5 goles 2H"),
        ("2H", "result_1_2h", analisis.get("probabilidades_segunda_mitad", {}).get("result_1_2h", 0.3),
         cuotas_reales.get("2h_result_1", "0"), f"Victoria {loc} 2H"),
        ("2H", "result_2_2h", analisis.get("probabilidades_segunda_mitad", {}).get("result_2_2h", 0.3),
         cuotas_reales.get("2h_result_2", "0"), f"Victoria {vis} 2H"),
        # Double Chance
        ("DC", "1x", analisis.get("probabilidades_double_chance", {}).get("dc_1x", 0.7),
         cuotas_reales.get("dc_1x", "0"), f"{loc} o Empate"),
        ("DC", "12", analisis.get("probabilidades_double_chance", {}).get("dc_12", 0.7),
         cuotas_reales.get("dc_12", "0"), f"{loc} o {vis}"),
        ("DC", "x2", analisis.get("probabilidades_double_chance", {}).get("dc_x2", 0.7),
         cuotas_reales.get("dc_x2", "0"), f"Empate o {vis}"),
        # Corners Over
        ("Corners", "over_85", analisis.get("probabilidades_corners", {}).get("over_85_corners", 0.6),
         cuotas_reales.get("corners_over_85", "0"), "Mas de 8.5 corners"),
        ("Corners", "over_95", analisis.get("probabilidades_corners", {}).get("over_105_corners", 0.5),
         cuotas_reales.get("corners_over_95", "0"), "Mas de 9.5 corners"),
        ("Corners", "over_105", analisis.get("probabilidades_corners", {}).get("over_105_corners", 0.4),
         cuotas_reales.get("corners_over_105", "0"), "Mas de 10.5 corners"),
        ("Corners", "over_115", analisis.get("probabilidades_corners", {}).get("over_115_corners", 0.3),
         cuotas_reales.get("corners_over_115", "0"), "Mas de 11.5 corners"),
        # Tarjetas Over
        ("Tarjetas", "over_35", analisis.get("probabilidades_tarjetas", {}).get("over_35_cards", 0.6),
         cuotas_reales.get("cards_over_35", "0"), "Mas de 3.5 tarjetas"),
        ("Tarjetas", "over_45", analisis.get("probabilidades_tarjetas", {}).get("over_45_cards", 0.4),
         cuotas_reales.get("cards_over_45", "0"), "Mas de 4.5 tarjetas"),
        ("Tarjetas", "over_55", analisis.get("probabilidades_tarjetas", {}).get("over_55_cards", 0.3),
         cuotas_reales.get("cards_over_55", "0"), "Mas de 5.5 tarjetas"),
        # Handicap
        ("Handicap", "home_minus_05", analisis.get("probabilidades_handicap", {}).get("handicap_local_05", 0.5),
         cuotas_reales.get("handicap_home_minus_05", "0"), f"{loc} -0.5"),
        ("Handicap", "home_plus_05", analisis.get("probabilidades_handicap", {}).get("handicap_local_05", 0.5),
         cuotas_reales.get("handicap_home_plus_05", "0"), f"{loc} +0.5"),
        ("Handicap", "away_minus_05", analisis.get("probabilidades_handicap", {}).get("handicap_visitante_05", 0.5),
         cuotas_reales.get("handicap_away_minus_05", "0"), f"{vis} -0.5"),
        ("Handicap", "away_plus_05", analisis.get("probabilidades_handicap", {}).get("handicap_visitante_05", 0.5),
         cuotas_reales.get("handicap_away_plus_05", "0"), f"{vis} +0.5"),
        ("Handicap", "home_minus_10", analisis.get("probabilidades_handicap", {}).get("handicap_local_10", 0.4),
         cuotas_reales.get("handicap_home_minus_10", "0"), f"{loc} -1.0"),
        ("Handicap", "away_minus_10", analisis.get("probabilidades_handicap", {}).get("handicap_visitante_10", 0.4),
         cuotas_reales.get("handicap_away_minus_10", "0"), f"{vis} -1.0"),
    ]


def _generar_justificacion_v2(pick: Dict[str, Any], analisis: Dict[str, Any]) -> str:
    """Genera justificacion V2 con analisis contextual detallado"""
    ve_pct = round(pick["valor_esperado"] * 100, 1)
    conf_pct = round(pick["confianza"], 1)
    cuota = pick["cuota"]
    ctx = round(pick.get("contexto_score", 0) * 100, 0)
    en_rango = pick.get("en_rango_prioritario", False)
    tipo = pick["tipo"]
    rend = analisis.get("rendimiento_equipos", {})

    tag = "PRIORITARIO" if en_rango else "EV OVERRIDE"
    base = f"[V2 {tag}] Cuota {cuota:.2f} | EV: +{ve_pct}% | Ctx: {ctx:.0f}%"

    detalles = {
        "1X2": (
            f"Forma: {rend.get('forma_local', 0.5):.2f} vs {rend.get('forma_visitante', 0.5):.2f} | "
            f"Ventaja: {rend.get('ventaja_local', 0):+.2f}"
        ),
        "BTTS": (
            f"Goles prom: {rend.get('goles_promedio_local', 1.3):.1f} + "
            f"{rend.get('goles_promedio_visitante', 1.3):.1f} | "
            f"H2H: {rend.get('h2h_goles_total', 2.7):.1f} goles"
        ),
        "Over/Under": (
            f"Goles esp: {analisis.get('probabilidades_over_under', {}).get('goles_esperados', 2.7):.1f} | "
            f"Ofensiva: {rend.get('goles_promedio_local', 1.3):.1f}+{rend.get('goles_promedio_visitante', 1.3):.1f}"
        ),
        "Corners": (
            f"Factor corners: {rend.get('corners_promedio', 1.0):.2f}x | "
            f"Estilo ofensivo: {'Si' if rend.get('forma_local', 0.5) > 0.5 else 'Moderado'}"
        ),
        "Tarjetas": (
            f"Factor disciplina: {rend.get('tarjetas_promedio', 1.0):.2f}x | "
            f"Intensidad: {'Alta' if abs(rend.get('ventaja_local', 0)) < 0.15 else 'Media'}"
        ),
        "DC": (
            f"Prob combinada alta | "
            f"Forma: {rend.get('forma_local', 0.5):.2f} vs {rend.get('forma_visitante', 0.5):.2f}"
        ),
        "Handicap": (
            f"Ventaja: {rend.get('ventaja_local', 0):+.2f} | "
            f"H2H goles: {rend.get('h2h_goles_total', 2.7):.1f}"
        ),
        "1H": f"Goles esp 1H: {analisis.get('probabilidades_primera_mitad', {}).get('goles_esperados_1h', 1.2):.1f}",
        "2H": f"Goles esp 2H: {analisis.get('probabilidades_segunda_mitad', {}).get('goles_2h_esperados', 1.3):.1f}",
    }

    detalle = detalles.get(tipo, "")
    if detalle:
        base += f" | {detalle}"

    return base


# ═══════════════════════════════════════════════════════════════
#  API PUBLICA - Funciones que usa el GUI
# ═══════════════════════════════════════════════════════════════

def generar_prediccion_v2(partido: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Genera prediccion con algoritmo V2"""
    try:
        analisis = analizar_partido_completo(partido)
        mejores = encontrar_mejores_apuestas_v2(analisis)

        if not mejores:
            return None

        if not es_liga_conocida(analisis["liga"]):
            return None

        mejor = mejores[0]

        return {
            "partido": analisis["partido"],
            "liga": analisis["liga"],
            "hora": analisis["hora"],
            "prediccion": mejor["descripcion"],
            "cuota": mejor["cuota"],
            "stake_recomendado": mejor["stake_recomendado"],
            "confianza": round(mejor["confianza"], 1),
            "valor_esperado": round(mejor["valor_esperado"], 3),
            "razon": mejor["justificacion"],
            "score_v2": round(mejor["score_v2"], 3),
            "contexto_score": round(mejor.get("contexto_score", 0), 3),
            "tipo_mercado": mejor["tipo"],
            "en_rango_prioritario": mejor["en_rango_prioritario"],
            "algoritmo": "v2",
            "opcion_numero": 1,
            "total_opciones": len(mejores),
        }
    except Exception as e:
        print(f"[V2] Error generando prediccion: {e}")
        return None


def filtrar_apuestas_inteligentes_v2(partidos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filtra picks V2 — menos picks, mayor rentabilidad.
    Maximo 3 picks por defecto (configurable).
    """
    predicciones_validas = []
    fecha = datetime.now().strftime('%Y-%m-%d')
    cfg = cargar_configuracion_v2()

    for partido in partidos:
        try:
            clave = f"{partido.get('local', '')}|{partido.get('visitante', '')}|{fecha}|v2"

            if clave in _cache_predicciones_v2:
                prediccion = _cache_predicciones_v2[clave]
            else:
                partido_con_fecha = {**partido, 'fecha': fecha}
                prediccion = generar_prediccion_v2(partido_con_fecha)
                if prediccion:
                    _cache_predicciones_v2[clave] = prediccion

            if prediccion:
                predicciones_validas.append(prediccion)
        except Exception as e:
            print(f"[V2] Error: {partido.get('local', '?')} vs {partido.get('visitante', '?')}: {e}")
            continue

    predicciones_validas.sort(key=lambda x: x.get("score_v2", 0), reverse=True)

    # Diversificacion global
    resultado = []
    conteo = {}
    for p in predicciones_validas:
        tipo = p.get("tipo_mercado", "")
        c = conteo.get(tipo, 0)
        if c >= V2_MAX_SAME_MARKET:
            continue
        resultado.append(p)
        conteo[tipo] = c + 1
        if len(resultado) >= cfg["max_picks"]:
            break

    return resultado


def generar_mensaje_v2(predicciones: List[Dict[str, Any]], fecha: str,
                       counter_numbers: Optional[List[int]] = None) -> str:
    """Genera mensaje Telegram para picks V2"""
    cfg = cargar_configuracion_v2()

    if not predicciones:
        return (
            f"BETGENIUX V2 ({fecha})\n\n"
            f"No se encontraron picks V2 para hoy.\n"
            f"Criterios: Cuotas {cfg['odds_pri_min']}-{cfg['odds_pri_max']}, "
            f"EV alto, max {cfg['max_picks']} picks."
        )

    if counter_numbers is None:
        try:
            from daily_counter import get_next_pronostico_numbers
            counter_numbers = get_next_pronostico_numbers(len(predicciones))
        except ImportError:
            counter_numbers = list(range(1, len(predicciones) + 1))

    mensaje = f"BETGENIUX V2 ({fecha})\n"
    mensaje += "Algoritmo experimental - Rentabilidad maxima\n\n"

    for i, pred in enumerate(predicciones):
        numero = counter_numbers[i] if i < len(counter_numbers) else i + 1
        rango_tag = "PRIORITARIO" if pred.get('en_rango_prioritario', False) else "EV ALTO"
        tipo = pred.get('tipo_mercado', '')

        mensaje += f"PRONOSTICO V2 #{numero} [{rango_tag}] [{tipo}]\n"
        mensaje += f"{pred['liga']}\n"
        mensaje += f"{pred['partido']}\n"
        mensaje += f"{pred['prediccion']}\n"
        mensaje += f"Cuota: {pred['cuota']} | Stake: {pred['stake_recomendado']}u\n"
        mensaje += f"Confianza: {pred['confianza']}% | EV: +{pred['valor_esperado']}\n"
        mensaje += f"{pred['hora']}\n\n"

    mensaje += "Apostar con responsabilidad\n"
    mensaje += (
        f"V2: Prioriza cuotas {cfg['odds_pri_min']}-{cfg['odds_pri_max']} | "
        f"Max {cfg['max_picks']} picks | Sin unders"
    )

    return mensaje
