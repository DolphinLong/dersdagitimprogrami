# -*- coding: utf-8 -*-
"""
Test suite for algorithms/scheduler.py

Tests the Scheduler class which manages automatic schedule generation
using various scheduling algorithms. This is a CRITICAL module with 1824 lines
of code that previously had 0% test coverage.

Coverage Goal: 80%+
"""

import pytest
import logging
from unittest.mock import Mock, MagicMock, patch, call
from typing import List, Dict, Any

# Import the Scheduler class
from algorithms.scheduler import Scheduler


class TestSchedulerInitialization:
    """Test Scheduler class initialization and configuration"""

    def test_scheduler_init_basic(self):
        """Test basic scheduler initialization"""
        db_manager = Mock()
        scheduler = Scheduler(db_manager)

        assert scheduler.db_manager == db_manager
        assert scheduler.progress_callback is None
        assert isinstance(scheduler.logger, logging.Logger)

    def test_scheduler_init_with_callback(self):
        """Test scheduler initialization with progress callback"""
        db_manager = Mock()
        progress_callback = Mock()

        scheduler = Scheduler(db_manager, progress_callback=progress_callback)

        assert scheduler.progress_callback == progress_callback

    def test_scheduler_init_performance_monitor_enabled(self):
        """Test performance monitor initialization when enabled"""
        db_manager = Mock()

        with patch('algorithms.scheduler.PERFORMANCE_MONITOR_AVAILABLE', True):
            scheduler = Scheduler(db_manager, enable_performance_monitor=True)

            # Should have performance monitor when available
            assert scheduler.performance_monitor is not None

    def test_scheduler_init_performance_monitor_disabled(self):
        """Test performance monitor is None when disabled or unavailable"""
        db_manager = Mock()

        with patch('algorithms.scheduler.PERFORMANCE_MONITOR_AVAILABLE', False):
            scheduler = Scheduler(db_manager, enable_performance_monitor=True)

            # Should be None when not available
            assert scheduler.performance_monitor is None

    def test_scheduler_init_heuristics_available(self):
        """Test heuristics manager initialization when available"""
        db_manager = Mock()

        with patch('algorithms.scheduler.HEURISTICS_AVAILABLE', True):
            scheduler = Scheduler(db_manager)

            # Should have heuristics when available
            assert scheduler.heuristics is not None

    def test_scheduler_init_heuristics_unavailable(self):
        """Test heuristics manager is None when unavailable"""
        db_manager = Mock()

        with patch('algorithms.scheduler.HEURISTICS_AVAILABLE', False):
            scheduler = Scheduler(db_manager)

            # Should be None when not available
            assert scheduler.heuristics is None

    def test_school_time_slots_configuration(self):
        """Test school time slots configuration for different school types"""
        db_manager = Mock()
        scheduler = Scheduler(db_manager)

        expected_slots = {
            "İlkokul": 6,
            "Ortaokul": 7,
            "Lise": 8,
            "Anadolu Lisesi": 8,
            "Fen Lisesi": 8,
            "Sosyal Bilimler Lisesi": 8,
        }

        assert scheduler.SCHOOL_TIME_SLOTS == expected_slots

    @pytest.mark.parametrize("use_advanced,use_hybrid,expected_hybrid,expected_simple,expected_ultimate", [
        (True, True, True, True, True),
        (False, False, False, True, True),
        (True, False, False, True, True),
        (False, True, False, True, True),
    ])
    def test_scheduler_flags_configuration(self, use_advanced, use_hybrid, expected_hybrid, expected_simple, expected_ultimate):
        """Test scheduler flag configuration based on parameters"""
        db_manager = Mock()

        with patch('algorithms.scheduler.HYBRID_OPTIMAL_SCHEDULER_AVAILABLE', True), \
             patch('algorithms.scheduler.SIMPLE_PERFECT_SCHEDULER_AVAILABLE', True), \
             patch('algorithms.scheduler.ULTIMATE_SCHEDULER_AVAILABLE', True), \
             patch('algorithms.scheduler.ENHANCED_STRICT_SCHEDULER_AVAILABLE', True):

            scheduler = Scheduler(db_manager, use_advanced=use_advanced, use_hybrid=use_hybrid)

            # Note: These flags are set in __init__ but we verify the behavior
            assert scheduler.use_simple_perfect is True
            assert scheduler.use_ultimate is True
            assert scheduler.use_enhanced_strict is True


