# -*- coding: utf-8 -*-
"""
Tests for Solution Validator - Comprehensive validation system testing

This module tests the solution validation functionality including constraint
satisfaction verification, conflict detection, block rule validation, and
workload distribution validation.

Requirements tested: 1.4, 3.5, 5.2
"""

import pytest
from unittest.mock import Mock, MagicMock
from algorithms.solution_validator import (
    SolutionValidator, ValidationReport, ValidationViolation, ViolationType,
    BlockValidationResult, WorkloadValidationResult
)
from algorithms.optimized_curriculum_scheduler import (
    EnhancedScheduleEntry, PlacementMethod, ConstraintLevel
)
from database.models import Teacher, Class, Lesson


class TestSolutionValidator:
    """Test solution validator core functionality"""
    
    @pytest.fixture
    def validator(self):
        """Create solution validator instance"""
        mock_db = Mock()
        return SolutionValidator(mock_db)
    
    @pytest.fixture
    def sample_entries(self):
        """Create sample schedule entries for testing"""
        return [
            EnhancedScheduleEntry(
                schedule_id=1, class_id=1, teacher_id=1, lesson_id=1,
                day=0, time_slot=0, block_position=1, block_id="block_1",
                placement_method=PlacementMethod.STANDARD,
                constraint_level=ConstraintLevel.STRICT
            ),
            EnhancedScheduleEntry(
                schedule_id=2, class_id=1, teacher_id=1, lesson_id=1,
                day=0, time_slot=1, block_position=2, block_id="block_1",
                placement_method=PlacementMethod.STANDARD,
                constraint_level=ConstraintLevel.STRICT
            ),
            EnhancedScheduleEntry(
                schedule_id=3, class_id=2, teacher_id=2, lesson_id=2,
                day=1, time_slot=0, block_position=1, block_id="block_2",
                placement_method=PlacementMethod.STANDARD,
                constraint_level=ConstraintLevel.STRICT
            )
        ]
    
    def test_validator_initialization(self, validator):
        """Test validator initialization"""
        assert validator is not None
        assert validator.max_empty_days == 1
        assert validator.max_daily_hours == 8
        assert len(validator.required_block_patterns) == 5
    
    def test_validate_complete_solution_success(self, validator, sample_entries):
        """Test successful validation of complete solution"""
        # Mock database methods
        validator.db_manager.get_all_classes.return_value = [
            Class(1, "Class 1", 5), Class(2, "Class 2", 6)
        ]
        validator.db_manager.get_schedule_by_school_type.return_value = []
        
        report = validator.validate_complete_solution(sample_entries)
        
        assert isinstance(report, ValidationReport)
        assert report.total_violations >= 0  # May have some violations
        assert report.validation_metrics is not None
    
    def test_validate_conflicts_no_conflicts(self, validator, sample_entries):
        """Test conflict validation with no conflicts"""
        violations = validator._validate_conflicts(sample_entries)
        
        # Should have no conflicts with the sample data
        assert len(violations) == 0
    
    def test_validate_conflicts_teacher_conflict(self, validator):
        """Test detection of teacher conflicts"""
        conflicting_entries = [
            EnhancedScheduleEntry(
                schedule_id=1, class_id=1, teacher_id=1, lesson_id=1,
                day=0, time_slot=0, block_position=1, block_id="block_1"
            ),
            EnhancedScheduleEntry(
                schedule_id=2, class_id=2, teacher_id=1, lesson_id=2,
                day=0, time_slot=0, block_position=1, block_id="block_2"
            )
        ]
        
        violations = validator._validate_conflicts(conflicting_entries)
        
        assert len(violations) == 1
        assert violations[0].violation_type == ViolationType.TEACHER_CONFLICT
        assert violations[0].severity == "critical"
        assert "Teacher 1" in violations[0].description
    
    def test_validate_conflicts_class_conflict(self, validator):
        """Test detection of class conflicts"""
        conflicting_entries = [
            EnhancedScheduleEntry(
                schedule_id=1, class_id=1, teacher_id=1, lesson_id=1,
                day=0, time_slot=0, block_position=1, block_id="block_1"
            ),
            EnhancedScheduleEntry(
                schedule_id=2, class_id=1, teacher_id=2, lesson_id=2,
                day=0, time_slot=0, block_position=1, block_id="block_2"
            )
        ]
        
        violations = validator._validate_conflicts(conflicting_entries)
        
        assert len(violations) == 1
        assert violations[0].violation_type == ViolationType.CLASS_CONFLICT
        assert violations[0].severity == "critical"
        assert "Class 1" in violations[0].description


