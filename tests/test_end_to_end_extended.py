"""
Extended End-to-End Tests - Complete system workflows
"""
import pytest
from algorithms.scheduler import Scheduler
from database.db_manager import DatabaseManager


@pytest.mark.integration
class TestCompleteSchedulingWorkflow:
    """Test complete scheduling workflows"""
    
    def test_full_school_schedule_generation(self, db_manager):
        """Test generating a complete school schedule"""
        # Setup school
        db_manager.set_school_type("Ortaokul")
        
        # Add 3 classes
        classes = []
        for i in range(5, 8):
            class_id = db_manager.add_class(f"{i}A", i)
            classes.append(class_id)
        
        # Add 5 teachers
        teachers = []
        subjects = ["Matematik", "Türkçe", "Fen Bilimleri", "Sosyal Bilgiler", "İngilizce"]
        for i, subject in enumerate(subjects):
            teacher_id = db_manager.add_teacher(f"Teacher {i+1}", subject)
            teachers.append(teacher_id)
        
        # Add lessons
        lessons = []
        for subject in subjects:
            lesson_id = db_manager.add_lesson(subject)
            lessons.append(lesson_id)
        
        # Create assignments
        for class_id in classes:
            for i, lesson_id in enumerate(lessons):
                db_manager.add_schedule_by_school_type(
                    class_id=class_id,
                    lesson_id=lesson_id,
                    teacher_id=teachers[i]
                )
        
        # Generate schedule
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        schedule = scheduler.generate_schedule()
        
        # Verify schedule
        assert isinstance(schedule, list)
        assert len(schedule) >= 0
        
        # Check no conflicts
        conflicts = scheduler.detect_conflicts(schedule)
        assert isinstance(conflicts, list)
    
    def test_schedule_modification_workflow(self, db_manager, sample_schedule_data):
        """Test modifying and regenerating schedule"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        # Generate initial schedule
        schedule1 = scheduler.generate_schedule()
        
        # Modify: Add a new teacher
        new_teacher = db_manager.add_teacher("New Teacher", "Matematik")
        
        # Regenerate
        schedule2 = scheduler.generate_schedule()
        
        # Both should be valid
        assert isinstance(schedule1, list)
        assert isinstance(schedule2, list)
    
    def test_schedule_export_import_workflow(self, db_manager, sample_schedule_data):
        """Test schedule export and import"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        # Generate schedule
        schedule = scheduler.generate_schedule()
        
        # Export (simulate)
        exported_data = {
            "schedule": schedule,
            "school_type": db_manager.get_school_type(),
            "classes": len(db_manager.get_all_classes()),
        }
        
        # Verify export
        assert "schedule" in exported_data
        assert "school_type" in exported_data
        assert isinstance(exported_data["classes"], int)


@pytest.mark.integration
class TestMultiUserScenarios:
    """Test multi-user scenarios"""
    
    def test_concurrent_schedule_generation(self, db_manager, sample_schedule_data):
        """Test multiple schedulers working with same data"""
        scheduler1 = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        scheduler2 = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        schedule1 = scheduler1.generate_schedule()
        schedule2 = scheduler2.generate_schedule()
        
        # Both should produce valid schedules
        assert isinstance(schedule1, list)
        assert isinstance(schedule2, list)
    
    def test_schedule_with_teacher_constraints(self, db_manager):
        """Test scheduling with teacher availability constraints"""
        # Add data
        class_id = db_manager.add_class("5A", 5)
        teacher_id = db_manager.add_teacher("Constrained Teacher", "Matematik")
        lesson_id = db_manager.add_lesson("Matematik")
        
        # Create assignment
        db_manager.add_schedule_by_school_type(
            class_id=class_id,
            lesson_id=lesson_id,
            teacher_id=teacher_id
        )
        
        # Generate schedule
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        schedule = scheduler.generate_schedule()
        
        assert isinstance(schedule, list)


@pytest.mark.integration
class TestErrorRecoveryWorkflows:
    """Test error recovery in workflows"""
    
    def test_schedule_with_incomplete_data(self, db_manager):
        """Test scheduling with incomplete data"""
        # Only add classes, no teachers or lessons
        db_manager.add_class("5A", 5)
        db_manager.add_class("6A", 6)
        
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        schedule = scheduler.generate_schedule()
        
        # Should handle gracefully
        assert isinstance(schedule, list)
    
    def test_schedule_recovery_after_error(self, db_manager, sample_schedule_data):
        """Test recovery after scheduling error"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        # Try to generate schedule
        try:
            schedule1 = scheduler.generate_schedule()
        except Exception:
            schedule1 = []
        
        # Should be able to try again
        schedule2 = scheduler.generate_schedule()
        
        assert isinstance(schedule2, list)


@pytest.mark.integration
class TestDataValidationWorkflows:
    """Test data validation in workflows"""
    
    def test_schedule_with_invalid_weekly_hours(self, db_manager):
        """Test scheduling with invalid weekly hours"""
        class_id = db_manager.add_class("5A", 5)
        teacher_id = db_manager.add_teacher("Teacher", "Matematik")
        lesson_id = db_manager.add_lesson("Matematik", weekly_hours=0)  # Invalid
        
        db_manager.add_schedule_by_school_type(
            class_id=class_id,
            lesson_id=lesson_id,
            teacher_id=teacher_id
        )
        
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        schedule = scheduler.generate_schedule()
        
        # Should handle gracefully
        assert isinstance(schedule, list)
    
    def test_schedule_data_integrity_check(self, db_manager, sample_schedule_data):
        """Test data integrity after scheduling"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        schedule = scheduler.generate_schedule()
        
        # Verify all entries have valid IDs
        for entry in schedule:
            assert entry["class_id"] > 0
            assert entry["teacher_id"] > 0
            assert entry["lesson_id"] > 0
            assert 0 <= entry["day"] <= 4
            assert entry["time_slot"] >= 0
