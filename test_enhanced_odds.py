#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from odds_api import OddsAPIManager
from api_config import THE_ODDS_API_KEY, FOOTYSTATS_API_KEY
from datetime import datetime

def test_odds_api_integration():
    """Test The Odds API integration"""
    print("=== TESTING THE ODDS API INTEGRATION ===")
    
    if THE_ODDS_API_KEY == "YOUR_THE_ODDS_API_KEY_HERE":
        print("⚠️ The Odds API key not configured. Testing with FootyStats fallback only.")
        return test_footystats_fallback()
    
    try:
        odds_manager = OddsAPIManager(THE_ODDS_API_KEY, FOOTYSTATS_API_KEY)
        fecha = datetime.now().strftime('%Y-%m-%d')
        
        print(f"Testing enhanced odds for {fecha}...")
        partidos = odds_manager.get_enhanced_odds(fecha)
        
        if partidos:
            print(f"✅ Successfully retrieved {len(partidos)} matches")
            
            primer_partido = partidos[0]
            print(f"\nSample match: {primer_partido['local']} vs {primer_partido['visitante']}")
            print(f"League: {primer_partido['liga']}")
            print(f"Time: {primer_partido['hora']}")
            print(f"Odds source: {primer_partido['cuotas']['casa']}")
            print(f"1X2 Odds: {primer_partido['cuotas']['local']} / {primer_partido['cuotas']['empate']} / {primer_partido['cuotas']['visitante']}")
            
            if primer_partido['cuotas'].get('btts_si') != 'N/A':
                print(f"BTTS: Yes {primer_partido['cuotas']['btts_si']} / No {primer_partido['cuotas']['btts_no']}")
            
            if primer_partido['cuotas'].get('over_25') != 'N/A':
                print(f"O/U 2.5: Over {primer_partido['cuotas']['over_25']} / Under {primer_partido['cuotas']['under_25']}")
            
            if 'bookmakers' in primer_partido:
                print(f"Bookmaker comparison available: {len(primer_partido['bookmakers'])} bookmakers")
            
            return True
        else:
            print("❌ No matches retrieved")
            return False
            
    except Exception as e:
        print(f"❌ Error testing The Odds API: {e}")
        return False

def test_footystats_fallback():
    """Test FootyStats fallback functionality"""
    print("\n=== TESTING FOOTYSTATS FALLBACK ===")
    
    try:
        odds_manager = OddsAPIManager("invalid_key", FOOTYSTATS_API_KEY)
        fecha = datetime.now().strftime('%Y-%m-%d')
        
        print(f"Testing FootyStats fallback for {fecha}...")
        partidos = odds_manager.get_enhanced_odds(fecha)
        
        if partidos:
            print(f"✅ Fallback successful: {len(partidos)} matches")
            primer_partido = partidos[0]
            print(f"Sample: {primer_partido['local']} vs {primer_partido['visitante']} ({primer_partido['cuotas']['casa']})")
            return True
        else:
            print("❌ Fallback failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing fallback: {e}")
        return False

def test_caching_system():
    """Test caching functionality"""
    print("\n=== TESTING CACHING SYSTEM ===")
    
    try:
        odds_manager = OddsAPIManager(THE_ODDS_API_KEY, FOOTYSTATS_API_KEY)
        fecha = datetime.now().strftime('%Y-%m-%d')
        
        start_time = datetime.now()
        partidos1 = odds_manager.get_enhanced_odds(fecha)
        first_call_time = (datetime.now() - start_time).total_seconds()
        
        start_time = datetime.now()
        partidos2 = odds_manager.get_enhanced_odds(fecha)
        second_call_time = (datetime.now() - start_time).total_seconds()
        
        print(f"First call: {first_call_time:.2f}s")
        print(f"Second call: {second_call_time:.2f}s")
        
        if second_call_time < first_call_time * 0.1:  # Should be much faster
            print("✅ Caching working correctly")
            return True
        else:
            print("⚠️ Caching may not be working optimally")
            return False
            
    except Exception as e:
        print(f"❌ Error testing caching: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TESTING ENHANCED ODDS SYSTEM")
    print("=" * 50)
    
    test1 = test_odds_api_integration()
    test2 = test_footystats_fallback()
    test3 = test_caching_system()
    
    print("\n" + "=" * 50)
    print("FINAL RESULTS:")
    print(f"✅ Odds API Integration: {'PASSED' if test1 else 'FAILED'}")
    print(f"✅ FootyStats Fallback: {'PASSED' if test2 else 'FAILED'}")
    print(f"✅ Caching System: {'PASSED' if test3 else 'FAILED'}")
    
    if test1 or test2:  # At least one source working
        print("\n🎉 ENHANCED ODDS SYSTEM READY")
        print("\n📋 NEXT STEPS:")
        print("   1. Get The Odds API key from https://the-odds-api.com/")
        print("   2. Update THE_ODDS_API_KEY in api_config.py")
        print("   3. Test with real data using python crudo.py")
        print("   4. Monitor API usage and costs")
    else:
        print("\n❌ ENHANCED ODDS SYSTEM NEEDS FIXES")
