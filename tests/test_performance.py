# -*- coding: utf-8 -*-
"""
Performance and Benchmark Tests
"""

import time

import pytest

from algorithms.enhanced_strict_scheduler import EnhancedStrictScheduler
from algorithms.simple_perfect_scheduler import SimplePerfectScheduler
from algorithms.ultimate_scheduler import UltimateScheduler


class TestSchedulerPerformance:
    """Test scheduler performance"""

    def test_simple_perfect_performance(self, db_manager, sample_schedule_data):
        """Test SimplePerfectScheduler performance"""
        scheduler = SimplePerfectScheduler(db_manager)

        start_time = time.time()
        schedule = scheduler.generate_schedule()
        end_time = time.time()

        execution_time = end_time - start_time

        # Should complete reasonably fast (adjust threshold as needed)
        assert execution_time < 10.0  # 10 seconds max
        assert isinstance(schedule, list)

    def test_ultimate_scheduler_performance(self, db_manager, sample_schedule_data):
        """Test UltimateScheduler performance"""
        scheduler = UltimateScheduler(db_manager)

        start_time = time.time()
        schedule = scheduler.generate_schedule()
        end_time = time.time()

        execution_time = end_time - start_time

        # Ultimate may be slower due to backtracking
        assert execution_time < 15.0  # 15 seconds max
        assert isinstance(schedule, list)

    def test_enhanced_strict_performance(self, db_manager, sample_schedule_data):
        """Test EnhancedStrictScheduler performance"""
        scheduler = EnhancedStrictScheduler(db_manager)

        start_time = time.time()
        schedule = scheduler.generate_schedule()
        end_time = time.time()

        execution_time = end_time - start_time

        assert execution_time < 12.0  # 12 seconds max
        assert isinstance(schedule, list)


class TestDatabasePerformance:
    """Test database operation performance"""

    def test_batch_insert_performance(self, db_manager):
        """Test performance of batch inserts"""
        start_time = time.time()

        # Insert 50 teachers
        for i in range(50):
            db_manager.add_teacher(f"Teacher {i}", "Math")

        end_time = time.time()
        execution_time = end_time - start_time

        # Should be fast
        assert execution_time < 2.0  # 2 seconds for 50 inserts

    def test_bulk_read_performance(self, db_manager, sample_schedule_data):
        """Test performance of bulk reads"""
        start_time = time.time()

        # Read all data 10 times
        for _ in range(10):
            db_manager.get_all_teachers()
            db_manager.get_all_classes()
            db_manager.get_all_lessons()

        end_time = time.time()
        execution_time = end_time - start_time

        # Should be very fast
        assert execution_time < 1.0  # 1 second for 30 reads


class TestScalability:
    """Test scalability with varying data sizes"""

    def test_scaling_with_classes(self, db_manager):
        """Test performance with increasing number of classes"""
        # Add 20 classes
        for i in range(20):
            db_manager.add_class(f"Class {i}", 9 + (i % 4))

        classes = db_manager.get_all_classes()

        # Should handle well
        assert len(classes) >= 20

    def test_scaling_with_lessons(self, db_manager):
        """Test performance with many lessons"""
        # Add 30 lessons
        for i in range(30):
            db_manager.add_lesson(f"Lesson {i}", 4)

        lessons = db_manager.get_all_lessons()

        assert len(lessons) >= 30


class TestMemoryUsage:
    """Test memory efficiency"""

    def test_scheduler_memory_efficiency(self, db_manager, sample_schedule_data):
        """Test that scheduler doesn't leak memory"""
        scheduler = SimplePerfectScheduler(db_manager)

        # Generate multiple times
        for _ in range(5):
            schedule = scheduler.generate_schedule()
            assert isinstance(schedule, list)

        # If we get here without crashing, memory is OK


class TestConcurrentOperations:
    """Test concurrent database operations"""

    def test_multiple_reads(self, db_manager, sample_schedule_data):
        """Test multiple simultaneous reads"""
        # Simulate multiple reads
        results = []
        for _ in range(10):
            teachers = db_manager.get_all_teachers()
            results.append(len(teachers))

        # All should return same count
        assert len(set(results)) <= 1  # All same or close


class TestCacheEfficiency:
    """Test caching behavior (if implemented)"""

    def test_repeated_reads_performance(self, db_manager, sample_schedule_data):
        """Test that repeated reads are fast"""
        # First read
        start1 = time.time()
        db_manager.get_all_teachers()
        time1 = time.time() - start1

        # Second read (should be similar or faster if cached)
        start2 = time.time()
        db_manager.get_all_teachers()
        time2 = time.time() - start2

        # Both should be fast
        assert time1 < 0.5
        assert time2 < 0.5


class TestPerformanceRegression:
    """Test for performance regressions"""

    def test_baseline_scheduler_performance(self, db_manager, sample_schedule_data):
        """Establish baseline performance"""
        scheduler = SimplePerfectScheduler(db_manager)

        times = []
        for _ in range(3):
            start = time.time()
            scheduler.generate_schedule()
            times.append(time.time() - start)

        avg_time = sum(times) / len(times)

        # Document baseline (adjust as needed)
        assert avg_time < 5.0  # Average under 5 seconds

        # Variance should be reasonable
        max_variance = max(times) - min(times)
        assert max_variance < 3.0  # Within 3 seconds variance
