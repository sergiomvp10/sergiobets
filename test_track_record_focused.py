#!/usr/bin/env python3
"""
Focused test for track record update with specific match
"""

from track_record import TrackRecordManager

def test_focused_update():
    """Test track record update with Athletic Club match specifically"""
    print("=" * 60)
    print("TESTING FOCUSED TRACK RECORD UPDATE")
    print("=" * 60)
    
    api_key = 'b37303668c4be1b78ac35b9e96460458e72b74749814a7d6f44983ac4b432079'
    tracker = TrackRecordManager(api_key)
    
    print("Running focused update with max_matches=1, timeout_per_match=15")
    result = tracker.actualizar_historial_con_resultados(max_matches=1, timeout_per_match=15)
    
    print(f"Update result: {result}")
    return result

if __name__ == "__main__":
    test_focused_update()