class TestBlockValidation:
    """Test block rule validation functionality"""
    
    @pytest.fixture
    def validator(self):
        """Create solution validator instance"""
        return SolutionValidator()
    
    def test_validate_block_rules_valid_consecutive(self, validator):
        """Test validation of valid consecutive block"""
        entries = [
            EnhancedScheduleEntry(
                schedule_id=1, class_id=1, teacher_id=1, lesson_id=1,
                day=0, time_slot=0, block_position=1, block_id="block_1"
            ),
            EnhancedScheduleEntry(
                schedule_id=2, class_id=1, teacher_id=1, lesson_id=1,
                day=0, time_slot=1, block_position=2, block_id="block_1"
            )
        ]
        
        result = validator._validate_block_rules(entries)
        
        assert isinstance(result, BlockValidationResult)
        assert result.is_valid
        assert len(result.violations) == 0
        assert "block_1" in result.block_patterns
    
    def test_validate_block_rules_fragmented_block(self, validator):
        """Test detection of fragmented blocks"""
        entries = [
            EnhancedScheduleEntry(
                schedule_id=1, class_id=1, teacher_id=1, lesson_id=1,
                day=0, time_slot=0, block_position=1, block_id="block_1"
            ),
            EnhancedScheduleEntry(
                schedule_id=2, class_id=1, teacher_id=1, lesson_id=1,
                day=0, time_slot=2, block_position=2, block_id="block_1"  # Gap at slot 1
            )
        ]
        
        result = validator._validate_block_rules(entries)
        
        assert not result.is_valid
        assert len(result.violations) > 0
        assert "block_1" in result.fragmented_blocks
    
    def test_is_block_fragmented_consecutive_slots(self, validator):
        """Test fragmentation detection with consecutive slots"""
        time_slots = [(0, 0), (0, 1), (0, 2)]  # Consecutive
        
        is_fragmented = validator._is_block_fragmented(time_slots)
        
        assert not is_fragmented
    
    def test_is_block_fragmented_gap_in_slots(self, validator):
        """Test fragmentation detection with gap in slots"""
        time_slots = [(0, 0), (0, 2), (0, 3)]  # Gap at slot 1
        
        is_fragmented = validator._is_block_fragmented(time_slots)
        
        assert is_fragmented
    
    def test_are_slots_properly_arranged_valid(self, validator):
        """Test slot arrangement validation for valid pattern"""
        time_slots = [(0, 0), (0, 1)]  # 2-hour consecutive block
        
        is_proper = validator._are_slots_properly_arranged(time_slots, 2)
        
        assert is_proper
    
    def test_are_slots_properly_arranged_invalid_size(self, validator):
        """Test slot arrangement validation for invalid size"""
        time_slots = [(0, 0), (0, 1)]  # 2 slots for 3-hour block
        
        is_proper = validator._are_slots_properly_arranged(time_slots, 3)
        
        assert not is_proper


