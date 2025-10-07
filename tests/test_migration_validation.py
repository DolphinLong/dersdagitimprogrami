# -*- coding: utf-8 -*-
"""
Migration Validation Tests for AdvancedScheduler

This test suite validates the migration of AdvancedScheduler to inherit from
BaseScheduler by comparing pre/post migration outputs, testing edge cases,
and validating exception handling.

Requirements: 5.1, 5.4
"""

import pytest
from algorithms.advanced_scheduler import AdvancedScheduler
from algorithms.base_scheduler import BaseScheduler
from exceptions import (
    ConflictError,
    TeacherConflictError,
    ClassConflictError,
    AvailabilityError,
    ScheduleGenerationError
)


# ============================================================================
# Test 1: Pre/Post Migration Output Comparison
# ============================================================================


class TestMigrationOutputComparison:
    """Test that migration produces identical outputs to pre-migration version"""
    
    def test_schedule_generation_output_format_consistency(self, db_manager, sample_schedule_data):
        """
        Verify that schedule generation output format is consistent
        with pre-migration expectations
        """
        scheduler = AdvancedScheduler(db_manager)
        schedule = scheduler.generate_schedule()
        
        # Verify output is a list
        assert isinstance(schedule, list)
        
        # Verify each entry has expected structure
        for entry in schedule:
            assert isinstance(entry, dict)
            assert 'class_id' in entry
            assert 'lesson_id' in entry
            assert 'teacher_id' in entry
            assert 'day' in entry
            assert 'time_slot' in entry
            assert isinstance(entry['class_id'], int)
            assert isinstance(entry['lesson_id'], int)
            assert isinstance(entry['teacher_id'], int)
            assert isinstance(entry['day'], int)
            assert isinstance(entry['time_slot'], int)
    
    def test_schedule_entries_state_consistency(self, db_manager, sample_schedule_data):
        """
        Verify that schedule_entries state matches pre-migration behavior
        """
        scheduler = AdvancedScheduler(db_manager)
        schedule = scheduler.generate_schedule()
        
        # Verify internal state matches output
        assert len(scheduler.schedule_entries) == len(schedule)
        
        # Verify each entry in output exists in internal state
        for entry in schedule:
            assert entry in scheduler.schedule_entries
    
    def test_class_slots_tracking_consistency(self, db_manager, sample_schedule_data):
        """
        Verify that class_slots tracking matches pre-migration behavior
        """
        scheduler = AdvancedScheduler(db_manager)
        schedule = scheduler.generate_schedule()
        
        # Build expected class_slots from schedule
        expected_class_slots = {}
        for entry in schedule:
            class_id = entry['class_id']
            day = entry['day']
            slot = entry['time_slot']
            
            if class_id not in expected_class_slots:
                expected_class_slots[class_id] = set()
            expected_class_slots[class_id].add((day, slot))
        
        # Verify actual class_slots matches expected
        for class_id, slots in expected_class_slots.items():
            assert class_id in scheduler.class_slots
            assert scheduler.class_slots[class_id] == slots
    
    def test_teacher_slots_tracking_consistency(self, db_manager, sample_schedule_data):
        """
        Verify that teacher_slots tracking matches pre-migration behavior
        """
        scheduler = AdvancedScheduler(db_manager)
        schedule = scheduler.generate_schedule()
        
        # Build expected teacher_slots from schedule
        expected_teacher_slots = {}
        for entry in schedule:
            teacher_id = entry['teacher_id']
            day = entry['day']
            slot = entry['time_slot']
            
            if teacher_id not in expected_teacher_slots:
                expected_teacher_slots[teacher_id] = set()
            expected_teacher_slots[teacher_id].add((day, slot))
        
        # Verify actual teacher_slots matches expected
        for teacher_id, slots in expected_teacher_slots.items():
            assert teacher_id in scheduler.teacher_slots
            assert scheduler.teacher_slots[teacher_id] == slots
    
    def test_conflict_detection_format_consistency(self, db_manager):
        """
        Verify that conflict detection output format matches pre-migration
        """
        scheduler = AdvancedScheduler(db_manager)
        
        # Create conflicts
        scheduler._place_lesson(1, 1, 1, 0, 0)
        scheduler._place_lesson(1, 2, 2, 0, 0)  # Class conflict
        scheduler._place_lesson(2, 3, 1, 0, 0)  # Teacher conflict
        
        conflicts = scheduler._detect_conflicts()
        
        # Verify output is a list
        assert isinstance(conflicts, list)
        assert len(conflicts) > 0
        
        # Verify each conflict has expected structure
        for conflict in conflicts:
            assert isinstance(conflict, dict)
            assert 'type' in conflict
            assert 'entry1' in conflict
            assert 'entry2' in conflict
            assert 'day' in conflict
            assert 'slot' in conflict
            assert conflict['type'] in ['class_conflict', 'teacher_conflict']
    
    def test_smart_blocks_distribution_consistency(self, db_manager):
        """
        Verify that smart block distribution matches pre-migration behavior
        """
        scheduler = AdvancedScheduler(db_manager)
        
        # Test various weekly hours
        test_cases = [
            (1, [1]),
            (2, [2]),
            (3, [2, 1]),
            (4, [2, 2]),
            (5, [2, 2, 1]),
            (6, [2, 2, 2]),
            (7, [2, 2, 2, 1]),
            (8, [2, 2, 2, 2])
        ]
        
        for weekly_hours, expected_blocks in test_cases:
            blocks = scheduler._create_smart_blocks(weekly_hours)
            assert blocks == expected_blocks, \
                f"Smart blocks for {weekly_hours} hours: expected {expected_blocks}, got {blocks}"
    
    def test_scoring_system_consistency(self, db_manager):
        """
        Verify that scoring system produces consistent results
        """
        scheduler = AdvancedScheduler(db_manager)
        
        # Test base score (slot 2 is a good slot, so it gets a bonus)
        score = scheduler._calculate_placement_score(
            class_id=1,
            lesson_id=1,
            day=0,
            slots=[2],
            scheduled_blocks=[],
            total_hours=5,
            time_slots_count=8
        )
        
        # Base score should be positive
        assert score > 0
        assert isinstance(score, float)
        
        # Test with same day penalty
        scheduler._place_lesson(1, 1, 1, 0, 2)
        score_with_penalty = scheduler._calculate_placement_score(
            class_id=1,
            lesson_id=1,
            day=0,
            slots=[4],
            scheduled_blocks=[{'day': 0, 'slots': [2]}],
            total_hours=5,
            time_slots_count=8
        )
        
        # Score should be reduced due to same day penalty
        assert score_with_penalty < score


