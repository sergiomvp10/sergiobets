#!/usr/bin/env python3
"""
Debug script to identify why the enhanced track record interface isn't appearing
"""

import sys
import os
import importlib.util

def test_track_record_imports():
    """Test that all required imports for enhanced track record work"""
    print("=== TESTING TRACK RECORD IMPORTS ===")
    
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

def test_betgeniux_unified_integration():
    """Test that BetGeniuXUnified has the enhanced track record method"""
    print("\n=== TESTING BETGENIUX_UNIFIED INTEGRATION ===")
    
    try:
        from betgeniux_unified import BetGeniuXUnified
        
        if hasattr(BetGeniuXUnified, 'abrir_track_record'):
            print("✅ BetGeniuXUnified has abrir_track_record method")
            
            import inspect
            method_source = inspect.getsource(BetGeniuXUnified.abrir_track_record)
            
            enhanced_indicators = [
                "Track Record Mejorado",
                "frame_filtros",
                "ttk.Treeview",
                "filtrar_pendientes",
                "DateEntry",
                "frame_estadisticas"
            ]
            
            found_indicators = []
            for indicator in enhanced_indicators:
                if indicator in method_source:
                    found_indicators.append(indicator)
            
            print(f"✅ Enhanced track record indicators found: {len(found_indicators)}/{len(enhanced_indicators)}")
            for indicator in found_indicators:
                print(f"   - {indicator}")
            
            if len(found_indicators) >= 4:  # At least 4 out of 6 indicators
                print("✅ Method appears to be the enhanced version")
                return True
            else:
                print("❌ Method appears to be the simplified version")
                return False
                
        else:
            print("❌ BetGeniuXUnified missing abrir_track_record method")
            return False
            
    except Exception as e:
        print(f"❌ Error testing BetGeniuXUnified integration: {e}")
        return False

def test_track_record_manager_availability():
    """Test that TrackRecordManager is available and functional"""
    print("\n=== TESTING TRACK RECORD MANAGER ===")
    
    try:
        from track_record import TrackRecordManager
        
        api_key = "b37303668c4be1b78ac35b9e96460458e72b74749814a7d6f44983ac4b432079"
        tracker = TrackRecordManager(api_key)
        
        print("✅ TrackRecordManager initialized successfully")
        
        metricas = tracker.calcular_metricas_rendimiento()
        
        if "error" in metricas:
            print(f"⚠️ TrackRecordManager returned error: {metricas['error']}")
            return True  # Still counts as working, just no data
        else:
            print("✅ TrackRecordManager metrics calculation works")
            print(f"   - Total predictions: {metricas.get('total_predicciones', 0)}")
            print(f"   - Pending predictions: {metricas.get('predicciones_pendientes', 0)}")
            return True
        
    except Exception as e:
        print(f"❌ Error testing TrackRecordManager: {e}")
        return False

def test_data_structure():
    """Test that the prediction data structure is compatible"""
    print("\n=== TESTING DATA STRUCTURE COMPATIBILITY ===")
    
    try:
        from json_storage import cargar_json
        
        historial = cargar_json('historial_predicciones.json') or []
        print(f"✅ Loaded {len(historial)} predictions from historial_predicciones.json")
        
        if historial:
            sample = historial[0]
            required_fields = ['fecha', 'partido', 'liga', 'prediccion', 'cuota']
            
            missing_fields = []
            for field in required_fields:
                if field not in sample:
                    missing_fields.append(field)
            
            if not missing_fields:
                print("✅ Data structure is compatible with enhanced interface")
                
                pendientes = len([p for p in historial if p.get("resultado_real") is None])
                acertados = len([p for p in historial if p.get("resultado_real") is not None and p.get("acierto", False)])
                fallados = len([p for p in historial if p.get("resultado_real") is not None and not p.get("acierto", False)])
                
                print(f"   - Pendientes: {pendientes}")
                print(f"   - Acertados: {acertados}")
                print(f"   - Fallados: {fallados}")
                
                return True
            else:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
        else:
            print("⚠️ No prediction data found - interface will work but show empty table")
            return True
        
    except Exception as e:
        print(f"❌ Error testing data structure: {e}")
        return False

