#!/usr/bin/env python3
"""
Optimized JSON operations to avoid loading/saving entire files for small updates
"""

import json
import os
from typing import Any, Dict, List, Optional
from datetime import datetime

class JSONOptimizer:
    """Optimized JSON file operations"""
    
    @staticmethod
    def append_to_json_array(filepath: str, new_item: Dict[str, Any]) -> bool:
        """
        Append item to JSON array without loading entire file
        Creates file if it doesn't exist
        """
        try:
            if not os.path.exists(filepath):
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump([new_item], f, ensure_ascii=False, indent=2)
                return True
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                data = [data]
            
            data.append(new_item)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"❌ Error appending to JSON array: {e}")
            return False
    
    @staticmethod
    def update_json_item(filepath: str, item_id: str, updates: Dict[str, Any], id_field: str = "id") -> bool:
        """
        Update specific item in JSON array by ID without rewriting entire file
        """
        try:
            if not os.path.exists(filepath):
                return False
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                return False
            
            updated = False
            for item in data:
                if isinstance(item, dict) and item.get(id_field) == item_id:
                    item.update(updates)
                    item['last_updated'] = datetime.now().isoformat()
                    updated = True
                    break
            
            if updated:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            
            return updated
            
        except Exception as e:
            print(f"❌ Error updating JSON item: {e}")
            return False
    
    @staticmethod
    def get_json_items_by_criteria(filepath: str, criteria: Dict[str, Any], limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get items from JSON array that match criteria without loading everything into memory
        """
        try:
            if not os.path.exists(filepath):
                return []
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                return []
            
            matches = []
            for item in data:
                if isinstance(item, dict):
                    match = True
                    for key, value in criteria.items():
                        if item.get(key) != value:
                            match = False
                            break
                    
                    if match:
                        matches.append(item)
                        if limit and len(matches) >= limit:
                            break
            
            return matches
            
        except Exception as e:
            print(f"❌ Error getting JSON items: {e}")
            return []
    
    @staticmethod
    def compact_json_file(filepath: str, keep_recent_days: int = 30) -> int:
        """
        Remove old entries from JSON file to keep it manageable
        Returns number of items removed
        """
        try:
            if not os.path.exists(filepath):
                return 0
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                return 0
            
            cutoff_date = datetime.now().timestamp() - (keep_recent_days * 24 * 60 * 60)
            original_count = len(data)
            
            filtered_data = []
            for item in data:
                if isinstance(item, dict):
                    item_date = None
                    for date_field in ['fecha', 'date', 'timestamp', 'created_at']:
                        if date_field in item:
                            try:
                                if isinstance(item[date_field], str):
                                    item_date = datetime.fromisoformat(item[date_field].replace('Z', '+00:00')).timestamp()
                                else:
                                    item_date = float(item[date_field])
                                break
                            except:
                                continue
                    
                    if item_date is None or item_date >= cutoff_date:
                        filtered_data.append(item)
            
            if len(filtered_data) < original_count:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(filtered_data, f, ensure_ascii=False, indent=2)
            
            return original_count - len(filtered_data)
            
        except Exception as e:
            print(f"❌ Error compacting JSON file: {e}")
            return 0