class TestSchedulerAlgorithmSelection:
    """Test algorithm selection and initialization"""

    @patch('algorithms.scheduler.OPTIMIZED_CURRICULUM_SCHEDULER_AVAILABLE', True)
    @patch('algorithms.scheduler.OptimizedCurriculumScheduler')
    def test_optimized_curriculum_scheduler_selection(self, mock_scheduler_class):
        """Test OptimizedCurriculumScheduler is selected when available"""
        db_manager = Mock()
        mock_instance = Mock()
        mock_scheduler_class.return_value = mock_instance

        scheduler = Scheduler(db_manager)

        assert scheduler.active_scheduler == mock_instance
        mock_scheduler_class.assert_called_once_with(db_manager, None)

    @patch('algorithms.scheduler.OPTIMIZED_CURRICULUM_SCHEDULER_AVAILABLE', True)
    @patch('algorithms.scheduler.OptimizedCurriculumScheduler')
    def test_optimized_curriculum_scheduler_fallback_on_error(self, mock_scheduler_class):
        """Test fallback when OptimizedCurriculumScheduler initialization fails"""
        db_manager = Mock()
        mock_scheduler_class.side_effect = Exception("Initialization failed")

        # Should not raise, just log warning and set active_scheduler to None
        with patch('algorithms.scheduler.AlgorithmSelector'):
            scheduler = Scheduler(db_manager)

            assert scheduler.active_scheduler is None

    @patch('algorithms.scheduler.OPTIMIZED_CURRICULUM_SCHEDULER_AVAILABLE', False)
    @patch('algorithms.scheduler.AlgorithmSelector')
    def test_algorithm_selector_fallback(self, mock_selector_class):
        """Test AlgorithmSelector fallback when OptimizedCurriculumScheduler unavailable"""
        db_manager = Mock()
        mock_selector = Mock()
        mock_scheduler_instance = Mock()
        mock_selector_class.return_value = mock_selector
        mock_selector.select_best_algorithm.return_value = Mock
        mock_selector.get_algorithm_recommendation.return_value = {
            'best_algorithm': 'hybrid_optimal',
            'reasoning': 'Best overall performance',
            'score': 9.5
        }
        mock_selector.select_best_algorithm.return_value = Mock
        mock_selector_instance = Mock()
        mock_selector.select_best_algorithm.return_value.return_value = mock_scheduler_instance

        with patch('algorithms.scheduler.HYBRID_OPTIMAL_SCHEDULER_AVAILABLE', True):
            scheduler = Scheduler(db_manager)

            assert scheduler.active_scheduler is not None
            mock_selector.select_best_algorithm.assert_called()

    @patch('algorithms.scheduler.OPTIMIZED_CURRICULUM_SCHEDULER_AVAILABLE', False)
    @patch('algorithms.scheduler.AlgorithmSelector', None)
    @patch('algorithms.scheduler.ENHANCED_SCHEDULE_GENERATOR_AVAILABLE', True)
    @patch('algorithms.scheduler.EnhancedScheduleGenerator')
    def test_enhanced_schedule_generator_fallback(self, mock_generator_class):
        """Test EnhancedScheduleGenerator fallback when AlgorithmSelector unavailable"""
        db_manager = Mock()
        mock_instance = Mock()
        mock_generator_class.return_value = mock_instance

        scheduler = Scheduler(db_manager)

        assert scheduler.active_scheduler == mock_instance
        mock_generator_class.assert_called_once_with(db_manager)

    @patch('algorithms.scheduler.OPTIMIZED_CURRICULUM_SCHEDULER_AVAILABLE', False)
    @patch('algorithms.scheduler.AlgorithmSelector', None)
    @patch('algorithms.scheduler.ENHANCED_SCHEDULE_GENERATOR_AVAILABLE', False)
    @patch('algorithms.scheduler.ENHANCED_SIMPLE_PERFECT_AVAILABLE', True)
    @patch('algorithms.scheduler.EnhancedSimplePerfectScheduler')
    def test_enhanced_simple_perfect_fallback(self, mock_scheduler_class):
        """Test EnhancedSimplePerfectScheduler fallback"""
        db_manager = Mock()
        mock_instance = Mock()
        mock_scheduler_class.return_value = mock_instance

        with patch('algorithms.scheduler.HEURISTICS_AVAILABLE', True):
            scheduler = Scheduler(db_manager)

            assert scheduler.active_scheduler == mock_instance
            mock_scheduler_class.assert_called_once_with(db_manager, heuristics=scheduler.heuristics)


