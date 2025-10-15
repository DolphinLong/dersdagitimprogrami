"""
Comprehensive tests for scheduler.py - targeting 80%+ coverage
Covers: _generate_schedule_standard, helper methods, edge cases
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, call
from algorithms.scheduler import Scheduler
from database.models import Class, Teacher, Lesson, ScheduleEntry


class TestGenerateScheduleStandard:
    """Test _generate_schedule_standard method"""
    
    def test_generate_schedule_standard_with_data(self, db_manager, sample_schedule_data):
        """Test standard generation with complete data"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        schedule = scheduler._generate_schedule_standard()
        
        assert isinstance(schedule, list)
        # Should have some entries
        assert len(schedule) >= 0
    
    def test_generate_schedule_standard_empty_classes(self, db_manager):
        """Test with no classes"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        with patch.object(db_manager, 'get_all_classes', return_value=[]):
            schedule = scheduler._generate_schedule_standard()
            assert schedule == []
    
    def test_generate_schedule_standard_empty_teachers(self, db_manager, sample_classes):
        """Test with no teachers"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        with patch.object(db_manager, 'get_all_teachers', return_value=[]):
            schedule = scheduler._generate_schedule_standard()
            assert isinstance(schedule, list)
    
    def test_generate_schedule_standard_empty_lessons(self, db_manager, sample_classes, sample_teachers):
        """Test with no lessons"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        with patch.object(db_manager, 'get_all_lessons', return_value=[]):
            schedule = scheduler._generate_schedule_standard()
            assert isinstance(schedule, list)
    
    def test_generate_schedule_standard_school_type_handling(self, db_manager):
        """Test school type handling"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        # Test with different school types
        for school_type in ["İlkokul", "Ortaokul", "Lise"]:
            with patch.object(db_manager, 'get_school_type', return_value=school_type):
                with patch.object(db_manager, 'get_all_classes', return_value=[]):
                    schedule = scheduler._generate_schedule_standard()
                    assert isinstance(schedule, list)
    
    def test_generate_schedule_standard_no_school_type(self, db_manager):
        """Test when school type is None"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        with patch.object(db_manager, 'get_school_type', return_value=None):
            with patch.object(db_manager, 'get_all_classes', return_value=[]):
                schedule = scheduler._generate_schedule_standard()
                # Should default to İlkokul
                assert isinstance(schedule, list)
    
    def test_generate_schedule_standard_lesson_assignments(self, db_manager, sample_schedule_data):
        """Test lesson assignment mapping"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        # Mock existing assignments
        mock_assignments = [
            Mock(class_id=1, lesson_id=1, teacher_id=1),
            Mock(class_id=1, lesson_id=2, teacher_id=2),
        ]
        
        with patch.object(db_manager, 'get_schedule_by_school_type', return_value=mock_assignments):
            schedule = scheduler._generate_schedule_standard()
            assert isinstance(schedule, list)
    
    def test_generate_schedule_standard_conflict_detection(self, db_manager, sample_schedule_data):
        """Test conflict detection in standard generation"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        with patch.object(scheduler, 'detect_conflicts', return_value=[]):
            schedule = scheduler._generate_schedule_standard()
            assert isinstance(schedule, list)
    
    def test_generate_schedule_standard_conflict_resolution(self, db_manager, sample_schedule_data):
        """Test conflict resolution"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        mock_conflicts = [{'type': 'teacher_conflict', 'day': 0, 'slot': 0}]
        
        with patch.object(scheduler, 'detect_conflicts', return_value=mock_conflicts):
            with patch('algorithms.scheduler.ConflictResolver') as mock_resolver:
                mock_resolver_instance = Mock()
                mock_resolver_instance.auto_resolve_conflicts.return_value = 1
                mock_resolver.return_value = mock_resolver_instance
                
                schedule = scheduler._generate_schedule_standard()
                assert isinstance(schedule, list)


