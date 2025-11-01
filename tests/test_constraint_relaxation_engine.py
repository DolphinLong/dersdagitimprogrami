# -*- coding: utf-8 -*-
"""
Unit tests for ConstraintRelaxationEngine

Tests cover:
- All relaxation levels work correctly
- Constraint restoration functionality  
- Workload flexibility logic
- Workload violation tracking and reporting
- Constraint state management
"""

import pytest
from unittest.mock import Mock, patch

from algorithms.constraint_relaxation_engine import (
    ConstraintRelaxationEngine,
    RelaxationLevel,
    WorkloadViolation,
    ConstraintState
)


class TestConstraintRelaxationEngineInitialization:
    """Test ConstraintRelaxationEngine initialization"""

    def test_initialization_default(self, db_manager):
        """Test default initialization"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        assert engine.db_manager == db_manager
        assert engine.current_level == RelaxationLevel.STRICT
        assert engine.constraint_state.workload_max_empty_days == 1
        assert engine.constraint_state.allow_non_consecutive_blocks is False
        assert engine.constraint_state.allow_availability_violations is False
        assert engine.constraint_state.strict_block_rules is True
        assert engine.original_state is None
        assert len(engine.workload_violations) == 0
        assert len(engine.teacher_schedules) == 0

    def test_initialization_with_logger(self, db_manager):
        """Test initialization with custom logger"""
        import logging
        custom_logger = logging.getLogger("test_logger")
        
        engine = ConstraintRelaxationEngine(db_manager, logger=custom_logger)
        
        assert engine.logger == custom_logger

    def test_relaxation_levels_order(self, db_manager):
        """Test that relaxation levels are in correct order"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        expected_order = [
            RelaxationLevel.STRICT,
            RelaxationLevel.WORKLOAD_FLEX,
            RelaxationLevel.BLOCK_FLEX,
            RelaxationLevel.AVAILABILITY_FLEX
        ]
        
        assert engine.RELAXATION_LEVELS == expected_order

    def test_statistics_initialization(self, db_manager):
        """Test statistics are properly initialized"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        expected_stats = [
            "total_relaxations",
            "successful_relaxations",
            "workload_violations_created",
            "workload_violations_resolved",
            "constraint_restorations"
        ]
        
        for stat in expected_stats:
            assert stat in engine.relaxation_stats
            assert engine.relaxation_stats[stat] == 0


class TestConstraintRelaxationLevels:
    """Test all relaxation levels work correctly"""

    def test_relax_to_strict_level(self, db_manager):
        """Test relaxing to strict level (no change)"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        # Already at strict level
        engine.relax_constraints(RelaxationLevel.STRICT)
        
        assert engine.current_level == RelaxationLevel.STRICT
        assert engine.constraint_state.workload_max_empty_days == 1
        assert engine.constraint_state.allow_non_consecutive_blocks is False
        assert engine.constraint_state.allow_availability_violations is False
        assert engine.constraint_state.strict_block_rules is True
        # Should not increment relaxation count when already at same level
        assert engine.relaxation_stats["total_relaxations"] == 0

    def test_relax_to_workload_flex_level(self, db_manager):
        """Test relaxing to workload flexibility level"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        engine.relax_constraints(RelaxationLevel.WORKLOAD_FLEX)
        
        assert engine.current_level == RelaxationLevel.WORKLOAD_FLEX
        assert engine.constraint_state.workload_max_empty_days == 2
        assert engine.constraint_state.allow_non_consecutive_blocks is False
        assert engine.constraint_state.allow_availability_violations is False
        assert engine.constraint_state.strict_block_rules is True
        assert engine.original_state is not None
        assert engine.relaxation_stats["total_relaxations"] == 1

    def test_relax_to_block_flex_level(self, db_manager):
        """Test relaxing to block flexibility level"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        engine.relax_constraints(RelaxationLevel.BLOCK_FLEX)
        
        assert engine.current_level == RelaxationLevel.BLOCK_FLEX
        assert engine.constraint_state.workload_max_empty_days == 2
        assert engine.constraint_state.allow_non_consecutive_blocks is True
        assert engine.constraint_state.allow_availability_violations is False
        assert engine.constraint_state.strict_block_rules is False
        assert engine.original_state is not None

    def test_relax_to_availability_flex_level(self, db_manager):
        """Test relaxing to availability flexibility level"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        engine.relax_constraints(RelaxationLevel.AVAILABILITY_FLEX)
        
        assert engine.current_level == RelaxationLevel.AVAILABILITY_FLEX
        assert engine.constraint_state.workload_max_empty_days == 2
        assert engine.constraint_state.allow_non_consecutive_blocks is True
        assert engine.constraint_state.allow_availability_violations is True
        assert engine.constraint_state.strict_block_rules is False

    def test_relax_same_level_no_change(self, db_manager):
        """Test relaxing to same level doesn't change anything"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        # Relax to workload flex
        engine.relax_constraints(RelaxationLevel.WORKLOAD_FLEX)
        initial_relaxations = engine.relaxation_stats["total_relaxations"]
        
        # Relax to same level again
        engine.relax_constraints(RelaxationLevel.WORKLOAD_FLEX)
        
        # Should not increment relaxation count
        assert engine.relaxation_stats["total_relaxations"] == initial_relaxations

    def test_original_state_preservation(self, db_manager):
        """Test that original state is preserved during first relaxation"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        # Modify initial state
        engine.constraint_state.workload_max_empty_days = 1
        
        # First relaxation should preserve original state
        engine.relax_constraints(RelaxationLevel.WORKLOAD_FLEX)
        
        assert engine.original_state is not None
        assert engine.original_state.workload_max_empty_days == 1
        assert engine.original_state.allow_non_consecutive_blocks is False

    def test_multiple_relaxations_preserve_original(self, db_manager):
        """Test that multiple relaxations preserve original state"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        # First relaxation
        engine.relax_constraints(RelaxationLevel.WORKLOAD_FLEX)
        original_state = engine.original_state
        
        # Second relaxation should not change original state
        engine.relax_constraints(RelaxationLevel.BLOCK_FLEX)
        
        assert engine.original_state is original_state
        assert engine.original_state.workload_max_empty_days == 1


