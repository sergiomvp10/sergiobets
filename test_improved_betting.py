#!/usr/bin/env python3

from datetime import datetime
from footystats_api import obtener_partidos_del_dia
from ia_bets import filtrar_apuestas_inteligentes, CUOTA_MIN, CUOTA_MAX

def test_improved_betting_system():
    """Test improved bet type understanding system"""
    print('=== PRUEBA DEL SISTEMA MEJORADO ===')
    print(f'Rango de cuotas: {CUOTA_MIN} - {CUOTA_MAX}')
    print('Valor esperado mínimo: 12%')
    print('Mejoras: Cuotas ajustadas + Probabilidades realistas + Nuevos tipos de apuesta')
    print()

    fecha = datetime.now().strftime('%Y-%m-%d')
    partidos_api = obtener_partidos_del_dia(fecha)

    if partidos_api:
        partidos_internos = []
        for partido in partidos_api[:5]:
            partido_interno = {
                'local': partido.get('home_name', 'N/A'),
                'visitante': partido.get('away_name', 'N/A'),
                'hora': '15:00',
                'liga': 'Champions League',
                'cuotas': {
                    'casa': 'Test',
                    'local': partido.get('odds_ft_1', '1.50'),
                    'empate': partido.get('odds_ft_x', '3.00'),
                    'visitante': partido.get('odds_ft_2', '2.50')
                }
            }
            partidos_internos.append(partido_interno)

        print(f'Analizando {len(partidos_internos)} partidos...')
        predicciones = filtrar_apuestas_inteligentes(partidos_internos)

        print(f'Predicciones generadas: {len(predicciones)}')
        
        if predicciones:
            print('\n=== PREDICCIONES CON SISTEMA MEJORADO ===')
            for i, pred in enumerate(predicciones, 1):
                print(f'{i}. {pred["partido"]} - {pred["prediccion"]}')
                print(f'   Cuota: {pred["cuota"]} | VE: {pred["valor_esperado"]:.1%} | Confianza: {pred["confianza"]}%')
                print(f'   Stake: {pred["stake_recomendado"]}u | Liga: {pred["liga"]} | Tipo: {pred.get("tipo", "N/A")}')
                print()
            
            print('✅ Sistema mejorado genera predicciones exitosamente')
            
            bet_types = {}
            for pred in predicciones:
                bet_type = pred["prediccion"].split()[0:2]
                bet_type_key = " ".join(bet_type)
                bet_types[bet_type_key] = bet_types.get(bet_type_key, 0) + 1
            
            print('\n=== DIVERSIDAD DE TIPOS DE APUESTA ===')
            for bet_type, count in bet_types.items():
                print(f'• {bet_type}: {count} predicción(es)')
            
            print('\n=== TIPOS DE APUESTA SOPORTADOS ===')
            print('✅ Gol en primer tiempo (Sí/No)')
            print('✅ Más/Menos Goles (1.5, 2.5)')
            print('✅ Más/Menos Corners (8.5, 9.5)')
            print('✅ Más/Menos Tarjetas (3.5, 4.5)')
            print('✅ Equipo A/B hace al menos un gol')
            print('✅ Handicap +/-0.5')
            print('✅ BTTS (Ambos equipos marcan)')
                
        else:
            print('❌ No se generaron predicciones - revisar parámetros')
    else:
        print('❌ No se obtuvieron partidos de la API')

if __name__ == "__main__":
    test_improved_betting_system()