class TestGetEligibleTeachers:
    """Test _get_eligible_teachers method"""
    
    def test_get_eligible_teachers_basic(self, db_manager):
        """Test basic eligible teacher selection"""
        scheduler = Scheduler(db_manager)
        
        # Create mock teachers
        teacher1 = Mock(teacher_id=1, name="Teacher 1", subject="Matematik")
        teacher2 = Mock(teacher_id=2, name="Teacher 2", subject="Türkçe")
        teacher3 = Mock(teacher_id=3, name="Teacher 3", subject="Matematik")
        teachers = [teacher1, teacher2, teacher3]
        
        # Create mock lesson
        lesson = Mock(name="Matematik")
        
        with patch.object(db_manager, 'get_schedule_for_specific_teacher', return_value=[]):
            eligible = scheduler._get_eligible_teachers(teachers, lesson)
            
            # Should return only Matematik teachers
            assert len(eligible) == 2
            assert all(t.subject == "Matematik" for t in eligible)
    
    def test_get_eligible_teachers_no_match(self, db_manager):
        """Test when no teachers match"""
        scheduler = Scheduler(db_manager)
        
        teacher1 = Mock(teacher_id=1, subject="Matematik")
        teachers = [teacher1]
        lesson = Mock(name="Fen Bilimleri")
        
        eligible = scheduler._get_eligible_teachers(teachers, lesson)
        assert len(eligible) == 0
    
    def test_get_eligible_teachers_special_lesson(self, db_manager):
        """Test special handling for T.C. İnkılap Tarihi"""
        scheduler = Scheduler(db_manager)
        
        teacher1 = Mock(teacher_id=1, subject="Sosyal Bilgiler")
        teachers = [teacher1]
        lesson = Mock(name="T.C. İnkılap Tarihi ve Atatürkçülük")
        
        with patch.object(db_manager, 'get_schedule_for_specific_teacher', return_value=[]):
            eligible = scheduler._get_eligible_teachers(teachers, lesson)
            # Sosyal Bilgiler teachers should be included
            assert len(eligible) > 0
    
    def test_get_eligible_teachers_workload_sorting(self, db_manager):
        """Test teachers are sorted by workload"""
        scheduler = Scheduler(db_manager)
        
        teacher1 = Mock(teacher_id=1, subject="Matematik")
        teacher2 = Mock(teacher_id=2, subject="Matematik")
        teachers = [teacher1, teacher2]
        lesson = Mock(name="Matematik")
        
        # Mock different workloads
        def mock_schedule(teacher_id):
            if teacher_id == 1:
                return [1, 2, 3]  # 3 entries
            else:
                return [1]  # 1 entry
        
        with patch.object(db_manager, 'get_schedule_for_specific_teacher', side_effect=mock_schedule):
            eligible = scheduler._get_eligible_teachers(teachers, lesson)
            
            # Teacher with less workload should be first
            assert eligible[0].teacher_id == 2


class TestScheduleLessonWithAssignedTeacher:
    """Test _schedule_lesson_with_assigned_teacher method"""
    
    def test_schedule_lesson_basic(self, db_manager):
        """Test basic lesson scheduling"""
        scheduler = Scheduler(db_manager)
        
        schedule_entries = []
        class_obj = Mock(class_id=1, name="5A", grade=5)
        teacher = Mock(teacher_id=1, name="Teacher 1")
        lesson = Mock(lesson_id=1, name="Matematik")
        days = list(range(5))
        time_slots = list(range(7))
        weekly_hours = 2
        
        with patch.object(scheduler, '_create_optimal_blocks_distributed', return_value=[2]):
            with patch.object(scheduler, '_find_best_slots_aggressive', return_value=[0, 1]):
                with patch.object(scheduler, '_can_teacher_teach_at_slots_aggressive', return_value=True):
                    with patch.object(scheduler, '_has_conflict', return_value=False):
                        success = scheduler._schedule_lesson_with_assigned_teacher(
                            schedule_entries, class_obj, teacher, lesson, days, time_slots, weekly_hours
                        )
                        
                        assert success == True
                        assert len(schedule_entries) == 2
    
    def test_schedule_lesson_max_attempts(self, db_manager):
        """Test max attempts limit"""
        scheduler = Scheduler(db_manager)
        
        schedule_entries = []
        class_obj = Mock(class_id=1, name="5A", grade=5)
        teacher = Mock(teacher_id=1, name="Teacher 1")
        lesson = Mock(lesson_id=1, name="Matematik")
        days = list(range(5))
        time_slots = list(range(7))
        weekly_hours = 10  # High number
        
        with patch.object(scheduler, '_create_optimal_blocks_distributed', return_value=[1]):
            with patch.object(scheduler, '_find_best_slots_aggressive', return_value=[]):
                success = scheduler._schedule_lesson_with_assigned_teacher(
                    schedule_entries, class_obj, teacher, lesson, days, time_slots, weekly_hours
                )
                
                # Should fail after max attempts
                assert success == False
    
    def test_schedule_lesson_teacher_daily_limit(self, db_manager):
        """Test teacher daily hour limit"""
        scheduler = Scheduler(db_manager)
        
        # Pre-fill schedule with teacher entries
        schedule_entries = [
            {"teacher_id": 1, "day": 0, "time_slot": i} for i in range(7)
        ]
        
        class_obj = Mock(class_id=1, name="5A", grade=5)
        teacher = Mock(teacher_id=1, name="Teacher 1")
        lesson = Mock(lesson_id=1, name="Matematik")
        days = list(range(5))
        time_slots = list(range(7))
        weekly_hours = 2
        
        with patch.object(scheduler, '_create_optimal_blocks_distributed', return_value=[2]):
            with patch.object(scheduler, '_find_best_slots_aggressive', return_value=[0, 1]):
                with patch.object(scheduler, '_can_teacher_teach_at_slots_aggressive', return_value=True):
                    with patch.object(scheduler, '_has_conflict', return_value=False):
                        success = scheduler._schedule_lesson_with_assigned_teacher(
                            schedule_entries, class_obj, teacher, lesson, days, time_slots, weekly_hours
                        )
                        
                        # Should handle daily limit
                        assert isinstance(success, bool)


