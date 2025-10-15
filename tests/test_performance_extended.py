"""
Extended Performance Tests
"""
import pytest
import time
from algorithms.scheduler import Scheduler


@pytest.mark.performance
class TestSchedulerPerformanceExtended:
    """Extended performance tests"""
    
    def test_large_schedule_generation(self, db_manager):
        """Test performance with large dataset"""
        # Create large dataset
        for i in range(10):
            db_manager.add_class(f"Class{i}", 5 + (i % 4))
        
        for i in range(15):
            db_manager.add_teacher(f"Teacher{i}", "Matematik")
        
        for i in range(8):
            db_manager.add_lesson(f"Lesson{i}")
        
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        start = time.time()
        schedule = scheduler.generate_schedule()
        duration = time.time() - start
        
        # Should complete in reasonable time
        assert duration < 30.0  # 30 seconds max
        assert isinstance(schedule, list)
    
    def test_conflict_detection_performance_large(self, db_manager):
        """Test conflict detection with large schedule"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        # Create large schedule
        schedule = []
        for day in range(5):
            for slot in range(7):
                for class_id in range(20):
                    schedule.append({
                        "class_id": class_id + 1,
                        "day": day,
                        "time_slot": slot,
                        "teacher_id": (class_id % 10) + 1,
                        "lesson_id": 1
                    })
        
        start = time.time()
        conflicts = scheduler.detect_conflicts(schedule)
        duration = time.time() - start
        
        # Should be fast
        assert duration < 2.0
        assert isinstance(conflicts, list)
    
    def test_multiple_schedule_generations_performance(self, db_manager, sample_schedule_data):
        """Test performance of multiple generations"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        start = time.time()
        for _ in range(5):
            schedule = scheduler.generate_schedule()
        duration = time.time() - start
        
        # Should complete all in reasonable time
        assert duration < 50.0  # 50 seconds for 5 generations
    
    def test_memory_usage_stability(self, db_manager, sample_schedule_data):
        """Test that memory usage is stable"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        # Generate multiple times
        for _ in range(10):
            schedule = scheduler.generate_schedule()
            
            # Schedule should be reasonable size
            assert len(schedule) < 10000  # Sanity check


@pytest.mark.performance
class TestHelperMethodPerformance:
    """Test performance of helper methods"""
    
    def test_has_conflict_performance(self, db_manager):
        """Test _has_conflict performance"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        # Create large schedule
        schedule = []
        for i in range(1000):
            schedule.append({
                "class_id": i % 10,
                "day": i % 5,
                "time_slot": i % 7,
                "teacher_id": i % 20,
                "lesson_id": 1
            })
        
        start = time.time()
        for _ in range(100):
            scheduler._has_conflict(schedule, {
                "class_id": 999,
                "day": 0,
                "time_slot": 0,
                "teacher_id": 999,
                "lesson_id": 1
            })
        duration = time.time() - start
        
        # Should be very fast
        assert duration < 1.0
    
    def test_get_eligible_teachers_performance(self, db_manager):
        """Test _get_eligible_teachers performance"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        # Create many teachers
        from unittest.mock import Mock
        teachers = [Mock(teacher_id=i, subject="Matematik") for i in range(100)]
        lesson = Mock(name="Matematik")
        
        start = time.time()
        for _ in range(100):
            eligible = scheduler._get_eligible_teachers(teachers, lesson)
        duration = time.time() - start
        
        # Should be fast
        assert duration < 1.0