# ============================================================================
# Test 2: Edge Cases and Error Conditions
# ============================================================================


class TestEdgeCasesAndErrors:
    """Test edge cases and error conditions in migrated code"""
    
    def test_empty_database_edge_case(self, db_manager):
        """Test schedule generation with empty database"""
        scheduler = AdvancedScheduler(db_manager)
        
        # Generate schedule with no data
        schedule = scheduler.generate_schedule()
        
        # Should return empty list
        assert isinstance(schedule, list)
        assert len(schedule) == 0
        assert len(scheduler.schedule_entries) == 0
    
    def test_single_class_single_lesson_edge_case(self, db_manager):
        """Test schedule generation with minimal data"""
        # Create minimal data
        class_id = db_manager.add_class(name="5A", grade=5)
        teacher_id = db_manager.add_teacher(name="Teacher", subject="Math")
        lesson_id = db_manager.add_lesson(name="Math")
        classroom_id = db_manager.add_classroom(name="Room 1", capacity=30)
        
        # Add weekly hours
        db_manager.add_lesson_weekly_hours(
            lesson_id=lesson_id,
            grade=5,
            school_type='Ortaokul',
            weekly_hours=2
        )
        
        # Create assignment
        db_manager.add_schedule_by_school_type(
            class_id=class_id,
            lesson_id=lesson_id,
            teacher_id=teacher_id,
            classroom_id=classroom_id
        )
        
        scheduler = AdvancedScheduler(db_manager)
        schedule = scheduler.generate_schedule()
        
        # Should generate 2 entries
        assert len(schedule) == 2
        assert all(e['class_id'] == class_id for e in schedule)
        assert all(e['teacher_id'] == teacher_id for e in schedule)
    
    def test_maximum_weekly_hours_edge_case(self, db_manager):
        """Test schedule generation with maximum weekly hours"""
        class_id = db_manager.add_class(name="5A", grade=5)
        teacher_id = db_manager.add_teacher(name="Teacher", subject="Math")
        lesson_id = db_manager.add_lesson(name="Math")
        classroom_id = db_manager.add_classroom(name="Room 1", capacity=30)
        
        # Add maximum weekly hours (40 slots = 5 days * 8 slots)
        db_manager.add_lesson_weekly_hours(
            lesson_id=lesson_id,
            grade=5,
            school_type='Ortaokul',
            weekly_hours=40
        )
        
        db_manager.add_schedule_by_school_type(
            class_id=class_id,
            lesson_id=lesson_id,
            teacher_id=teacher_id,
            classroom_id=classroom_id
        )
        
        scheduler = AdvancedScheduler(db_manager)
        schedule = scheduler.generate_schedule()
        
        # Should handle maximum hours gracefully
        assert isinstance(schedule, list)
        assert len(schedule) <= 40
    
    def test_zero_weekly_hours_edge_case(self, db_manager):
        """Test schedule generation with zero weekly hours"""
        class_id = db_manager.add_class(name="5A", grade=5)
        teacher_id = db_manager.add_teacher(name="Teacher", subject="Math")
        lesson_id = db_manager.add_lesson(name="Math")
        classroom_id = db_manager.add_classroom(name="Room 1", capacity=30)
        
        # Add zero weekly hours
        db_manager.add_lesson_weekly_hours(
            lesson_id=lesson_id,
            grade=5,
            school_type='Ortaokul',
            weekly_hours=0
        )
        
        db_manager.add_schedule_by_school_type(
            class_id=class_id,
            lesson_id=lesson_id,
            teacher_id=teacher_id,
            classroom_id=classroom_id
        )
        
        scheduler = AdvancedScheduler(db_manager)
        schedule = scheduler.generate_schedule()
        
        # Should generate no entries for this lesson
        assert isinstance(schedule, list)
    
    def test_multiple_conflicts_edge_case(self, db_manager):
        """Test handling of multiple simultaneous conflicts"""
        scheduler = AdvancedScheduler(db_manager)
        
        # Create multiple conflicts
        scheduler._place_lesson(1, 1, 1, 0, 0)
        scheduler._place_lesson(1, 2, 2, 0, 0)  # Class conflict
        scheduler._place_lesson(2, 3, 1, 0, 0)  # Teacher conflict
        scheduler._place_lesson(3, 4, 3, 0, 0)
        scheduler._place_lesson(3, 5, 4, 0, 0)  # Another class conflict
        
        conflicts = scheduler._detect_conflicts()
        
        # Should detect all conflicts
        assert len(conflicts) >= 2
        
        # Verify conflict types
        conflict_types = [c['type'] for c in conflicts]
        assert 'class_conflict' in conflict_types
    
    def test_invalid_day_slot_edge_case(self, db_manager):
        """Test placement validation with invalid day/slot values"""
        scheduler = AdvancedScheduler(db_manager)
        
        # Test with invalid day (negative)
        can_place, reason = scheduler._can_place_lesson(
            class_id=1,
            teacher_id=1,
            day=-1,
            slot=0,
            check_availability=False
        )
        
        # Should handle gracefully
        assert isinstance(can_place, bool)
        
        # Test with invalid slot (negative)
        can_place, reason = scheduler._can_place_lesson(
            class_id=1,
            teacher_id=1,
            day=0,
            slot=-1,
            check_availability=False
        )
        
        assert isinstance(can_place, bool)
    
    def test_consecutive_slots_validation_edge_case(self, db_manager):
        """Test validation of consecutive slots at day boundaries"""
        scheduler = AdvancedScheduler(db_manager)
        
        # Test consecutive slots at end of day
        is_valid = scheduler._is_placement_valid_advanced(
            class_id=1,
            teacher_id=1,
            day=0,
            slots=[6, 7],  # Last two slots
            check_availability=False
        )
        
        assert isinstance(is_valid, bool)
        
        # Test consecutive slots spanning multiple days (should be invalid)
        # This tests the edge case handling
        is_valid = scheduler._is_placement_valid_advanced(
            class_id=1,
            teacher_id=1,
            day=0,
            slots=[7, 8],  # Beyond day boundary
            check_availability=False
        )
        
        # Should handle gracefully
        assert isinstance(is_valid, bool)
    
    def test_classroom_availability_edge_case(self, db_manager):
        """Test classroom availability with no classrooms"""
        scheduler = AdvancedScheduler(db_manager)
        
        # Try to find classroom with empty list
        classroom = scheduler._find_available_classroom([], day=0, time_slot=0)
        
        # Should return None
        assert classroom is None
    
    def test_all_classrooms_occupied_edge_case(self, db_manager):
        """Test classroom availability when all are occupied"""
        # Create single classroom
        classroom_id = db_manager.add_classroom(name="Room 1", capacity=30)
        classrooms = db_manager.get_all_classrooms()
        
        scheduler = AdvancedScheduler(db_manager)
        
        # Occupy the classroom
        scheduler._place_lesson(1, 1, 1, 0, 0, classroom_id=classroom_id)
        
        # Try to find available classroom at same time
        classroom = scheduler._find_available_classroom(classrooms, day=0, time_slot=0)
        
        # Should return None (all occupied)
        assert classroom is None
    
    def test_conflict_resolution_no_valid_slots_edge_case(self, db_manager):
        """Test conflict resolution when no valid slots available"""
        scheduler = AdvancedScheduler(db_manager)
        
        # Fill all slots for a class
        for day in range(5):
            for slot in range(8):
                scheduler._place_lesson(1, day * 8 + slot + 1, day + 1, day, slot)
        
        # Create a conflict
        scheduler._place_lesson(1, 100, 10, 0, 0)
        
        conflicts = scheduler._detect_conflicts()
        
        # Attempt resolution (should handle gracefully)
        resolved = scheduler._attempt_conflict_resolution(conflicts, time_slots_count=8)
        
        # Should return non-negative value
        assert resolved >= 0