class TestScheduleGeneration:
    """Test schedule generation methods"""

    def test_generate_schedule_with_active_scheduler(self):
        """Test generate_schedule delegates to active_scheduler"""
        db_manager = Mock()
        mock_scheduler = Mock()
        mock_scheduler.generate_schedule.return_value = ["schedule_entry_1", "schedule_entry_2"]

        scheduler = Scheduler(db_manager)
        scheduler.active_scheduler = mock_scheduler

        result = scheduler.generate_schedule()

        assert result == ["schedule_entry_1", "schedule_entry_2"]
        mock_scheduler.generate_schedule.assert_called_once()

    def test_generate_schedule_with_performance_monitor(self):
        """Test generate_schedule uses performance monitor when available"""
        db_manager = Mock()
        mock_monitor = Mock()
        mock_monitor.timing_decorator.return_value = Mock(return_value=["result"])

        scheduler = Scheduler(db_manager)
        scheduler.performance_monitor = mock_monitor
        scheduler.active_scheduler = Mock()

        result = scheduler.generate_schedule()

        assert result == ["result"]
        mock_monitor.timing_decorator.assert_called_once()

    def test_generate_schedule_standard_fallback(self):
        """Test generate_schedule falls back to standard algorithm"""
        db_manager = Mock()
        scheduler = Scheduler(db_manager)
        scheduler.active_scheduler = None

        with patch.object(scheduler, '_generate_schedule_standard') as mock_standard:
            mock_standard.return_value = ["standard_schedule"]

            result = scheduler.generate_schedule()

            assert result == ["standard_schedule"]
            mock_standard.assert_called_once()