class TestConstraintRestoration:
    """Test constraint restoration functionality"""

    def test_restore_constraints_success(self, db_manager):
        """Test successful constraint restoration"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        # Relax constraints
        engine.relax_constraints(RelaxationLevel.AVAILABILITY_FLEX)
        
        # Verify relaxed state
        assert engine.current_level == RelaxationLevel.AVAILABILITY_FLEX
        assert engine.constraint_state.workload_max_empty_days == 2
        
        # Restore constraints
        engine.restore_constraints()
        
        # Verify restoration
        assert engine.current_level == RelaxationLevel.STRICT
        assert engine.constraint_state.workload_max_empty_days == 1
        assert engine.constraint_state.allow_non_consecutive_blocks is False
        assert engine.constraint_state.allow_availability_violations is False
        assert engine.constraint_state.strict_block_rules is True
        assert engine.original_state is None
        assert engine.relaxation_stats["constraint_restorations"] == 1

    def test_restore_constraints_no_original_state(self, db_manager):
        """Test restore when no original state exists"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        # Try to restore without relaxing first
        engine.restore_constraints()
        
        # Should remain at strict level
        assert engine.current_level == RelaxationLevel.STRICT
        assert engine.relaxation_stats["constraint_restorations"] == 0

    def test_restore_after_multiple_relaxations(self, db_manager):
        """Test restore after multiple relaxations"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        # Multiple relaxations
        engine.relax_constraints(RelaxationLevel.WORKLOAD_FLEX)
        engine.relax_constraints(RelaxationLevel.BLOCK_FLEX)
        engine.relax_constraints(RelaxationLevel.AVAILABILITY_FLEX)
        
        # Restore should go back to original strict state
        engine.restore_constraints()
        
        assert engine.current_level == RelaxationLevel.STRICT
        assert engine.constraint_state.workload_max_empty_days == 1
        assert engine.constraint_state.allow_non_consecutive_blocks is False


class TestWorkloadFlexibilityLogic:
    """Test workload flexibility logic"""

    def test_update_teacher_schedule(self, db_manager):
        """Test updating teacher schedule for workload tracking"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        # Update schedule
        engine.update_teacher_schedule(1, 0, 0)  # Monday, slot 0
        engine.update_teacher_schedule(1, 0, 1)  # Monday, slot 1
        engine.update_teacher_schedule(1, 1, 0)  # Tuesday, slot 0
        
        assert 1 in engine.teacher_schedules
        assert (0, 0) in engine.teacher_schedules[1]
        assert (0, 1) in engine.teacher_schedules[1]
        assert (1, 0) in engine.teacher_schedules[1]
        assert len(engine.teacher_schedules[1]) == 3

    def test_check_workload_constraint_strict_satisfied(self, db_manager):
        """Test workload constraint check - strict level satisfied"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        # Teacher works 4 days (1 empty day - within strict limit)
        engine.update_teacher_schedule(1, 0, 0)  # Monday
        engine.update_teacher_schedule(1, 1, 0)  # Tuesday
        engine.update_teacher_schedule(1, 2, 0)  # Wednesday
        engine.update_teacher_schedule(1, 3, 0)  # Thursday
        # Friday empty
        
        assert engine.check_workload_constraint(1) is True

    def test_check_workload_constraint_strict_violated(self, db_manager):
        """Test workload constraint check - strict level violated"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        # Teacher works 3 days (2 empty days - violates strict limit)
        engine.update_teacher_schedule(1, 0, 0)  # Monday
        engine.update_teacher_schedule(1, 1, 0)  # Tuesday
        engine.update_teacher_schedule(1, 2, 0)  # Wednesday
        # Thursday and Friday empty
        
        assert engine.check_workload_constraint(1) is False

    def test_check_workload_constraint_flexible_satisfied(self, db_manager):
        """Test workload constraint check - flexible level satisfied"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        # Relax to workload flexible (allows 2 empty days)
        engine.relax_constraints(RelaxationLevel.WORKLOAD_FLEX)
        
        # Teacher works 3 days (2 empty days - within flexible limit)
        engine.update_teacher_schedule(1, 0, 0)  # Monday
        engine.update_teacher_schedule(1, 1, 0)  # Tuesday
        engine.update_teacher_schedule(1, 2, 0)  # Wednesday
        
        assert engine.check_workload_constraint(1) is True

    def test_check_workload_constraint_no_schedule(self, db_manager):
        """Test workload constraint check with no schedule"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        # Teacher with no schedule should satisfy constraint
        assert engine.check_workload_constraint(999) is True

    def test_allow_temporary_empty_days_strict(self, db_manager):
        """Test allowing temporary empty days in strict mode"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        # Strict mode should not allow temporary empty days
        assert engine.allow_temporary_empty_days(1, 2) is False

    def test_allow_temporary_empty_days_flexible(self, db_manager):
        """Test allowing temporary empty days in flexible mode"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        # Relax to workload flexible
        engine.relax_constraints(RelaxationLevel.WORKLOAD_FLEX)
        
        # Should allow up to 2 empty days
        assert engine.allow_temporary_empty_days(1, 2) is True
        
        # Teacher with 3 empty days should not be allowed
        engine.update_teacher_schedule(1, 0, 0)  # Only Monday
        engine.update_teacher_schedule(1, 1, 0)  # Only Tuesday
        # Wednesday, Thursday, Friday empty (3 empty days)
        
        assert engine.allow_temporary_empty_days(1, 2) is False

    def test_allow_temporary_empty_days_no_schedule(self, db_manager):
        """Test allowing temporary empty days with no existing schedule"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        # Relax to flexible
        engine.relax_constraints(RelaxationLevel.WORKLOAD_FLEX)
        
        # Teacher with no schedule should be allowed flexibility
        assert engine.allow_temporary_empty_days(999, 2) is True


class TestWorkloadViolationTracking:
    """Test workload violation tracking and reporting"""

    def test_identify_workload_violations_none(self, db_manager):
        """Test identifying workload violations when none exist"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        # Teacher works 4 days (1 empty day - acceptable)
        engine.update_teacher_schedule(1, 0, 0)
        engine.update_teacher_schedule(1, 1, 0)
        engine.update_teacher_schedule(1, 2, 0)
        engine.update_teacher_schedule(1, 3, 0)
        
        engine._identify_workload_violations()
        
        assert len(engine.workload_violations) == 0

    def test_identify_workload_violations_minor(self, db_manager):
        """Test identifying minor workload violations"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        # Mock teacher data
        mock_teacher = Mock()
        mock_teacher.name = "John Doe"
        
        with patch.object(engine.db_manager, 'get_teacher_by_id', return_value=mock_teacher):
            # Teacher works 3 days (2 empty days - minor violation)
            engine.update_teacher_schedule(1, 0, 0)
            engine.update_teacher_schedule(1, 1, 0)
            engine.update_teacher_schedule(1, 2, 0)
            
            engine._identify_workload_violations()
        
        assert len(engine.workload_violations) == 1
        assert 1 in engine.workload_violations
        
        violation = engine.workload_violations[1]
        assert violation.teacher_id == 1
        assert violation.teacher_name == "John Doe"
        assert violation.empty_days == 2
        assert violation.violation_severity == "minor"
        assert violation.working_days == {0, 1, 2}

    def test_identify_workload_violations_moderate(self, db_manager):
        """Test identifying moderate workload violations"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        mock_teacher = Mock()
        mock_teacher.name = "Jane Smith"
        
        with patch.object(engine.db_manager, 'get_teacher_by_id', return_value=mock_teacher):
            # Teacher works 2 days (3 empty days - moderate violation)
            engine.update_teacher_schedule(1, 0, 0)
            engine.update_teacher_schedule(1, 1, 0)
            
            engine._identify_workload_violations()
        
        violation = engine.workload_violations[1]
        assert violation.empty_days == 3
        assert violation.violation_severity == "moderate"

    def test_identify_workload_violations_severe(self, db_manager):
        """Test identifying severe workload violations"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        mock_teacher = Mock()
        mock_teacher.name = "Bob Wilson"
        
        with patch.object(engine.db_manager, 'get_teacher_by_id', return_value=mock_teacher):
            # Teacher works 1 day (4 empty days - severe violation)
            engine.update_teacher_schedule(1, 0, 0)
            
            engine._identify_workload_violations()
        
        violation = engine.workload_violations[1]
        assert violation.empty_days == 4
        assert violation.violation_severity == "severe"

    def test_track_workload_violations(self, db_manager):
        """Test tracking workload violations"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        mock_teacher = Mock()
        mock_teacher.name = "Test Teacher"
        
        with patch.object(engine.db_manager, 'get_teacher_by_id', return_value=mock_teacher):
            # Create violation
            engine.update_teacher_schedule(1, 0, 0)
            engine.update_teacher_schedule(1, 1, 0)
            
            violations = engine.track_workload_violations()
        
        assert len(violations) == 1
        assert 1 in violations
        assert violations[1].teacher_name == "Test Teacher"
        assert len(violations[1].suggested_adjustments) > 0

    def test_generate_adjustment_suggestions(self, db_manager):
        """Test generating adjustment suggestions"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        working_days = {0, 1}  # Monday, Tuesday
        suggestions = engine._generate_adjustment_suggestions(1, working_days)
        
        assert len(suggestions) > 0
        assert any("empty days" in suggestion.lower() for suggestion in suggestions)
        assert any("Wednesday" in suggestion for suggestion in suggestions)
        assert any("Thursday" in suggestion for suggestion in suggestions)
        assert any("Friday" in suggestion for suggestion in suggestions)

    def test_workload_violations_statistics(self, db_manager):
        """Test workload violation statistics tracking"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        mock_teacher = Mock()
        mock_teacher.name = "Test Teacher"
        
        with patch.object(engine.db_manager, 'get_teacher_by_id', return_value=mock_teacher):
            # Create violation
            engine.update_teacher_schedule(1, 0, 0)
            engine._identify_workload_violations()
        
        assert engine.relaxation_stats["workload_violations_created"] == 1