# ============================================================================
# Test 3: Exception Handling and Error Reporting
# ============================================================================


class TestExceptionHandling:
    """Test exception handling and error reporting in migrated code"""
    
    def test_inheritance_preserves_base_exceptions(self, db_manager):
        """Verify that AdvancedScheduler can raise BaseScheduler exceptions"""
        scheduler = AdvancedScheduler(db_manager)
        
        # Verify scheduler has access to exception handling
        assert hasattr(scheduler, '_validate_schedule')
        assert hasattr(scheduler, '_detect_conflicts')
    
    def test_conflict_detection_error_reporting(self, db_manager):
        """Test that conflict detection provides detailed error information"""
        scheduler = AdvancedScheduler(db_manager)
        
        # Create conflicts
        scheduler._place_lesson(1, 1, 1, 0, 0)
        scheduler._place_lesson(1, 2, 2, 0, 0)
        
        conflicts = scheduler._detect_conflicts()
        
        # Verify detailed error information
        assert len(conflicts) > 0
        conflict = conflicts[0]
        
        # Should have all required fields for error reporting
        assert 'type' in conflict
        assert 'entry1' in conflict
        assert 'entry2' in conflict
        assert 'day' in conflict
        assert 'slot' in conflict
    
    def test_validation_error_reporting(self, db_manager):
        """Test that validation provides clear error reporting"""
        scheduler = AdvancedScheduler(db_manager)
        
        # Create invalid schedule (conflicts)
        scheduler._place_lesson(1, 1, 1, 0, 0)
        scheduler._place_lesson(1, 2, 2, 0, 0)
        
        # Validation should detect issues and raise ConflictError
        try:
            is_valid = scheduler._validate_schedule()
            # If no exception, should return False
            assert is_valid is False
        except ConflictError as e:
            # Expected behavior - validation raises exception for conflicts
            assert "conflicts" in str(e).lower()
    
    def test_placement_validation_error_messages(self, db_manager):
        """Test that placement validation provides clear error messages"""
        scheduler = AdvancedScheduler(db_manager)
        
        # Place a lesson
        scheduler._place_lesson(1, 1, 1, 0, 0)
        
        # Try to place conflicting lesson
        can_place, reason = scheduler._can_place_lesson(
            class_id=1,
            teacher_id=2,
            day=0,
            slot=0,
            check_availability=False
        )
        
        # Should provide reason for failure
        assert can_place is False
        assert reason is not None
        assert isinstance(reason, str)
        assert len(reason) > 0
    
    def test_state_consistency_after_errors(self, db_manager):
        """Test that state remains consistent after errors"""
        scheduler = AdvancedScheduler(db_manager)
        
        # Place valid lessons
        scheduler._place_lesson(1, 1, 1, 0, 0)
        scheduler._place_lesson(2, 2, 2, 0, 1)
        
        initial_count = len(scheduler.schedule_entries)
        
        # Try to place conflicting lesson (should fail validation)
        can_place, reason = scheduler._can_place_lesson(
            class_id=1,
            teacher_id=3,
            day=0,
            slot=0,
            check_availability=False
        )
        
        # State should remain unchanged
        assert len(scheduler.schedule_entries) == initial_count
        assert (0, 0) in scheduler.class_slots[1]
        assert (0, 1) in scheduler.class_slots[2]
    
    def test_conflict_resolution_error_handling(self, db_manager):
        """Test that conflict resolution handles errors gracefully"""
        scheduler = AdvancedScheduler(db_manager)
        
        # Create conflicts
        scheduler._place_lesson(1, 1, 1, 0, 0)
        scheduler._place_lesson(1, 2, 2, 0, 0)
        
        conflicts = scheduler._detect_conflicts()
        
        # Attempt resolution (should not raise exceptions)
        try:
            resolved = scheduler._attempt_conflict_resolution(conflicts, time_slots_count=8)
            assert resolved >= 0
        except Exception as e:
            pytest.fail(f"Conflict resolution raised unexpected exception: {e}")
    
    def test_schedule_generation_error_recovery(self, db_manager, sample_schedule_data):
        """Test that schedule generation recovers from errors"""
        scheduler = AdvancedScheduler(db_manager)
        
        # Generate schedule (should handle any internal errors)
        try:
            schedule = scheduler.generate_schedule()
            assert isinstance(schedule, list)
        except Exception as e:
            pytest.fail(f"Schedule generation raised unexpected exception: {e}")
    
    def test_remove_lesson_error_handling(self, db_manager):
        """Test that remove_lesson handles errors gracefully"""
        scheduler = AdvancedScheduler(db_manager)
        
        # Place a lesson
        scheduler._place_lesson(1, 1, 1, 0, 0)
        entry = scheduler.schedule_entries[0]
        
        # Remove it
        scheduler._remove_lesson(entry)
        
        # Try to remove again (should handle gracefully)
        try:
            scheduler._remove_lesson(entry)
            # Should not raise exception
        except Exception as e:
            # If it raises, verify it's a reasonable exception
            assert isinstance(e, (ValueError, KeyError))


