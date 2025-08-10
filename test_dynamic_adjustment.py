#!/usr/bin/env python3

import sys
import os

try:
    from ia_bets import ajustar_cuota_a_rango, generar_mercados_alternativos, encontrar_mejores_apuestas
    from json_storage import guardar_json
    print("✅ Imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

print("\n🧪 Test 1: Basic odds adjustment")
cuota_original = 1.20
cuota_min, cuota_max = 1.30, 1.60
cuota_ajustada, tipo_ajuste = ajustar_cuota_a_rango(cuota_original, 0.7, cuota_min, cuota_max)
print(f"Original: {cuota_original} -> Ajustada: {cuota_ajustada} (Tipo: {tipo_ajuste})")

cuota_original = 1.80
cuota_ajustada, tipo_ajuste = ajustar_cuota_a_rango(cuota_original, 0.5, cuota_min, cuota_max)
print(f"Original: {cuota_original} -> Ajustada: {cuota_ajustada} (Tipo: {tipo_ajuste})")

cuota_original = 1.45
cuota_ajustada, tipo_ajuste = ajustar_cuota_a_rango(cuota_original, 0.6, cuota_min, cuota_max)
print(f"Original: {cuota_original} -> Ajustada: {cuota_ajustada} (Tipo: {tipo_ajuste})")

print("\n🧪 Test 2: Setting test configuration")
test_config = {"odds_min": 1.25, "odds_max": 1.75}
guardar_json("config_app.json", test_config)
print(f"Config set: {test_config}")

print("\n🧪 Test 3: Testing encontrar_mejores_apuestas with dynamic adjustment")
mock_analisis = {
    "partido": "Test Team A vs Test Team B",
    "liga": "Premier League",
    "hora": "15:00",
    "probabilidades_1x2": {"local": 0.45, "empate": 0.30, "visitante": 0.25},
    "cuotas_disponibles": {"local": "2.20", "empate": "3.30", "visitante": "4.00"},
    "probabilidades_btts": {"btts_si": 0.65, "btts_no": 0.35},
    "probabilidades_over_under": {
        "over_15": 0.85, "under_15": 0.15,
        "over_25": 0.55, "under_25": 0.45,
        "goles_esperados": 2.8
    },
    "probabilidades_handicap": {"handicap_local_05": 0.55, "handicap_visitante_05": 0.45},
    "probabilidades_corners": {"over_85_corners": 0.70, "over_105_corners": 0.50},
    "probabilidades_tarjetas": {"over_35_cards": 0.75, "over_55_cards": 0.40}
}

try:
    mejores_apuestas = encontrar_mejores_apuestas(mock_analisis, num_opciones=3)
    print(f"✅ Found {len(mejores_apuestas)} betting options")
    
    for i, apuesta in enumerate(mejores_apuestas, 1):
        ajuste_info = f" (Ajuste: {apuesta.get('ajuste', 'N/A')})" if apuesta.get('ajuste') != 'ninguno' else ""
        cuota_orig = f" [Orig: {apuesta.get('cuota_original', 'N/A')}]" if 'cuota_original' in apuesta else ""
        print(f"  {i}. {apuesta['tipo']} - {apuesta['descripcion']}")
        print(f"     Cuota: {apuesta['cuota']}{cuota_orig}{ajuste_info}")
        print(f"     VE: {apuesta['valor_esperado']:.3f}, Confianza: {apuesta['confianza']:.1f}%")
        
except Exception as e:
    print(f"❌ Error testing encontrar_mejores_apuestas: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Dynamic adjustment tests completed!")
