#!/usr/bin/env python3

import sys
import os

try:
    from ia_bets import encontrar_mejores_apuestas, obtener_cuotas_configuradas
    from json_storage import guardar_json
    print("✅ Imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

print("\n🧪 Test 1: Real odds filtering")
cuota_min, cuota_max = obtener_cuotas_configuradas()
print(f"Current configured range: {cuota_min} - {cuota_max}")

test_odds = [1.20, 1.35, 1.45, 1.55, 1.80]
for cuota in test_odds:
    in_range = cuota_min <= cuota <= cuota_max
    status = "✅ ACCEPTED" if in_range else "❌ FILTERED OUT"
    print(f"Odds {cuota}: {status}")

print("\n🧪 Test 2: Setting test configuration")
test_config = {"odds_min": 1.25, "odds_max": 1.75}
guardar_json("config_app.json", test_config)
print(f"Config set: {test_config}")

print("\n🧪 Test 3: Testing encontrar_mejores_apuestas with real odds")
mock_analisis = {
    "partido": "Test Team A vs Test Team B",
    "liga": "Premier League",
    "hora": "15:00",
    "probabilidades_1x2": {"local": 0.45, "empate": 0.30, "visitante": 0.25},
    "probabilidades_btts": {"btts_si": 0.65, "btts_no": 0.35},
    "probabilidades_over_under": {
        "over_15": 0.85, "under_15": 0.15,
        "over_25": 0.55, "under_25": 0.45,
        "goles_esperados": 2.8
    },
    "probabilidades_corners": {"over_85_corners": 0.70, "over_105_corners": 0.50},
    "cuotas_disponibles": {
        "casa": "FootyStats",
        "local": "1.45", "empate": "3.20", "visitante": "4.50",
        "btts_si": "1.55", "btts_no": "2.10",
        "over_15": "1.35", "under_15": "2.80",
        "over_25": "1.65", "under_25": "2.20",
        "corners_over_85": "1.40", "corners_over_105": "1.75",
        "1h_over_05": "1.50", "1h_over_15": "2.30"
    }
}

try:
    mejores_apuestas = encontrar_mejores_apuestas(mock_analisis, num_opciones=3)
    print(f"✅ Found {len(mejores_apuestas)} betting options")
    
    for i, apuesta in enumerate(mejores_apuestas, 1):
        print(f"  {i}. {apuesta['tipo']} - {apuesta['descripcion']}")
        print(f"     Cuota real: {apuesta['cuota']}")
        print(f"     VE: {apuesta['valor_esperado']:.3f}, Confianza: {apuesta['confianza']:.1f}%")
        
except Exception as e:
    print(f"❌ Error testing encontrar_mejores_apuestas: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Real odds filtering tests completed!")
