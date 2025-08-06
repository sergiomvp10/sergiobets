#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ia_bets import (
    es_liga_conocida, 
    generar_prediccion, 
    analizar_partido_completo,
    encontrar_mejores_apuestas,
    calcular_value_bet,
    CUOTA_MIN,
    CUOTA_MAX
)
from footystats_api import obtener_partidos_del_dia
from league_utils import detectar_liga_por_imagen

def debug_salzburg_bruges():
    """Debug específico para el partido Salzburg vs Bruges"""
    print("🔍 DIAGNÓSTICO: Salzburg vs Bruges")
    print("=" * 50)
    
    print("\n1. VERIFICACIÓN DE LIGA:")
    liga_test = "Champions League"
    es_conocida = es_liga_conocida(liga_test)
    print(f"   Liga: {liga_test}")
    print(f"   ¿Es conocida?: {es_conocida}")
    
    print(f"\n2. RANGOS DE CUOTAS PERMITIDOS:")
    print(f"   Mínimo: {CUOTA_MIN}")
    print(f"   Máximo: {CUOTA_MAX}")
    
    print(f"\n3. SIMULACIÓN DEL PARTIDO:")
    partido_test = {
        "hora": "21:00",
        "liga": "Champions League",
        "local": "Red Bull Salzburg",
        "visitante": "Club Brugge",
        "cuotas": {
            "casa": "Bet365",
            "local": "2.10",    # Fuera del rango 1.30-1.60
            "empate": "3.40",   # Fuera del rango
            "visitante": "3.20" # Fuera del rango
        }
    }
    
    print(f"   Partido: {partido_test['local']} vs {partido_test['visitante']}")
    print(f"   Liga: {partido_test['liga']}")
    print(f"   Cuotas: Local={partido_test['cuotas']['local']}, Empate={partido_test['cuotas']['empate']}, Visitante={partido_test['cuotas']['visitante']}")
    
    print(f"\n4. ANÁLISIS DEL PARTIDO:")
    try:
        analisis = analizar_partido_completo(partido_test)
        print(f"   ✅ Análisis generado correctamente")
        print(f"   Liga detectada: {analisis['liga']}")
        print(f"   Cuotas disponibles: {analisis['cuotas_disponibles']}")
    except Exception as e:
        print(f"   ❌ Error en análisis: {e}")
        return
    
    print(f"\n5. BÚSQUEDA DE MEJORES APUESTAS:")
    try:
        mejores_apuestas = encontrar_mejores_apuestas(analisis, num_opciones=3)
        print(f"   Apuestas encontradas: {len(mejores_apuestas)}")
        
        if mejores_apuestas:
            for i, apuesta in enumerate(mejores_apuestas, 1):
                print(f"   Apuesta {i}:")
                print(f"     Tipo: {apuesta['tipo']}")
                print(f"     Descripción: {apuesta['descripcion']}")
                print(f"     Cuota: {apuesta['cuota']}")
                print(f"     Valor esperado: {apuesta['valor_esperado']:.3f}")
                print(f"     ¿En rango de cuotas?: {CUOTA_MIN <= apuesta['cuota'] <= CUOTA_MAX}")
        else:
            print(f"   ❌ No se encontraron apuestas válidas")
            
    except Exception as e:
        print(f"   ❌ Error buscando apuestas: {e}")
        return
    
    print(f"\n6. GENERACIÓN DE PREDICCIÓN:")
    try:
        prediccion = generar_prediccion(partido_test, opcion_numero=1)
        if prediccion:
            print(f"   ✅ Predicción generada:")
            print(f"     Partido: {prediccion['partido']}")
            print(f"     Liga: {prediccion['liga']}")
            print(f"     Predicción: {prediccion['prediccion']}")
            print(f"     Cuota: {prediccion['cuota']}")
            print(f"     Valor esperado: {prediccion['valor_esperado']}")
        else:
            print(f"   ❌ No se pudo generar predicción")
            
            print(f"\n   DIAGNÓSTICO DE FALLO:")
            
            if not es_liga_conocida(analisis["liga"]):
                print(f"     ❌ Liga no reconocida: {analisis['liga']}")
            else:
                print(f"     ✅ Liga reconocida: {analisis['liga']}")
            
            if not mejores_apuestas:
                print(f"     ❌ No hay apuestas que cumplan criterios de value betting")
                print(f"     Razones posibles:")
                print(f"       - Cuotas fuera del rango {CUOTA_MIN}-{CUOTA_MAX}")
                print(f"       - Valor esperado menor al 5%")
                print(f"       - Error en cálculo de probabilidades")
            else:
                print(f"     ✅ Hay {len(mejores_apuestas)} apuestas válidas")
                
    except Exception as e:
        print(f"   ❌ Error generando predicción: {e}")
    
    print(f"\n7. VERIFICACIÓN DE DATOS REALES DE LA API:")
    try:
        partidos_reales = obtener_partidos_del_dia()
        print(f"   Partidos obtenidos de la API: {len(partidos_reales)}")
        
        salzburg_match = None
        for partido in partidos_reales:
            local = partido.get('local', '').lower()
            visitante = partido.get('visitante', '').lower()
            if ('salzburg' in local or 'salzburg' in visitante or 
                'bruges' in local or 'bruges' in visitante or
                'brugge' in local or 'brugge' in visitante):
                salzburg_match = partido
                break
        
        if salzburg_match:
            print(f"   ✅ Partido encontrado en API:")
            print(f"     Local: {salzburg_match.get('local', 'N/A')}")
            print(f"     Visitante: {salzburg_match.get('visitante', 'N/A')}")
            print(f"     Liga: {salzburg_match.get('liga', 'N/A')}")
            print(f"     Cuotas: {salzburg_match.get('cuotas', 'N/A')}")
            
            liga_detectada = detectar_liga_por_imagen(
                salzburg_match.get('home_image', ''),
                salzburg_match.get('away_image', '')
            )
            print(f"     Liga detectada por imagen: {liga_detectada}")
            
        else:
            print(f"   ❌ Partido Salzburg vs Bruges no encontrado en API de hoy")
            print(f"   Partidos disponibles:")
            for i, partido in enumerate(partidos_reales[:5], 1):
                print(f"     {i}. {partido.get('local', 'N/A')} vs {partido.get('visitante', 'N/A')} ({partido.get('liga', 'N/A')})")
            if len(partidos_reales) > 5:
                print(f"     ... y {len(partidos_reales) - 5} más")
                
    except Exception as e:
        print(f"   ❌ Error obteniendo datos de la API: {e}")
    
    print(f"\n" + "=" * 50)
    print(f"🔍 DIAGNÓSTICO COMPLETADO")

if __name__ == "__main__":
    debug_salzburg_bruges()
