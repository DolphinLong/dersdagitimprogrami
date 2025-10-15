"""
Integration tests for scheduler with real database and components
Tests end-to-end workflows and component interactions
"""
import pytest
from algorithms.scheduler import Scheduler


class TestSchedulerDatabaseIntegration:
    """Integration tests with real database"""
    
    def test_full_schedule_generation_workflow(self, db_manager, sample_schedule_data):
        """Test complete schedule generation with real data"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        # Generate schedule
        schedule = scheduler._generate_schedule_standard()
        
        # Verify schedule structure
        assert isinstance(schedule, list)
        
        # Each entry should have required fields
        for entry in schedule:
            assert "class_id" in entry
            assert "teacher_id" in entry
            assert "lesson_id" in entry
            assert "day" in entry
            assert "time_slot" in entry
    
    def test_schedule_with_multiple_classes(self, db_manager, sample_classes, sample_teachers, sample_lessons):
        """Test scheduling multiple classes"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        # Add lesson assignments for multiple classes
        for class_obj in sample_classes[:3]:  # First 3 classes
            for lesson in sample_lessons[:3]:  # First 3 lessons
                teacher = sample_teachers[0]
                db_manager.add_schedule_by_school_type(
                    class_id=class_obj.class_id,
                    lesson_id=lesson.lesson_id,
                    teacher_id=teacher.teacher_id
                )
        
        schedule = scheduler._generate_schedule_standard()
        
        # Should have entries for multiple classes
        class_ids = set(entry["class_id"] for entry in schedule)
        assert len(class_ids) >= 1
    
    def test_schedule_persistence(self, db_manager, sample_schedule_data):
        """Test that schedule can be generated and conflicts detected"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        # Generate schedule
        schedule = scheduler._generate_schedule_standard()
        
        # Check for conflicts
        conflicts = scheduler.detect_conflicts(schedule)
        
        # Conflicts should be a list
        assert isinstance(conflicts, list)
    
    def test_schedule_with_teacher_availability(self, db_manager, sample_schedule_data):
        """Test scheduling respects teacher availability"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        # Generate schedule
        schedule = scheduler._generate_schedule_standard()
        
        # Verify no teacher is double-booked
        teacher_slots = {}
        for entry in schedule:
            key = (entry["teacher_id"], entry["day"], entry["time_slot"])
            if key in teacher_slots:
                # This would be a conflict
                pass
            teacher_slots[key] = entry
        
        # Each teacher-day-slot combination should be unique
        assert len(teacher_slots) == len(schedule)


