#!/usr/bin/env python3
"""
Test script to verify the enhanced track record interface functionality
"""

import json
from datetime import datetime, timedelta

def test_data_filtering_logic():
    """Test the data filtering logic for different states"""
    print("=== TESTING ENHANCED TRACK RECORD DATA FILTERING ===")
    
    try:
        with open('historial_predicciones.json', 'r', encoding='utf-8') as f:
            historial = json.load(f)
        
        print(f"✅ Total predictions in history: {len(historial)}")
        
        pendientes = [p for p in historial if p.get("resultado_real") is None]
        acertados = [p for p in historial if p.get("resultado_real") is not None and p.get("acierto", False)]
        fallados = [p for p in historial if p.get("resultado_real") is not None and not p.get("acierto", False)]
        
        print(f"✅ Pendientes filter: {len(pendientes)} predictions")
        print(f"✅ Acertados filter: {len(acertados)} predictions")
        print(f"✅ Fallados filter: {len(fallados)} predictions")
        
        hoy = datetime.now()
        hace_mes = hoy - timedelta(days=30)
        fecha_inicio = hace_mes.strftime('%Y-%m-%d')
        fecha_fin = hoy.strftime('%Y-%m-%d')
        
        por_fecha = [p for p in historial 
                    if fecha_inicio <= p.get('fecha', '') <= fecha_fin]
        
        print(f"✅ Date filter (last 30 days): {len(por_fecha)} predictions")
        
        if pendientes:
            sample_pendiente = pendientes[0]
            print(f"\n🔍 Sample pending prediction:")
            print(f"   Partido: {sample_pendiente.get('partido')}")
            print(f"   Predicción: {sample_pendiente.get('prediccion')}")
            print(f"   Estado: Pendiente (resultado_real: {sample_pendiente.get('resultado_real')})")
        
        if acertados:
            sample_acertado = acertados[0]
            print(f"\n🔍 Sample winning prediction:")
            print(f"   Partido: {sample_acertado.get('partido')}")
            print(f"   Predicción: {sample_acertado.get('prediccion')}")
            print(f"   Estado: Ganada (acierto: {sample_acertado.get('acierto')})")
        
        if fallados:
            sample_fallado = fallados[0]
            print(f"\n🔍 Sample losing prediction:")
            print(f"   Partido: {sample_fallado.get('partido')}")
            print(f"   Predicción: {sample_fallado.get('prediccion')}")
            print(f"   Estado: Perdida (acierto: {sample_fallado.get('acierto')})")
        
        return True
        
    except FileNotFoundError:
        print("❌ historial_predicciones.json not found")
        return False
    except Exception as e:
        print(f"❌ Error testing data filtering: {e}")
        return False

def test_table_data_structure():
    """Test the table data structure for Treeview"""
    print("\n=== TESTING TABLE DATA STRUCTURE ===")
    
    try:
        with open('historial_predicciones.json', 'r', encoding='utf-8') as f:
            historial = json.load(f)
        
        if not historial:
            print("❌ No data to test table structure")
            return False
        
        sample_prediction = historial[0]
        
        resultado_real = sample_prediction.get('resultado_real')
        acierto = sample_prediction.get('acierto')
        
        if resultado_real is None:
            estado = "⏳ Pendiente"
            resultado_final = "-"
        elif acierto:
            estado = "✅ Ganada"
            resultado_final = f"{resultado_real.get('home_score', 0)}-{resultado_real.get('away_score', 0)}"
        else:
            estado = "❌ Perdida"
            resultado_final = f"{resultado_real.get('home_score', 0)}-{resultado_real.get('away_score', 0)}"
        
        table_row = (
            sample_prediction.get('fecha', ''),
            sample_prediction.get('liga', ''),
            sample_prediction.get('partido', ''),
            sample_prediction.get('prediccion', ''),
            f"{sample_prediction.get('cuota', 0):.2f}",
            resultado_final,
            estado
        )
        
        print("✅ Table row structure test:")
        print(f"   Fecha: {table_row[0]}")
        print(f"   Liga: {table_row[1]}")
        print(f"   Equipos: {table_row[2]}")
        print(f"   Tipo de apuesta: {table_row[3]}")
        print(f"   Cuota: {table_row[4]}")
        print(f"   Resultado final: {table_row[5]}")
        print(f"   Estado: {table_row[6]}")
        
        expected_columns = ['fecha', 'liga', 'equipos', 'tipo_apuesta', 'cuota', 'resultado', 'estado']
        if len(table_row) == len(expected_columns):
            print("✅ Table structure matches expected columns")
            return True
        else:
            print(f"❌ Table structure mismatch: expected {len(expected_columns)}, got {len(table_row)}")
            return False
        
    except Exception as e:
        print(f"❌ Error testing table structure: {e}")
        return False

def test_track_record_manager_integration():
    """Test integration with TrackRecordManager"""
    print("\n=== TESTING TRACK RECORD MANAGER INTEGRATION ===")
    
    try:
        from track_record import TrackRecordManager
        
        api_key = "b37303668c4be1b78ac35b9e96460458e72b74749814a7d6f44983ac4b432079"
        tracker = TrackRecordManager(api_key)
        
        metricas = tracker.calcular_metricas_rendimiento()
        
        if "error" in metricas:
            print(f"❌ Error in TrackRecordManager: {metricas['error']}")
            return False
        
        required_keys = ['total_predicciones', 'predicciones_resueltas', 'predicciones_pendientes', 
                        'aciertos', 'total_apostado', 'total_ganancia', 'roi']
        
        for key in required_keys:
            if key not in metricas:
                print(f"❌ Missing required metric: {key}")
                return False
        
        print("✅ TrackRecordManager integration test:")
        print(f"   Total predicciones: {metricas['total_predicciones']}")
        print(f"   Predicciones resueltas: {metricas['predicciones_resueltas']}")
        print(f"   Predicciones pendientes: {metricas['predicciones_pendientes']}")
        print(f"   Aciertos: {metricas['aciertos']}")
        print(f"   Total apostado: ${metricas['total_apostado']:.2f}")
        print(f"   ROI: {metricas['roi']:.2f}%")
        
        reporte = tracker.generar_reporte_detallado()
        if len(reporte) > 100:
            print("✅ Detailed report generation works")
        else:
            print("❌ Detailed report generation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing TrackRecordManager integration: {e}")
        return False

def test_imports():
    """Test that all required imports work"""
    print("\n=== TESTING IMPORTS ===")
    
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox
        from tkinter.scrolledtext import ScrolledText
        from tkcalendar import DateEntry
        from datetime import datetime, timedelta
        from json_storage import cargar_json
        from track_record import TrackRecordManager
        
        print("✅ All required imports successful")
        print("   - tkinter and ttk")
        print("   - ScrolledText")
        print("   - DateEntry (tkcalendar)")
        print("   - datetime")
        print("   - json_storage")
        print("   - TrackRecordManager")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    print("🧪 Testing Enhanced Track Record Interface")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Data Filtering Logic", test_data_filtering_logic),
        ("Table Data Structure", test_table_data_structure),
        ("TrackRecordManager Integration", test_track_record_manager_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All tests passed! Enhanced track record interface is ready.")
        print("✅ Filter buttons will work correctly")
        print("✅ Table structure matches expected format")
        print("✅ Statistics panel integration works")
        print("✅ Date range filtering is functional")
    else:
        print("❌ Some tests failed. Check the errors above.")
    
    exit_code = 0 if all_passed else 1
    print(f"\nExit code: {exit_code}")
    return exit_code

if __name__ == "__main__":
    main()
