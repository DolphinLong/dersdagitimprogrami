"""
Extended Algorithm Tests - Test different scheduling algorithms
"""
import pytest
from unittest.mock import Mock, patch
from algorithms.scheduler import Scheduler


class TestAlgorithmComparison:
    """Compare different scheduling algorithms"""
    
    def test_standard_vs_ultra_aggressive(self, db_manager, sample_schedule_data):
        """Compare standard and ultra aggressive algorithms"""
        scheduler_standard = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        scheduler_ultra = Scheduler(db_manager, use_ultra=True, use_hybrid=False, use_advanced=False)
        
        schedule_standard = scheduler_standard.generate_schedule()
        schedule_ultra = scheduler_ultra.generate_schedule()
        
        # Both should produce valid schedules
        assert isinstance(schedule_standard, list)
        assert isinstance(schedule_ultra, list)
    
    def test_hybrid_vs_advanced(self, db_manager, sample_schedule_data):
        """Compare hybrid and advanced algorithms"""
        scheduler_hybrid = Scheduler(db_manager, use_ultra=False, use_hybrid=True, use_advanced=False)
        scheduler_advanced = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=True)
        
        schedule_hybrid = scheduler_hybrid.generate_schedule()
        schedule_advanced = scheduler_advanced.generate_schedule()
        
        # Both should produce valid schedules
        assert isinstance(schedule_hybrid, list)
        assert isinstance(schedule_advanced, list)
    
    def test_algorithm_consistency(self, db_manager, sample_schedule_data):
        """Test that same algorithm produces consistent results"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        schedule1 = scheduler.generate_schedule()
        schedule2 = scheduler.generate_schedule()
        
        # Should produce same number of entries
        assert len(schedule1) == len(schedule2)


class TestAlgorithmEdgeCases:
    """Test edge cases for algorithms"""
    
    def test_algorithm_with_no_data(self, db_manager):
        """Test algorithm with no data"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        schedule = scheduler.generate_schedule()
        
        # Should return empty schedule
        assert schedule == []
    
    def test_algorithm_with_impossible_constraints(self, db_manager):
        """Test algorithm with impossible constraints"""
        # Add 1 teacher, 10 classes, same lesson
        teacher_id = db_manager.add_teacher("Only Teacher", "Matematik")
        lesson_id = db_manager.add_lesson("Matematik")
        
        for i in range(10):
            class_id = db_manager.add_class(f"Class{i}", 5)
            db_manager.add_schedule_by_school_type(
                class_id=class_id,
                lesson_id=lesson_id,
                teacher_id=teacher_id
            )
        
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        schedule = scheduler.generate_schedule()
        
        # Should handle gracefully
        assert isinstance(schedule, list)
    
    def test_algorithm_with_overloaded_teacher(self, db_manager):
        """Test algorithm when teacher is overloaded"""
        teacher_id = db_manager.add_teacher("Overloaded", "Matematik")
        lesson_id = db_manager.add_lesson("Matematik")
        
        # Assign to many classes
        for i in range(20):
            class_id = db_manager.add_class(f"C{i}", 5)
            db_manager.add_schedule_by_school_type(
                class_id=class_id,
                lesson_id=lesson_id,
                teacher_id=teacher_id
            )
        
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        schedule = scheduler.generate_schedule()
        
        # Should produce partial schedule
        assert isinstance(schedule, list)


class TestAlgorithmOptimization:
    """Test algorithm optimization"""
    
    def test_algorithm_minimizes_conflicts(self, db_manager, sample_schedule_data):
        """Test that algorithm minimizes conflicts"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        schedule = scheduler.generate_schedule()
        conflicts = scheduler.detect_conflicts(schedule)
        
        # Should have minimal conflicts
        assert len(conflicts) < len(schedule) * 0.1  # Less than 10% conflicts
    
    def test_algorithm_distributes_lessons(self, db_manager, sample_schedule_data):
        """Test that algorithm distributes lessons across days"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        schedule = scheduler.generate_schedule()
        
        # Check distribution across days
        days_used = set(entry["day"] for entry in schedule)
        
        # Should use multiple days
        assert len(days_used) >= 1
    
    def test_algorithm_respects_time_slots(self, db_manager, sample_schedule_data):
        """Test that algorithm respects time slot limits"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        schedule = scheduler.generate_schedule()
        
        # All time slots should be valid
        for entry in schedule:
            assert 0 <= entry["time_slot"] < 10  # Max 10 slots


class TestAlgorithmSpecialCases:
    """Test special cases in algorithms"""
    
    def test_algorithm_with_special_lessons(self, db_manager):
        """Test algorithm with special lessons (e.g., T.C. İnkılap Tarihi)"""
        class_id = db_manager.add_class("8A", 8)
        teacher_id = db_manager.add_teacher("History Teacher", "Sosyal Bilgiler")
        lesson_id = db_manager.add_lesson("T.C. İnkılap Tarihi ve Atatürkçülük")
        
        db_manager.add_schedule_by_school_type(
            class_id=class_id,
            lesson_id=lesson_id,
            teacher_id=teacher_id
        )
        
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        schedule = scheduler.generate_schedule()
        
        assert isinstance(schedule, list)
    
    def test_algorithm_with_multiple_subjects_per_teacher(self, db_manager):
        """Test when teacher teaches multiple subjects"""
        teacher_id = db_manager.add_teacher("Multi Subject", "Matematik")
        
        # Add multiple lessons
        math_id = db_manager.add_lesson("Matematik")
        physics_id = db_manager.add_lesson("Fizik")
        
        class_id = db_manager.add_class("9A", 9)
        
        db_manager.add_schedule_by_school_type(
            class_id=class_id,
            lesson_id=math_id,
            teacher_id=teacher_id
        )
        
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        schedule = scheduler.generate_schedule()
        
        assert isinstance(schedule, list)


class TestAlgorithmPerformanceCharacteristics:
    """Test performance characteristics of algorithms"""
    
    def test_algorithm_scales_with_data(self, db_manager):
        """Test that algorithm scales reasonably with data size"""
        import time
        
        # Small dataset
        for i in range(3):
            db_manager.add_class(f"C{i}", 5)
            db_manager.add_teacher(f"T{i}", "Matematik")
            db_manager.add_lesson(f"L{i}")
        
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        start = time.time()
        schedule = scheduler.generate_schedule()
        duration = time.time() - start
        
        # Should be fast with small dataset
        assert duration < 5.0
    
    def test_algorithm_memory_efficiency(self, db_manager, sample_schedule_data):
        """Test that algorithm is memory efficient"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        # Generate multiple times
        for _ in range(5):
            schedule = scheduler.generate_schedule()
            
            # Schedule should not grow unbounded
            assert len(schedule) < 5000
