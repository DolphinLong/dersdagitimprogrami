# -*- coding: utf-8 -*-
"""
Tests for cache manager
"""

import time

import pytest

from utils.cache_manager import (
    CacheManager,
    LRUCache,
    ScheduleCache,
    cached,
    get_cache,
    get_schedule_cache,
)


class TestCacheManager:
    """Test CacheManager functionality"""

    @pytest.fixture
    def cache(self):
        """Create fresh cache instance"""
        return CacheManager(ttl=1)  # 1 second TTL for testing

    def test_cache_set_get(self, cache):
        """Test basic set and get"""
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_cache_miss(self, cache):
        """Test cache miss"""
        assert cache.get("nonexistent") is None

    def test_cache_expiration(self, cache):
        """Test cache expiration"""
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # Wait for expiration
        time.sleep(1.1)
        assert cache.get("key1") is None

    def test_cache_delete(self, cache):
        """Test cache deletion"""
        cache.set("key1", "value1")
        cache.delete("key1")
        assert cache.get("key1") is None

    def test_cache_clear(self, cache):
        """Test cache clear"""
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_cache_stats(self, cache):
        """Test cache statistics"""
        cache.set("key1", "value1")
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss
        
        stats = cache.get_stats()
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['size'] == 1

    def test_invalidate_pattern(self, cache):
        """Test pattern-based invalidation"""
        cache.set("user:1:name", "Alice")
        cache.set("user:2:name", "Bob")
        cache.set("product:1:name", "Widget")
        
        count = cache.invalidate_pattern("user:")
        assert count == 2
        assert cache.get("user:1:name") is None
        assert cache.get("product:1:name") == "Widget"


class TestCachedDecorator:
    """Test @cached decorator"""

    def test_cached_decorator(self):
        """Test function caching with decorator"""
        call_count = 0
        
        @cached(ttl=60)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call - should execute
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # Second call - should use cache
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Not incremented
        
        # Different argument - should execute
        result3 = expensive_function(10)
        assert result3 == 20
        assert call_count == 2

    def test_cached_with_kwargs(self):
        """Test caching with keyword arguments"""
        call_count = 0
        
        @cached(ttl=60)
        def function_with_kwargs(x, y=10):
            nonlocal call_count
            call_count += 1
            return x + y
        
        result1 = function_with_kwargs(5, y=10)
        result2 = function_with_kwargs(5, y=10)
        
        assert call_count == 1  # Second call used cache


class TestLRUCache:
    """Test LRU Cache"""

    def test_lru_basic(self):
        """Test basic LRU cache operations"""
        cache = LRUCache(max_size=3)
        
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        
        assert cache.get("a") == 1
        assert cache.get("b") == 2
        assert cache.get("c") == 3

    def test_lru_eviction(self):
        """Test LRU eviction"""
        cache = LRUCache(max_size=3)
        
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        
        # Add fourth item - should evict "a"
        cache.set("d", 4)
        
        assert cache.get("a") is None
        assert cache.get("d") == 4

    def test_lru_access_order(self):
        """Test that access updates order"""
        cache = LRUCache(max_size=3)
        
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        
        # Access "a" to make it most recently used
        cache.get("a")
        
        # Add fourth item - should evict "b" (least recently used)
        cache.set("d", 4)
        
        assert cache.get("a") == 1
        assert cache.get("b") is None

    def test_lru_clear(self):
        """Test LRU cache clear"""
        cache = LRUCache(max_size=3)
        
        cache.set("a", 1)
        cache.set("b", 2)
        cache.clear()
        
        assert cache.size() == 0


class TestScheduleCache:
    """Test ScheduleCache"""

    @pytest.fixture
    def schedule_cache(self):
        """Create fresh schedule cache"""
        cache = ScheduleCache()
        cache.clear_all()
        return cache

    def test_class_schedule_cache(self, schedule_cache):
        """Test class schedule caching"""
        schedule = [{"day": 1, "slot": 1, "lesson": "Math"}]
        
        schedule_cache.set_class_schedule(1, schedule)
        cached = schedule_cache.get_class_schedule(1)
        
        assert cached == schedule

    def test_teacher_schedule_cache(self, schedule_cache):
        """Test teacher schedule caching"""
        schedule = [{"day": 1, "slot": 1, "class": "9-A"}]
        
        schedule_cache.set_teacher_schedule(1, schedule)
        cached = schedule_cache.get_teacher_schedule(1)
        
        assert cached == schedule

    def test_lesson_assignments_cache(self, schedule_cache):
        """Test lesson assignments caching"""
        assignments = [{"lesson_id": 1, "teacher_id": 1, "hours": 4}]
        
        schedule_cache.set_lesson_assignments(1, assignments)
        cached = schedule_cache.get_lesson_assignments(1)
        
        assert cached == assignments

    def test_invalidate_class(self, schedule_cache):
        """Test class cache invalidation"""
        schedule = [{"day": 1, "slot": 1}]
        assignments = [{"lesson_id": 1}]
        
        schedule_cache.set_class_schedule(1, schedule)
        schedule_cache.set_lesson_assignments(1, assignments)
        
        schedule_cache.invalidate_class(1)
        
        assert schedule_cache.get_class_schedule(1) is None
        assert schedule_cache.get_lesson_assignments(1) is None

    def test_invalidate_teacher(self, schedule_cache):
        """Test teacher cache invalidation"""
        schedule = [{"day": 1, "slot": 1}]
        
        schedule_cache.set_teacher_schedule(1, schedule)
        schedule_cache.invalidate_teacher(1)
        
        assert schedule_cache.get_teacher_schedule(1) is None

    def test_cache_stats(self, schedule_cache):
        """Test cache statistics"""
        schedule_cache.set_class_schedule(1, [])
        schedule_cache.get_class_schedule(1)
        
        stats = schedule_cache.get_stats()
        
        assert 'class_schedules' in stats
        assert 'teacher_schedules' in stats
        assert 'lesson_assignments' in stats


class TestGlobalCache:
    """Test global cache instances"""

    def test_get_cache_singleton(self):
        """Test that get_cache returns singleton"""
        cache1 = get_cache()
        cache2 = get_cache()
        
        assert cache1 is cache2

    def test_get_schedule_cache_singleton(self):
        """Test that get_schedule_cache returns singleton"""
        cache1 = get_schedule_cache()
        cache2 = get_schedule_cache()
        
        assert cache1 is cache2


class TestCachePerformance:
    """Test cache performance improvements"""

    def test_cache_improves_performance(self):
        """Test that caching improves performance"""
        import time
        
        call_count = 0
        
        @cached(ttl=60)
        def slow_function(x):
            nonlocal call_count
            call_count += 1
            time.sleep(0.01)  # Simulate slow operation
            return x * 2
        
        # First call
        start = time.time()
        result1 = slow_function(5)
        time1 = time.time() - start
        
        # Second call (cached)
        start = time.time()
        result2 = slow_function(5)
        time2 = time.time() - start
        
        assert result1 == result2
        assert call_count == 1
        assert time2 < time1  # Cached call should be faster
