# -*- coding: utf-8 -*-
"""
Unit tests for BacktrackingManager

Tests cover:
- Solution stack operations and restoration
- Backtrack depth limits work correctly  
- Alternative slot generation accuracy
- Constraint ordering and conflict detection
- Slot scoring and optimization
- Randomization functionality
"""

import pytest
from unittest.mock import Mock, patch

from algorithms.backtracking_manager import (
    BacktrackingManager,
    PlacementDecision,
    SolutionState,
    TimeSlotScore,
    ConstraintType
)


class TestBacktrackingManagerInitialization:
    """Test BacktrackingManager initialization"""

    def test_initialization_default(self, db_manager):
        """Test default initialization"""
        manager = BacktrackingManager(db_manager)
        
        assert manager.db_manager == db_manager
        assert manager.max_depth == 10
        assert len(manager.solution_stack) == 0
        assert manager.current_state.depth == 0
        assert manager.randomization_enabled is True
        assert len(manager.constraint_order) == 5

    def test_initialization_custom_depth(self, db_manager):
        """Test initialization with custom max depth"""
        manager = BacktrackingManager(db_manager, max_depth=5)
        
        assert manager.max_depth == 5

    def test_school_config_setup(self, db_manager):
        """Test school configuration setup"""
        with patch.object(db_manager, 'get_school_type', return_value="Lise"):
            manager = BacktrackingManager(db_manager)
            
            assert manager.school_config["school_type"] == "Lise"
            assert manager.school_config["time_slots_count"] == 8
            assert manager.school_config["days_per_week"] == 5

    def test_statistics_initialization(self, db_manager):
        """Test statistics are properly initialized"""
        manager = BacktrackingManager(db_manager)
        
        expected_stats = [
            "total_backtracks",
            "successful_backtracks", 
            "max_depth_reached",
            "alternative_slots_generated",
            "constraint_violations_detected",
            "randomizations_applied"
        ]
        
        for stat in expected_stats:
            assert stat in manager.stats
            assert manager.stats[stat] == 0


class TestSolutionStackOperations:
    """Test solution stack operations and restoration"""

    def test_push_solution_state(self, db_manager):
        """Test pushing solution state onto stack"""
        manager = BacktrackingManager(db_manager)
        
        # Initial state
        assert len(manager.solution_stack) == 0
        assert manager.current_state.depth == 0
        
        # Push state
        manager.push_solution_state()
        
        assert len(manager.solution_stack) == 1
        assert manager.current_state.depth == 1

    def test_pop_solution_state_success(self, db_manager):
        """Test successful pop of solution state"""
        manager = BacktrackingManager(db_manager)
        
        # Push a state first
        manager.current_state.decision_count = 5
        manager.push_solution_state()
        
        # Modify current state
        manager.current_state.decision_count = 10
        
        # Pop state
        success = manager.pop_solution_state()
        
        assert success is True
        assert manager.current_state.decision_count == 5
        assert len(manager.solution_stack) == 0
        assert manager.stats["total_backtracks"] == 1

    def test_pop_solution_state_empty_stack(self, db_manager):
        """Test pop from empty stack"""
        manager = BacktrackingManager(db_manager)
        
        success = manager.pop_solution_state()
        
        assert success is False
        assert manager.stats["total_backtracks"] == 0

    def test_push_beyond_max_depth(self, db_manager):
        """Test pushing beyond maximum depth"""
        manager = BacktrackingManager(db_manager, max_depth=2)
        
        # Push to max depth
        manager.push_solution_state()
        manager.push_solution_state()
        
        assert len(manager.solution_stack) == 2
        
        # Try to push beyond max depth
        manager.push_solution_state()
        
        # Should not exceed max depth
        assert len(manager.solution_stack) == 2

    def test_solution_state_copy(self, db_manager):
        """Test that solution state is properly copied"""
        manager = BacktrackingManager(db_manager)
        
        # Add some data to current state
        manager.current_state.teacher_slots[1] = {(0, 0), (0, 1)}
        manager.current_state.class_slots[1] = {(0, 0)}
        
        # Push state
        manager.push_solution_state()
        
        # Modify current state
        manager.current_state.teacher_slots[1].add((0, 2))
        manager.current_state.class_slots[1].add((0, 1))
        
        # Pop state
        manager.pop_solution_state()
        
        # Should restore original state
        assert manager.current_state.teacher_slots[1] == {(0, 0), (0, 1)}
        assert manager.current_state.class_slots[1] == {(0, 0)}


