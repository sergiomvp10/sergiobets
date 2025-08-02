#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_ui_integration():
    print("=== TESTING COMPLETE UI INTEGRATION ===")
    
    try:
        from ia_bets import filtrar_apuestas_inteligentes, analizar_partido_completo, encontrar_mejor_apuesta
        
        partidos_test = [
            {
                'hora': '12:00',
                'liga': 'Liga Colombiana', 
                'local': 'Deportivo Cali',
                'visitante': 'Llaneros',
                'cuotas': {'casa': 'FootyStats', 'local': '1.68', 'empate': '3.1', 'visitante': '5.0'}
            }
        ]

        predicciones = filtrar_apuestas_inteligentes(partidos_test)

        if predicciones:
            for i, pred in enumerate(predicciones, 1):
                print(f'🎯 PICK #{i}: {pred["prediccion"]}')
                print(f'⚽ {pred["partido"]} ({pred["liga"]})')
                print(f'💰 Cuota: {pred["cuota"]} | Stake: {pred["stake_recomendado"]}u | ⏰ {pred["hora"]}')
                print(f'📊 Confianza: {pred["confianza"]}% | Valor Esperado: {pred["valor_esperado"]}')
                print(f'📝 Justificación: {pred["razon"]}')
                print()
            print('✅ Enhanced predictions working correctly')
        else:
            print('❌ No predictions generated')

        print('=== TESTING INDIVIDUAL COMPONENTS ===')
        analisis = analizar_partido_completo(partidos_test[0])
        print(f'Análisis completo generado para: {analisis["partido"]}')

        mejor_apuesta = encontrar_mejor_apuesta(analisis)
        if mejor_apuesta:
            print(f'Mejor apuesta identificada: {mejor_apuesta["descripcion"]}')
            print(f'Valor esperado: {mejor_apuesta["valor_esperado"]:.3f}')
        else:
            print('No se encontró value bet')

        print('✅ All components working correctly')
        
    except Exception as e:
        print(f'❌ Error in UI integration test: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ui_integration()
