#!/usr/bin/env python3
"""
Test script to verify optimizations work correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_cache import APICache
from thread_pool_manager import ThreadPoolManager
from json_optimizer import JSONOptimizer
from error_handler import handle_errors, safe_api_call
import time
import json

def test_api_cache():
    """Test API caching functionality"""
    print("🧪 TESTING API CACHE")
    print("=" * 40)
    
    cache = APICache(cache_duration_minutes=1)  # Short duration for testing
    
    result = cache.get("test_key")
    print(f"Cache miss result: {result}")
    
    test_data = {"matches": [{"team1": "A", "team2": "B"}]}
    cache.set("test_key", test_data)
    
    result = cache.get("test_key")
    print(f"Cache hit result: {result}")
    
    print("Waiting for cache expiration...")
    time.sleep(65)  # Wait for expiration
    
    result = cache.get("test_key")
    print(f"Expired cache result: {result}")
    
    print("✅ API Cache test completed\n")

def test_thread_pool():
    """Test thread pool functionality"""
    print("🧪 TESTING THREAD POOL")
    print("=" * 40)
    
    def sample_task(x):
        time.sleep(0.1)  # Simulate work
        return x * 2
    
    manager = ThreadPoolManager(max_workers=2)
    
    items = [1, 2, 3, 4, 5]
    start_time = time.time()
    
    results = manager.execute_parallel(sample_task, items, timeout=10)
    
    end_time = time.time()
    
    print(f"Input: {items}")
    print(f"Results: {results}")
    print(f"Time taken: {end_time - start_time:.2f}s")
    
    manager.shutdown()
    print("✅ Thread Pool test completed\n")

def test_json_optimizer():
    """Test JSON optimization functionality"""
    print("🧪 TESTING JSON OPTIMIZER")
    print("=" * 40)
    
    test_file = "test_optimization.json"
    
    if os.path.exists(test_file):
        os.remove(test_file)
    
    item1 = {"id": "1", "name": "Test 1", "value": 100}
    success = JSONOptimizer.append_to_json_array(test_file, item1)
    print(f"Append to new file: {success}")
    
    item2 = {"id": "2", "name": "Test 2", "value": 200}
    success = JSONOptimizer.append_to_json_array(test_file, item2)
    print(f"Append to existing file: {success}")
    
    updates = {"value": 150, "updated": True}
    success = JSONOptimizer.update_json_item(test_file, "1", updates)
    print(f"Update item: {success}")
    
    items = JSONOptimizer.get_json_items_by_criteria(test_file, {"updated": True})
    print(f"Items with updated=True: {len(items)}")
    
    if os.path.exists(test_file):
        os.remove(test_file)
    
    print("✅ JSON Optimizer test completed\n")

@handle_errors(default_return="Error handled")
def test_error_handler():
    """Test error handling decorator"""
    print("🧪 TESTING ERROR HANDLER")
    print("=" * 40)
    
    result = 1 / 0
    return "This won't be reached"

def run_all_tests():
    """Run all optimization tests"""
    print("🚀 RUNNING OPTIMIZATION TESTS")
    print("=" * 50)
    
    test_api_cache()
    test_thread_pool()
    test_json_optimizer()
    
    result = test_error_handler()
    print(f"Error handler result: {result}")
    
    print("🎉 ALL OPTIMIZATION TESTS COMPLETED!")

if __name__ == "__main__":
    run_all_tests()