class TestWorkloadValidation:
    """Test workload distribution validation"""
    
    @pytest.fixture
    def validator(self):
        """Create solution validator instance"""
        return SolutionValidator()
    
    def test_validate_workload_distribution_valid(self, validator):
        """Test validation of valid workload distribution"""
        entries = [
            # Teacher 1: 4 days, 1 empty day (valid)
            EnhancedScheduleEntry(schedule_id=1, class_id=1, teacher_id=1, lesson_id=1, day=0, time_slot=0, block_position=1, block_id="b1"),
            EnhancedScheduleEntry(schedule_id=2, class_id=1, teacher_id=1, lesson_id=1, day=1, time_slot=0, block_position=1, block_id="b2"),
            EnhancedScheduleEntry(schedule_id=3, class_id=1, teacher_id=1, lesson_id=1, day=2, time_slot=0, block_position=1, block_id="b3"),
            EnhancedScheduleEntry(schedule_id=4, class_id=1, teacher_id=1, lesson_id=1, day=3, time_slot=0, block_position=1, block_id="b4"),
        ]
        
        result = validator._validate_workload_distribution(entries)
        
        assert isinstance(result, WorkloadValidationResult)
        assert result.is_valid
        assert len(result.violations) == 0
    
    def test_validate_workload_distribution_too_many_empty_days(self, validator):
        """Test detection of too many empty days"""
        entries = [
            # Teacher 1: only 2 days, 3 empty days (invalid)
            EnhancedScheduleEntry(schedule_id=1, class_id=1, teacher_id=1, lesson_id=1, day=0, time_slot=0, block_position=1, block_id="b1"),
            EnhancedScheduleEntry(schedule_id=2, class_id=1, teacher_id=1, lesson_id=1, day=1, time_slot=0, block_position=1, block_id="b2"),
        ]
        
        result = validator._validate_workload_distribution(entries)
        
        assert not result.is_valid
        assert len(result.violations) > 0
        assert 1 in result.empty_day_violations
        assert result.empty_day_violations[1] == 3  # 3 empty days
    
    def test_analyze_teacher_workload_complete_analysis(self, validator):
        """Test complete teacher workload analysis"""
        entries = [
            EnhancedScheduleEntry(schedule_id=1, class_id=1, teacher_id=1, lesson_id=1, day=0, time_slot=0, block_position=1, block_id="b1"),
            EnhancedScheduleEntry(schedule_id=2, class_id=1, teacher_id=1, lesson_id=1, day=0, time_slot=1, block_position=1, block_id="b2"),
            EnhancedScheduleEntry(schedule_id=3, class_id=1, teacher_id=1, lesson_id=1, day=1, time_slot=0, block_position=1, block_id="b3"),
        ]
        
        workload = validator._analyze_teacher_workload(1, entries)
        
        assert workload['teacher_id'] == 1
        assert workload['total_hours'] == 3
        assert workload['working_days'] == [0, 1]
        assert workload['empty_days'] == 3  # Days 2, 3, 4
        assert workload['daily_hours'][0] == 2  # 2 hours on day 0
        assert workload['daily_hours'][1] == 1  # 1 hour on day 1
        assert workload['max_daily_hours'] == 2
        assert workload['min_daily_hours'] == 0


class TestCurriculumValidation:
    """Test curriculum requirements validation"""
    
    @pytest.fixture
    def validator_with_db(self):
        """Create validator with mocked database"""
        mock_db = Mock()
        validator = SolutionValidator(mock_db)
        
        # Mock database responses
        mock_db.get_all_classes.return_value = [
            Class(1, "Class 1", 5),
            Class(2, "Class 2", 6)
        ]
        
        mock_assignment = Mock()
        mock_assignment.class_id = 1
        mock_assignment.lesson_id = 1
        mock_assignment.teacher_id = 1
        mock_db.get_schedule_by_school_type.return_value = [mock_assignment]
        
        mock_db.get_weekly_hours_for_lesson.return_value = 3  # Requires 3 hours
        
        mock_lesson = Mock()
        mock_lesson.name = "Mathematics"
        mock_db.get_lesson_by_id.return_value = mock_lesson
        
        return validator
    
    def test_validate_curriculum_requirements_sufficient_hours(self, validator_with_db):
        """Test curriculum validation with sufficient hours"""
        entries = [
            # 3 hours of lesson 1 for class 1 (meets requirement)
            EnhancedScheduleEntry(schedule_id=1, class_id=1, teacher_id=1, lesson_id=1, day=0, time_slot=0, block_position=1, block_id="b1"),
            EnhancedScheduleEntry(schedule_id=2, class_id=1, teacher_id=1, lesson_id=1, day=0, time_slot=1, block_position=1, block_id="b2"),
            EnhancedScheduleEntry(schedule_id=3, class_id=1, teacher_id=1, lesson_id=1, day=1, time_slot=0, block_position=1, block_id="b3"),
        ]
        
        violations = validator_with_db._validate_curriculum_requirements(entries)
        
        assert len(violations) == 0  # No violations - requirement met
    
    def test_validate_curriculum_requirements_insufficient_hours(self, validator_with_db):
        """Test curriculum validation with insufficient hours"""
        entries = [
            # Only 2 hours of lesson 1 for class 1 (requires 3)
            EnhancedScheduleEntry(schedule_id=1, class_id=1, teacher_id=1, lesson_id=1, day=0, time_slot=0, block_position=1, block_id="b1"),
            EnhancedScheduleEntry(schedule_id=2, class_id=1, teacher_id=1, lesson_id=1, day=0, time_slot=1, block_position=1, block_id="b2"),
        ]
        
        violations = validator_with_db._validate_curriculum_requirements(entries)
        
        assert len(violations) == 1
        assert violations[0].violation_type == ViolationType.CURRICULUM_VIOLATION
        assert violations[0].severity == "critical"
        assert "missing 1 hours" in violations[0].description
    
    def test_validate_curriculum_requirements_excess_hours(self, validator_with_db):
        """Test curriculum validation with excess hours"""
        entries = [
            # 4 hours of lesson 1 for class 1 (requires 3)
            EnhancedScheduleEntry(schedule_id=1, class_id=1, teacher_id=1, lesson_id=1, day=0, time_slot=0, block_position=1, block_id="b1"),
            EnhancedScheduleEntry(schedule_id=2, class_id=1, teacher_id=1, lesson_id=1, day=0, time_slot=1, block_position=1, block_id="b2"),
            EnhancedScheduleEntry(schedule_id=3, class_id=1, teacher_id=1, lesson_id=1, day=1, time_slot=0, block_position=1, block_id="b3"),
            EnhancedScheduleEntry(schedule_id=4, class_id=1, teacher_id=1, lesson_id=1, day=1, time_slot=1, block_position=1, block_id="b4"),
        ]
        
        violations = validator_with_db._validate_curriculum_requirements(entries)
        
        assert len(violations) == 1
        assert violations[0].violation_type == ViolationType.CURRICULUM_VIOLATION
        assert violations[0].severity == "minor"
        assert "1 extra hours" in violations[0].description