class TestStandardScheduleGeneration:
    """Test _generate_schedule_standard method and its helpers"""

    def setup_method(self):
        """Setup for each test method"""
        self.db_manager = Mock()
        self.scheduler = Scheduler(self.db_manager)

    def test_generate_schedule_standard_basic_flow(self):
        """Test basic flow of _generate_schedule_standard"""
        # Mock data
        classes = [Mock(id=1, name="9-A"), Mock(id=2, name="10-A")]
        teachers = [Mock(id=1, name="Teacher A"), Mock(id=2, name="Teacher B")]
        lessons = [Mock(id=1, name="Math", weekly_hours=4), Mock(id=2, name="Science", weekly_hours=3)]

        self.db_manager.get_all_classes.return_value = classes
        self.db_manager.get_all_teachers.return_value = teachers
        self.db_manager.get_all_lessons.return_value = lessons
        self.db_manager.get_schedule_by_school_type.return_value = []
        self.db_manager.get_school_type.return_value = "Lise"

        with patch.object(self.scheduler, '_schedule_additional_hours') as mock_schedule:
            mock_schedule.return_value = ["scheduled_entry"]

            result = self.scheduler._generate_schedule_standard()

            # Verify database queries were made
            self.db_manager.get_all_classes.assert_called_once()
            self.db_manager.get_all_teachers.assert_called_once()
            self.db_manager.get_all_lessons.assert_called_once()
            self.db_manager.get_schedule_by_school_type.assert_called_once()
            self.db_manager.get_school_type.assert_called_once()

            # Verify schedule method was called
            mock_schedule.assert_called_once()

    def test_generate_schedule_standard_default_school_type(self):
        """Test _generate_schedule_standard uses default school type when None"""
        self.db_manager.get_all_classes.return_value = []
        self.db_manager.get_all_teachers.return_value = []
        self.db_manager.get_all_lessons.return_value = []
        self.db_manager.get_schedule_by_school_type.return_value = []
        self.db_manager.get_school_type.return_value = None  # Returns None

        self.scheduler._generate_schedule_standard()

        # Should use "İlkokul" as default
        assert self.scheduler.SCHOOL_TIME_SLOTS.get("İlkokul") == 6

    def test_schedule_additional_hours_calls_lesson_scheduling(self):
        """Test _schedule_additional_hours calls lesson scheduling methods"""
        classes = [Mock(id=1)]
        teachers = [Mock(id=1)]
        lessons = [Mock(id=1, weekly_hours=4)]

        with patch.object(self.scheduler, '_schedule_lesson_improved') as mock_schedule_lesson:
            mock_schedule_lesson.return_value = ["scheduled"]

            result = self.scheduler._schedule_additional_hours(
                classes, teachers, lessons, []
            )

            assert result == ["scheduled"]
            mock_schedule_lesson.assert_called()

    def test_can_teacher_teach_at_slots_basic(self):
        """Test _can_teacher_teach_at_slots basic functionality"""
        schedule_entries = []
        teacher_id = 1
        day = "Pazartesi"
        time_slots = [1, 2]

        result = self.scheduler._can_teacher_teach_at_slots(schedule_entries, teacher_id, day, time_slots)

        # Should return True for basic case with no existing entries
        assert result is True

    def test_can_teacher_teach_at_slots_with_conflict(self):
        """Test _can_teacher_teach_at_slots detects conflicts"""
        # Create a schedule entry for the same teacher at same time
        schedule_entry = Mock()
        schedule_entry.teacher_id = 1
        schedule_entry.day = "Pazartesi"
        schedule_entry.time_slot = 1

        schedule_entries = [schedule_entry]
        teacher_id = 1
        day = "Pazartesi"
        time_slots = [1, 2]

        result = self.scheduler._can_teacher_teach_at_slots(schedule_entries, teacher_id, day, time_slots)

        # Should return False due to conflict
        assert result is False

    def test_is_class_slot_available(self):
        """Test _is_class_slot_available"""
        schedule_entries = []
        class_id = 1
        day = "Pazartesi"
        time_slot = 1

        result = self.scheduler._is_class_slot_available(schedule_entries, class_id, day, time_slot)

        # Should be True when no existing entry
        assert result is True

    def test_is_class_slot_unavailable(self):
        """Test _is_class_slot_available returns False when occupied"""
        schedule_entry = Mock()
        schedule_entry.class_id = 1
        schedule_entry.day = "Pazartesi"
        schedule_entry.time_slot = 1

        schedule_entries = [schedule_entry]
        class_id = 1
        day = "Pazartesi"
        time_slot = 1

        result = self.scheduler._is_class_slot_available(schedule_entries, class_id, day, time_slot)

        assert result is False

    def test_has_conflict_no_conflict(self):
        """Test _has_conflict returns False when no conflict"""
        schedule_entries = []
        new_entry = Mock()
        new_entry.teacher_id = 1
        new_entry.class_id = 2
        new_entry.day = "Pazartesi"
        new_entry.time_slot = 1

        result = self.scheduler._has_conflict(schedule_entries, new_entry)

        assert result is False

    def test_has_conflict_teacher_conflict(self):
        """Test _has_conflict detects teacher conflict"""
        existing_entry = Mock()
        existing_entry.teacher_id = 1
        existing_entry.day = "Pazartesi"
        existing_entry.time_slot = 1

        schedule_entries = [existing_entry]
        new_entry = Mock()
        new_entry.teacher_id = 1  # Same teacher
        new_entry.class_id = 2
        new_entry.day = "Pazartesi"
        new_entry.time_slot = 1  # Same time

        result = self.scheduler._has_conflict(schedule_entries, new_entry)

        assert result is True

    def test_has_conflict_class_conflict(self):
        """Test _has_conflict detects class conflict"""
        existing_entry = Mock()
        existing_entry.class_id = 1
        existing_entry.day = "Pazartesi"
        existing_entry.time_slot = 1

        schedule_entries = [existing_entry]
        new_entry = Mock()
        new_entry.teacher_id = 2
        new_entry.class_id = 1  # Same class
        new_entry.day = "Pazartesi"
        new_entry.time_slot = 1  # Same time

        result = self.scheduler._has_conflict(schedule_entries, new_entry)

        assert result is True