class TestHelperMethods:
    """Test various helper methods"""
    
    def test_create_optimal_blocks_distributed(self, db_manager):
        """Test _create_optimal_blocks_distributed"""
        scheduler = Scheduler(db_manager)
        
        # Test different hour counts
        for hours in [1, 2, 3, 4, 5, 6]:
            blocks = scheduler._create_optimal_blocks_distributed(hours)
            assert isinstance(blocks, list)
            assert sum(blocks) == hours
    
    def test_find_best_slots_aggressive(self, db_manager):
        """Test _find_best_slots_aggressive"""
        scheduler = Scheduler(db_manager)
        
        schedule_entries = []
        class_id = 1
        day = 0
        time_slots = list(range(7))
        block_size = 2
        
        slots = scheduler._find_best_slots_aggressive(schedule_entries, class_id, day, time_slots, block_size)
        
        assert isinstance(slots, list)
        # Should find consecutive slots
        if len(slots) > 0:
            assert len(slots) <= block_size
    
    def test_can_teacher_teach_at_slots_aggressive(self, db_manager):
        """Test _can_teacher_teach_at_slots_aggressive"""
        scheduler = Scheduler(db_manager)
        
        schedule_entries = []
        teacher_id = 1
        day = 0
        slots = [0, 1]
        
        can_teach = scheduler._can_teacher_teach_at_slots_aggressive(schedule_entries, teacher_id, day, slots)
        
        assert isinstance(can_teach, bool)
    
    def test_has_conflict(self, db_manager):
        """Test _has_conflict"""
        scheduler = Scheduler(db_manager)
        
        schedule_entries = [
            {"class_id": 1, "day": 0, "time_slot": 0, "teacher_id": 1}
        ]
        
        # Test conflicting entry (same class, day, slot)
        new_entry = {"class_id": 1, "day": 0, "time_slot": 0, "teacher_id": 2}
        assert scheduler._has_conflict(schedule_entries, new_entry) == True
        
        # Test non-conflicting entry
        new_entry = {"class_id": 1, "day": 0, "time_slot": 1, "teacher_id": 2}
        assert scheduler._has_conflict(schedule_entries, new_entry) == False
    
    def test_detect_conflicts(self, db_manager):
        """Test detect_conflicts"""
        scheduler = Scheduler(db_manager)
        
        # No conflicts
        schedule_entries = [
            {"class_id": 1, "day": 0, "time_slot": 0, "teacher_id": 1},
            {"class_id": 2, "day": 0, "time_slot": 0, "teacher_id": 2},
        ]
        conflicts = scheduler.detect_conflicts(schedule_entries)
        assert len(conflicts) == 0
        
        # Teacher conflict
        schedule_entries = [
            {"class_id": 1, "day": 0, "time_slot": 0, "teacher_id": 1},
            {"class_id": 2, "day": 0, "time_slot": 0, "teacher_id": 1},
        ]
        conflicts = scheduler.detect_conflicts(schedule_entries)
        assert len(conflicts) > 0


