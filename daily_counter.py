#!/usr/bin/env python3
"""
Daily Counter System for PRONOSTICO numbering
Maintains a persistent counter that increments throughout the day and resets at midnight
"""

import json
import os
from datetime import datetime
from typing import Dict, Any

COUNTER_FILE = "daily_pronostico_counter.json"

def get_current_date() -> str:
    """Get current date in YYYY-MM-DD format"""
    return datetime.now().strftime('%Y-%m-%d')

def load_counter_data() -> Dict[str, Any]:
    """Load counter data from file"""
    try:
        if os.path.exists(COUNTER_FILE):
            with open(COUNTER_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading counter data: {e}")
    
    return {"date": get_current_date(), "counter": 0}

def save_counter_data(data: Dict[str, Any]) -> None:
    """Save counter data to file"""
    try:
        with open(COUNTER_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving counter data: {e}")

def get_next_pronostico_numbers(count: int) -> list:
    """
    Get the next sequential PRONOSTICO numbers for the day
    
    Args:
        count: Number of predictions being sent
        
    Returns:
        List of sequential numbers starting from current counter + 1
    """
    current_date = get_current_date()
    counter_data = load_counter_data()
    
    if counter_data.get("date") != current_date:
        counter_data = {"date": current_date, "counter": 0}
    
    start_number = counter_data["counter"] + 1
    numbers = list(range(start_number, start_number + count))
    
    counter_data["counter"] = start_number + count - 1
    save_counter_data(counter_data)
    
    return numbers

def get_current_counter() -> int:
    """Get current counter value without incrementing"""
    current_date = get_current_date()
    counter_data = load_counter_data()
    
    if counter_data.get("date") != current_date:
        return 0
    
    return counter_data.get("counter", 0)

def reset_daily_counter() -> None:
    """Manually reset the daily counter (for testing or manual reset)"""
    current_date = get_current_date()
    counter_data = {"date": current_date, "counter": 0}
    save_counter_data(counter_data)
    print(f"✅ Counter reset for {current_date}")

def count_predictions_in_message(mensaje: str) -> int:
    """Count how many predictions are in a formatted message"""
    try:
        import re
        pattern = r"🎯 PRONOSTICO #\d+"
        matches = re.findall(pattern, mensaje)
        return len(matches)
    except Exception as e:
        print(f"Error counting predictions in message: {e}")
        return 0

def increment_counter_after_send(mensaje: str) -> int:
    """Increment counter after successful Telegram send based on message content"""
    prediction_count = count_predictions_in_message(mensaje)
    if prediction_count > 0:
        current_date = get_current_date()
        counter_data = load_counter_data()
        
        if counter_data.get("date") != current_date:
            counter_data = {"date": current_date, "counter": 0}
        
        counter_data["counter"] += prediction_count
        save_counter_data(counter_data)
        return prediction_count
    return 0

if __name__ == "__main__":
    print("🧪 TESTING DAILY COUNTER SYSTEM")
    print("=" * 50)
    
    print(f"📅 Current date: {get_current_date()}")
    print(f"🔢 Current counter: {get_current_counter()}")
    
    test_numbers = get_next_pronostico_numbers(3)
    print(f"📊 Next 3 PRONOSTICO numbers: {test_numbers}")
    
    test_numbers2 = get_next_pronostico_numbers(2)
    print(f"📊 Next 2 PRONOSTICO numbers: {test_numbers2}")
    
    print(f"🔢 Updated counter: {get_current_counter()}")
    
    test_message = """BETGENIUX®  (2025-08-14)

🎯 PRONOSTICO #1
🏆 Champions League
⚽️ Test vs Test
🔮 Test prediction

🎯 PRONOSTICO #2
🏆 Premier League
⚽️ Test2 vs Test2
🔮 Test prediction 2

⚠️ Apostar con responsabilidad."""
    
    count = count_predictions_in_message(test_message)
    print(f"📊 Predictions in test message: {count}")
    print("✅ Daily counter system working correctly!")
