"""
Performance Benchmarking - Measure and track performance metrics
"""
import pytest
import time
import json
import os
from algorithms.scheduler import Scheduler


@pytest.mark.benchmark
class TestSchedulerBenchmarks:
    """Benchmark tests for scheduler"""
    
    def test_benchmark_schedule_generation(self, db_manager, sample_schedule_data, benchmark):
        """Benchmark schedule generation"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        # Benchmark
        result = benchmark(scheduler.generate_schedule)
        
        # Verify result
        assert isinstance(result, list)
    
    def test_benchmark_conflict_detection(self, db_manager, benchmark):
        """Benchmark conflict detection"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        # Create large schedule
        schedule = [
            {"class_id": i % 10, "day": i % 5, "time_slot": i % 7, 
             "teacher_id": i % 20, "lesson_id": 1}
            for i in range(100)
        ]
        
        # Benchmark
        result = benchmark(scheduler.detect_conflicts, schedule)
        
        # Verify result
        assert isinstance(result, list)
    
    def test_benchmark_block_distribution(self, db_manager, benchmark):
        """Benchmark block distribution"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        # Benchmark
        result = benchmark(scheduler._create_optimal_blocks_distributed, 10)
        
        # Verify result
        assert sum(result) == 10


@pytest.mark.benchmark
class TestDatabaseBenchmarks:
    """Benchmark tests for database operations"""
    
    def test_benchmark_add_class(self, db_manager, benchmark):
        """Benchmark adding a class"""
        counter = [0]
        
        def add_class():
            counter[0] += 1
            return db_manager.add_class(f"Bench{counter[0]}", 5)
        
        # Benchmark
        result = benchmark(add_class)
        
        # Verify result
        assert result is not None
    
    def test_benchmark_get_all_classes(self, db_manager, sample_classes, benchmark):
        """Benchmark getting all classes"""
        # Benchmark
        result = benchmark(db_manager.get_all_classes)
        
        # Verify result
        assert isinstance(result, list)
    
    def test_benchmark_query_schedule(self, db_manager, sample_schedule_data, benchmark):
        """Benchmark querying schedule"""
        # Benchmark
        result = benchmark(db_manager.get_schedule_by_school_type)
        
        # Verify result
        assert isinstance(result, list)


@pytest.mark.benchmark
class TestAlgorithmBenchmarks:
    """Benchmark tests for algorithms"""
    
    def test_benchmark_standard_algorithm(self, db_manager, sample_schedule_data, benchmark):
        """Benchmark standard algorithm"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        # Benchmark
        result = benchmark(scheduler._generate_schedule_standard)
        
        # Verify result
        assert isinstance(result, list)
    
    def test_benchmark_ultra_algorithm(self, db_manager, sample_schedule_data, benchmark):
        """Benchmark ultra aggressive algorithm"""
        scheduler = Scheduler(db_manager, use_ultra=True, use_hybrid=False, use_advanced=False)
        
        # Benchmark
        result = benchmark(scheduler.generate_schedule)
        
        # Verify result
        assert isinstance(result, list)


@pytest.mark.benchmark
class TestPerformanceMetrics:
    """Track performance metrics over time"""
    
    def test_track_schedule_generation_time(self, db_manager, sample_schedule_data):
        """Track schedule generation time"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        times = []
        for _ in range(5):
            start = time.time()
            schedule = scheduler.generate_schedule()
            duration = time.time() - start
            times.append(duration)
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        # Save metrics
        metrics = {
            "avg_time": avg_time,
            "min_time": min_time,
            "max_time": max_time,
            "runs": 5
        }
        
        # Verify performance
        assert avg_time < 10.0
        assert max_time < 15.0
    
    def test_track_memory_usage(self, db_manager, sample_schedule_data):
        """Track memory usage"""
        import sys
        
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        # Generate schedule
        schedule = scheduler.generate_schedule()
        
        # Measure memory
        schedule_size = sys.getsizeof(schedule)
        
        # Save metrics
        metrics = {
            "schedule_size": schedule_size,
            "entry_count": len(schedule)
        }
        
        # Verify memory usage
        assert schedule_size < 1024 * 1024  # Less than 1MB
    
    def test_track_throughput(self, db_manager, sample_schedule_data):
        """Track throughput (requests per second)"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        start = time.time()
        count = 0
        
        # Run for 5 seconds
        while time.time() - start < 5:
            schedule = scheduler.generate_schedule()
            count += 1
        
        duration = time.time() - start
        throughput = count / duration
        
        # Save metrics
        metrics = {
            "throughput": throughput,
            "total_requests": count,
            "duration": duration
        }
        
        # Verify throughput
        assert throughput > 0.1  # At least 0.1 requests per second


@pytest.mark.benchmark
class TestComparativeBenchmarks:
    """Compare performance of different approaches"""
    
    def test_compare_algorithms(self, db_manager, sample_schedule_data):
        """Compare different algorithm performances"""
        results = {}
        
        # Standard
        scheduler_std = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        start = time.time()
        schedule_std = scheduler_std.generate_schedule()
        results["standard"] = time.time() - start
        
        # Ultra
        scheduler_ultra = Scheduler(db_manager, use_ultra=True, use_hybrid=False, use_advanced=False)
        start = time.time()
        schedule_ultra = scheduler_ultra.generate_schedule()
        results["ultra"] = time.time() - start
        
        # Verify all completed
        assert all(t < 30.0 for t in results.values())
    
    def test_compare_data_sizes(self, db_manager):
        """Compare performance with different data sizes"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        results = {}
        
        for size in [5, 10, 20]:
            # Add data
            for i in range(size):
                db_manager.add_class(f"Size{size}_C{i}", 5)
                db_manager.add_teacher(f"Size{size}_T{i}", "Matematik")
                db_manager.add_lesson(f"Size{size}_L{i}")
            
            # Measure
            start = time.time()
            schedule = scheduler.generate_schedule()
            results[size] = time.time() - start
        
        # Verify scaling
        assert all(t < 60.0 for t in results.values())


# Benchmarking Configuration
"""
To run benchmarks:
pytest tests/test_benchmark.py -v -m benchmark

To run with pytest-benchmark:
pip install pytest-benchmark
pytest tests/test_benchmark.py -v -m benchmark --benchmark-only

To save baseline:
pytest tests/test_benchmark.py -v -m benchmark --benchmark-save=baseline

To compare with baseline:
pytest tests/test_benchmark.py -v -m benchmark --benchmark-compare=baseline

To generate benchmark report:
pytest tests/test_benchmark.py -v -m benchmark --benchmark-json=benchmark.json
"""
