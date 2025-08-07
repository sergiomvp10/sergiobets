#!/usr/bin/env python3

from datetime import datetime
from ia_bets import generar_mensaje_ia

def test_new_telegram_format():
    """Test the new Telegram message format"""
    print('=== PRUEBA DEL NUEVO FORMATO DE TELEGRAM ===')
    
    predicciones_ejemplo = [
        {
            'liga': 'Champions League',
            'partido': 'Real Madrid vs Barcelona',
            'prediccion': 'Más de 2.5 goles',
            'cuota': '1.65',
            'stake_recomendado': '3',
            'confianza': 87,
            'valor_esperado': 15.2,
            'razon': 'Análisis probabilístico indica ventaja matemática',
            'hora': '15:00'
        },
        {
            'liga': 'Premier League',
            'partido': 'Manchester City vs Arsenal',
            'prediccion': 'Más de 8.5 corners',
            'cuota': '1.55',
            'stake_recomendado': '2',
            'confianza': 82,
            'valor_esperado': 12.8,
            'razon': 'Equipos ofensivos con alta media de corners',
            'hora': '17:30'
        }
    ]
    
    fecha = datetime.now().strftime('%Y-%m-%d')
    mensaje = generar_mensaje_ia(predicciones_ejemplo, fecha)
    
    print("MENSAJE GENERADO:")
    print("=" * 50)
    print(mensaje)
    print("=" * 50)
    
    print("\n✅ Formato actualizado exitosamente")
    print("Cambios implementados:")
    print("- PICK → PRONOSTICO con contador incremental")
    print("- Eliminado 'VALUE BET'")
    print("- Eliminado 'VE:' de línea de confianza")
    print("- Bullets (•) → Guiones (-) en resumen")
    print("- Eliminado disclaimer final")

if __name__ == "__main__":
    test_new_telegram_format()
