#!/usr/bin/env python3
"""
Test script to investigate API issues with specific matches
"""

import json
from datetime import datetime, timedelta
from track_record import TrackRecordManager

def test_athletic_match_specifically():
    """Test the specific Athletic Club vs Atletico GO match"""
    print("=" * 60)
    print("TESTING ATHLETIC CLUB VS ATLETICO GO MATCH")
    print("=" * 60)
    
    api_key = 'b37303668c4be1b78ac35b9e96460458e72b74749814a7d6f44983ac4b432079'
    tracker = TrackRecordManager(api_key)
    
    test_date = '2025-08-04'
    print(f'Testing API for date: {test_date}')
    
    variations = [
        ('Athletic Club', 'Atletico GO'),
        ('Athletic Club', 'Atlético GO'),
        ('Athletic', 'Atletico GO'),
        ('Athletic Bilbao', 'Atletico GO'),
        ('Ath Bilbao', 'Atletico GO')
    ]
    
    for home, away in variations:
        print(f'Testing: {home} vs {away}')
        result = tracker.obtener_resultado_partido(test_date, home, away, timeout=15)
        if result:
            print(f'  ✅ Found match: {result}')
            print(f'  Total corners: {result.get("total_corners", 0)}')
            return result
        else:
            print(f'  ❌ No match found')
    
    return None

def test_api_raw_response():
    """Test what the API actually returns for August 04, 2025"""
    print("\n" + "=" * 60)
    print("TESTING RAW API RESPONSE FOR AUGUST 04, 2025")
    print("=" * 60)
    
    import requests
    
    api_key = 'b37303668c4be1b78ac35b9e96460458e72b74749814a7d6f44983ac4b432079'
    endpoint = "https://api.footystats.org/todays-matches"
    
    params = {
        "key": api_key,
        "date": "2025-08-04",
        "timezone": "America/Bogota"
    }
    
    try:
        response = requests.get(endpoint, params=params, timeout=15)
        print(f"API Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            partidos = data.get("data", [])
            print(f"Total matches returned: {len(partidos)}")
            
            athletic_matches = []
            for partido in partidos:
                home_name = partido.get("home_name", "")
                away_name = partido.get("away_name", "")
                if ('athletic' in home_name.lower() or 'atletico' in home_name.lower() or
                    'athletic' in away_name.lower() or 'atletico' in away_name.lower()):
                    athletic_matches.append(partido)
                    print(f"Found Athletic/Atletico match: {home_name} vs {away_name}")
                    print(f"  Status: {partido.get('status', 'N/A')}")
                    print(f"  Corners: {partido.get('team_a_corners', 'N/A')} + {partido.get('team_b_corners', 'N/A')} = {partido.get('totalCornerCount', 'N/A')}")
            
            if not athletic_matches:
                print("No Athletic/Atletico matches found")
                print("First 5 matches from API:")
                for i, partido in enumerate(partidos[:5]):
                    print(f"  {i+1}. {partido.get('home_name')} vs {partido.get('away_name')}")
            
            return athletic_matches
        else:
            print(f"API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return []
            
    except Exception as e:
        print(f"API Request Error: {e}")
        return []

if __name__ == "__main__":
    print("🔧 INVESTIGATING API ISSUES WITH ATHLETIC CLUB MATCH")
    print("=" * 60)
    print(f"Test run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    result = test_athletic_match_specifically()
    
    raw_matches = test_api_raw_response()
    
    print("\n" + "=" * 60)
    print("API INVESTIGATION SUMMARY")
    print("=" * 60)
    
    if result:
        print("✅ Athletic Club vs Atletico GO match found via search")
        if result.get('total_corners', 0) > 8.5:
            print("✅ Corner bet should be WIN (>8.5 corners)")
        else:
            print(f"❌ Corner bet validation failed: {result.get('total_corners', 0)} corners")
    else:
        print("❌ Athletic Club vs Atletico GO match NOT found via search")
    
    if raw_matches:
        print(f"✅ Found {len(raw_matches)} Athletic/Atletico matches in raw API response")
    else:
        print("❌ No Athletic/Atletico matches found in raw API response")
    
    print(f"\n🏁 Investigation completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