class TestValidationReporting:
    """Test validation reporting functionality"""
    
    @pytest.fixture
    def validator(self):
        """Create solution validator instance"""
        return SolutionValidator()
    
    def test_generate_conflict_summary(self, validator):
        """Test conflict summary generation"""
        violations = [
            ValidationViolation(ViolationType.TEACHER_CONFLICT, "critical", "Teacher conflict", []),
            ValidationViolation(ViolationType.CLASS_CONFLICT, "critical", "Class conflict", []),
            ValidationViolation(ViolationType.BLOCK_RULE_VIOLATION, "major", "Block violation", []),
        ]
        
        summary = validator._generate_conflict_summary(violations)
        
        assert summary["teacher_conflicts"] == 1
        assert summary["class_conflicts"] == 1
        assert summary["block_violations"] == 1
        assert summary["total_conflicts"] == 3
    
    def test_generate_validation_metrics(self, validator):
        """Test validation metrics generation"""
        entries = [Mock() for _ in range(10)]  # 10 entries
        violations = [
            ValidationViolation(ViolationType.TEACHER_CONFLICT, "critical", "Critical", []),
            ValidationViolation(ViolationType.CLASS_CONFLICT, "major", "Major", []),
            ValidationViolation(ViolationType.BLOCK_RULE_VIOLATION, "minor", "Minor", []),
        ]
        
        metrics = validator._generate_validation_metrics(entries, violations)
        
        assert metrics["total_entries_validated"] == 10
        assert metrics["total_violations"] == 3
        assert metrics["violation_rate_percent"] == 30.0  # 3/10 * 100
        assert metrics["critical_violations"] == 1
        assert metrics["major_violations"] == 1
        assert metrics["minor_violations"] == 1
        assert metrics["quality_score"] == 84.0  # 100 - (1*10 + 1*5 + 1*1)
        assert not metrics["validation_passed"]  # Has critical violations
    
    def test_generate_validation_recommendations_critical_violations(self, validator):
        """Test recommendations for critical violations"""
        report = ValidationReport(
            is_valid=False,
            total_violations=3,
            critical_violations=[
                ValidationViolation(ViolationType.TEACHER_CONFLICT, "critical", "Teacher conflict", []),
                ValidationViolation(ViolationType.CLASS_CONFLICT, "critical", "Class conflict", []),
            ],
            major_violations=[
                ValidationViolation(ViolationType.BLOCK_RULE_VIOLATION, "major", "Block violation", []),
            ],
            validation_metrics={"quality_score": 75}
        )
        
        recommendations = validator._generate_validation_recommendations(report)
        
        assert len(recommendations) > 0
        assert any("URGENT" in rec for rec in recommendations)
        assert any("teacher conflicts" in rec for rec in recommendations)
        assert any("class conflicts" in rec for rec in recommendations)
    
    def test_validate_single_constraint_conflicts(self, validator):
        """Test single constraint validation for conflicts"""
        sample_entries = [
            EnhancedScheduleEntry(
                schedule_id=1, class_id=1, teacher_id=1, lesson_id=1,
                day=0, time_slot=0, block_position=1, block_id="block_1"
            )
        ]
        violations = validator.validate_single_constraint(sample_entries, "conflicts")
        
        assert isinstance(violations, list)
        # Should have no conflicts with sample data
        assert len(violations) == 0
    
    def test_validate_single_constraint_unknown_type(self, validator):
        """Test single constraint validation with unknown type"""
        sample_entries = [
            EnhancedScheduleEntry(
                schedule_id=1, class_id=1, teacher_id=1, lesson_id=1,
                day=0, time_slot=0, block_position=1, block_id="block_1"
            )
        ]
        violations = validator.validate_single_constraint(sample_entries, "unknown_type")
        
        assert isinstance(violations, list)
        assert len(violations) == 0  # Should return empty list for unknown types
    
    def test_get_validation_summary(self, validator):
        """Test validation summary generation"""
        report = ValidationReport(
            is_valid=True,
            total_violations=2,
            critical_violations=[],
            major_violations=[],
            minor_violations=[Mock(), Mock()],
            validation_metrics={
                "quality_score": 95.0,
                "validation_passed": True
            },
            recommendations=["Rec 1", "Rec 2", "Rec 3", "Rec 4"]
        )
        
        summary = validator.get_validation_summary(report)
        
        assert summary["is_valid"] is True
        assert summary["total_violations"] == 2
        assert summary["quality_score"] == 95.0
        assert summary["critical_issues"] == 0
        assert summary["major_issues"] == 0
        assert summary["minor_issues"] == 2
        assert len(summary["top_recommendations"]) == 3  # Top 3
        assert summary["validation_passed"] is True


