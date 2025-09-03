#!/usr/bin/env python3
"""Quick test to verify optimizations work without long waits"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all optimization modules can be imported"""
    print("🧪 TESTING OPTIMIZATION IMPORTS")
    print("=" * 40)
    
    try:
        from api_cache import APICache
        print("✅ APICache imported successfully")
        
        from error_handler import safe_api_call, safe_file_operation
        print("✅ Error handlers imported successfully")
        
        from thread_pool_manager import ThreadPoolManager, thread_manager
        print("✅ Thread pool manager imported successfully")
        
        from json_optimizer import JSONOptimizer
        print("✅ JSON optimizer imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality of optimization modules"""
    print("\n🧪 TESTING BASIC FUNCTIONALITY")
    print("=" * 40)
    
    try:
        cache = APICache(cache_duration_minutes=1)
        cache.set("test_key", {"test": "data"})
        result = cache.get("test_key")
        if result and result.get("test") == "data":
            print("✅ API Cache basic functionality works")
        else:
            print("❌ API Cache test failed")
            return False
        
        executor = thread_manager.get_executor()
        if executor:
            print("✅ Thread pool executor available")
        else:
            print("❌ Thread pool executor failed")
            return False
        
        test_file = "test_json_opt.json"
        success = JSONOptimizer.append_to_json_array(test_file, {"test": "item"})
        if success and os.path.exists(test_file):
            print("✅ JSON optimizer basic functionality works")
            os.remove(test_file)  # Cleanup
        else:
            print("❌ JSON optimizer test failed")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        return False

def test_integration():
    """Test integration with existing code"""
    print("\n🧪 TESTING INTEGRATION")
    print("=" * 40)
    
    try:
        from footystats_api import clear_api_cache
        cleared = clear_api_cache()
        print(f"✅ API cache clearing works (cleared {cleared} entries)")
        
        print("✅ All integrations appear to be working")
        
        return True
    except Exception as e:
        print(f"❌ Integration test error: {e}")
        return False

def run_quick_tests():
    """Run all quick tests"""
    print("🚀 RUNNING QUICK OPTIMIZATION VERIFICATION")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_basic_functionality,
        test_integration
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 RESULTS: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 ALL OPTIMIZATION TESTS PASSED!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = run_quick_tests()
    sys.exit(0 if success else 1)