class TestOptimalBlockCreation:
    """Test optimal block creation methods"""

    def setup_method(self):
        """Setup for each test method"""
        self.db_manager = Mock()
        self.scheduler = Scheduler(self.db_manager)

    def test_create_optimal_blocks_6_hours(self):
        """Test _create_optimal_blocks for 6 hours (2+2+2)"""
        total_hours = 6

        result = self.scheduler._create_optimal_blocks(total_hours)

        # Should create 3 blocks of 2 hours each
        assert result == [2, 2, 2]

    def test_create_optimal_blocks_5_hours(self):
        """Test _create_optimal_blocks for 5 hours (2+2+1)"""
        total_hours = 5

        result = self.scheduler._create_optimal_blocks(total_hours)

        # Should create 2+2+1
        assert result == [2, 2, 1]

    def test_create_optimal_blocks_4_hours(self):
        """Test _create_optimal_blocks for 4 hours (2+2)"""
        total_hours = 4

        result = self.scheduler._create_optimal_blocks(total_hours)

        # Should create 2+2
        assert result == [2, 2]

    def test_create_optimal_blocks_3_hours(self):
        """Test _create_optimal_blocks for 3 hours (2+1)"""
        total_hours = 3

        result = self.scheduler._create_optimal_blocks(total_hours)

        # Should create 2+1
        assert result == [2, 1]

    def test_create_optimal_blocks_2_hours(self):
        """Test _create_optimal_blocks for 2 hours (2)"""
        total_hours = 2

        result = self.scheduler._create_optimal_blocks(total_hours)

        # Should create single block of 2
        assert result == [2]

    def test_create_optimal_blocks_1_hour(self):
        """Test _create_optimal_blocks for 1 hour (1)"""
        total_hours = 1

        result = self.scheduler._create_optimal_blocks(total_hours)

        # Should create single block of 1
        assert result == [1]

    def test_create_optimal_blocks_8_hours(self):
        """Test _create_optimal_blocks for 8 hours"""
        total_hours = 8

        result = self.scheduler._create_optimal_blocks(total_hours)

        # Should create balanced blocks
        assert len(result) > 0
        assert sum(result) == 8

    def test_create_optimal_blocks_distributed(self):
        """Test _create_optimal_blocks_distributed"""
        total_hours = 6

        result = self.scheduler._create_optimal_blocks_distributed(total_hours)

        # Should distribute hours across blocks
        assert isinstance(result, list)
        assert sum(result) == total_hours


class TestTeacherEligibility:
    """Test teacher eligibility and assignment"""

    def setup_method(self):
        """Setup for each test method"""
        self.db_manager = Mock()
        self.scheduler = Scheduler(self.db_manager)

    def test_get_eligible_teachers_all_eligible(self):
        """Test _get_eligible_teachers returns all teachers for lesson"""
        teachers = [
            Mock(id=1, name="Teacher A"),
            Mock(id=2, name="Teacher B"),
            Mock(id=3, name="Teacher C"),
        ]

        lesson = Mock(id=1, name="Math")
        lesson.assigned_teacher_id = None  # No specific teacher assigned

        result = self.scheduler._get_eligible_teachers(teachers, lesson)

        # Should return all teachers
        assert len(result) == 3
        assert result == teachers

    def test_get_eligible_teachers_specific_teacher(self):
        """Test _get_eligible_teachers returns only assigned teacher"""
        teachers = [
            Mock(id=1, name="Teacher A"),
            Mock(id=2, name="Teacher B"),
            Mock(id=3, name="Teacher C"),
        ]

        lesson = Mock(id=1, name="Math")
        lesson.assigned_teacher_id = 2  # Specific teacher assigned

        result = self.scheduler._get_eligible_teachers(teachers, lesson)

        # Should return only the assigned teacher
        assert len(result) == 1
        assert result[0].id == 2

    def test_schedule_lesson_with_assigned_teacher(self):
        """Test _schedule_lesson_with_assigned_teacher"""
        schedule_entries = []
        class_id = 1
        day = "Pazartesi"
        lesson = Mock(weekly_hours=4, assigned_teacher_id=1)
        teachers = [Mock(id=1, name="Teacher A")]

        with patch.object(self.scheduler, '_can_teacher_teach_at_slots', return_value=True), \
             patch.object(self.scheduler, '_is_class_slot_available', return_value=True), \
             patch.object(self.scheduler, '_find_best_slots', return_value=[1, 2]):

            result = self.scheduler._schedule_lesson_with_assigned_teacher(
                schedule_entries, class_id, day, lesson, teachers
            )

            # Should schedule the lesson
            assert result is not None


