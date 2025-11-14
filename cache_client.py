"""
Shared Redis Cache Client for Project Lavos Platform
Provides unified caching across all services (C++, Spring Boot, FastAPI)

@author Matthew David Scott
"""

import redis
import json
import hashlib
import os
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)

class CacheClient:
    """Redis cache client with intelligent key management."""

    def __init__(self, redis_url: str = None):
        """
        Initialize Redis client.

        Args:
            redis_url: Redis connection URL (default: localhost:6379)
        """
        if redis_url is None:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

        try:
            self.redis = redis.from_url(redis_url, decode_responses=True)
            self.redis.ping()
            logger.info(f"Connected to Redis: {redis_url}")
        except Exception as e:
            logger.warning(f"Redis unavailable: {e}. Caching disabled.")
            self.redis = None

    def _generate_key(self, service: str, input_data: str) -> str:
        """Generate cache key from service name and input."""
        hash_value = hashlib.sha256(input_data.encode()).hexdigest()[:16]
        return f"{service}:{hash_value}"

    def get(self, service: str, input_data: str) -> Optional[Any]:
        """
        Get cached result.

        Args:
            service: Service name ('sentiment', 'phishing', 'leads', etc.)
            input_data: Input text/data

        Returns:
            Cached result or None if not found
        """
        if self.redis is None:
            return None

        try:
            key = self._generate_key(service, input_data)
            cached = self.redis.get(key)

            if cached:
                logger.debug(f"Cache HIT: {service}:{input_data[:30]}...")
                return json.loads(cached)
            else:
                logger.debug(f"Cache MISS: {service}:{input_data[:30]}...")
                return None

        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    def set(self, service: str, input_data: str, result: Any, ttl: int = 3600):
        """
        Cache result with TTL.

        Args:
            service: Service name
            input_data: Input text/data
            result: Result to cache
            ttl: Time to live in seconds (default: 1 hour)
        """
        if self.redis is None:
            return

        try:
            key = self._generate_key(service, input_data)
            self.redis.setex(key, ttl, json.dumps(result))
            logger.debug(f"Cached: {service}:{input_data[:30]}... (TTL: {ttl}s)")
        except Exception as e:
            logger.error(f"Cache set error: {e}")

    def get_stats(self) -> dict:
        """Get Redis statistics."""
        if self.redis is None:
            return {"status": "disabled"}

        try:
            info = self.redis.info()
            return {
                "status": "connected",
                "used_memory_human": info.get("used_memory_human"),
                "total_keys": self.redis.dbsize(),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(info)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _calculate_hit_rate(self, info: dict) -> float:
        """Calculate cache hit rate percentage."""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses

        if total == 0:
            return 0.0

        return round((hits / total) * 100, 2)


# Singleton instance
_cache_client = None

def get_cache() -> CacheClient:
    """Get shared cache client instance."""
    global _cache_client
    if _cache_client is None:
        _cache_client = CacheClient()
    return _cache_client