class TestBacktrackDepthLimits:
    """Test backtrack depth limits work correctly"""

    def test_is_depth_limit_reached_false(self, db_manager):
        """Test depth limit not reached"""
        manager = BacktrackingManager(db_manager, max_depth=5)
        
        # Push some states
        for _ in range(3):
            manager.push_solution_state()
        
        assert manager.is_depth_limit_reached() is False

    def test_is_depth_limit_reached_true(self, db_manager):
        """Test depth limit reached"""
        manager = BacktrackingManager(db_manager, max_depth=3)
        
        # Push to max depth
        for _ in range(3):
            manager.push_solution_state()
        
        assert manager.is_depth_limit_reached() is True

    def test_get_current_depth(self, db_manager):
        """Test getting current depth"""
        manager = BacktrackingManager(db_manager)
        
        assert manager.get_current_depth() == 0
        
        manager.push_solution_state()
        assert manager.get_current_depth() == 1
        
        manager.push_solution_state()
        assert manager.get_current_depth() == 2

    def test_backtrack_respects_depth_limit(self, db_manager):
        """Test that backtrack works correctly with depth limits"""
        manager = BacktrackingManager(db_manager, max_depth=2)
        
        # Fill to max depth
        for _ in range(2):
            manager.push_solution_state()
        
        # Backtrack should succeed - we can backtrack from any depth
        success = manager.backtrack()
        assert success is True  # Can backtrack from max depth
        
        # But cannot push beyond max depth
        manager.push_solution_state()
        manager.push_solution_state()
        assert len(manager.solution_stack) == 2  # Should not exceed max

    def test_max_depth_reached_statistics(self, db_manager):
        """Test max depth reached statistics tracking"""
        manager = BacktrackingManager(db_manager, max_depth=3)
        
        # Push to different depths and pop
        manager.push_solution_state()
        manager.push_solution_state()
        manager.pop_solution_state()  # Depth 1 when popped
        
        manager.push_solution_state()
        manager.push_solution_state()
        manager.push_solution_state()  # This should hit max depth warning
        manager.pop_solution_state()  # Depth 2 when popped
        
        assert manager.stats["max_depth_reached"] == 2


