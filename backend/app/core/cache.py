"""
Cache implementation for improved API performance.
"""
import time
import functools
import hashlib
import json
from typing import Dict, Any, Callable, Optional, TypeVar, cast
import logging

from app.core.config import settings

# Type variable for generic function return type
T = TypeVar('T')

# Setup logger
logger = logging.getLogger(__name__)

# In-memory cache storage
_cache: Dict[str, Dict[str, Any]] = {}

def _generate_cache_key(func_name: str, args: tuple, kwargs: Dict[str, Any]) -> str:
    """
    Generate a cache key from function name and arguments.
    
    Args:
        func_name: Name of the function being cached
        args: Positional arguments
        kwargs: Keyword arguments
        
    Returns:
        Cache key string
    """
    # Convert arguments to a JSON-serializable format
    cache_data = {
        'func': func_name,
        'args': [str(arg) for arg in args],
        'kwargs': {k: str(v) for k, v in kwargs.items()}
    }
    
    # Convert to JSON and create hash
    json_data = json.dumps(cache_data, sort_keys=True)
    return hashlib.md5(json_data.encode()).hexdigest()

def cache(ttl: Optional[int] = None) -> Callable:
    """
    Cache decorator for functions.
    
    Args:
        ttl: Time-to-live in seconds (defaults to settings.CACHE_TTL)
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Skip caching if disabled in settings
            if not settings.ENABLE_CACHE:
                return func(*args, **kwargs)
            
            # Set TTL from parameter or settings
            cache_ttl = ttl if ttl is not None else settings.CACHE_TTL
            
            # Generate cache key
            cache_key = _generate_cache_key(func.__name__, args, kwargs)
            
            # Check if result is in cache and not expired
            if cache_key in _cache:
                entry = _cache[cache_key]
                if entry['expire_time'] > time.time():
                    logger.debug(f"Cache hit: {func.__name__}")
                    return cast(T, entry['value'])
                else:
                    # Remove expired entry
                    logger.debug(f"Cache expired: {func.__name__}")
                    del _cache[cache_key]
            
            # Calculate and cache result
            result = func(*args, **kwargs)
            _cache[cache_key] = {
                'value': result,
                'expire_time': time.time() + cache_ttl
            }
            logger.debug(f"Cache miss: {func.__name__}")
            
            return result
        return wrapper
    return decorator

def clear_cache() -> None:
    """Clear all cached data."""
    global _cache
    _cache = {}
    logger.info("Cache cleared")

def get_cache_stats() -> Dict[str, int]:
    """
    Get statistics about the cache.
    
    Returns:
        Dictionary with cache statistics
    """
    # Count total, expired, and valid entries
    now = time.time()
    total = len(_cache)
    expired = sum(1 for entry in _cache.values() if entry['expire_time'] <= now)
    valid = total - expired
    
    return {
        "total_entries": total,
        "expired_entries": expired,
        "valid_entries": valid
    }

def remove_expired_entries() -> int:
    """
    Remove all expired entries from the cache.
    
    Returns:
        Number of removed entries
    """
    global _cache
    now = time.time()
    expired_keys = [
        key for key, entry in _cache.items() 
        if entry['expire_time'] <= now
    ]
    
    for key in expired_keys:
        del _cache[key]
    
    removed_count = len(expired_keys)
    logger.info(f"Removed {removed_count} expired cache entries")
    
    return removed_count
