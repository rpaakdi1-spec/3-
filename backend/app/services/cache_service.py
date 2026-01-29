"""
Advanced Redis Caching Service
- Cache decorators
- Cache invalidation strategies
- Cache warming
"""

import json
import hashlib
from typing import Any, Optional, Callable
from functools import wraps
from datetime import timedelta
import redis
from loguru import logger

from app.core.config import settings


class CacheService:
    """Advanced Redis Caching Service"""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
            decode_responses=True
        )
        self.default_ttl = 300  # 5 minutes
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache"""
        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value, default=str)
            self.redis_client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            return self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """Get remaining TTL for key"""
        try:
            return self.redis_client.ttl(key)
        except Exception as e:
            logger.error(f"Cache TTL error: {e}")
            return -1
    
    def flush_all(self) -> bool:
        """Flush all cache (use with caution)"""
        try:
            self.redis_client.flushdb()
            logger.warning("Cache flushed!")
            return True
        except Exception as e:
            logger.error(f"Cache flush error: {e}")
            return False
    
    def cache_decorator(
        self,
        prefix: str,
        ttl: Optional[int] = None,
        key_builder: Optional[Callable] = None
    ):
        """
        Cache decorator for functions
        
        Usage:
            @cache_service.cache_decorator(prefix="users", ttl=600)
            async def get_user(user_id: int):
                return await db.query(User).filter(User.id == user_id).first()
        """
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Build cache key
                if key_builder:
                    cache_key = key_builder(*args, **kwargs)
                else:
                    cache_key = self._generate_key(prefix, *args, **kwargs)
                
                # Try to get from cache
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit: {cache_key}")
                    return cached_value
                
                # Cache miss - execute function
                logger.debug(f"Cache miss: {cache_key}")
                result = await func(*args, **kwargs)
                
                # Store in cache
                self.set(cache_key, result, ttl=ttl)
                
                return result
            
            return wrapper
        return decorator
    
    def invalidate_cache_group(self, group: str):
        """
        Invalidate all caches in a group
        
        Example:
            cache_service.invalidate_cache_group("users:*")
        """
        deleted = self.delete_pattern(f"{group}*")
        logger.info(f"Invalidated {deleted} cache keys in group: {group}")
        return deleted
    
    def get_cache_stats(self) -> dict:
        """Get cache statistics"""
        try:
            info = self.redis_client.info("stats")
            memory = self.redis_client.info("memory")
            
            return {
                "total_keys": self.redis_client.dbsize(),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0)
                ),
                "memory_used_mb": round(
                    memory.get("used_memory", 0) / 1024 / 1024, 2
                ),
                "memory_peak_mb": round(
                    memory.get("used_memory_peak", 0) / 1024 / 1024, 2
                )
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}
    
    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """Calculate cache hit rate"""
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2)
    
    def warm_cache(self, data_loaders: list):
        """
        Warm cache with frequently accessed data
        
        Args:
            data_loaders: List of (key, loader_func, ttl) tuples
        """
        logger.info(f"Starting cache warming with {len(data_loaders)} loaders")
        
        warmed = 0
        for key, loader_func, ttl in data_loaders:
            try:
                if not self.exists(key):
                    data = loader_func()
                    self.set(key, data, ttl=ttl)
                    warmed += 1
            except Exception as e:
                logger.error(f"Cache warming error for key {key}: {e}")
        
        logger.info(f"Cache warming complete: {warmed}/{len(data_loaders)} keys warmed")
        return warmed


# Global cache service instance
cache_service = CacheService()


# Common cache patterns
class CachePatterns:
    """Common cache key patterns"""
    
    USER = "user:{user_id}"
    VEHICLE = "vehicle:{vehicle_id}"
    DISPATCH = "dispatch:{dispatch_id}"
    ORDER = "order:{order_id}"
    CLIENT = "client:{client_id}"
    
    ANALYTICS_DASHBOARD = "analytics:dashboard"
    ANALYTICS_VEHICLES = "analytics:vehicles"
    ANALYTICS_DRIVERS = "analytics:drivers"
    
    REALTIME_MONITORING = "realtime:monitoring"
    
    @staticmethod
    def user_key(user_id: int) -> str:
        return f"user:{user_id}"
    
    @staticmethod
    def dispatch_list(filters: dict) -> str:
        filter_hash = hashlib.md5(str(sorted(filters.items())).encode()).hexdigest()
        return f"dispatch:list:{filter_hash}"