class TestAlternativeSlotGeneration:
    """Test alternative slot generation accuracy"""

    def test_get_alternative_slots_empty_schedule(self, db_manager):
        """Test alternative slot generation with empty schedule"""
        manager = BacktrackingManager(db_manager)
        
        # Mock teacher availability
        with patch.object(manager, '_is_teacher_available', return_value=True):
            slots = manager.get_alternative_slots(
                class_id=1,
                teacher_id=1, 
                lesson_id=1,
                existing_teacher_slots={},
                existing_class_slots={}
            )
        
        # Should have many available slots
        assert len(slots) > 0
        assert all(isinstance(slot, TimeSlotScore) for slot in slots)
        assert manager.stats["alternative_slots_generated"] == 1

    def test_get_alternative_slots_with_conflicts(self, db_manager):
        """Test alternative slot generation with existing conflicts"""
        manager = BacktrackingManager(db_manager)
        
        # Create existing conflicts
        existing_teacher_slots = {1: {(0, 0), (0, 1)}}
        existing_class_slots = {1: {(0, 2), (1, 0)}}
        
        with patch.object(manager, '_is_teacher_available', return_value=True):
            slots = manager.get_alternative_slots(
                class_id=1,
                teacher_id=1,
                lesson_id=1,
                existing_teacher_slots=existing_teacher_slots,
                existing_class_slots=existing_class_slots
            )
        
        # Should exclude conflicted slots
        for slot in slots:
            assert (slot.day, slot.slot) not in existing_teacher_slots[1]
            assert (slot.day, slot.slot) not in existing_class_slots[1]

    def test_slot_scoring_morning_preference(self, db_manager):
        """Test that morning slots get higher scores"""
        manager = BacktrackingManager(db_manager)
        
        # Test morning vs afternoon scoring
        morning_score = manager._calculate_time_preference_score(0)  # First slot
        afternoon_score = manager._calculate_time_preference_score(6)  # Late slot
        
        assert morning_score > afternoon_score

    def test_slot_scoring_continuity_bonus(self, db_manager):
        """Test continuity bonus in slot scoring"""
        manager = BacktrackingManager(db_manager)
        
        existing_teacher_slots = {1: {(0, 0)}}  # Teacher has lesson at day 0, slot 0
        existing_class_slots = {}
        
        # Adjacent slot should get continuity bonus
        adjacent_score = manager._calculate_teacher_schedule_score(
            teacher_id=1, day=0, slot=1, existing_teacher_slots=existing_teacher_slots
        )
        
        # Non-adjacent slot should get lower score
        non_adjacent_score = manager._calculate_teacher_schedule_score(
            teacher_id=1, day=0, slot=3, existing_teacher_slots=existing_teacher_slots
        )
        
        assert adjacent_score > non_adjacent_score

    def test_alternative_slot_strategies(self, db_manager):
        """Test different alternative slot strategies"""
        manager = BacktrackingManager(db_manager)
        
        with patch.object(manager, '_is_teacher_available', return_value=True):
            # Test optimal slots strategy
            optimal_slots = manager._find_optimal_slots(
                class_id=1, teacher_id=1, 
                existing_teacher_slots={}, existing_class_slots={}
            )
            
            # Should find high-scoring morning slots
            assert len(optimal_slots) > 0
            assert all(slot.score >= 10.0 for slot in optimal_slots)

    def test_workload_balanced_slots(self, db_manager):
        """Test workload balanced slot generation"""
        manager = BacktrackingManager(db_manager)
        
        # Teacher already has lessons on day 0
        existing_teacher_slots = {1: {(0, 0), (0, 1), (0, 2)}}
        
        with patch.object(manager, '_is_teacher_available', return_value=True):
            balanced_slots = manager._find_workload_balanced_slots(
                class_id=1, teacher_id=1,
                existing_teacher_slots=existing_teacher_slots,
                existing_class_slots={}
            )
        
        # Should prefer other days
        for slot in balanced_slots:
            assert slot.day != 0  # Should avoid day 0 which is overloaded

    def test_block_formation_scoring(self, db_manager):
        """Test block formation potential scoring"""
        manager = BacktrackingManager(db_manager)
        
        with patch.object(manager, '_is_slot_available_for_block', return_value=True):
            score = manager._calculate_block_formation_score(
                class_id=1, teacher_id=1, day=0, slot=1,
                existing_teacher_slots={}, existing_class_slots={}
            )
            
            # Should get bonus for block formation potential
            assert score > 0


class TestConflictDetection:
    """Test conflict detection functionality"""

    def test_detect_slot_conflicts_no_conflicts(self, db_manager):
        """Test conflict detection with no conflicts"""
        manager = BacktrackingManager(db_manager)
        
        with patch.object(manager, '_is_teacher_available', return_value=True):
            conflicts = manager._detect_slot_conflicts(
                class_id=1, teacher_id=1, day=0, slot=0,
                existing_teacher_slots={}, existing_class_slots={}
            )
        
        assert len(conflicts) == 0

    def test_detect_slot_conflicts_class_conflict(self, db_manager):
        """Test detection of class conflicts"""
        manager = BacktrackingManager(db_manager)
        
        existing_class_slots = {1: {(0, 0)}}
        
        with patch.object(manager, '_is_teacher_available', return_value=True):
            conflicts = manager._detect_slot_conflicts(
                class_id=1, teacher_id=1, day=0, slot=0,
                existing_teacher_slots={}, existing_class_slots=existing_class_slots
            )
        
        assert len(conflicts) > 0
        assert any("Class 1 already has lesson" in conflict for conflict in conflicts)
        assert manager.stats["constraint_violations_detected"] > 0

    def test_detect_slot_conflicts_teacher_conflict(self, db_manager):
        """Test detection of teacher conflicts"""
        manager = BacktrackingManager(db_manager)
        
        existing_teacher_slots = {1: {(0, 0)}}
        
        with patch.object(manager, '_is_teacher_available', return_value=True):
            conflicts = manager._detect_slot_conflicts(
                class_id=1, teacher_id=1, day=0, slot=0,
                existing_teacher_slots=existing_teacher_slots, existing_class_slots={}
            )
        
        assert len(conflicts) > 0
        assert any("Teacher 1 already teaching" in conflict for conflict in conflicts)

    def test_detect_slot_conflicts_availability(self, db_manager):
        """Test detection of availability conflicts"""
        manager = BacktrackingManager(db_manager)
        
        with patch.object(manager, '_is_teacher_available', return_value=False):
            conflicts = manager._detect_slot_conflicts(
                class_id=1, teacher_id=1, day=0, slot=0,
                existing_teacher_slots={}, existing_class_slots={}
            )
        
        assert len(conflicts) > 0
        assert any("not available" in conflict for conflict in conflicts)

    def test_is_teacher_available_database_query(self, db_manager):
        """Test teacher availability database query"""
        manager = BacktrackingManager(db_manager)
        
        # Mock database response
        with patch.object(db_manager, 'get_teacher_availability', return_value=True):
            available = manager._is_teacher_available(1, 0, 0)
            assert available is True
        
        with patch.object(db_manager, 'get_teacher_availability', return_value=None):
            available = manager._is_teacher_available(1, 0, 0)
            assert available is False

    def test_is_teacher_available_error_handling(self, db_manager):
        """Test teacher availability error handling"""
        manager = BacktrackingManager(db_manager)
        
        # Mock database error
        with patch.object(db_manager, 'get_teacher_availability', side_effect=Exception("DB Error")):
            available = manager._is_teacher_available(1, 0, 0)
            # Should default to available on error
            assert available is True