def test_method_signature():
    """Test that the method signature is correct for the class"""
    print("\n=== TESTING METHOD SIGNATURE ===")
    
    try:
        from betgeniux_unified import BetGeniuXUnified
        import inspect
        
        method = getattr(BetGeniuXUnified, 'abrir_track_record')
        signature = inspect.signature(method)
        
        print(f"✅ Method signature: {signature}")
        
        params = list(signature.parameters.keys())
        if params == ['self']:
            print("✅ Method signature is correct (only self parameter)")
            return True
        else:
            print(f"❌ Unexpected parameters: {params}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing method signature: {e}")
        return False

def check_for_conflicts():
    """Check for potential import conflicts or issues"""
    print("\n=== CHECKING FOR CONFLICTS ===")
    
    try:
        with open('betgeniux_unified.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        track_record_count = content.count('def abrir_track_record')
        print(f"✅ Found {track_record_count} definition(s) of abrir_track_record")
        
        if track_record_count == 1:
            print("✅ No duplicate method definitions")
        else:
            print("⚠️ Multiple definitions found - this could cause issues")
        
        required_imports = [
            'from tkinter import ttk',
            'from tkcalendar import DateEntry',
            'from track_record import TrackRecordManager'
        ]
        
        missing_imports = []
        for imp in required_imports:
            if imp not in content:
                missing_imports.append(imp)
        
        if not missing_imports:
            print("✅ All required imports are present")
        else:
            print(f"❌ Missing imports: {missing_imports}")
        
        return len(missing_imports) == 0
        
    except Exception as e:
        print(f"❌ Error checking for conflicts: {e}")
        return False

def check_user_scenario():
    """Check what the user might be experiencing"""
    print("\n=== CHECKING USER SCENARIO ===")
    
    try:
        files_with_track_record = []
        
        for filename in ['betgeniux_unified.py', 'crudo.py']:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'def abrir_track_record' in content:
                        files_with_track_record.append(filename)
        
        print(f"✅ Files with abrir_track_record: {files_with_track_record}")
        
        for filename in files_with_track_record:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if "Track Record Mejorado" in content and "frame_filtros" in content:
                print(f"✅ {filename} has enhanced interface")
            else:
                print(f"❌ {filename} has simplified interface")
        
        pycache_files = []
        if os.path.exists('__pycache__'):
            for file in os.listdir('__pycache__'):
                if 'betgeniux_unified' in file:
                    pycache_files.append(file)
        
        if pycache_files:
            print(f"⚠️ Found cached files: {pycache_files}")
            print("⚠️ User might need to clear Python cache")
        else:
            print("✅ No problematic cache files found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking user scenario: {e}")
        return False

def main():
    print("🔍 Debugging Track Record Interface Issue")
    print("=" * 60)
    
    tests = [
        ("Track Record Imports", test_track_record_imports),
        ("BetGeniuXUnified Integration", test_betgeniux_unified_integration),
        ("TrackRecordManager Availability", test_track_record_manager_availability),
        ("Data Structure Compatibility", test_data_structure),
        ("Method Signature", test_method_signature),
        ("Conflict Detection", check_for_conflicts),
        ("User Scenario Analysis", check_user_scenario)
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 60)
    print("📊 Debug Results:")
    
    issues_found = []
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not result:
            issues_found.append(test_name)
    
    print("\n" + "=" * 60)
    if not issues_found:
        print("🤔 No obvious issues found. Possible causes:")
        print("1. User might be running a cached version")
        print("2. User might be running the wrong file")
        print("3. There might be a runtime import issue")
        print("4. User might need to restart their application")
        
        print("\n💡 Recommended solutions:")
        print("1. Clear Python cache: rm -rf __pycache__")
        print("2. Ensure running: python betgeniux_unified.py")
        print("3. Restart the application completely")
        print("4. Check if imports are working at runtime")
    else:
        print(f"❌ Issues found in: {', '.join(issues_found)}")
        print("🔧 These issues need to be addressed")
    
    return len(issues_found) == 0

if __name__ == "__main__":
    main()