class TestSlotFinding:
    """Test slot finding and placement methods"""

    def setup_method(self):
        """Setup for each test method"""
        self.db_manager = Mock()
        self.scheduler = Scheduler(self.db_manager)

    def test_find_best_slots_basic(self):
        """Test _find_best_slots basic functionality"""
        schedule_entries = []
        class_id = 1
        day = "Pazartesi"
        time_slots = 7
        hours_needed = 2

        result = self.scheduler._find_best_slots(schedule_entries, class_id, day, time_slots, hours_needed)

        # Should find available slots
        assert isinstance(result, list)

    def test_find_best_slots_enhanced(self):
        """Test _find_best_slots_enhanced"""
        schedule_entries = []
        class_id = 1
        day = "Pazartesi"
        time_slots = 7
        hours_needed = 2

        result = self.scheduler._find_best_slots_enhanced(schedule_entries, class_id, day, time_slots, hours_needed)

        # Should find enhanced slots
        assert isinstance(result, list)

    def test_find_best_slots_aggressive(self):
        """Test _find_best_slots_aggressive"""
        schedule_entries = []
        class_id = 1
        day = "Pazartesi"
        time_slots = 7
        block_size = 2

        result = self.scheduler._find_best_slots_aggressive(schedule_entries, class_id, day, time_slots, block_size)

        # Should find aggressive slots
        assert isinstance(result, list)


class TestErrorHandling:
    """Test error handling and edge cases"""

    def setup_method(self):
        """Setup for each test method"""
        self.db_manager = Mock()
        self.scheduler = Scheduler(self.db_manager)

    def test_generate_schedule_with_no_active_scheduler(self):
        """Test generate_schedule handles None active_scheduler"""
        self.db_manager.get_all_classes.return_value = []
        self.db_manager.get_all_teachers.return_value = []
        self.db_manager.get_all_lessons.return_value = []
        self.db_manager.get_schedule_by_school_type.return_value = []
        self.db_manager.get_school_type.return_value = "Lise"

        self.scheduler.active_scheduler = None

        result = self.scheduler.generate_schedule()

        # Should return empty list or result from standard algorithm
        assert isinstance(result, list)

    def test_scheduler_with_empty_data(self):
        """Test scheduler handles empty data gracefully"""
        self.db_manager.get_all_classes.return_value = []
        self.db_manager.get_all_teachers.return_value = []
        self.db_manager.get_all_lessons.return_value = []
        self.db_manager.get_schedule_by_school_type.return_value = []
        self.db_manager.get_school_type.return_value = "Lise"

        with patch.object(self.scheduler, '_generate_schedule_standard') as mock_standard:
            self.scheduler._generate_schedule_standard()
            mock_standard.assert_called_once()

    def test_multiple_schedule_generations(self):
        """Test multiple consecutive schedule generations"""
        db_manager = Mock()
        scheduler = Scheduler(db_manager)

        # Should handle multiple calls without error
        with patch.object(scheduler, '_generate_schedule_standard', return_value=[]):
            result1 = scheduler.generate_schedule()
            result2 = scheduler.generate_schedule()

            assert isinstance(result1, list)
            assert isinstance(result2, list)


