"""
Redis cache implementation for the Poly Micro Manager backend.
This module provides cache functionality to improve performance by caching frequently accessed data.
"""
import json
import os
from typing import Any, Optional, Union, Dict
import redis
import logging
from datetime import timedelta
from functools import wraps

# Set up logging
logger = logging.getLogger("cache")

# Get Redis configuration from environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "False").lower() in ("true", "1", "t")
CACHE_TTL = int(os.getenv("CACHE_TTL", 300))  # Default 5 minutes

# Initialize Redis client
redis_client = None
if CACHE_ENABLED:
    try:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1
        )
        redis_client.ping()  # Test connection
        logger.info(f"Redis cache initialized at {REDIS_HOST}:{REDIS_PORT}")
    except redis.RedisError as e:
        logger.warning(f"Redis connection failed: {e}. Cache will be disabled.")
        redis_client = None
        CACHE_ENABLED = False


def serialize(data: Any) -> str:
    """Serialize data to JSON string"""
    return json.dumps(data)


def deserialize(data_str: str) -> Any:
    """Deserialize JSON string to data"""
    return json.loads(data_str)


async def get_cache(key: str) -> Optional[Any]:
    """Get data from cache by key"""
    if not CACHE_ENABLED or not redis_client:
        return None
    
    try:
        cached_data = redis_client.get(key)
        if cached_data:
            logger.debug(f"Cache hit for key: {key}")
            return deserialize(cached_data)
        logger.debug(f"Cache miss for key: {key}")
        return None
    except Exception as e:
        logger.error(f"Error getting data from cache: {e}")
        return None


async def set_cache(key: str, data: Any, ttl: int = CACHE_TTL) -> bool:
    """Set data in cache with expiration time"""
    if not CACHE_ENABLED or not redis_client:
        return False
    
    try:
        serialized_data = serialize(data)
        return redis_client.setex(key, ttl, serialized_data)
    except Exception as e:
        logger.error(f"Error setting data in cache: {e}")
        return False


async def delete_cache(key: str) -> bool:
    """Delete data from cache by key"""
    if not CACHE_ENABLED or not redis_client:
        return False
    
    try:
        return bool(redis_client.delete(key))
    except Exception as e:
        logger.error(f"Error deleting data from cache: {e}")
        return False


async def clear_cache_pattern(pattern: str) -> int:
    """Clear all keys matching pattern"""
    if not CACHE_ENABLED or not redis_client:
        return 0
    
    try:
        keys = redis_client.keys(pattern)
        if keys:
            return redis_client.delete(*keys)
        return 0
    except Exception as e:
        logger.error(f"Error clearing cache pattern: {e}")
        return 0


def cache_key_builder(prefix: str, *args, **kwargs) -> str:
    """Build a cache key from prefix and parameters"""
    # Create key from positional args and keyword args
    key_parts = [prefix]
    
    if args:
        key_parts.extend([str(arg) for arg in args])
    
    if kwargs:
        # Sort kwargs by key to ensure consistent order
        for k, v in sorted(kwargs.items()):
            if k != "self" and k != "cls":
                key_parts.append(f"{k}:{v}")
    
    return ":".join(key_parts)


def cached(ttl: int = CACHE_TTL, prefix: Optional[str] = None):
    """
    Decorator to cache function results.
    
    Usage:
        @cached(ttl=300, prefix="projects")
        async def get_projects(self):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not CACHE_ENABLED:
                return await func(*args, **kwargs)
            
            # Generate cache key
            cache_prefix = prefix or f"cache:{func.__module__}:{func.__name__}"
            cache_key = cache_key_builder(cache_prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_result = await get_cache(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            if result is not None:
                await set_cache(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


def invalidate_cache(prefix: str):
    """
    Decorator to invalidate cache after function execution.
    
    Usage:
        @invalidate_cache(prefix="projects")
        async def update_project(self, project_id, data):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            if CACHE_ENABLED:
                pattern = f"{prefix}*"
                await clear_cache_pattern(pattern)
                logger.debug(f"Invalidated cache pattern: {pattern}")
            
            return result
        return wrapper
    return decorator
