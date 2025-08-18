#!/usr/bin/env python3
"""Test daily counter persistence and reset functionality"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_daily_counter_persistence():
    """Test that counter persists between calls and resets daily"""
    print("🧪 TESTING DAILY COUNTER PERSISTENCE")
    print("=" * 50)
    
    try:
        from daily_counter import get_current_counter, get_next_pronostico_numbers, reset_daily_counter
        
        print("Testing daily counter persistence...")
        reset_daily_counter()
        
        print(f"Initial counter: {get_current_counter()}")
        
        nums1 = get_next_pronostico_numbers(2)
        print(f"First batch: {nums1}")
        print(f"Counter after first batch: {get_current_counter()}")
        
        nums2 = get_next_pronostico_numbers(1)
        print(f"Second batch: {nums2}")
        print(f"Counter after second batch: {get_current_counter()}")
        
        nums3 = get_next_pronostico_numbers(3)
        print(f"Third batch: {nums3}")
        print(f"Final counter: {get_current_counter()}")
        
        expected_sequence = [1, 2, 3, 4, 5, 6]
        actual_sequence = nums1 + nums2 + nums3
        
        if actual_sequence == expected_sequence:
            print("✅ Counter persistence test PASSED!")
            print(f"Expected: {expected_sequence}")
            print(f"Actual: {actual_sequence}")
            return True
        else:
            print("❌ Counter persistence test FAILED!")
            print(f"Expected: {expected_sequence}")
            print(f"Actual: {actual_sequence}")
            return False
        
    except Exception as e:
        print(f"❌ Error testing counter persistence: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_daily_counter_persistence()