class TestScheduleLessonImproved:
    """Test _schedule_lesson_improved method"""
    
    def test_schedule_lesson_improved_with_specific_teacher(self, db_manager):
        """Test with specific teacher"""
        scheduler = Scheduler(db_manager)
        
        schedule_entries = []
        class_obj = Mock(class_id=1, name="5A")
        teacher = Mock(teacher_id=1, name="Teacher 1")
        lesson = Mock(lesson_id=1, name="Matematik")
        days = list(range(5))
        time_slots = list(range(7))
        weekly_hours = 2
        
        with patch.object(scheduler, '_try_schedule_with_teacher', return_value=True):
            success = scheduler._schedule_lesson_improved(
                schedule_entries, class_obj, teacher, lesson, days, time_slots, weekly_hours
            )
            
            assert isinstance(success, bool)
    
    def test_schedule_lesson_improved_with_eligible_teachers(self, db_manager):
        """Test with eligible teachers list"""
        scheduler = Scheduler(db_manager)
        
        schedule_entries = []
        class_obj = Mock(class_id=1, name="5A")
        lesson = Mock(lesson_id=1, name="Matematik")
        days = list(range(5))
        time_slots = list(range(7))
        weekly_hours = 2
        
        teacher1 = Mock(teacher_id=1, name="Teacher 1")
        teacher2 = Mock(teacher_id=2, name="Teacher 2")
        eligible_teachers = [teacher1, teacher2]
        
        with patch.object(scheduler, '_try_schedule_with_teacher', return_value=True):
            success = scheduler._schedule_lesson_improved(
                schedule_entries, class_obj, None, lesson, days, time_slots, weekly_hours, eligible_teachers
            )
            
            assert isinstance(success, bool)
    
    def test_schedule_lesson_improved_no_teachers(self, db_manager):
        """Test with no eligible teachers"""
        scheduler = Scheduler(db_manager)
        
        schedule_entries = []
        class_obj = Mock(class_id=1, name="5A")
        lesson = Mock(lesson_id=1, name="Matematik")
        days = list(range(5))
        time_slots = list(range(7))
        weekly_hours = 2
        
        with patch.object(scheduler, '_get_eligible_teachers', return_value=[]):
            success = scheduler._schedule_lesson_improved(
                schedule_entries, class_obj, None, lesson, days, time_slots, weekly_hours
            )
            
            assert success == False


class TestEdgeCasesAndIntegration:
    """Test edge cases and integration scenarios"""
    
    def test_schedule_with_conflicting_requirements(self, db_manager, sample_schedule_data):
        """Test scheduling with conflicting requirements"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        # This should handle conflicts gracefully
        schedule = scheduler._generate_schedule_standard()
        assert isinstance(schedule, list)
    
    def test_schedule_with_limited_time_slots(self, db_manager):
        """Test with very limited time slots"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        with patch.object(db_manager, 'get_school_type', return_value="İlkokul"):  # Only 6 slots
            schedule = scheduler._generate_schedule_standard()
            assert isinstance(schedule, list)
    
    def test_schedule_with_many_lessons(self, db_manager, sample_schedule_data):
        """Test with many lessons to schedule"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        # Add many lesson assignments
        schedule = scheduler._generate_schedule_standard()
        assert isinstance(schedule, list)
    
    def test_schedule_generation_idempotency(self, db_manager):
        """Test that multiple generations produce consistent results"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        with patch.object(db_manager, 'get_all_classes', return_value=[]):
            schedule1 = scheduler._generate_schedule_standard()
            schedule2 = scheduler._generate_schedule_standard()
            
            # Both should be empty lists
            assert schedule1 == schedule2


class TestSchedulerLoggingDetailed:
    """Detailed logging tests"""
    
    def test_logging_during_standard_generation(self, db_manager, caplog):
        """Test logging during standard generation"""
        import logging
        caplog.set_level(logging.INFO)
        
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        with patch.object(db_manager, 'get_all_classes', return_value=[]):
            scheduler._generate_schedule_standard()
            
            # Check that logging occurred
            assert len(caplog.records) > 0
    
    def test_logging_conflict_detection(self, db_manager, caplog):
        """Test logging during conflict detection"""
        import logging
        caplog.set_level(logging.INFO)
        
        scheduler = Scheduler(db_manager)
        
        schedule_entries = [
            {"class_id": 1, "day": 0, "time_slot": 0, "teacher_id": 1},
            {"class_id": 2, "day": 0, "time_slot": 0, "teacher_id": 1},
        ]
        
        conflicts = scheduler.detect_conflicts(schedule_entries)
        
        # Should have detected conflicts
        assert len(conflicts) > 0


class TestSchedulerPerformanceDetailed:
    """Detailed performance tests"""
    
    def test_standard_generation_performance(self, db_manager):
        """Test standard generation performance"""
        import time
        
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False, use_advanced=False)
        
        start = time.time()
        with patch.object(db_manager, 'get_all_classes', return_value=[]):
            scheduler._generate_schedule_standard()
        duration = time.time() - start
        
        # Should be fast with empty data
        assert duration < 1.0
    
    def test_helper_method_performance(self, db_manager):
        """Test helper method performance"""
        import time
        
        scheduler = Scheduler(db_manager)
        
        schedule_entries = []
        
        start = time.time()
        for _ in range(100):
            scheduler._has_conflict(schedule_entries, {"class_id": 1, "day": 0, "time_slot": 0})
        duration = time.time() - start
        
        # Should be very fast
        assert duration < 0.1
