import random
from typing import List, Dict, Any, Optional

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

def calcular_probabilidades(cuotas: Dict[str, str]) -> Dict[str, float]:
    try:
        local = float(cuotas.get("local", "1.00"))
        empate = float(cuotas.get("empate", "1.00"))
        visitante = float(cuotas.get("visitante", "1.00"))
        
        prob_local = 1 / local if local > 0 else 0
        prob_empate = 1 / empate if empate > 0 else 0
        prob_visitante = 1 / visitante if visitante > 0 else 0
        
        total = prob_local + prob_empate + prob_visitante
        
        if total > 0:
            probabilidades = {
                "local": prob_local / total,
                "empate": prob_empate / total,
                "visitante": prob_visitante / total
            }
        else:
            probabilidades = {"local": 0.33, "empate": 0.33, "visitante": 0.34}
        
        if cuotas.get('btts_si') and cuotas.get('btts_si') != 'N/A':
            try:
                btts_si = float(cuotas['btts_si'])
                btts_no = float(cuotas.get('btts_no', '2.0'))
                prob_btts_si = 1 / btts_si if btts_si > 0 else 0
                prob_btts_no = 1 / btts_no if btts_no > 0 else 0
                total_btts = prob_btts_si + prob_btts_no
                
                if total_btts > 0:
                    probabilidades["btts_si"] = prob_btts_si / total_btts
                    probabilidades["btts_no"] = prob_btts_no / total_btts
            except (ValueError, TypeError):
                pass
        
        if cuotas.get('over_25') and cuotas.get('over_25') != 'N/A':
            try:
                over_25 = float(cuotas['over_25'])
                under_25 = float(cuotas.get('under_25', '2.0'))
                prob_over = 1 / over_25 if over_25 > 0 else 0
                prob_under = 1 / under_25 if under_25 > 0 else 0
                total_ou = prob_over + prob_under
                
                if total_ou > 0:
                    probabilidades["over_25"] = prob_over / total_ou
                    probabilidades["under_25"] = prob_under / total_ou
            except (ValueError, TypeError):
                pass
        
        return probabilidades
        
    except (ValueError, TypeError):
        return {"local": 0.33, "empate": 0.33, "visitante": 0.34}

def analizar_partido(partido: Dict[str, Any]) -> Dict[str, Any]:
    cuotas = partido.get("cuotas", {})
    probabilidades = calcular_probabilidades(cuotas)
    
    mejor_opcion = max(probabilidades.items(), key=lambda x: x[1])
    resultado_predicho = mejor_opcion[0]
    confianza = mejor_opcion[1]
    
    try:
        cuota_predicha = float(cuotas.get(resultado_predicho, "1.00"))
    except (ValueError, TypeError):
        cuota_predicha = 1.00
    
    valor_esperado = (confianza * cuota_predicha) - 1
    
    return {
        "partido": f"{partido.get('local', 'Local')} vs {partido.get('visitante', 'Visitante')}",
        "liga": partido.get("liga", "Desconocida"),
        "prediccion": resultado_predicho,
        "cuota": cuota_predicha,
        "confianza": confianza,
        "valor_esperado": valor_esperado,
        "probabilidades": probabilidades
    }

def generar_prediccion(partido: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        analisis = analizar_partido(partido)
        
        if not es_liga_conocida(analisis["liga"]):
            return None
        
        if not (CUOTA_MIN <= analisis["cuota"] <= CUOTA_MAX):
            return None
        
        if analisis["valor_esperado"] <= 0:
            return None
        
        stake_recomendado = min(10, max(1, int(analisis["confianza"] * 15)))
        
        prediccion_texto = {
            "local": f"Victoria de {partido.get('local', 'Local')}",
            "visitante": f"Victoria de {partido.get('visitante', 'Visitante')}",
            "empate": "Empate"
        }.get(analisis["prediccion"], "Resultado incierto")
        
        return {
            "partido": analisis["partido"],
            "liga": analisis["liga"],
            "hora": partido.get("hora", "00:00"),
            "prediccion": prediccion_texto,
            "cuota": analisis["cuota"],
            "stake_recomendado": stake_recomendado,
            "confianza": round(analisis["confianza"] * 100, 1),
            "valor_esperado": round(analisis["valor_esperado"], 3),
            "razon": f"Cuota {analisis['cuota']} en rango óptimo, liga conocida"
        }
    except Exception as e:
        print(f"Error generando predicción para partido: {e}")
        return None

def filtrar_apuestas_inteligentes(partidos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    predicciones_validas = []
    
    for partido in partidos:
        try:
            prediccion = generar_prediccion(partido)
            if prediccion:
                predicciones_validas.append(prediccion)
        except Exception as e:
            print(f"Error procesando partido {partido.get('local', 'N/A')} vs {partido.get('visitante', 'N/A')}: {e}")
            continue
    
    predicciones_validas.sort(key=lambda x: x["valor_esperado"], reverse=True)
    
    return predicciones_validas[:5]

def generar_mensaje_ia(predicciones: List[Dict[str, Any]], fecha: str) -> str:
    if not predicciones:
        return f"🤖 IA SERGIOBETS - {fecha}\n\n❌ No se encontraron apuestas recomendadas para hoy.\nCriterios: Cuotas 1.50-1.75, ligas conocidas, valor esperado positivo."
    
    mensaje = f"🤖 IA SERGIOBETS - PICKS DEL DÍA ({fecha})\n\n"
    
    for i, pred in enumerate(predicciones, 1):
        mensaje += f"🎯 PICK #{i}\n"
        mensaje += f"🏆 {pred['liga']}\n"
        mensaje += f"⚽ {pred['partido']}\n"
        mensaje += f"🔮 {pred['prediccion']}\n"
        mensaje += f"💰 Cuota: {pred['cuota']} | Stake: {pred['stake_recomendado']}u\n"
        mensaje += f"📊 Confianza: {pred['confianza']}% | VE: {pred['valor_esperado']}\n"
        mensaje += f"⏰ {pred['hora']}\n\n"
    
    mensaje += "🧠 Predicciones generadas por IA basadas en análisis de cuotas y ligas.\n"
    mensaje += "⚠️ Apostar con responsabilidad."
    
    return mensaje

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