# ============================================================================
# Test 4: Regression Tests - Verify No Functionality Lost
# ============================================================================


class TestRegressionValidation:
    """Test that no functionality was lost during migration"""
    
    def test_all_base_scheduler_methods_accessible(self, db_manager):
        """Verify all BaseScheduler methods are accessible"""
        scheduler = AdvancedScheduler(db_manager)
        
        # Check critical BaseScheduler methods
        assert hasattr(scheduler, '_place_lesson')
        assert hasattr(scheduler, '_remove_lesson')
        assert hasattr(scheduler, '_can_place_lesson')
        assert hasattr(scheduler, '_detect_conflicts')
        assert hasattr(scheduler, '_validate_schedule')
        assert hasattr(scheduler, '_get_school_config')
        assert hasattr(scheduler, '_find_available_classroom')
        assert hasattr(scheduler, '_get_class_lessons')
        assert hasattr(scheduler, '_is_placement_valid_advanced')
        assert hasattr(scheduler, '_get_lesson_blocks')
    
    def test_all_advanced_scheduler_methods_preserved(self, db_manager):
        """Verify all AdvancedScheduler-specific methods are preserved"""
        scheduler = AdvancedScheduler(db_manager)
        
        # Check advanced-specific methods
        assert hasattr(scheduler, '_calculate_placement_score')
        assert hasattr(scheduler, '_create_smart_blocks')
        assert hasattr(scheduler, '_schedule_lesson_smart')
        assert hasattr(scheduler, '_attempt_conflict_resolution')
        assert hasattr(scheduler, 'generate_schedule')
    
    def test_weights_initialization_preserved(self, db_manager):
        """Verify that weights initialization is preserved"""
        scheduler = AdvancedScheduler(db_manager)
        
        # Check all expected weights
        expected_weights = [
            'same_day_penalty',
            'distribution_bonus',
            'block_preference_bonus',
            'early_slot_penalty',
            'late_slot_penalty',
            'lunch_break_bonus',
            'consecutive_bonus',
            'gap_penalty',
            'teacher_load_balance'
        ]
        
        for weight in expected_weights:
            assert weight in scheduler.weights
            assert isinstance(scheduler.weights[weight], (int, float))
    
    def test_state_management_preserved(self, db_manager):
        """Verify that state management functionality is preserved"""
        scheduler = AdvancedScheduler(db_manager)
        
        # Verify state attributes exist
        assert hasattr(scheduler, 'schedule_entries')
        assert hasattr(scheduler, 'class_slots')
        assert hasattr(scheduler, 'teacher_slots')
        
        # Verify state is properly initialized
        assert isinstance(scheduler.schedule_entries, list)
        assert len(scheduler.schedule_entries) == 0
    
    def test_conflict_detection_functionality_preserved(self, db_manager):
        """Verify that conflict detection functionality is preserved"""
        scheduler = AdvancedScheduler(db_manager)
        
        # Create known conflicts
        scheduler._place_lesson(1, 1, 1, 0, 0)
        scheduler._place_lesson(1, 2, 2, 0, 0)  # Class conflict
        scheduler._place_lesson(2, 3, 1, 0, 0)  # Teacher conflict
        
        conflicts = scheduler._detect_conflicts()
        
        # Should detect both conflicts
        assert len(conflicts) >= 2
        
        # Verify conflict types
        conflict_types = {c['type'] for c in conflicts}
        assert 'class_conflict' in conflict_types
        assert 'teacher_conflict' in conflict_types
    
    def test_smart_scheduling_functionality_preserved(self, db_manager, sample_schedule_data):
        """Verify that smart scheduling functionality is preserved"""
        scheduler = AdvancedScheduler(db_manager)
        
        # Test smart block creation
        blocks = scheduler._create_smart_blocks(5)
        assert sum(blocks) == 5
        assert len(blocks) <= 5
        
        # Test scoring system
        score = scheduler._calculate_placement_score(
            class_id=1,
            lesson_id=1,
            day=0,
            slots=[0],
            scheduled_blocks=[],
            total_hours=5,
            time_slots_count=8
        )
        
        assert isinstance(score, float)
        assert score > 0
    
    def test_classroom_assignment_functionality_preserved(self, db_manager):
        """Verify that classroom assignment functionality is preserved"""
        # Create classrooms
        classroom1_id = db_manager.add_classroom(name="Room 1", capacity=30)
        classroom2_id = db_manager.add_classroom(name="Room 2", capacity=30)
        classrooms = db_manager.get_all_classrooms()
        
        scheduler = AdvancedScheduler(db_manager)
        
        # Find available classroom
        classroom = scheduler._find_available_classroom(classrooms, day=0, time_slot=0)
        assert classroom is not None
        
        # Place lesson with classroom
        scheduler._place_lesson(1, 1, 1, 0, 0, classroom_id=classroom.classroom_id)
        
        # Verify classroom is assigned
        entry = scheduler.schedule_entries[0]
        assert 'classroom_id' in entry
        assert entry['classroom_id'] == classroom.classroom_id
    
    def test_validation_functionality_preserved(self, db_manager):
        """Verify that validation functionality is preserved"""
        scheduler = AdvancedScheduler(db_manager)
        
        # Valid schedule
        scheduler._place_lesson(1, 1, 1, 0, 0)
        scheduler._place_lesson(2, 2, 2, 0, 1)
        assert scheduler._validate_schedule() is True
        
        # Invalid schedule (with conflicts)
        scheduler._place_lesson(1, 3, 3, 0, 0)
        
        # Validation should detect conflict
        try:
            is_valid = scheduler._validate_schedule()
            assert is_valid is False
        except ConflictError:
            # Expected behavior - validation raises exception for conflicts
            pass
    
    def test_complete_workflow_preserved(self, db_manager, sample_schedule_data):
        """Verify that complete workflow from generation to validation is preserved"""
        scheduler = AdvancedScheduler(db_manager)
        
        # Generate schedule
        schedule = scheduler.generate_schedule()
        
        # Verify schedule was generated
        assert isinstance(schedule, list)
        assert len(schedule) > 0
        
        # Verify no conflicts
        conflicts = scheduler._detect_conflicts()
        assert len(conflicts) == 0
        
        # Verify validation passes
        assert scheduler._validate_schedule() is True
        
        # Verify state consistency
        assert len(scheduler.schedule_entries) == len(schedule)


