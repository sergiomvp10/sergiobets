#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_checkbox_predictions():
    print("=== TESTING CHECKBOX PREDICTION SELECTION ===")
    
    try:
        from ia_bets import filtrar_apuestas_inteligentes, generar_mensaje_ia
        
        partidos_test = [
            {
                "hora": "15:30",
                "liga": "Liga Colombiana", 
                "local": "Deportivo Cali",
                "visitante": "Llaneros",
                "cuotas": {"casa": "FootyStats", "local": "1.45", "empate": "3.8", "visitante": "6.2"}
            },
            {
                "hora": "18:00",
                "liga": "Liga Argentina",
                "local": "San Lorenzo", 
                "visitante": "Tigre",
                "cuotas": {"casa": "FootyStats", "local": "1.55", "empate": "3.4", "visitante": "5.8"}
            }
        ]
        
        print("1. Testing prediction generation...")
        predicciones = filtrar_apuestas_inteligentes(partidos_test)
        print(f"   Generated {len(predicciones)} predictions")
        
        for i, pred in enumerate(predicciones, 1):
            print(f"   PICK #{i}: {pred['prediccion']} - {pred['partido']}")
        
        print("\n2. Testing selective message generation...")
        if predicciones:
            predicciones_seleccionadas = [predicciones[0]]
            mensaje_selectivo = generar_mensaje_ia(predicciones_seleccionadas, "2025-08-02")
            print(f"   Selective message generated for {len(predicciones_seleccionadas)} prediction(s)")
            print(f"   Message length: {len(mensaje_selectivo)} characters")
        
        print("\n3. Testing empty selection handling...")
        predicciones_vacias = []
        mensaje_vacio = generar_mensaje_ia(predicciones_vacias, "2025-08-02")
        print(f"   Empty selection message length: {len(mensaje_vacio)} characters")
        
        print("\n✅ Checkbox prediction selection test completed")
        return True
        
    except Exception as e:
        print(f"❌ Error in checkbox prediction test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_checkbox_predictions()
    if success:
        print("✅ Checkbox prediction test passed")
    else:
        print("❌ Checkbox prediction test failed")
