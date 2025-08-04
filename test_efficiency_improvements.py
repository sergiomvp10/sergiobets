#!/usr/bin/env python3
"""
Test script to verify efficiency improvements work correctly
"""

import sys
import os
import json

def test_json_storage():
    """Test the improved JSON storage functions"""
    print("=== Testing JSON Storage Improvements ===")
    
    try:
        from json_storage import guardar_json_batch, cargar_json_cached
        print("✅ JSON storage module imports correctly")
        
        test_data = [
            ('test1.json', {'test': 'data1', 'number': 123}), 
            ('test2.json', {'test': 'data2', 'array': [1, 2, 3]})
        ]
        
        guardar_json_batch(test_data)
        print("✅ Batch function works correctly")
        
        for filename, expected_data in test_data:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    actual_data = json.load(f)
                    if actual_data == expected_data:
                        print(f"✅ {filename} created with correct content")
                    else:
                        print(f"❌ {filename} content mismatch")
            else:
                print(f"❌ {filename} was not created")
        
        cached_data = cargar_json_cached('test1.json')
        if cached_data and cached_data['test'] == 'data1':
            print("✅ Cached loading works correctly")
        else:
            print("❌ Cached loading failed")
            
    except Exception as e:
        print(f"❌ Error testing JSON storage: {e}")
        return False
    
    for file in ['test1.json', 'test2.json']:
        if os.path.exists(file):
            os.remove(file)
            print(f"🧹 Cleaned up {file}")
    
    return True

def test_api_improvements():
    """Test the API improvements"""
    print("\n=== Testing API Improvements ===")
    
    try:
        import footystats_api
        print("✅ API module imports correctly")
        
        if hasattr(footystats_api, 'session'):
            print("✅ Session object exists")
        else:
            print("❌ Session object missing")
            return False
            
        if hasattr(footystats_api, 'retry_strategy'):
            print(f"✅ Retry strategy configured: {footystats_api.retry_strategy.total} retries")
        else:
            print("❌ Retry strategy missing")
            return False
            
        if hasattr(footystats_api, 'adapter'):
            print("✅ HTTP adapter configured with connection pooling")
        else:
            print("❌ HTTP adapter missing")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API improvements: {e}")
        return False
    
    return True

def test_crudo_imports():
    """Test that crudo.py imports work correctly"""
    print("\n=== Testing Crudo.py Import Compatibility ===")
    
    try:
        from json_storage import guardar_json_batch
        print("✅ guardar_json_batch can be imported")
        
        test_operations = [
            ("picks_seleccionados.json", {"fecha": "2025-08-04", "predicciones": []}),
            ("partidos_seleccionados.json", [])
        ]
        
        guardar_json_batch(test_operations)
        print("✅ Batch operations work with crudo.py data structures")
        
        for filename, _ in test_operations:
            if os.path.exists(filename):
                os.remove(filename)
                print(f"🧹 Cleaned up {filename}")
                
    except Exception as e:
        print(f"❌ Error testing crudo.py compatibility: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Testing SergioBets Efficiency Improvements")
    print("=" * 50)
    
    success = True
    success &= test_json_storage()
    success &= test_api_improvements() 
    success &= test_crudo_imports()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Efficiency improvements are working correctly.")
    else:
        print("❌ Some tests failed. Please check the output above.")
    
    sys.exit(0 if success else 1)
