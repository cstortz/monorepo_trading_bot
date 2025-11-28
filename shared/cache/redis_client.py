"""
Shared Redis Cache Client for Trading Bot Monorepo

Provides caching functionality for all services in the monorepo.
"""

import redis
import json
import os
from typing import Optional, Any, Dict, List
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis cache client for the trading bot monorepo."""
    
    # Cache key prefixes
    CACHE_PREFIX = "trading_bot"
    KRAKEN_PAIRS_KEY = f"{CACHE_PREFIX}:kraken:pairs"
    KRAKEN_PAIRS_ACTIVE_KEY = f"{CACHE_PREFIX}:kraken:pairs:active"
    KRAKEN_PAIRS_TOTAL_KEY = f"{CACHE_PREFIX}:kraken:pairs:total"
    KRAKEN_PAIRS_TIMESTAMP_KEY = f"{CACHE_PREFIX}:kraken:pairs:timestamp"
    
    # Default expiration times (in seconds)
    DEFAULT_EXPIRATION = 3600  # 1 hour
    
    def __init__(
        self, 
        host: Optional[str] = None,
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        decode_responses: bool = True
    ):
        """
        Initialize Redis cache client.
        
        Args:
            host: Redis host (defaults to 'redis' for Docker, 'localhost' otherwise)
            port: Redis port (default: 6379)
            db: Redis database number (default: 0)
            password: Redis password (optional)
            decode_responses: Whether to decode responses as strings (default: True)
        """
        self.host = host or os.getenv("REDIS_HOST", "redis")
        self.port = int(os.getenv("REDIS_PORT", port))
        self.db = db
        self.password = password or os.getenv("REDIS_PASSWORD")
        self.decode_responses = decode_responses
        
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=decode_responses,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.client.ping()
            logger.info(f"Connected to Redis at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None
    
    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        if not self.client:
            return False
        try:
            self.client.ping()
            return True
        except Exception:
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        if not self.is_connected():
            return None
        
        try:
            value = self.client.get(key)
            if value:
                # Try to parse as JSON, fallback to string
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value
            return None
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None
    
    def set(
        self, 
        key: str, 
        value: Any, 
        expiration: Optional[int] = None
    ) -> bool:
        """
        Set a value in cache.
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized if not a string)
            expiration: Expiration time in seconds (default: DEFAULT_EXPIRATION)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            return False
        
        try:
            # Serialize value if not a string
            if not isinstance(value, str):
                value = json.dumps(value)
            
            expiration = expiration or self.DEFAULT_EXPIRATION
            self.client.setex(key, expiration, value)
            return True
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete a key from cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            return False
        
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching a pattern.
        
        Args:
            pattern: Redis key pattern (e.g., "trading_bot:kraken:*")
            
        Returns:
            Number of keys deleted
        """
        if not self.is_connected():
            return 0
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error clearing cache pattern {pattern}: {e}")
            return 0
    
    def get_kraken_pairs(self) -> Optional[Dict[str, Any]]:
        """
        Get cached Kraken pairs.
        
        Returns:
            Dictionary with pairs data or None if not cached
        """
        if not self.is_connected():
            return None
        
        try:
            pairs_data = self.get(self.KRAKEN_PAIRS_KEY)
            if pairs_data:
                return pairs_data
            return None
        except Exception as e:
            logger.error(f"Error getting cached Kraken pairs: {e}")
            return None
    
    def set_kraken_pairs(
        self, 
        pairs: Dict[str, Any],
        expiration: int = DEFAULT_EXPIRATION
    ) -> bool:
        """
        Cache Kraken pairs data.
        
        Args:
            pairs: Dictionary containing pairs data
            expiration: Expiration time in seconds (default: 1 hour)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            return False
        
        try:
            # Store main pairs data
            success = self.set(self.KRAKEN_PAIRS_KEY, pairs, expiration)
            
            # Also store metadata separately for quick access
            if success and isinstance(pairs, dict):
                if "active_pairs" in pairs:
                    self.client.setex(
                        self.KRAKEN_PAIRS_ACTIVE_KEY,
                        expiration,
                        pairs["active_pairs"]
                    )
                if "total_pairs" in pairs:
                    self.client.setex(
                        self.KRAKEN_PAIRS_TOTAL_KEY,
                        expiration,
                        pairs["total_pairs"]
                    )
                # Store timestamp
                from datetime import datetime
                self.client.setex(
                    self.KRAKEN_PAIRS_TIMESTAMP_KEY,
                    expiration,
                    datetime.utcnow().isoformat()
                )
            
            return success
        except Exception as e:
            logger.error(f"Error caching Kraken pairs: {e}")
            return False
    
    def clear_kraken_pairs_cache(self) -> bool:
        """
        Clear all Kraken pairs cache.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            return False
        
        try:
            pattern = f"{self.CACHE_PREFIX}:kraken:pairs*"
            deleted = self.clear_pattern(pattern)
            logger.info(f"Cleared {deleted} Kraken pairs cache keys")
            return True
        except Exception as e:
            logger.error(f"Error clearing Kraken pairs cache: {e}")
            return False
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get cache information and statistics.
        
        Returns:
            Dictionary with cache info
        """
        if not self.is_connected():
            return {
                "connected": False,
                "message": "Redis not connected"
            }
        
        try:
            info = self.client.info()
            cached_pairs = self.get_kraken_pairs()
            timestamp = self.client.get(self.KRAKEN_PAIRS_TIMESTAMP_KEY)
            
            return {
                "connected": True,
                "host": self.host,
                "port": self.port,
                "db": self.db,
                "kraken_pairs_cached": cached_pairs is not None,
                "kraken_pairs_timestamp": timestamp,
                "redis_version": info.get("redis_version"),
                "used_memory_human": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients")
            }
        except Exception as e:
            logger.error(f"Error getting cache info: {e}")
            return {
                "connected": False,
                "error": str(e)
            }


# Global cache instance
_cache_instance: Optional[RedisCache] = None


def get_cache() -> Optional[RedisCache]:
    """
    Get or create the global Redis cache instance.
    
    Returns:
        RedisCache instance or None if Redis is unavailable
    """
    global _cache_instance
    
    if _cache_instance is None:
        _cache_instance = RedisCache()
    
    if not _cache_instance.is_connected():
        return None
    
    return _cache_instance

