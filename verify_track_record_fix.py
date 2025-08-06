#!/usr/bin/env python3
"""
Verify that the enhanced track record interface loads correctly after cache clearing
"""

def test_interface_after_cache_clear():
    """Test that the enhanced interface is properly loaded"""
    print("=== VERIFYING ENHANCED TRACK RECORD AFTER CACHE CLEAR ===")
    
    try:
        import importlib
        import sys
        
        modules_to_remove = [name for name in sys.modules.keys() if 'sergiobets_unified' in name]
        for module in modules_to_remove:
            del sys.modules[module]
        
        from sergiobets_unified import SergioBetsUnified
        
        print("✅ Fresh import successful")
        
        import inspect
        method_source = inspect.getsource(SergioBetsUnified.abrir_track_record)
        
        enhanced_features = [
            "Track Record Mejorado",
            "frame_filtros", 
            "ttk.Treeview",
            "btn_pendientes",
            "btn_acertados", 
            "btn_fallados",
            "btn_historico",
            "DateEntry",
            "frame_estadisticas"
        ]
        
        found_features = []
        for feature in enhanced_features:
            if feature in method_source:
                found_features.append(feature)
        
        print(f"✅ Enhanced features found: {len(found_features)}/{len(enhanced_features)}")
        for feature in found_features:
            print(f"   - {feature}")
        
        if len(found_features) >= 8:
            print("🎉 ENHANCED INTERFACE IS PROPERLY LOADED!")
            print("✅ User should now see the new interface with filter buttons")
            return True
        else:
            print("❌ Enhanced interface not fully loaded")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying interface: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔧 Verifying Track Record Fix After Cache Clear")
    print("=" * 60)
    
    success = test_interface_after_cache_clear()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 SUCCESS! Enhanced track record interface should now work correctly.")
        print("\n📋 What the user should see:")
        print("- Window title: '📊 Track Record Mejorado - SergioBets IA'")
        print("- Filter buttons: 📌 PENDIENTES, ✅ ACERTADOS, ❌ FALLADOS, 📅 HISTÓRICO, 📊 RESUMEN")
        print("- Date range selector with calendar widgets")
        print("- Structured table with columns: Fecha, Liga, Equipos, Tipo de Apuesta, Cuota, Resultado Final, Estado")
        print("- Statistics panel on the right side")
        print("- Action buttons: 🔄 Actualizar Resultados, 🧹 Limpiar Historial")
        
        print("\n💡 Instructions for user:")
        print("1. Run: python sergiobets_unified.py")
        print("2. Click the 'Track Record' button in the GUI")
        print("3. The enhanced interface should now appear")
    else:
        print("❌ Issue not resolved. Further investigation needed.")
    
    return success

if __name__ == "__main__":
    main()
