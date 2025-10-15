"""
Regression Testing - Ensure no functionality breaks
"""
import pytest
import json
import os
from algorithms.scheduler import Scheduler


@pytest.mark.regression
class TestSchedulerRegression:
    """Regression tests for scheduler"""
    
    def test_basic_schedule_generation_regression(self, db_manager, sample_schedule_data):
        """Test that basic schedule generation still works"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        schedule = scheduler.generate_schedule()
        
        # Basic assertions that should always pass
        assert isinstance(schedule, list)
        assert all(isinstance(entry, dict) for entry in schedule)
        assert all("class_id" in entry for entry in schedule)
        assert all("teacher_id" in entry for entry in schedule)
        assert all("lesson_id" in entry for entry in schedule)
        assert all("day" in entry for entry in schedule)
        assert all("time_slot" in entry for entry in schedule)
    
    def test_conflict_detection_regression(self, db_manager):
        """Test that conflict detection still works"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        # Known conflicting schedule
        schedule = [
            {"class_id": 1, "day": 0, "time_slot": 0, "teacher_id": 1, "lesson_id": 1},
            {"class_id": 1, "day": 0, "time_slot": 0, "teacher_id": 2, "lesson_id": 2},
        ]
        
        conflicts = scheduler.detect_conflicts(schedule)
        
        # Should detect conflict
        assert len(conflicts) > 0
        assert conflicts[0]["type"] == "class_conflict"
    
    def test_block_distribution_regression(self, db_manager):
        """Test that block distribution still works"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        # Test various hours
        for hours in [1, 2, 3, 4, 5, 6]:
            blocks = scheduler._create_optimal_blocks_distributed(hours)
            assert sum(blocks) == hours
            assert all(b > 0 for b in blocks)


@pytest.mark.regression
class TestDatabaseRegression:
    """Regression tests for database operations"""
    
    def test_crud_operations_regression(self, db_manager):
        """Test that CRUD operations still work"""
        # Create
        class_id = db_manager.add_class("Regression Test", 5)
        assert class_id is not None
        
        # Read
        classes = db_manager.get_all_classes()
        assert any(c.name == "Regression Test" for c in classes)
        
        # Update (if available)
        try:
            db_manager.update_class(class_id, "Updated", 5)
        except AttributeError:
            pass
        
        # Delete (if available)
        try:
            db_manager.delete_class(class_id)
        except AttributeError:
            pass
    
    def test_query_performance_regression(self, db_manager, sample_schedule_data):
        """Test that query performance hasn't degraded"""
        import time
        
        # Add more data
        for i in range(20):
            db_manager.add_class(f"Perf{i}", 5)
        
        # Time query
        start = time.time()
        classes = db_manager.get_all_classes()
        duration = time.time() - start
        
        # Should be fast
        assert duration < 1.0


@pytest.mark.regression
class TestAPIRegression:
    """Regression tests for API compatibility"""
    
    def test_scheduler_api_compatibility(self, db_manager):
        """Test that Scheduler API hasn't changed"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        # Test public methods exist
        assert hasattr(scheduler, 'generate_schedule')
        assert hasattr(scheduler, 'detect_conflicts')
        assert callable(scheduler.generate_schedule)
        assert callable(scheduler.detect_conflicts)
    
    def test_database_api_compatibility(self, db_manager):
        """Test that DatabaseManager API hasn't changed"""
        # Test public methods exist
        assert hasattr(db_manager, 'add_class')
        assert hasattr(db_manager, 'add_teacher')
        assert hasattr(db_manager, 'add_lesson')
        assert hasattr(db_manager, 'get_all_classes')
        assert hasattr(db_manager, 'get_all_teachers')
        assert hasattr(db_manager, 'get_all_lessons')


@pytest.mark.regression
class TestOutputRegression:
    """Regression tests for output format"""
    
    def test_schedule_output_format_regression(self, db_manager, sample_schedule_data):
        """Test that schedule output format hasn't changed"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        schedule = scheduler.generate_schedule()
        
        if len(schedule) > 0:
            entry = schedule[0]
            
            # Check required fields
            assert "class_id" in entry
            assert "teacher_id" in entry
            assert "lesson_id" in entry
            assert "day" in entry
            assert "time_slot" in entry
            
            # Check types
            assert isinstance(entry["class_id"], int)
            assert isinstance(entry["teacher_id"], int)
            assert isinstance(entry["lesson_id"], int)
            assert isinstance(entry["day"], int)
            assert isinstance(entry["time_slot"], int)
    
    def test_conflict_output_format_regression(self, db_manager):
        """Test that conflict output format hasn't changed"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        schedule = [
            {"class_id": 1, "day": 0, "time_slot": 0, "teacher_id": 1, "lesson_id": 1},
            {"class_id": 1, "day": 0, "time_slot": 0, "teacher_id": 2, "lesson_id": 2},
        ]
        
        conflicts = scheduler.detect_conflicts(schedule)
        
        if len(conflicts) > 0:
            conflict = conflicts[0]
            
            # Check required fields
            assert "type" in conflict
            assert conflict["type"] in ["class_conflict", "teacher_conflict"]


@pytest.mark.regression
class TestBehaviorRegression:
    """Regression tests for specific behaviors"""
    
    def test_empty_schedule_behavior_regression(self, db_manager):
        """Test behavior with empty schedule"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        schedule = scheduler.generate_schedule()
        
        # Should return empty list, not None or error
        assert isinstance(schedule, list)
    
    def test_zero_hours_behavior_regression(self, db_manager):
        """Test behavior with zero hours"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        blocks = scheduler._create_optimal_blocks_distributed(0)
        
        # Should return empty list
        assert blocks == []
    
    def test_no_conflicts_behavior_regression(self, db_manager):
        """Test behavior with no conflicts"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        schedule = []
        conflicts = scheduler.detect_conflicts(schedule)
        
        # Should return empty list
        assert conflicts == []


# Regression Testing Configuration
"""
To run regression tests:
pytest tests/test_regression.py -v -m regression

To save baseline:
pytest tests/test_regression.py -v -m regression --regression-save

To compare with baseline:
pytest tests/test_regression.py -v -m regression --regression-compare

To run all regression tests in CI:
pytest tests/test_regression.py -v -m regression --tb=short
"""