class TestRandomizationFunctionality:
    """Test randomization functionality"""

    def test_apply_randomization_enabled(self, db_manager):
        """Test randomization when enabled"""
        manager = BacktrackingManager(db_manager)
        manager.randomization_enabled = True
        
        # Create test slots
        slots = [
            TimeSlotScore(0, 0, 10.0),
            TimeSlotScore(0, 1, 9.0),
            TimeSlotScore(0, 2, 8.0),
            TimeSlotScore(0, 3, 7.0)
        ]
        
        original_order = [(s.day, s.slot) for s in slots]
        
        # Apply randomization multiple times to check it works
        manager.apply_randomization(slots)
        
        # Order might change (though not guaranteed in single test)
        assert manager.stats["randomizations_applied"] == 1

    def test_apply_randomization_disabled(self, db_manager):
        """Test randomization when disabled"""
        manager = BacktrackingManager(db_manager)
        manager.randomization_enabled = False
        
        slots = [
            TimeSlotScore(0, 0, 10.0),
            TimeSlotScore(0, 1, 9.0)
        ]
        
        original_order = [(s.day, s.slot) for s in slots]
        
        # Apply randomization - should not change anything
        manager.apply_randomization(slots)
        
        # Order should remain the same
        new_order = [(s.day, s.slot) for s in slots]
        assert new_order == original_order
        assert manager.stats["randomizations_applied"] == 0

    def test_apply_randomization_insufficient_slots(self, db_manager):
        """Test randomization with insufficient slots"""
        manager = BacktrackingManager(db_manager)
        
        # Single slot - should not randomize
        slots = [TimeSlotScore(0, 0, 10.0)]
        manager.apply_randomization(slots)
        
        assert manager.stats["randomizations_applied"] == 0

    def test_set_randomization_seed(self, db_manager):
        """Test setting randomization seed"""
        manager = BacktrackingManager(db_manager)
        
        # Set seed
        manager.set_randomization_seed(42)
        assert manager.randomization_seed == 42
        
        # Set to None
        manager.set_randomization_seed(None)
        assert manager.randomization_seed is None

    def test_enable_disable_randomization(self, db_manager):
        """Test enabling/disabling randomization"""
        manager = BacktrackingManager(db_manager)
        
        # Initially enabled
        assert manager.randomization_enabled is True
        
        # Disable
        manager.enable_randomization(False)
        assert manager.randomization_enabled is False
        
        # Enable
        manager.enable_randomization(True)
        assert manager.randomization_enabled is True