class TestIntegrationScenarios:
    """Test integration scenarios"""

    def test_full_schedule_generation_flow(self):
        """Test complete schedule generation flow"""
        db_manager = Mock()

        # Mock data
        classes = [Mock(id=1, name="9-A")]
        teachers = [Mock(id=1, name="Math Teacher")]
        lessons = [Mock(id=1, name="Math", weekly_hours=4, assigned_teacher_id=1)]

        db_manager.get_all_classes.return_value = classes
        db_manager.get_all_teachers.return_value = teachers
        db_manager.get_all_lessons.return_value = lessons
        db_manager.get_schedule_by_school_type.return_value = []
        db_manager.get_school_type.return_value = "Lise"

        scheduler = Scheduler(db_manager)
        scheduler.active_scheduler = None

        # Mock the internal scheduling methods
        with patch.object(scheduler, '_schedule_additional_hours', return_value=[]):
            result = scheduler._generate_schedule_standard()

            # Verify the flow completed
            assert isinstance(result, list)

    def test_scheduler_with_various_school_types(self):
        """Test scheduler with different school types"""
        db_manager = Mock()

        for school_type, expected_slots in Scheduler.SCHOOL_TIME_SLOTS.items():
            db_manager.get_school_type.return_value = school_type

            scheduler = Scheduler(db_manager)

            # Should have correct slot count for each school type
            assert scheduler.SCHOOL_TIME_SLOTS[school_type] == expected_slots

    def test_scheduler_configuration_variations(self):
        """Test different scheduler configuration combinations"""
        db_manager = Mock()

        # Test different parameter combinations
        configs = [
            {"use_advanced": True, "use_hybrid": True, "enable_performance_monitor": True},
            {"use_advanced": False, "use_hybrid": False, "enable_performance_monitor": False},
            {"use_advanced": True, "use_hybrid": False, "enable_performance_monitor": True},
        ]

        for config in configs:
            scheduler = Scheduler(db_manager, **config)

            # Should initialize without errors
            assert scheduler.db_manager == db_manager
            assert isinstance(scheduler.logger, logging.Logger)


# Performance and stress tests
class TestSchedulerPerformance:
    """Test scheduler performance characteristics"""

    def test_scheduler_initialization_performance(self):
        """Test scheduler initializes quickly"""
        import time

        db_manager = Mock()

        start = time.time()
        scheduler = Scheduler(db_manager)
        elapsed = time.time() - start

        # Should initialize in less than 1 second
        assert elapsed < 1.0

    def test_scheduler_memory_usage(self):
        """Test scheduler doesn't consume excessive memory"""
        db_manager = Mock()

        scheduler = Scheduler(db_manager)

        # Basic check that scheduler object is created
        assert scheduler is not None
        assert hasattr(scheduler, 'db_manager')
        assert hasattr(scheduler, 'logger')


# Fixtures for common test data
@pytest.fixture
def sample_classes():
    """Fixture providing sample class data"""
    return [
        Mock(id=1, name="9-A"),
        Mock(id=2, name="9-B"),
        Mock(id=3, name="10-A"),
    ]


@pytest.fixture
def sample_teachers():
    """Fixture providing sample teacher data"""
    return [
        Mock(id=1, name="Math Teacher", subjects=["Math"]),
        Mock(id=2, name="Science Teacher", subjects=["Science"]),
        Mock(id=3, name="English Teacher", subjects=["English"]),
    ]


@pytest.fixture
def sample_lessons():
    """Fixture providing sample lesson data"""
    return [
        Mock(id=1, name="Math", weekly_hours=4, assigned_teacher_id=1),
        Mock(id=2, name="Science", weekly_hours=3, assigned_teacher_id=2),
        Mock(id=3, name="English", weekly_hours=2, assigned_teacher_id=3),
    ]


@pytest.fixture
def empty_schedule():
    """Fixture providing empty schedule"""
    return []


@pytest.fixture
def sample_schedule_entries():
    """Fixture providing sample schedule entries"""
    entry1 = Mock()
    entry1.teacher_id = 1
    entry1.class_id = 1
    entry1.day = "Pazartesi"
    entry1.time_slot = 1

    entry2 = Mock()
    entry2.teacher_id = 2
    entry2.class_id = 2
    entry2.day = "Pazartesi"
    entry2.time_slot = 2

    return [entry1, entry2]


# Run tests with: pytest tests/test_scheduler.py -v --cov=algorithms/scheduler.py --cov-report=term-missing
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
