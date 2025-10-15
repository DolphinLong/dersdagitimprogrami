# -*- coding: utf-8 -*-
"""
Comprehensive Cache Manager
Extends caching strategy beyond teacher availability
"""

import logging
import time
from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Centralized cache management system
    
    Provides caching for:
    - Teacher availability
    - Class schedules
    - Teacher schedules
    - Lesson assignments
    - Database queries
    """

    def __init__(self, ttl: int = 300):
        """
        Initialize cache manager
        
        Args:
            ttl: Time to live in seconds (default: 5 minutes)
        """
        self.ttl = ttl
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._hit_count = 0
        self._miss_count = 0

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        if key not in self._cache:
            self._miss_count += 1
            return None

        value, timestamp = self._cache[key]
        
        # Check if expired
        if time.time() - timestamp > self.ttl:
            del self._cache[key]
            self._miss_count += 1
            return None

        self._hit_count += 1
        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
        """
        self._cache[key] = (value, time.time())

    def delete(self, key: str) -> None:
        """
        Delete value from cache
        
        Args:
            key: Cache key
        """
        if key in self._cache:
            del self._cache[key]

    def clear(self) -> None:
        """Clear all cache"""
        self._cache.clear()
        self._hit_count = 0
        self._miss_count = 0

    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching pattern
        
        Args:
            pattern: Pattern to match (simple string matching)
            
        Returns:
            Number of keys invalidated
        """
        keys_to_delete = [
            key for key in self._cache.keys()
            if pattern in key
        ]
        
        for key in keys_to_delete:
            del self._cache[key]
        
        return len(keys_to_delete)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache stats
        """
        total_requests = self._hit_count + self._miss_count
        hit_rate = (
            self._hit_count / total_requests * 100
            if total_requests > 0
            else 0
        )
        
        return {
            'size': len(self._cache),
            'hits': self._hit_count,
            'misses': self._miss_count,
            'hit_rate': hit_rate,
            'ttl': self.ttl
        }


# Global cache instance
_global_cache = None


def get_cache() -> CacheManager:
    """
    Get global cache instance
    
    Returns:
        CacheManager instance
    """
    global _global_cache
    if _global_cache is None:
        _global_cache = CacheManager()
    return _global_cache


def cached(ttl: Optional[int] = None, key_prefix: str = ""):
    """
    Decorator for caching function results
    
    Args:
        ttl: Time to live in seconds (None = use cache default)
        key_prefix: Prefix for cache key
        
    Example:
        @cached(ttl=60, key_prefix="schedule")
        def get_class_schedule(class_id):
            # Expensive operation
            return schedule
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache()
            
            # Generate cache key
            key_parts = [key_prefix, func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return result
            
            # Execute function
            logger.debug(f"Cache miss: {cache_key}")
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result)
            
            return result
        
        return wrapper
    return decorator


class LRUCache:
    """
    Least Recently Used (LRU) Cache
    
    More sophisticated caching with size limit
    """

    def __init__(self, max_size: int = 100):
        """
        Initialize LRU cache
        
        Args:
            max_size: Maximum number of items to cache
        """
        self.max_size = max_size
        self._cache: Dict[str, Any] = {}
        self._access_order: list = []

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        if key not in self._cache:
            return None

        # Update access order
        self._access_order.remove(key)
        self._access_order.append(key)
        
        return self._cache[key]

    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
        """
        # If key exists, update it
        if key in self._cache:
            self._access_order.remove(key)
        
        # If cache is full, remove least recently used
        elif len(self._cache) >= self.max_size:
            lru_key = self._access_order.pop(0)
            del self._cache[lru_key]
        
        # Add new item
        self._cache[key] = value
        self._access_order.append(key)

    def clear(self) -> None:
        """Clear cache"""
        self._cache.clear()
        self._access_order.clear()

    def size(self) -> int:
        """Get current cache size"""
        return len(self._cache)


class ScheduleCache:
    """
    Specialized cache for schedule data
    
    Provides domain-specific caching for schedules
    """

    def __init__(self):
        """Initialize schedule cache"""
        self._class_schedules = CacheManager(ttl=600)  # 10 minutes
        self._teacher_schedules = CacheManager(ttl=600)
        self._lesson_assignments = CacheManager(ttl=300)  # 5 minutes

    def get_class_schedule(self, class_id: int) -> Optional[list]:
        """Get cached class schedule"""
        return self._class_schedules.get(f"class:{class_id}")

    def set_class_schedule(self, class_id: int, schedule: list) -> None:
        """Cache class schedule"""
        self._class_schedules.set(f"class:{class_id}", schedule)

    def get_teacher_schedule(self, teacher_id: int) -> Optional[list]:
        """Get cached teacher schedule"""
        return self._teacher_schedules.get(f"teacher:{teacher_id}")

    def set_teacher_schedule(self, teacher_id: int, schedule: list) -> None:
        """Cache teacher schedule"""
        self._teacher_schedules.set(f"teacher:{teacher_id}", schedule)

    def get_lesson_assignments(self, class_id: int) -> Optional[list]:
        """Get cached lesson assignments"""
        return self._lesson_assignments.get(f"assignments:{class_id}")

    def set_lesson_assignments(self, class_id: int, assignments: list) -> None:
        """Cache lesson assignments"""
        self._lesson_assignments.set(f"assignments:{class_id}", assignments)

    def invalidate_class(self, class_id: int) -> None:
        """Invalidate all cache for a class"""
        self._class_schedules.delete(f"class:{class_id}")
        self._lesson_assignments.delete(f"assignments:{class_id}")

    def invalidate_teacher(self, teacher_id: int) -> None:
        """Invalidate all cache for a teacher"""
        self._teacher_schedules.delete(f"teacher:{teacher_id}")

    def clear_all(self) -> None:
        """Clear all schedule caches"""
        self._class_schedules.clear()
        self._teacher_schedules.clear()
        self._lesson_assignments.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'class_schedules': self._class_schedules.get_stats(),
            'teacher_schedules': self._teacher_schedules.get_stats(),
            'lesson_assignments': self._lesson_assignments.get_stats()
        }


# Global schedule cache instance
_schedule_cache = None


def get_schedule_cache() -> ScheduleCache:
    """Get global schedule cache instance"""
    global _schedule_cache
    if _schedule_cache is None:
        _schedule_cache = ScheduleCache()
    return _schedule_cache