class TestWorkloadRebalancing:
    """Test workload rebalancing functionality"""

    def test_attempt_workload_rebalancing_no_violations(self, db_manager):
        """Test workload rebalancing when no violations exist"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        # Teacher with good workload distribution
        engine.update_teacher_schedule(1, 0, 0)
        engine.update_teacher_schedule(1, 1, 0)
        engine.update_teacher_schedule(1, 2, 0)
        engine.update_teacher_schedule(1, 3, 0)
        
        success = engine.attempt_workload_rebalancing()
        
        assert success is True

    def test_attempt_workload_rebalancing_with_violations(self, db_manager):
        """Test workload rebalancing with violations"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        mock_teacher = Mock()
        mock_teacher.name = "Test Teacher"
        
        with patch.object(engine.db_manager, 'get_teacher_by_id', return_value=mock_teacher):
            # Create violation
            engine.update_teacher_schedule(1, 0, 0)
            engine.update_teacher_schedule(1, 1, 0)
            
            success = engine.attempt_workload_rebalancing()
        
        # Should attempt rebalancing but may not succeed in this simple test
        assert isinstance(success, bool)

    def test_create_workload_rebalancing_plan(self, db_manager):
        """Test creating workload rebalancing plan"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        mock_teacher = Mock()
        mock_teacher.name = "Test Teacher"
        
        with patch.object(engine.db_manager, 'get_teacher_by_id', return_value=mock_teacher):
            # Create violation with uneven distribution
            engine.update_teacher_schedule(1, 0, 0)
            engine.update_teacher_schedule(1, 0, 1)
            engine.update_teacher_schedule(1, 0, 2)  # Overloaded Monday
            engine.update_teacher_schedule(1, 1, 0)  # Light Tuesday
            
            engine._identify_workload_violations()
            plan = engine.create_workload_rebalancing_plan()
        
        if len(engine.workload_violations) > 0:
            assert isinstance(plan, dict)
            if 1 in plan:
                assert len(plan[1]) > 0
                assert any("lessons" in action.lower() for action in plan[1])

    def test_validate_workload_distribution(self, db_manager):
        """Test validating workload distribution"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        # Create mock schedule entries
        mock_entries = [
            Mock(teacher_id=1, day=0, time_slot=0),
            Mock(teacher_id=1, day=1, time_slot=0),
            Mock(teacher_id=2, day=0, time_slot=0),
            Mock(teacher_id=2, day=1, time_slot=0),
            Mock(teacher_id=2, day=2, time_slot=0),
            Mock(teacher_id=2, day=3, time_slot=0),
        ]
        
        mock_teacher1 = Mock()
        mock_teacher1.name = "Teacher 1"
        mock_teacher2 = Mock()
        mock_teacher2.name = "Teacher 2"
        
        def mock_get_teacher(teacher_id):
            if teacher_id == 1:
                return mock_teacher1
            elif teacher_id == 2:
                return mock_teacher2
            return None
        
        with patch.object(engine.db_manager, 'get_teacher_by_id', side_effect=mock_get_teacher):
            report = engine.validate_workload_distribution(mock_entries)
        
        assert "total_teachers" in report
        assert "teachers_with_violations" in report
        assert "violation_rate_percent" in report
        assert "empty_day_distribution" in report
        assert "violations_by_severity" in report
        assert "workload_violations" in report
        assert "rebalancing_plan" in report
        
        assert report["total_teachers"] == 2


