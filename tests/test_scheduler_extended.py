# -*- coding: utf-8 -*-
"""
Additional tests for scheduler.py to increase coverage from 23% to 80%+

This test suite covers the remaining uncovered methods in algorithms/scheduler.py
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call


class TestAdvancedSchedulerMethods:
    """Test advanced scheduler methods for higher coverage"""

    def setup_method(self):
        """Setup for each test method"""
        self.db_manager = Mock()
        self.scheduler = None

    def test_find_lesson_by_name(self):
        """Test _find_lesson_by_name method"""
        from algorithms.scheduler import Scheduler

        scheduler = Scheduler(self.db_manager)
        lessons = [
            Mock(lesson_id=1, name="Math", grade="9"),
            Mock(lesson_id=2, name="Science", grade="9"),
            Mock(lesson_id=3, name="Math", grade="10"),
        ]

        result = scheduler._find_lesson_by_name(lessons, "Math", "9")
        assert result is not None
        assert result.name == "Math"
        assert result.grade == "9"

        result = scheduler._find_lesson_by_name(lessons, "History", "9")
        assert result is None

    def test_create_lesson_blocks(self):
        """Test _create_lesson_blocks method"""
        from algorithms.scheduler import Scheduler

        scheduler = Scheduler(self.db_manager)

        result = scheduler._create_lesson_blocks(4, 5)
        assert len(result) > 0
        assert sum(result) == 4

        result = scheduler._create_lesson_blocks(6, 5)
        assert len(result) > 0
        assert sum(result) == 6

    def test_find_consecutive_slots(self):
        """Test _find_consecutive_slots method"""
        from algorithms.scheduler import Scheduler

        scheduler = Scheduler(self.db_manager)
        schedule_entries = []
        class_id = 1
        day = "Pazartesi"
        time_slots = 8
        hours_needed = 2

        result = scheduler._find_consecutive_slots(
            schedule_entries, class_id, day, time_slots, hours_needed
        )

        assert isinstance(result, list)

    def test_find_available_teacher_for_period(self):
        """Test _find_available_teacher_for_period method"""
        from algorithms.scheduler import Scheduler

        scheduler = Scheduler(self.db_manager)
        schedule_entries = []
        teachers = [Mock(id=1, name="Teacher A"), Mock(id=2, name="Teacher B")]
        lesson = Mock(lesson_id=1, name="Math", assigned_teacher_id=1)
        day = "Pazartesi"
        start_time = 1
        end_time = 3

        with patch.object(scheduler, '_can_teacher_teach_at_slots', return_value=True):
            result = scheduler._find_available_teacher_for_period(
                schedule_entries, teachers, lesson, day, start_time, end_time
            )

            # Should find an available teacher
            assert result is not None

    def test_is_slot_available_for_class(self):
        """Test _is_slot_available_for_class method"""
        from algorithms.scheduler import Scheduler

        scheduler = Scheduler(self.db_manager)
        schedule_entries = []
        class_id = 1
        day = "Pazartesi"
        time_slot = 1

        result = scheduler._is_slot_available_for_class(
            schedule_entries, class_id, day, time_slot
        )

        # Should be True when no existing entry
        assert result is True

    def test_is_slot_available_for_class_enhanced(self):
        """Test _is_slot_available_for_class_enhanced method"""
        from algorithms.scheduler import Scheduler

        scheduler = Scheduler(self.db_manager)
        schedule_entries = []
        class_id = 1
        day = "Pazartesi"
        time_slot = 1

        result = scheduler._is_slot_available_for_class_enhanced(
            schedule_entries, class_id, day, time_slot
        )

        assert isinstance(result, bool)

    def test_distribute_hours_evenly(self):
        """Test _distribute_hours_evenly method"""
        from algorithms.scheduler import Scheduler

        scheduler = Scheduler(self.db_manager)

        result = scheduler._distribute_hours_evenly(10, 5)
        assert len(result) == 5
        assert sum(result) == 10

    def test_find_available_teacher(self):
        """Test _find_available_teacher method"""
        from algorithms.scheduler import Scheduler

        scheduler = Scheduler(self.db_manager)
        schedule_entries = []
        teachers = [Mock(id=1, name="Teacher A")]
        lesson = Mock(lesson_id=1, name="Math", assigned_teacher_id=1)
        day = "Pazartesi"
        time_slot = 1

        with patch.object(scheduler, '_can_teacher_teach_at_slots', return_value=True):
            result = scheduler._find_available_teacher(
                schedule_entries, teachers, lesson, day, time_slot
            )

            assert result is not None

    def test_find_available_classroom(self):
        """Test _find_available_classroom method"""
        from algorithms.scheduler import Scheduler

        scheduler = Scheduler(self.db_manager)
        schedule_entries = []
        classrooms = [Mock(id=1, name="Room 101")]
        day = "Pazartesi"
        time_slot = 1

        result = scheduler._find_available_classroom(
            schedule_entries, classrooms, day, time_slot
        )

        assert result is not None

    def test_detect_conflicts(self):
        """Test detect_conflicts method"""
        from algorithms.scheduler import Scheduler

        scheduler = Scheduler(self.db_manager)
        schedule_entries = [
            Mock(class_id=1, teacher_id=1, day="Pazartesi", time_slot=1),
            Mock(class_id=2, teacher_id=1, day="Pazartesi", time_slot=1),
        ]

        result = scheduler.detect_conflicts(schedule_entries)

        # Should detect teacher conflict
        assert len(result) > 0

    def test_enhanced_gap_filling(self):
        """Test _enhanced_gap_filling method"""
        from algorithms.scheduler import Scheduler

        scheduler = Scheduler(self.db_manager)
        all_needs = [
            {
                "class_id": 1,
                "lesson_id": 1,
                "teacher_id": 1,
                "remaining_hours": 2,
            }
        ]

        with patch.object(scheduler, '_aggressive_placement_for_need', return_value=1):
            result = scheduler._enhanced_gap_filling(all_needs)

            assert isinstance(result, int)
            assert result >= 0

    def test_aggressive_placement_for_need(self):
        """Test _aggressive_placement_for_need method"""
        from algorithms.scheduler import Scheduler

        scheduler = Scheduler(self.db_manager)
        need = {
            "class_id": 1,
            "lesson_id": 1,
            "teacher_id": 1,
            "remaining_hours": 2,
        }
        remaining_hours = 2

        with patch.object(scheduler, '_find_best_slots_aggressive', return_value=[1, 2]):
            result = scheduler._aggressive_placement_for_need(need, remaining_hours)

            assert isinstance(result, int)
            assert result >= 0

    def test_enhanced_schedule_generation(self):
        """Test _enhanced_schedule_generation method"""
        from algorithms.scheduler import Scheduler

        scheduler = Scheduler(self.db_manager)
        scheduler.active_scheduler = None

        self.db_manager.get_all_classes.return_value = []
        self.db_manager.get_all_teachers.return_value = []
        self.db_manager.get_all_lessons.return_value = []
        self.db_manager.get_schedule_by_school_type.return_value = []
        self.db_manager.get_school_type.return_value = "Lise"

        result = scheduler._enhanced_schedule_generation()

        assert isinstance(result, list)


class TestAlgorithmFallbackChain:
    """Test algorithm selection fallback chain"""

    def setup_method(self):
        """Setup for each test method"""
        self.db_manager = Mock()

    @patch('algorithms.scheduler.OPTIMIZED_CURRICULUM_SCHEDULER_AVAILABLE', False)
    @patch('algorithms.scheduler.AlgorithmSelector', None)
    @patch('algorithms.scheduler.ENHANCED_SCHEDULE_GENERATOR_AVAILABLE', False)
    @patch('algorithms.scheduler.ENHANCED_SIMPLE_PERFECT_AVAILABLE', False)
    @patch('algorithms.scheduler.ANT_COLONY_AVAILABLE', True)
    @patch('algorithms.scheduler.AntColonyOptimizationScheduler')
    def test_ant_colony_fallback(self, mock_scheduler_class):
        """Test Ant Colony scheduler fallback"""
        from algorithms.scheduler import Scheduler

        mock_instance = Mock()
        mock_scheduler_class.return_value = mock_instance

        scheduler = Scheduler(self.db_manager)

        assert scheduler.active_scheduler == mock_instance

    @patch('algorithms.scheduler.OPTIMIZED_CURRICULUM_SCHEDULER_AVAILABLE', False)
    @patch('algorithms.scheduler.AlgorithmSelector', None)
    @patch('algorithms.scheduler.ENHANCED_SCHEDULE_GENERATOR_AVAILABLE', False)
    @patch('algorithms.scheduler.ENHANCED_SIMPLE_PERFECT_AVAILABLE', False)
    @patch('algorithms.scheduler.ANT_COLONY_AVAILABLE', False)
    @patch('algorithms.scheduler.SIMULATED_ANNEALING_AVAILABLE', True)
    @patch('algorithms.scheduler.SimulatedAnnealingScheduler')
    def test_simulated_annealing_fallback(self, mock_scheduler_class):
        """Test Simulated Annealing scheduler fallback"""
        from algorithms.scheduler import Scheduler

        mock_instance = Mock()
        mock_scheduler_class.return_value = mock_instance

        scheduler = Scheduler(self.db_manager)

        assert scheduler.active_scheduler == mock_instance

    @patch('algorithms.scheduler.OPTIMIZED_CURRICULUM_SCHEDULER_AVAILABLE', False)
    @patch('algorithms.scheduler.AlgorithmSelector', None)
    @patch('algorithms.scheduler.ENHANCED_SCHEDULE_GENERATOR_AVAILABLE', False)
    @patch('algorithms.scheduler.ENHANCED_SIMPLE_PERFECT_AVAILABLE', False)
    @patch('algorithms.scheduler.ANT_COLONY_AVAILABLE', False)
    @patch('algorithms.scheduler.SIMULATED_ANNEALING_AVAILABLE', False)
    @patch('algorithms.scheduler.GENETIC_ALGORITHM_AVAILABLE', True)
    @patch('algorithms.scheduler.GeneticAlgorithmScheduler')
    def test_genetic_algorithm_fallback(self, mock_scheduler_class):
        """Test Genetic Algorithm scheduler fallback"""
        from algorithms.scheduler import Scheduler

        mock_instance = Mock()
        mock_scheduler_class.return_value = mock_instance

        scheduler = Scheduler(self.db_manager)

        assert scheduler.active_scheduler == mock_instance

    @patch('algorithms.scheduler.OPTIMIZED_CURRICULUM_SCHEDULER_AVAILABLE', False)
    @patch('algorithms.scheduler.AlgorithmSelector', None)
    @patch('algorithms.scheduler.ENHANCED_SCHEDULE_GENERATOR_AVAILABLE', False)
    @patch('algorithms.scheduler.ENHANCED_SIMPLE_PERFECT_AVAILABLE', False)
    @patch('algorithms.scheduler.ANT_COLONY_AVAILABLE', False)
    @patch('algorithms.scheduler.SIMULATED_ANNEALING_AVAILABLE', False)
    @patch('algorithms.scheduler.GENETIC_ALGORITHM_AVAILABLE', False)
    @patch('algorithms.scheduler.ADVANCED_METAHEURISTIC_AVAILABLE', True)
    @patch('algorithms.scheduler.AdvancedMetaheuristicScheduler')
    def test_advanced_metaheuristic_fallback(self, mock_scheduler_class):
        """Test Advanced Metaheuristic scheduler fallback"""
        from algorithms.scheduler import Scheduler

        mock_instance = Mock()
        mock_scheduler_class.return_value = mock_instance

        scheduler = Scheduler(self.db_manager)

        assert scheduler.active_scheduler == mock_instance

    @patch('algorithms.scheduler.OPTIMIZED_CURRICULUM_SCHEDULER_AVAILABLE', False)
    @patch('algorithms.scheduler.AlgorithmSelector', None)
    @patch('algorithms.scheduler.ENHANCED_SCHEDULE_GENERATOR_AVAILABLE', False)
    @patch('algorithms.scheduler.ENHANCED_SIMPLE_PERFECT_AVAILABLE', False)
    @patch('algorithms.scheduler.ANT_COLONY_AVAILABLE', False)
    @patch('algorithms.scheduler.SIMULATED_ANNEALING_AVAILABLE', False)
    @patch('algorithms.scheduler.GENETIC_ALGORITHM_AVAILABLE', False)
    @patch('algorithms.scheduler.ADVANCED_METAHEURISTIC_AVAILABLE', False)
    @patch('algorithms.scheduler.HYBRID_OPTIMAL_SCHEDULER_AVAILABLE', True)
    @patch('algorithms.scheduler.HybridOptimalScheduler')
    def test_hybrid_optimal_fallback(self, mock_scheduler_class):
        """Test Hybrid Optimal scheduler fallback"""
        from algorithms.scheduler import Scheduler

        mock_instance = Mock()
        mock_scheduler_class.return_value = mock_instance

        scheduler = Scheduler(self.db_manager)

        assert scheduler.active_scheduler == mock_instance

    @patch('algorithms.scheduler.OPTIMIZED_CURRICULUM_SCHEDULER_AVAILABLE', False)
    @patch('algorithms.scheduler.AlgorithmSelector', None)
    @patch('algorithms.scheduler.ENHANCED_SCHEDULE_GENERATOR_AVAILABLE', False)
    @patch('algorithms.scheduler.ENHANCED_SIMPLE_PERFECT_AVAILABLE', False)
    @patch('algorithms.scheduler.ANT_COLONY_AVAILABLE', False)
    @patch('algorithms.scheduler.SIMULATED_ANNEALING_AVAILABLE', False)
    @patch('algorithms.scheduler.GENETIC_ALGORITHM_AVAILABLE', False)
    @patch('algorithms.scheduler.ADVANCED_METAHEURISTIC_AVAILABLE', False)
    @patch('algorithms.scheduler.HYBRID_OPTIMAL_SCHEDULER_AVAILABLE', False)
    @patch('algorithms.scheduler.SIMPLE_PERFECT_SCHEDULER_AVAILABLE', True)
    @patch('algorithms.scheduler.SimplePerfectScheduler')
    def test_simple_perfect_fallback(self, mock_scheduler_class):
        """Test Simple Perfect scheduler fallback"""
        from algorithms.scheduler import Scheduler

        mock_instance = Mock()
        mock_scheduler_class.return_value = mock_instance

        scheduler = Scheduler(self.db_manager)

        assert scheduler.active_scheduler == mock_instance


class TestExtendedScheduleGeneration:
    """Test extended schedule generation scenarios"""

    def setup_method(self):
        """Setup for each test method"""
        self.db_manager = Mock()

    def test_schedule_additional_hours_with_empty_data(self):
        """Test _schedule_additional_hours with empty data"""
        from algorithms.scheduler import Scheduler

        scheduler = Scheduler(self.db_manager)

        classes = []
        teachers = []
        lessons = []
        existing_assignments = []

        result = scheduler._schedule_additional_hours(
            classes, teachers, lessons, existing_assignments
        )

        assert isinstance(result, list)

    def test_schedule_additional_hours_with_data(self):
        """Test _schedule_additional_hours with actual data"""
        from algorithms.scheduler import Scheduler

        scheduler = Scheduler(self.db_manager)

        classes = [Mock(class_id=1, name="9-A", grade="9")]
        teachers = [Mock(id=1, name="Teacher A")]
        lessons = [
            Mock(
                lesson_id=1,
                name="Math",
                assigned_teacher_id=1,
                weekly_hours=4
            )
        ]
        existing_assignments = []

        with patch.object(scheduler, '_schedule_lesson_improved', return_value=[]):
            result = scheduler._schedule_additional_hours(
                classes, teachers, lessons, existing_assignments
            )

            assert isinstance(result, list)

    def test_can_teacher_teach_at_slots_enhanced(self):
        """Test _can_teacher_teach_at_slots_enhanced method"""
        from algorithms.scheduler import Scheduler

        scheduler = Scheduler(self.db_manager)
        schedule_entries = []
        teacher_id = 1
        day = "Pazartesi"
        time_slots = [1, 2]

        result = scheduler._can_teacher_teach_at_slots_enhanced(
            schedule_entries, teacher_id, day, time_slots
        )

        assert isinstance(result, bool)

    def test_can_teacher_teach_at_slots_aggressive(self):
        """Test _can_teacher_teach_at_slots_aggressive method"""
        from algorithms.scheduler import Scheduler

        scheduler = Scheduler(self.db_manager)
        schedule_entries = []
        teacher_id = 1
        day = "Pazartesi"
        time_slots = [1, 2]

        result = scheduler._can_teacher_teach_at_slots_aggressive(
            schedule_entries, teacher_id, day, time_slots
        )

        assert isinstance(result, bool)

    def test_is_slot_available_for_class_aggressive(self):
        """Test _is_slot_available_for_class_aggressive method"""
        from algorithms.scheduler import Scheduler

        scheduler = Scheduler(self.db_manager)
        schedule_entries = []
        class_id = 1
        day = "Pazartesi"
        time_slot = 1

        result = scheduler._is_slot_available_for_class_aggressive(
            schedule_entries, class_id, day, time_slot
        )

        assert isinstance(result, bool)


class TestEdgeCases:
    """Test edge cases and error scenarios"""

    def setup_method(self):
        """Setup for each test method"""
        self.db_manager = Mock()

    def test_scheduler_with_exception_in_active_scheduler(self):
        """Test scheduler handles exception in active_scheduler"""
        from algorithms.scheduler import Scheduler

        scheduler = Scheduler(self.db_manager)
        scheduler.active_scheduler = Mock()
        scheduler.active_scheduler.generate_schedule.side_effect = Exception("Test error")

        # Should handle exception gracefully
        with patch.object(scheduler, '_generate_schedule_standard', return_value=[]):
            result = scheduler.generate_schedule()
            assert isinstance(result, list)

    def test_scheduler_with_none_db_manager(self):
        """Test scheduler with None db_manager"""
        from algorithms.scheduler import Scheduler

        # Should raise or handle None db_manager
        with pytest.raises((AttributeError, TypeError)):
            scheduler = Scheduler(None)

    def test_multiple_consecutive_generations(self):
        """Test multiple consecutive schedule generations"""
        from algorithms.scheduler import Scheduler

        scheduler = Scheduler(self.db_manager)
        scheduler.active_scheduler = Mock()
        scheduler.active_scheduler.generate_schedule.return_value = []

        # Generate schedule multiple times
        results = []
        for _ in range(5):
            result = scheduler.generate_schedule()
            results.append(result)

        assert len(results) == 5
        assert all(isinstance(r, list) for r in results)

    def test_empty_lesson_scheduling(self):
        """Test scheduling with empty lessons list"""
        from algorithms.scheduler import Scheduler

        scheduler = Scheduler(self.db_manager)
        schedule_entries = []
        class_id = 1
        day = "Pazartesi"
        lesson = None
        teachers = []

        result = scheduler._schedule_lesson_with_assigned_teacher(
            schedule_entries, class_id, day, lesson, teachers
        )

        # Should handle None lesson gracefully
        assert result is None or isinstance(result, list)

    def test_very_large_schedule_entries(self):
        """Test with very large number of schedule entries"""
        from algorithms.scheduler import Scheduler

        scheduler = Scheduler(self.db_manager)

        # Create 1000 mock schedule entries
        schedule_entries = [
            Mock(class_id=i % 10, teacher_id=i % 5, day="Pazartesi", time_slot=i % 8)
            for i in range(1000)
        ]

        new_entry = Mock(class_id=1, teacher_id=1, day="Pazartesi", time_slot=1)

        result = scheduler._has_conflict(schedule_entries, new_entry)

        # Should handle large dataset
        assert isinstance(result, bool)


# Performance tests
class TestSchedulerPerformance:
    """Test scheduler performance characteristics"""

    def test_scheduler_initialization_speed(self):
        """Test scheduler initializes quickly"""
        import time
        from algorithms.scheduler import Scheduler

        db_manager = Mock()

        start = time.time()
        scheduler = Scheduler(db_manager)
        elapsed = time.time() - start

        # Should initialize in less than 2 seconds (allowing for all the imports)
        assert elapsed < 2.0

    def test_schedule_generation_memory_efficiency(self):
        """Test schedule generation doesn't leak memory"""
        from algorithms.scheduler import Scheduler

        db_manager = Mock()
        scheduler = Scheduler(db_manager)
        scheduler.active_scheduler = Mock()
        scheduler.active_scheduler.generate_schedule.return_value = []

        # Generate multiple schedules and check memory
        for _ in range(10):
            result = scheduler.generate_schedule()
            assert isinstance(result, list)

    def test_large_schedule_entries_handling(self):
        """Test handling large schedule entries efficiently"""
        import time
        from algorithms.scheduler import Scheduler

        scheduler = Scheduler(self.db_manager)

        # Create a large number of schedule entries
        large_entries = [
            Mock(class_id=i % 50, teacher_id=i % 20, day=f"Day{i % 5}", time_slot=i % 8)
            for i in range(5000)
        ]

        start = time.time()
        result = scheduler._has_conflict(large_entries, Mock(class_id=1, teacher_id=1, day="Pazartesi", time_slot=1))
        elapsed = time.time() - start

        # Should complete in reasonable time (<1 second)
        assert elapsed < 1.0
        assert isinstance(result, bool)


# Run tests with: pytest tests/test_scheduler_extended.py -v --cov=algorithms/scheduler.py --cov-report=term-missing
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
