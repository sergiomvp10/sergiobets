#!/usr/bin/env python3
"""
Thread pool manager for efficient concurrent operations
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Callable, Any, Dict
import threading

class ThreadPoolManager:
    """Manages thread pools for different types of operations"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self._executor = None
        self._lock = threading.Lock()
    
    def get_executor(self) -> ThreadPoolExecutor:
        """Get or create thread pool executor"""
        if self._executor is None:
            with self._lock:
                if self._executor is None:
                    self._executor = ThreadPoolExecutor(max_workers=self.max_workers)
        return self._executor
    
    def execute_parallel(self, func: Callable, items: List[Any], timeout: int = 30) -> List[Any]:
        """
        Execute function on multiple items in parallel
        
        Args:
            func: Function to execute
            items: List of items to process
            timeout: Timeout for all operations
            
        Returns:
            List of results (None for failed operations)
        """
        if not items:
            return []
        
        executor = self.get_executor()
        results = [None] * len(items)
        
        try:
            future_to_index = {
                executor.submit(func, item): i 
                for i, item in enumerate(items)
            }
            
            for future in as_completed(future_to_index, timeout=timeout):
                index = future_to_index[future]
                try:
                    results[index] = future.result()
                except Exception as e:
                    print(f"❌ Task {index} failed: {e}")
                    results[index] = None
                    
        except Exception as e:
            print(f"❌ Parallel execution error: {e}")
        
        return results
    
    def shutdown(self):
        """Shutdown the thread pool"""
        if self._executor:
            self._executor.shutdown(wait=True)
            self._executor = None

thread_manager = ThreadPoolManager(max_workers=4)
