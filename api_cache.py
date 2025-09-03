#!/usr/bin/env python3
"""
Simple API cache system to avoid redundant calls
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

class APICache:
    """Simple file-based cache for API responses"""
    
    def __init__(self, cache_dir: str = "cache", cache_duration_minutes: int = 30):
        self.cache_dir = cache_dir
        self.cache_duration = timedelta(minutes=cache_duration_minutes)
        
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    def _get_cache_file(self, key: str) -> str:
        """Get cache file path for a given key"""
        safe_key = key.replace("/", "_").replace(":", "_").replace(" ", "_")
        return os.path.join(self.cache_dir, f"{safe_key}.json")
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached data if it exists and is not expired"""
        try:
            cache_file = self._get_cache_file(key)
            
            if not os.path.exists(cache_file):
                return None
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cached_time > self.cache_duration:
                os.remove(cache_file)
                return None
            
            return cache_data['data']
            
        except Exception as e:
            print(f"Error reading cache for {key}: {e}")
            return None
    
    def set(self, key: str, data: Dict[str, Any]) -> None:
        """Cache data with current timestamp"""
        try:
            cache_file = self._get_cache_file(key)
            
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Error writing cache for {key}: {e}")
    
    def clear_expired(self) -> int:
        """Clear all expired cache files and return count of cleared files"""
        cleared = 0
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.cache_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            cache_data = json.load(f)
                        
                        cached_time = datetime.fromisoformat(cache_data['timestamp'])
                        if datetime.now() - cached_time > self.cache_duration:
                            os.remove(filepath)
                            cleared += 1
                    except:
                        os.remove(filepath)
                        cleared += 1
        except Exception as e:
            print(f"Error clearing expired cache: {e}")
        
        return cleared
