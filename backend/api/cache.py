"""
Redis caching layer (with fallback to in-memory cache)
"""

import json
import os
from typing import Optional, Any
from datetime import timedelta

# Try to import Redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# In-memory cache fallback
memory_cache = {}
cache_ttl = {}


def get_redis_client():
    """Get Redis client"""
    if not REDIS_AVAILABLE:
        return None
    
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    try:
        r = redis.from_url(redis_url, decode_responses=True)
        r.ping()
        return r
    except:
        return None


def get_cached_recommendations(key: str) -> Optional[Any]:
    """Get cached recommendations"""
    redis_client = get_redis_client()
    
    if redis_client:
        try:
            cached = redis_client.get(key)
            if cached:
                return json.loads(cached)
        except:
            pass
    
    # Fallback to memory cache
    if key in memory_cache:
        return memory_cache[key]
    
    return None


def cache_recommendations(key: str, data: Any, ttl: int = 3600):
    """Cache recommendations"""
    redis_client = get_redis_client()
    
    if redis_client:
        try:
            redis_client.setex(key, ttl, json.dumps(data, default=str))
            return
        except:
            pass
    
    # Fallback to memory cache
    memory_cache[key] = data
    cache_ttl[key] = timedelta(seconds=ttl)


def get_cached_movie(key: str) -> Optional[Any]:
    """Get cached movie"""
    redis_client = get_redis_client()
    
    if redis_client:
        try:
            cached = redis_client.get(key)
            if cached:
                return json.loads(cached)
        except:
            pass
    
    if key in memory_cache:
        return memory_cache[key]
    
    return None


def cache_movie(key: str, data: Any, ttl: int = 86400):
    """Cache movie data"""
    redis_client = get_redis_client()
    
    if redis_client:
        try:
            redis_client.setex(key, ttl, json.dumps(data, default=str))
            return
        except:
            pass
    
    memory_cache[key] = data
    cache_ttl[key] = timedelta(seconds=ttl)

