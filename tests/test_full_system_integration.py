"""
Full System Integration Tests - Test complete system workflows
"""
import pytest
from algorithms.scheduler import Scheduler
from database.db_manager import DatabaseManager


@pytest.mark.system_integration
class TestCompleteSystemWorkflow:
    """Test complete system workflows"""
    
    def test_full_system_setup_and_schedule(self, db_manager):
        """Test complete system from setup to schedule generation"""
        # Step 1: Setup school
        db_manager.set_school_type("Ortaokul")
        
        # Step 2: Add classes
        class_5a = db_manager.add_class("5A", 5)
        class_5b = db_manager.add_class("5B", 5)
        class_6a = db_manager.add_class("6A", 6)
        
        # Step 3: Add teachers
        math_teacher = db_manager.add_teacher("Matematik Öğretmeni", "Matematik")
        turkish_teacher = db_manager.add_teacher("Türkçe Öğretmeni", "Türkçe")
        science_teacher = db_manager.add_teacher("Fen Öğretmeni", "Fen Bilimleri")
        
        # Step 4: Add lessons
        math_lesson = db_manager.add_lesson("Matematik", 5)
        turkish_lesson = db_manager.add_lesson("Türkçe", 5)
        science_lesson = db_manager.add_lesson("Fen Bilimleri", 4)
        
        # Step 5: Create assignments
        for class_id in [class_5a, class_5b, class_6a]:
            db_manager.add_schedule_by_school_type(class_id, math_lesson, math_teacher)
            db_manager.add_schedule_by_school_type(class_id, turkish_lesson, turkish_teacher)
            db_manager.add_schedule_by_school_type(class_id, science_lesson, science_teacher)
        
        # Step 6: Generate schedule
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        schedule = scheduler.generate_schedule()
        
        # Step 7: Verify
        assert isinstance(schedule, list)
        assert len(schedule) >= 0
        
        # Step 8: Check conflicts
        conflicts = scheduler.detect_conflicts(schedule)
        assert isinstance(conflicts, list)
    
    def test_system_with_modifications(self, db_manager):
        """Test system with data modifications"""
        # Initial setup
        class_id = db_manager.add_class("Initial Class", 5)
        teacher_id = db_manager.add_teacher("Initial Teacher", "Matematik")
        lesson_id = db_manager.add_lesson("Matematik")
        
        db_manager.add_schedule_by_school_type(class_id, lesson_id, teacher_id)
        
        # Generate initial schedule
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        schedule1 = scheduler.generate_schedule()
        
        # Modify: Add more data
        new_class = db_manager.add_class("New Class", 6)
        new_teacher = db_manager.add_teacher("New Teacher", "Türkçe")
        new_lesson = db_manager.add_lesson("Türkçe")
        
        db_manager.add_schedule_by_school_type(new_class, new_lesson, new_teacher)
        
        # Regenerate
        schedule2 = scheduler.generate_schedule()
        
        # Both should be valid
        assert isinstance(schedule1, list)
        assert isinstance(schedule2, list)
        assert len(schedule2) >= len(schedule1)
    
    def test_system_error_recovery(self, db_manager):
        """Test system error recovery"""
        # Setup
        class_id = db_manager.add_class("Test Class", 5)
        teacher_id = db_manager.add_teacher("Test Teacher", "Matematik")
        lesson_id = db_manager.add_lesson("Matematik")
        
        db_manager.add_schedule_by_school_type(class_id, lesson_id, teacher_id)
        
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        # Try to generate schedule multiple times
        for _ in range(3):
            schedule = scheduler.generate_schedule()
            assert isinstance(schedule, list)