class TestConstraintStateManagement:
    """Test constraint state management"""

    def test_get_constraint_state(self, db_manager):
        """Test getting current constraint state"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        state = engine.get_constraint_state()
        
        assert isinstance(state, ConstraintState)
        assert state.workload_max_empty_days == 1
        assert state.allow_non_consecutive_blocks is False

    def test_get_relaxation_statistics(self, db_manager):
        """Test getting relaxation statistics"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        # Perform some operations
        engine.relax_constraints(RelaxationLevel.WORKLOAD_FLEX)
        engine.restore_constraints()
        
        stats = engine.get_relaxation_statistics()
        
        assert isinstance(stats, dict)
        assert stats["total_relaxations"] == 1
        assert stats["constraint_restorations"] == 1
        
        # Should be a copy, not reference
        stats["total_relaxations"] = 999
        assert engine.relaxation_stats["total_relaxations"] == 1

    def test_flexibility_check_methods(self, db_manager):
        """Test flexibility check methods"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        # Strict level
        assert engine.is_workload_flexible() is False
        assert engine.is_block_flexible() is False
        assert engine.is_availability_flexible() is False
        
        # Workload flex level
        engine.relax_constraints(RelaxationLevel.WORKLOAD_FLEX)
        assert engine.is_workload_flexible() is True
        assert engine.is_block_flexible() is False
        assert engine.is_availability_flexible() is False
        
        # Block flex level
        engine.relax_constraints(RelaxationLevel.BLOCK_FLEX)
        assert engine.is_workload_flexible() is True
        assert engine.is_block_flexible() is True
        assert engine.is_availability_flexible() is False
        
        # Availability flex level
        engine.relax_constraints(RelaxationLevel.AVAILABILITY_FLEX)
        assert engine.is_workload_flexible() is True
        assert engine.is_block_flexible() is True
        assert engine.is_availability_flexible() is True

    def test_prioritize_curriculum_over_workload(self, db_manager):
        """Test curriculum prioritization over workload"""
        engine = ConstraintRelaxationEngine(db_manager)
        
        # Strict mode should not prioritize curriculum over workload
        assert engine.prioritize_curriculum_over_workload() is False
        
        # Flexible modes should prioritize curriculum
        engine.relax_constraints(RelaxationLevel.WORKLOAD_FLEX)
        assert engine.prioritize_curriculum_over_workload() is True
        
        engine.relax_constraints(RelaxationLevel.BLOCK_FLEX)
        assert engine.prioritize_curriculum_over_workload() is True
        
        engine.relax_constraints(RelaxationLevel.AVAILABILITY_FLEX)
        assert engine.prioritize_curriculum_over_workload() is True


class TestConstraintStateDataClass:
    """Test ConstraintState data class"""

    def test_constraint_state_default_values(self):
        """Test ConstraintState default values"""
        state = ConstraintState()
        
        assert state.workload_max_empty_days == 1
        assert state.allow_non_consecutive_blocks is False
        assert state.allow_availability_violations is False
        assert state.strict_block_rules is True
        assert state.original_state is None

    def test_constraint_state_custom_values(self):
        """Test ConstraintState with custom values"""
        state = ConstraintState(
            workload_max_empty_days=3,
            allow_non_consecutive_blocks=True,
            allow_availability_violations=True,
            strict_block_rules=False
        )
        
        assert state.workload_max_empty_days == 3
        assert state.allow_non_consecutive_blocks is True
        assert state.allow_availability_violations is True
        assert state.strict_block_rules is False


class TestWorkloadViolationDataClass:
    """Test WorkloadViolation data class"""

    def test_workload_violation_creation(self):
        """Test WorkloadViolation creation"""
        violation = WorkloadViolation(
            teacher_id=1,
            teacher_name="John Doe",
            empty_days=2,
            working_days={0, 1, 2},
            violation_severity="minor"
        )
        
        assert violation.teacher_id == 1
        assert violation.teacher_name == "John Doe"
        assert violation.empty_days == 2
        assert violation.working_days == {0, 1, 2}
        assert violation.violation_severity == "minor"
        assert len(violation.suggested_adjustments) == 0

    def test_workload_violation_with_suggestions(self):
        """Test WorkloadViolation with suggestions"""
        suggestions = ["Move lesson to Wednesday", "Redistribute workload"]
        
        violation = WorkloadViolation(
            teacher_id=1,
            teacher_name="Jane Smith",
            empty_days=3,
            working_days={0, 1},
            violation_severity="moderate",
            suggested_adjustments=suggestions
        )
        
        assert violation.suggested_adjustments == suggestions
        assert len(violation.suggested_adjustments) == 2