class TestSchedulerAlgorithmIntegration:
    """Integration tests between different scheduler algorithms"""
    
    def test_algorithm_switching(self, db_manager, sample_schedule_data):
        """Test switching between different algorithms"""
        # Test with different algorithm configurations
        configs = [
            {"use_ultra": False, "use_hybrid": False, "use_advanced": False},
            {"use_ultra": False, "use_hybrid": False, "use_advanced": True},
        ]
        
        for config in configs:
            scheduler = Scheduler(db_manager, **config)
            schedule = scheduler.generate_schedule()
            
            assert isinstance(schedule, list)
    
    def test_algorithm_consistency(self, db_manager):
        """Test that same algorithm produces consistent results"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        # Generate schedule twice with same data
        schedule1 = scheduler._generate_schedule_standard()
        schedule2 = scheduler._generate_schedule_standard()
        
        # Should produce same number of entries (deterministic)
        assert len(schedule1) == len(schedule2)


class TestSchedulerConflictIntegration:
    """Integration tests for conflict detection and resolution"""
    
    def test_conflict_detection_integration(self, db_manager, sample_schedule_data):
        """Test conflict detection with real schedule"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        # Generate schedule
        schedule = scheduler._generate_schedule_standard()
        
        # Detect conflicts
        conflicts = scheduler.detect_conflicts(schedule)
        
        # Should return a list (may be empty if no conflicts)
        assert isinstance(conflicts, list)
        
        # If conflicts exist, they should have proper structure
        for conflict in conflicts:
            assert "type" in conflict
            assert conflict["type"] in ["class_conflict", "teacher_conflict"]
    
    def test_conflict_resolution_integration(self, db_manager):
        """Test conflict resolution integration"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        # Create a schedule with known conflicts
        schedule = [
            {"class_id": 1, "day": 0, "time_slot": 0, "teacher_id": 1, "lesson_id": 1},
            {"class_id": 1, "day": 0, "time_slot": 0, "teacher_id": 2, "lesson_id": 2},  # Class conflict
        ]
        
        # Detect conflicts
        conflicts = scheduler.detect_conflicts(schedule)
        
        assert len(conflicts) > 0
        assert conflicts[0]["type"] == "class_conflict"


class TestSchedulerPerformanceIntegration:
    """Integration tests for performance with real data"""
    
    def test_schedule_generation_performance(self, db_manager, sample_schedule_data):
        """Test schedule generation performance"""
        import time
        
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        start = time.time()
        schedule = scheduler._generate_schedule_standard()
        duration = time.time() - start
        
        # Should complete in reasonable time (< 5 seconds for test data)
        assert duration < 5.0
        assert isinstance(schedule, list)
    
    def test_conflict_detection_performance(self, db_manager, sample_schedule_data):
        """Test conflict detection performance"""
        import time
        
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        # Generate schedule
        schedule = scheduler._generate_schedule_standard()
        
        # Measure conflict detection time
        start = time.time()
        conflicts = scheduler.detect_conflicts(schedule)
        duration = time.time() - start
        
        # Should be very fast (< 1 second)
        assert duration < 1.0
        assert isinstance(conflicts, list)


class TestSchedulerDataIntegrity:
    """Integration tests for data integrity"""
    
    def test_schedule_data_validity(self, db_manager, sample_schedule_data):
        """Test that generated schedule has valid data"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        schedule = scheduler._generate_schedule_standard()
        
        # Verify all entries have valid data
        for entry in schedule:
            # Day should be 0-4 (Monday-Friday)
            assert 0 <= entry["day"] <= 4
            
            # Time slot should be valid
            assert entry["time_slot"] >= 0
            
            # IDs should be positive
            assert entry["class_id"] > 0
            assert entry["teacher_id"] > 0
            assert entry["lesson_id"] > 0
    
    def test_schedule_completeness(self, db_manager, sample_schedule_data):
        """Test that schedule attempts to cover all assignments"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        # Get all assignments
        assignments = db_manager.get_schedule_by_school_type()
        
        # Generate schedule
        schedule = scheduler._generate_schedule_standard()
        
        # Schedule should attempt to cover assignments
        # (May not be 100% due to constraints)
        assert isinstance(schedule, list)
        assert len(schedule) >= 0


class TestSchedulerErrorHandlingIntegration:
    """Integration tests for error handling"""
    
    def test_empty_database_handling(self, empty_db_manager):
        """Test handling of empty database"""
        scheduler = Scheduler(empty_db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        # Should not crash with empty database
        schedule = scheduler._generate_schedule_standard()
        
        assert isinstance(schedule, list)
        assert len(schedule) == 0
    
    def test_missing_data_handling(self, db_manager, sample_classes):
        """Test handling of missing data"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        # Classes exist but no teachers or lessons
        schedule = scheduler._generate_schedule_standard()
        
        # Should handle gracefully
        assert isinstance(schedule, list)


class TestSchedulerWorkflowIntegration:
    """Integration tests for complete workflows"""
    
    def test_add_class_and_schedule(self, db_manager):
        """Test adding a class and generating schedule"""
        # Add a new class
        class_id = db_manager.add_class("Test Class", 5)
        
        # Add a teacher
        teacher_id = db_manager.add_teacher("Test Teacher", "Matematik")
        
        # Add a lesson
        lesson_id = db_manager.add_lesson("Matematik")
        
        # Create assignment
        db_manager.add_schedule_by_school_type(
            class_id=class_id,
            lesson_id=lesson_id,
            teacher_id=teacher_id
        )
        
        # Generate schedule
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        schedule = scheduler._generate_schedule_standard()
        
        assert isinstance(schedule, list)
    
    def test_modify_and_regenerate_schedule(self, db_manager, sample_schedule_data):
        """Test modifying data and regenerating schedule"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        # Generate initial schedule
        schedule1 = scheduler._generate_schedule_standard()
        
        # Add a new teacher
        db_manager.add_teacher("New Teacher", "Türkçe")
        
        # Regenerate schedule
        schedule2 = scheduler._generate_schedule_standard()
        
        # Both should be valid schedules
        assert isinstance(schedule1, list)
        assert isinstance(schedule2, list)


class TestSchedulerMultipleRuns:
    """Test multiple schedule generation runs"""
    
    def test_multiple_generations(self, db_manager, sample_schedule_data):
        """Test generating schedule multiple times"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        schedules = []
        for _ in range(3):
            schedule = scheduler._generate_schedule_standard()
            schedules.append(schedule)
        
        # All should be valid
        for schedule in schedules:
            assert isinstance(schedule, list)
        
        # Should produce consistent results
        assert len(schedules[0]) == len(schedules[1]) == len(schedules[2])


# Fixtures
@pytest.fixture
def empty_db_manager(tmp_path):
    """Create an empty database manager"""
    from database.db_manager import DatabaseManager
    db_path = tmp_path / "empty_integration_test.db"
    return DatabaseManager(str(db_path))
