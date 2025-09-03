#!/usr/bin/env python3
"""
Test completo de integración para verificar que el formato BETGENIUX® 
funciona correctamente en sergiobets_unified.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from daily_counter import reset_daily_counter, get_next_pronostico_numbers
from ia_bets import generar_mensaje_ia
from datetime import datetime

def test_integration():
    print("🧪 PRUEBA DE INTEGRACIÓN COMPLETA - FORMATO BETGENIUX®")
    print("=" * 70)
    
    reset_daily_counter()
    
    predicciones_test = [
        {
            'liga': 'Brasileirão',
            'partido': 'Criciúma vs Atlético PR',
            'prediccion': 'Más de 1.5 goles',
            'cuota': 1.55,
            'stake_recomendado': 10,
            'confianza': 60.0,
            'valor_esperado': 0.373,
            'hora': '15:00'
        },
        {
            'liga': 'Premier League',
            'partido': 'Manchester City vs Arsenal',
            'prediccion': 'Over 2.5 goles',
            'cuota': 1.85,
            'stake_recomendado': 8,
            'confianza': 75.0,
            'valor_esperado': 0.421,
            'hora': '15:30'
        }
    ]
    
    fecha = datetime.now().strftime('%Y-%m-%d')
    
    print("1️⃣ PROBANDO GENERACIÓN DE MENSAJE PARA TELEGRAM")
    mensaje_telegram = generar_mensaje_ia(predicciones_test, fecha)
    print(mensaje_telegram)
    print()
    
    print("2️⃣ PROBANDO CONTADOR INDIVIDUAL PARA GUI")
    for i, pred in enumerate(predicciones_test):
        try:
            counter_numbers = get_next_pronostico_numbers(1)
            numero_pronostico = counter_numbers[0]
        except ImportError:
            numero_pronostico = i + 1
        
        pred_text = f"🎯 PRONOSTICO #{numero_pronostico}: {pred['prediccion']} | ⚽️ {pred['partido']} | 💰 {pred['cuota']} | ⏰ {pred['hora']}"
        print(f"GUI Display: {pred_text}")
    
    print()
    print("3️⃣ VERIFICACIÓN DE ELEMENTOS REQUERIDOS")
    
    elementos_requeridos = [
        ("Header BETGENIUX®", "BETGENIUX®" in mensaje_telegram),
        ("Formato fecha", f"({fecha})" in mensaje_telegram),
        ("Numeración secuencial", "#1" in mensaje_telegram and "#2" in mensaje_telegram),
        ("Emoji predicción", "🎯 PRONOSTICO #" in mensaje_telegram),
        ("Emoji liga", "🏆" in mensaje_telegram),
        ("Emoji partido", "⚽️" in mensaje_telegram),
        ("Emoji predicción tipo", "🔮" in mensaje_telegram),
        ("Emoji dinero", "💰" in mensaje_telegram),
        ("Emoji estadísticas", "📊" in mensaje_telegram),
        ("Emoji tiempo", "⏰" in mensaje_telegram),
        ("Advertencia responsabilidad", "⚠️ Apostar con responsabilidad" in mensaje_telegram),
    ]
    
    todos_pasaron = True
    for descripcion, resultado in elementos_requeridos:
        estado = "✅" if resultado else "❌"
        print(f"{estado} {descripcion}")
        if not resultado:
            todos_pasaron = False
    
    print()
    print("4️⃣ VERIFICACIÓN DE ARCHIVOS DE SALIDA")
    archivos_esperados = [
        "pronosticos_seleccionados.json",
        "pronosticos_seleccionados.txt"
    ]
    
    print("Archivos que debería generar sergiobets_unified.py:")
    for archivo in archivos_esperados:
        print(f"📄 {archivo}")
    
    print()
    print("=" * 70)
    if todos_pasaron:
        print("🎉 INTEGRACIÓN COMPLETA EXITOSA!")
        print("✅ El formato BETGENIUX® está correctamente implementado")
        print("✅ La numeración secuencial funciona correctamente")
        print("✅ Todos los elementos requeridos están presentes")
    else:
        print("❌ FALLOS EN LA INTEGRACIÓN!")
        print("🔧 Revisar elementos faltantes arriba")
    
    return todos_pasaron

if __name__ == "__main__":
    test_integration()