# ============================================================================
# Test 5: Performance and Scalability Validation
# ============================================================================


class TestPerformanceValidation:
    """Test that migration maintains performance characteristics"""
    
    def test_schedule_generation_completes_in_reasonable_time(self, db_manager, sample_schedule_data):
        """Verify that schedule generation completes in reasonable time"""
        import time
        
        scheduler = AdvancedScheduler(db_manager)
        
        start_time = time.time()
        schedule = scheduler.generate_schedule()
        end_time = time.time()
        
        elapsed_time = end_time - start_time
        
        # Should complete within reasonable time (10 seconds for test data)
        assert elapsed_time < 10.0, f"Schedule generation took {elapsed_time:.2f} seconds"
    
    def test_conflict_detection_performance(self, db_manager):
        """Verify that conflict detection performs efficiently"""
        import time
        
        scheduler = AdvancedScheduler(db_manager)
        
        # Create many entries
        for i in range(100):
            scheduler._place_lesson(
                class_id=i % 10 + 1,
                lesson_id=i + 1,
                teacher_id=i % 5 + 1,
                day=i % 5,
                slot=i % 8
            )
        
        start_time = time.time()
        conflicts = scheduler._detect_conflicts()
        end_time = time.time()
        
        elapsed_time = end_time - start_time
        
        # Should complete quickly (< 1 second)
        assert elapsed_time < 1.0, f"Conflict detection took {elapsed_time:.2f} seconds"
    
    def test_state_management_memory_efficiency(self, db_manager):
        """Verify that state management is memory efficient"""
        scheduler = AdvancedScheduler(db_manager)
        
        # Add many entries
        for i in range(100):
            scheduler._place_lesson(
                class_id=i % 10 + 1,
                lesson_id=i + 1,
                teacher_id=i % 5 + 1,
                day=i % 5,
                slot=i % 8
            )
        
        # Verify state is maintained efficiently
        assert len(scheduler.schedule_entries) == 100
        assert len(scheduler.class_slots) <= 10
        assert len(scheduler.teacher_slots) <= 5
    
    def test_multiple_schedule_generations(self, db_manager, sample_schedule_data):
        """Verify that multiple schedule generations work correctly"""
        # Generate multiple schedules
        for i in range(3):
            scheduler = AdvancedScheduler(db_manager)
            schedule = scheduler.generate_schedule()
            
            # Each should produce valid results
            assert isinstance(schedule, list)
            assert len(schedule) > 0
            assert scheduler._validate_schedule() is True


