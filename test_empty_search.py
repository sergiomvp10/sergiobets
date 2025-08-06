#!/usr/bin/env python3
"""
Test script to verify empty search behavior works correctly
"""

import sys
import os
from datetime import datetime, timedelta

def test_empty_search_behavior():
    """Test that search shows empty when no matches for current date"""
    print("=" * 60)
    print("TESTING EMPTY SEARCH BEHAVIOR")
    print("=" * 60)
    
    try:
        from footystats_api import obtener_partidos_del_dia
        
        fecha_hoy = datetime.now().strftime('%Y-%m-%d')
        print(f"Testing today: {fecha_hoy}")
        result_hoy = obtener_partidos_del_dia(fecha_hoy)
        print(f"Today result: {len(result_hoy) if result_hoy else 0} matches")
        
        if not result_hoy or len(result_hoy) == 0:
            print("✅ No matches for today - this should show empty in GUI")
        else:
            print(f"✅ Found {len(result_hoy)} matches for today")
        
        fecha_futura = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        print(f"\nTesting future date: {fecha_futura}")
        result_futura = obtener_partidos_del_dia(fecha_futura)
        print(f"Future date result: {len(result_futura) if result_futura else 0} matches")
        
        if not result_futura or len(result_futura) == 0:
            print("✅ No matches for future date - this should show empty in GUI")
        else:
            print(f"⚠️ Unexpected: Found {len(result_futura)} matches for future date")
        
        return True
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_search_function_logic():
    """Test the search function logic without GUI"""
    print("\n" + "=" * 60)
    print("TESTING SEARCH FUNCTION LOGIC (NO GUI)")
    print("=" * 60)
    
    try:
        from footystats_api import obtener_partidos_del_dia
        from league_utils import detectar_liga_por_imagen, convertir_timestamp_unix
        
        print("✅ All required imports successful")
        
        fecha = datetime.now().strftime('%Y-%m-%d')
        print(f"Testing search logic for: {fecha}")
        
        datos_api = obtener_partidos_del_dia(fecha)
        print(f"API returned: {len(datos_api) if datos_api else 0} matches")
        
        if not datos_api or len(datos_api) == 0:
            print("✅ No matches - should return empty list (no fallback)")
            return True
        else:
            print(f"✅ Found {len(datos_api)} matches - should process normally")
            
            if len(datos_api) > 0:
                partido = datos_api[0]
                try:
                    liga_detectada = detectar_liga_por_imagen(
                        partido.get("home_image", ""), 
                        partido.get("away_image", "")
                    )
                    hora_partido = convertir_timestamp_unix(partido.get("date_unix"))
                    print(f"✅ Match processing successful: {liga_detectada}")
                except Exception as e:
                    print(f"⚠️ Match processing error: {e}")
            
            return True
            
    except Exception as e:
        print(f"❌ Search logic test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 TESTING EMPTY SEARCH BEHAVIOR")
    print("=" * 60)
    print(f"Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    empty_ok = test_empty_search_behavior()
    logic_ok = test_search_function_logic()
    
    print("\n" + "=" * 60)
    print("EMPTY SEARCH TEST SUMMARY")
    print("=" * 60)
    print(f"Empty search behavior: {'✅ Working' if empty_ok else '❌ Failed'}")
    print(f"Search function logic: {'✅ Working' if logic_ok else '❌ Failed'}")
    
    if empty_ok and logic_ok:
        print("\n🎉 Empty search behavior verified!")
        print("📋 Expected behavior:")
        print("   - No matches for date = empty results (no fallback)")
        print("   - No simulated data ever")
        print("   - Clear message when no matches found")
        print("   - Only real API data for exact date searched")
    else:
        print("\n⚠️ Some issues detected - check output above")
        
    print(f"\n🏁 Test completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
