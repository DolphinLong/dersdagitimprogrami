"""
Load Testing - Test system under heavy load
"""
import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from algorithms.scheduler import Scheduler


@pytest.mark.load
class TestLoadPerformance:
    """Load testing for scheduler"""
    
    def test_concurrent_schedule_generation(self, db_manager, sample_schedule_data):
        """Test multiple concurrent schedule generations"""
        num_threads = 10
        results = []
        
        def generate_schedule():
            scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
            start = time.time()
            schedule = scheduler.generate_schedule()
            duration = time.time() - start
            return len(schedule), duration
        
        # Run concurrent generations
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(generate_schedule) for _ in range(num_threads)]
            
            for future in as_completed(futures):
                results.append(future.result())
        
        # Verify all completed
        assert len(results) == num_threads
        
        # Check performance
        avg_duration = sum(r[1] for r in results) / len(results)
        assert avg_duration < 15.0  # Average should be reasonable
    
    def test_rapid_fire_requests(self, db_manager, sample_schedule_data):
        """Test rapid consecutive requests"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        start = time.time()
        for _ in range(20):
            schedule = scheduler.generate_schedule()
        duration = time.time() - start
        
        # Should handle 20 requests in reasonable time
        assert duration < 100.0
    
    def test_large_dataset_performance(self, db_manager):
        """Test performance with large dataset"""
        # Create large dataset
        for i in range(50):
            db_manager.add_class(f"Class{i}", 5 + (i % 4))
        
        for i in range(100):
            db_manager.add_teacher(f"Teacher{i}", "Matematik")
        
        for i in range(20):
            db_manager.add_lesson(f"Lesson{i}")
        
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        start = time.time()
        schedule = scheduler.generate_schedule()
        duration = time.time() - start
        
        # Should complete even with large dataset
        assert duration < 60.0
        assert isinstance(schedule, list)
    
    def test_memory_under_load(self, db_manager, sample_schedule_data):
        """Test memory usage under load"""
        import sys
        
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        schedules = []
        for _ in range(50):
            schedule = scheduler.generate_schedule()
            schedules.append(schedule)
        
        # Memory should not grow unbounded
        total_size = sum(sys.getsizeof(s) for s in schedules)
        assert total_size < 10 * 1024 * 1024  # Less than 10MB


@pytest.mark.load
class TestStressScenarios:
    """Stress testing scenarios"""
    
    def test_continuous_operation(self, db_manager, sample_schedule_data):
        """Test continuous operation for extended period"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        start = time.time()
        count = 0
        
        # Run for 10 seconds
        while time.time() - start < 10:
            schedule = scheduler.generate_schedule()
            count += 1
        
        # Should handle many requests
        assert count > 0
    
    def test_peak_load_handling(self, db_manager, sample_schedule_data):
        """Test handling of peak load"""
        num_requests = 100
        
        def make_request():
            scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
            return scheduler.generate_schedule()
        
        start = time.time()
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            results = [f.result() for f in as_completed(futures)]
        duration = time.time() - start
        
        # Should handle peak load
        assert len(results) == num_requests
        assert duration < 120.0  # 2 minutes max


@pytest.mark.load
class TestScalability:
    """Test system scalability"""
    
    def test_linear_scaling(self, db_manager):
        """Test that performance scales linearly"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        # Test with different data sizes
        times = []
        
        for size in [5, 10, 20]:
            # Clear and add data
            for i in range(size):
                db_manager.add_class(f"C{i}", 5)
                db_manager.add_teacher(f"T{i}", "Matematik")
                db_manager.add_lesson(f"L{i}")
            
            start = time.time()
            schedule = scheduler.generate_schedule()
            duration = time.time() - start
            times.append(duration)
        
        # Performance should scale reasonably
        # (not exponentially)
        assert times[1] < times[0] * 3  # 2x data shouldn't take 3x time
    
    def test_concurrent_scaling(self, db_manager, sample_schedule_data):
        """Test scaling with concurrent requests"""
        results = {}
        
        for num_threads in [1, 5, 10]:
            def generate():
                scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
                return scheduler.generate_schedule()
            
            start = time.time()
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = [executor.submit(generate) for _ in range(num_threads)]
                [f.result() for f in as_completed(futures)]
            duration = time.time() - start
            
            results[num_threads] = duration
        
        # Should handle increased concurrency
        assert all(d < 60.0 for d in results.values())


# Load Testing Configuration
"""
To run load tests:
pytest tests/test_load.py -v -m load

For stress testing:
pytest tests/test_load.py -v -m load --duration=300

To generate load test report:
pytest tests/test_load.py -v -m load --html=load_report.html
"""
