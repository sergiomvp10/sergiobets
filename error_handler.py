#!/usr/bin/env python3
"""
Centralized error handling decorator for consistent error management
"""

import functools
import json
import requests
from typing import Any, Callable, Optional

def handle_errors(default_return=None, log_errors=True, error_prefix="Error"):
    """
    Decorator to handle errors consistently across the application
    
    Args:
        default_return: Value to return if an error occurs
        log_errors: Whether to print error messages
        error_prefix: Prefix for error messages
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    print(f"❌ {error_prefix} in {func.__name__}: {e}")
                return default_return
        return wrapper
    return decorator

def safe_api_call(func: Callable) -> Callable:
    """Decorator specifically for API calls with timeout and connection error handling"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except requests.exceptions.Timeout:
            print(f"⏰ Timeout in {func.__name__}")
            return []
        except requests.exceptions.ConnectionError:
            print(f"🌐 Connection error in {func.__name__}")
            return []
        except Exception as e:
            print(f"❌ Error in {func.__name__}: {e}")
            return []
    return wrapper

def safe_file_operation(default_return=None):
    """Decorator for file operations with proper error handling"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except FileNotFoundError:
                print(f"📁 File not found in {func.__name__}")
                return default_return
            except PermissionError:
                print(f"🔒 Permission denied in {func.__name__}")
                return default_return
            except json.JSONDecodeError:
                print(f"📄 Invalid JSON in {func.__name__}")
                return default_return
            except Exception as e:
                print(f"❌ File operation error in {func.__name__}: {e}")
                return default_return
        return wrapper
    return decorator