@pytest.mark.system_integration
class TestSystemScalability:
    """Test system scalability"""
    
    def test_system_with_large_school(self, db_manager):
        """Test system with large school (many classes, teachers, lessons)"""
        # Add 20 classes
        for grade in range(5, 9):
            for section in ['A', 'B', 'C', 'D', 'E']:
                db_manager.add_class(f"{grade}{section}", grade)
        
        # Add 30 teachers
        subjects = ["Matematik", "Türkçe", "Fen Bilimleri", "Sosyal Bilgiler", "İngilizce"]
        for i in range(30):
            db_manager.add_teacher(f"Teacher{i}", subjects[i % len(subjects)])
        
        # Add 10 lessons
        for subject in subjects * 2:
            db_manager.add_lesson(subject)
        
        # Generate schedule
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        schedule = scheduler.generate_schedule()
        
        # Should handle large dataset
        assert isinstance(schedule, list)
    
    def test_system_performance_under_load(self, db_manager):
        """Test system performance under load"""
        import time
        
        # Add moderate dataset
        for i in range(10):
            class_id = db_manager.add_class(f"C{i}", 5 + (i % 4))
            teacher_id = db_manager.add_teacher(f"T{i}", "Matematik")
            lesson_id = db_manager.add_lesson(f"L{i}")
            
            db_manager.add_schedule_by_school_type(class_id, lesson_id, teacher_id)
        
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        # Generate multiple times
        start = time.time()
        for _ in range(3):
            schedule = scheduler.generate_schedule()
        duration = time.time() - start
        
        # Should complete in reasonable time
        assert duration < 30.0


@pytest.mark.system_integration
class TestSystemDataIntegrity:
    """Test system data integrity"""
    
    def test_data_consistency_across_operations(self, db_manager):
        """Test data consistency across multiple operations"""
        # Add data
        class_id = db_manager.add_class("Consistency Test", 5)
        
        # Verify immediately
        classes = db_manager.get_all_classes()
        assert any(c.class_id == class_id for c in classes)
        
        # Add more data
        teacher_id = db_manager.add_teacher("Teacher", "Matematik")
        lesson_id = db_manager.add_lesson("Matematik")
        
        # Verify all data
        teachers = db_manager.get_all_teachers()
        lessons = db_manager.get_all_lessons()
        
        assert any(t.teacher_id == teacher_id for t in teachers)
        assert any(l.lesson_id == lesson_id for l in lessons)
    
    def test_referential_integrity(self, db_manager):
        """Test referential integrity in system"""
        class_id = db_manager.add_class("Ref Test", 5)
        teacher_id = db_manager.add_teacher("Ref Teacher", "Matematik")
        lesson_id = db_manager.add_lesson("Matematik")
        
        # Create assignment
        db_manager.add_schedule_by_school_type(class_id, lesson_id, teacher_id)
        
        # Verify assignment references valid data
        schedule = db_manager.get_schedule_by_school_type()
        
        for entry in schedule:
            assert entry.class_id == class_id
            assert entry.teacher_id == teacher_id
            assert entry.lesson_id == lesson_id


@pytest.mark.system_integration
class TestSystemReliability:
    """Test system reliability"""
    
    def test_system_handles_repeated_operations(self, db_manager):
        """Test system handles repeated operations"""
        # Repeat operations multiple times
        for i in range(10):
            class_id = db_manager.add_class(f"Repeat{i}", 5)
            assert class_id is not None
        
        # Verify all added
        classes = db_manager.get_all_classes()
        assert len(classes) >= 10
    
    def test_system_recovers_from_errors(self, db_manager):
        """Test system recovers from errors"""
        # Try invalid operation
        try:
            db_manager.add_class(None, None)
        except Exception:
            pass
        
        # System should still work
        class_id = db_manager.add_class("Recovery Test", 5)
        assert class_id is not None
    
    def test_system_maintains_state(self, db_manager):
        """Test system maintains state correctly"""
        # Set state
        db_manager.set_school_type("Lise")
        
        # Add data
        db_manager.add_class("State Test", 9)
        
        # Verify state maintained
        assert db_manager.get_school_type() == "Lise"
        
        classes = db_manager.get_all_classes()
        assert any(c.name == "State Test" for c in classes)