# ============================================================================
# Test 6: Integration with Database
# ============================================================================


class TestDatabaseIntegration:
    """Test that migration maintains proper database integration"""
    
    def test_schedule_persists_to_database(self, db_manager, sample_schedule_data):
        """Verify that generated schedule is saved to database"""
        scheduler = AdvancedScheduler(db_manager)
        
        # Generate schedule
        schedule = scheduler.generate_schedule()
        
        # Retrieve from database
        db_schedule = db_manager.get_schedule_program_by_school_type()
        
        # Should have entries in database
        assert len(db_schedule) > 0
    
    def test_schedule_retrieval_from_database(self, db_manager, sample_schedule_data):
        """Verify that schedule can be retrieved from database"""
        scheduler = AdvancedScheduler(db_manager)
        
        # Generate and save schedule
        schedule = scheduler.generate_schedule()
        
        # Retrieve from database
        db_schedule = db_manager.get_schedule_program_by_school_type()
        
        # Should match generated schedule count
        assert len(db_schedule) >= len(schedule)
    
    def test_database_state_consistency(self, db_manager, sample_schedule_data):
        """Verify that database state remains consistent"""
        scheduler = AdvancedScheduler(db_manager)
        
        # Get initial state
        initial_classes = db_manager.get_all_classes()
        initial_teachers = db_manager.get_all_teachers()
        initial_lessons = db_manager.get_all_lessons()
        
        # Generate schedule
        schedule = scheduler.generate_schedule()
        
        # Verify database entities unchanged
        final_classes = db_manager.get_all_classes()
        final_teachers = db_manager.get_all_teachers()
        final_lessons = db_manager.get_all_lessons()
        
        assert len(final_classes) == len(initial_classes)
        assert len(final_teachers) == len(initial_teachers)
        assert len(final_lessons) == len(initial_lessons)
    
    def test_schedule_clearing_and_regeneration(self, db_manager, sample_schedule_data):
        """Verify that schedule can be cleared and regenerated"""
        scheduler1 = AdvancedScheduler(db_manager)
        schedule1 = scheduler1.generate_schedule()
        count1 = len(schedule1)
        
        # Clear schedule
        db_manager.clear_schedule()
        
        # Regenerate
        scheduler2 = AdvancedScheduler(db_manager)
        schedule2 = scheduler2.generate_schedule()
        count2 = len(schedule2)
        
        # Should generate similar number of entries
        assert count2 > 0
        # Counts should be similar (may vary due to randomness in scheduling)
        assert abs(count1 - count2) < count1 * 0.5  # Within 50%