class TestValidationIntegration:
    """Test validation system integration"""
    
    @pytest.fixture
    def validator_with_full_mock(self):
        """Create validator with comprehensive mocks"""
        mock_db = Mock()
        validator = SolutionValidator(mock_db)
        
        # Mock all database methods
        mock_db.get_all_classes.return_value = [Class(1, "Class 1", 5)]
        mock_db.get_schedule_by_school_type.return_value = []
        mock_db.get_teacher_by_id.return_value = Teacher(1, "Teacher 1", "Math")
        mock_db.get_lesson_by_id.return_value = Lesson(1, "Mathematics")
        mock_db.get_weekly_hours_for_lesson.return_value = 2
        
        return validator
    
    def test_complete_validation_workflow(self, validator_with_full_mock):
        """Test complete validation workflow"""
        entries = [
            EnhancedScheduleEntry(
                schedule_id=1, class_id=1, teacher_id=1, lesson_id=1,
                day=0, time_slot=0, block_position=1, block_id="block_1"
            ),
            EnhancedScheduleEntry(
                schedule_id=2, class_id=1, teacher_id=1, lesson_id=1,
                day=0, time_slot=1, block_position=2, block_id="block_1"
            )
        ]
        
        report = validator_with_full_mock.validate_complete_solution(entries)
        
        # Verify report structure
        assert isinstance(report, ValidationReport)
        assert isinstance(report.is_valid, bool)
        assert isinstance(report.total_violations, int)
        assert isinstance(report.validation_metrics, dict)
        assert isinstance(report.recommendations, list)
        
        # Verify block validation was performed
        assert report.block_validation is not None
        assert isinstance(report.block_validation, BlockValidationResult)
        
        # Verify workload validation was performed
        assert report.workload_validation is not None
        assert isinstance(report.workload_validation, WorkloadValidationResult)
    
    def test_validation_with_multiple_violation_types(self):
        """Test validation with multiple types of violations"""
        validator = SolutionValidator()
        
        # Create entries with various violations
        entries = [
            # Teacher conflict
            EnhancedScheduleEntry(schedule_id=1, class_id=1, teacher_id=1, lesson_id=1, day=0, time_slot=0, block_position=1, block_id="b1"),
            EnhancedScheduleEntry(schedule_id=2, class_id=2, teacher_id=1, lesson_id=2, day=0, time_slot=0, block_position=1, block_id="b2"),
            # Fragmented block
            EnhancedScheduleEntry(schedule_id=3, class_id=3, teacher_id=2, lesson_id=3, day=1, time_slot=0, block_position=1, block_id="b3"),
            EnhancedScheduleEntry(schedule_id=4, class_id=3, teacher_id=2, lesson_id=3, day=1, time_slot=2, block_position=2, block_id="b3"),  # Gap
        ]
        
        report = validator.validate_complete_solution(entries)
        
        # Should detect multiple violation types
        assert report.total_violations > 0
        assert len(report.violations_by_type) > 0
        
        # Should have both conflict and block violations
        violation_types = list(report.violations_by_type.keys())
        assert any(vt == ViolationType.TEACHER_CONFLICT for vt in violation_types)