class TestTryPlacement:
    """Test try_placement method"""

    def test_try_placement_success(self, db_manager):
        """Test successful lesson placement"""
        manager = BacktrackingManager(db_manager)
        
        with patch.object(manager, 'get_alternative_slots') as mock_get_slots:
            # Mock available slots
            mock_get_slots.return_value = [
                TimeSlotScore(0, 0, 10.0),
                TimeSlotScore(0, 1, 9.0)
            ]
            
            success, placements = manager.try_placement(
                class_id=1, lesson_id=1, teacher_id=1, weekly_hours=2,
                lesson_name="Math", teacher_name="John",
                existing_teacher_slots={}, existing_class_slots={}
            )
        
        assert success is True
        assert len(placements) == 2
        assert all(isinstance(p, PlacementDecision) for p in placements)
        assert manager.stats["successful_backtracks"] == 1

    def test_try_placement_no_slots(self, db_manager):
        """Test placement failure when no slots available"""
        manager = BacktrackingManager(db_manager)
        
        with patch.object(manager, 'get_alternative_slots', return_value=[]):
            success, placements = manager.try_placement(
                class_id=1, lesson_id=1, teacher_id=1, weekly_hours=1,
                lesson_name="Math", teacher_name="John",
                existing_teacher_slots={}, existing_class_slots={}
            )
        
        assert success is False
        assert len(placements) == 0

    def test_try_placement_partial_success(self, db_manager):
        """Test placement with partial success"""
        manager = BacktrackingManager(db_manager)
        
        call_count = 0
        def mock_get_slots(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return [TimeSlotScore(0, 0, 10.0)]  # First hour succeeds
            else:
                return []  # Second hour fails
        
        with patch.object(manager, 'get_alternative_slots', side_effect=mock_get_slots):
            success, placements = manager.try_placement(
                class_id=1, lesson_id=1, teacher_id=1, weekly_hours=2,
                lesson_name="Math", teacher_name="John",
                existing_teacher_slots={}, existing_class_slots={}
            )
        
        assert success is False  # Should fail if can't place all hours
        assert len(placements) == 0  # Should backtrack on failure


class TestStatisticsAndUtilities:
    """Test statistics and utility methods"""

    def test_get_statistics(self, db_manager):
        """Test getting statistics"""
        manager = BacktrackingManager(db_manager)
        
        # Modify some stats
        manager.stats["total_backtracks"] = 5
        manager.stats["successful_backtracks"] = 3
        
        stats = manager.get_statistics()
        
        assert isinstance(stats, dict)
        assert stats["total_backtracks"] == 5
        assert stats["successful_backtracks"] == 3
        
        # Should be a copy, not reference
        stats["total_backtracks"] = 10
        assert manager.stats["total_backtracks"] == 5

    def test_reset_state(self, db_manager):
        """Test resetting manager state"""
        manager = BacktrackingManager(db_manager)
        
        # Add some state
        manager.push_solution_state()
        manager.stats["total_backtracks"] = 5
        manager.current_state.decision_count = 10
        
        # Reset
        manager.reset_state()
        
        assert len(manager.solution_stack) == 0
        assert manager.current_state.decision_count == 0
        assert manager.stats["total_backtracks"] == 0

    def test_placement_decision_get_slot_key(self, db_manager):
        """Test PlacementDecision slot key method"""
        decision = PlacementDecision(
            class_id=1, lesson_id=1, teacher_id=1,
            day=2, time_slot=3, block_position=1, block_id="test"
        )
        
        assert decision.get_slot_key() == (2, 3)

    def test_solution_state_copy_method(self, db_manager):
        """Test SolutionState copy method"""
        state = SolutionState()
        state.teacher_slots[1] = {(0, 0), (0, 1)}
        state.class_slots[1] = {(1, 0)}
        state.depth = 5
        
        copied_state = state.copy()
        
        assert copied_state.depth == 5
        assert copied_state.teacher_slots[1] == {(0, 0), (0, 1)}
        assert copied_state.class_slots[1] == {(1, 0)}
        
        # Modify original - copy should not change
        state.teacher_slots[1].add((0, 2))
        assert (0, 2) not in copied_state.teacher_slots[1]

    def test_time_slot_score_comparison(self, db_manager):
        """Test TimeSlotScore comparison for sorting"""
        slot1 = TimeSlotScore(0, 0, 10.0)
        slot2 = TimeSlotScore(0, 1, 5.0)
        
        # Higher scores should be "less than" for sorting (best first)
        assert slot1 < slot2
        
        slots = [slot2, slot1]
        slots.sort()
        
        assert slots[0].score == 10.0  # Highest score first
        assert slots[1].score == 5.0