# -*- coding: utf-8 -*-
"""
Unit tests for BottleneckAnalyzer

Tests cover:
- Resource bottleneck identification algorithms
- Constraint pattern analysis
- Utilization pattern analysis
- Targeted improvement suggestion generation
- Bottleneck scoring calculations
- Resource utilization calculations
"""

import pytest
from unittest.mock import Mock, patch
from collections import defaultdict

from algorithms.bottleneck_analyzer import (
    BottleneckAnalyzer,
    ResourceBottleneck,
    ConstraintAnalysis,
    UtilizationPattern
)


class TestBottleneckAnalyzerInitialization:
    """Test BottleneckAnalyzer initialization"""

    def test_initialization_default(self):
        """Test default initialization"""
        analyzer = BottleneckAnalyzer()
        
        assert analyzer.db_manager is None
        assert analyzer.weights['conflict_frequency'] == 0.4
        assert analyzer.weights['resource_utilization'] == 0.3
        assert analyzer.weights['constraint_severity'] == 0.2
        assert analyzer.weights['improvement_potential'] == 0.1

    def test_initialization_with_db_manager(self):
        """Test initialization with database manager"""
        mock_db = Mock()
        analyzer = BottleneckAnalyzer(mock_db)
        
        assert analyzer.db_manager == mock_db


class TestResourceBottleneckIdentification:
    """Test resource bottleneck identification"""

    def test_identify_teacher_bottlenecks(self):
        """Test identification of teacher bottlenecks"""
        analyzer = BottleneckAnalyzer()
        
        teacher_conflicts = {101: 5, 102: 3, 103: 8}
        class_conflicts = {}
        slot_conflicts = {(0, 1): 2, (1, 2): 4}
        lesson_failures = {1: 2, 2: 1}
        teacher_utilization = {
            101: {'utilization_rate': 0.9},
            102: {'utilization_rate': 0.6},
            103: {'utilization_rate': 0.95}
        }
        class_utilization = {}
        
        bottlenecks = analyzer.identify_resource_bottlenecks(
            teacher_conflicts, class_conflicts, slot_conflicts,
            lesson_failures, teacher_utilization, class_utilization
        )
        
        # Should identify teacher bottlenecks
        teacher_bottlenecks = [b for b in bottlenecks if b.resource_type == 'teacher']
        assert len(teacher_bottlenecks) == 3
        
        # Should be sorted by bottleneck score (highest first)
        scores = [b.bottleneck_score for b in teacher_bottlenecks]
        assert scores == sorted(scores, reverse=True)
        
        # Teacher 103 should have highest score (most conflicts + highest utilization)
        top_bottleneck = teacher_bottlenecks[0]
        assert top_bottleneck.resource_id == 103
        assert top_bottleneck.conflict_count == 8
        assert top_bottleneck.utilization_rate == 0.95

    def test_identify_class_bottlenecks(self):
        """Test identification of class bottlenecks"""
        analyzer = BottleneckAnalyzer()
        
        teacher_conflicts = {}
        class_conflicts = {201: 4, 202: 6}
        slot_conflicts = {}
        lesson_failures = {}
        teacher_utilization = {}
        class_utilization = {
            201: {'utilization_rate': 0.8},
            202: {'utilization_rate': 0.7}
        }
        
        bottlenecks = analyzer.identify_resource_bottlenecks(
            teacher_conflicts, class_conflicts, slot_conflicts,
            lesson_failures, teacher_utilization, class_utilization
        )
        
        class_bottlenecks = [b for b in bottlenecks if b.resource_type == 'class']
        assert len(class_bottlenecks) == 2
        
        # Class 202 should have higher score (more conflicts)
        top_bottleneck = class_bottlenecks[0]
        assert top_bottleneck.resource_id == 202
        assert top_bottleneck.conflict_count == 6

    def test_identify_time_slot_bottlenecks(self):
        """Test identification of time slot bottlenecks"""
        analyzer = BottleneckAnalyzer()
        
        teacher_conflicts = {}
        class_conflicts = {}
        slot_conflicts = {(0, 1): 8, (1, 2): 5, (2, 3): 3}
        lesson_failures = {}
        teacher_utilization = {}
        class_utilization = {}
        
        bottlenecks = analyzer.identify_resource_bottlenecks(
            teacher_conflicts, class_conflicts, slot_conflicts,
            lesson_failures, teacher_utilization, class_utilization
        )
        
        slot_bottlenecks = [b for b in bottlenecks if b.resource_type == 'time_slot']
        assert len(slot_bottlenecks) == 3
        
        # Slot (0,1) should have highest score (most conflicts)
        top_bottleneck = slot_bottlenecks[0]
        assert top_bottleneck.resource_name == "Day_0_Slot_1"
        assert top_bottleneck.conflict_count == 8

    def test_identify_lesson_bottlenecks(self):
        """Test identification of lesson bottlenecks"""
        analyzer = BottleneckAnalyzer()
        
        teacher_conflicts = {}
        class_conflicts = {}
        slot_conflicts = {}
        lesson_failures = {1: 5, 2: 2, 3: 8}
        teacher_utilization = {}
        class_utilization = {}
        
        bottlenecks = analyzer.identify_resource_bottlenecks(
            teacher_conflicts, class_conflicts, slot_conflicts,
            lesson_failures, teacher_utilization, class_utilization
        )
        
        lesson_bottlenecks = [b for b in bottlenecks if b.resource_type == 'lesson']
        assert len(lesson_bottlenecks) == 3
        
        # Lesson 3 should have highest score (most failures)
        top_bottleneck = lesson_bottlenecks[0]
        assert top_bottleneck.resource_id == 3
        assert top_bottleneck.conflict_count == 8

    def test_bottleneck_scoring_calculation(self):
        """Test bottleneck score calculation"""
        analyzer = BottleneckAnalyzer()
        
        # Test teacher with high conflicts and high utilization
        score = analyzer._calculate_resource_bottleneck_score(10, 0.9, 'teacher')
        
        # Should be high due to conflicts and overutilization penalty
        assert score > 4.0  # Base score (10 * 0.4) + utilization penalty + teacher multiplier
        
        # Test teacher with low conflicts and normal utilization
        score_low = analyzer._calculate_resource_bottleneck_score(2, 0.7, 'teacher')
        assert score_low < score

    def test_improvement_potential_estimation(self):
        """Test improvement potential estimation"""
        analyzer = BottleneckAnalyzer()
        
        # High conflicts with high utilization should have high potential
        potential_high = analyzer._estimate_improvement_potential(10, 0.9, 'teacher')
        
        # Low conflicts with low utilization should have lower potential
        potential_low = analyzer._estimate_improvement_potential(2, 0.4, 'teacher')
        
        assert potential_high > potential_low
        assert 0 <= potential_high <= 1
        assert 0 <= potential_low <= 1


class TestConstraintPatternAnalysis:
    """Test constraint pattern analysis"""

    def test_analyze_constraint_patterns(self):
        """Test constraint pattern analysis"""
        analyzer = BottleneckAnalyzer()
        
        constraint_violations = {
            'teacher_availability': 10,
            'block_rules': 5,
            'workload_distribution': 3
        }
        
        # Mock failure log
        failure_log = [
            Mock(
                constraint_violations=['teacher_availability'],
                teacher_id=101,
                class_id=201,
                attempted_slots=[(0, 1), (0, 2)]
            ),
            Mock(
                constraint_violations=['block_rules'],
                teacher_id=102,
                attempted_slots=[(1, 1)]
            )
        ]
        
        analyses = analyzer.analyze_constraint_patterns(constraint_violations, failure_log)
        
        assert len(analyses) == 3
        
        # Should be sorted by severity score
        severities = [a.severity_score for a in analyses]
        assert severities == sorted(severities, reverse=True)
        
        # Teacher availability should have highest frequency
        top_analysis = analyses[0]
        assert top_analysis.constraint_type == 'teacher_availability'
        assert top_analysis.frequency == 10

    def test_constraint_severity_calculation(self):
        """Test constraint severity calculation"""
        analyzer = BottleneckAnalyzer()
        
        # High frequency with many affected resources should have high severity
        severity = analyzer._calculate_constraint_severity(
            'teacher_availability',
            10,  # High frequency
            [('teacher', 101), ('teacher', 102), ('class', 201)],  # Multiple resources
            {(0, 1): 5, (1, 2): 3}  # Multiple time patterns
        )
        
        assert severity > 5.0  # Should be significant
        
        # Low frequency with few resources should have lower severity
        severity_low = analyzer._calculate_constraint_severity(
            'minor_constraint',
            2,  # Low frequency
            [('teacher', 101)],  # Single resource
            {(0, 1): 1}  # Single time pattern
        )
        
        assert severity_low < severity

    def test_constraint_resolution_suggestions(self):
        """Test constraint resolution suggestion generation"""
        analyzer = BottleneckAnalyzer()
        
        # Test teacher availability suggestions
        suggestions = analyzer._generate_constraint_resolution_suggestions(
            'teacher_availability', 10, [('teacher', 101)], {(0, 1): 5}
        )
        
        assert len(suggestions) > 0
        assert any('availability' in s.lower() for s in suggestions)
        
        # Test block rules suggestions
        suggestions = analyzer._generate_constraint_resolution_suggestions(
            'block_rules', 5, [('class', 201)], {(1, 2): 3}
        )
        
        assert len(suggestions) > 0
        assert any('block' in s.lower() for s in suggestions)


class TestUtilizationPatternAnalysis:
    """Test utilization pattern analysis"""

    def test_analyze_utilization_patterns(self):
        """Test utilization pattern analysis"""
        analyzer = BottleneckAnalyzer()
        
        teacher_utilization = {
            101: {'utilization_rate': 0.8, 'variance': 0.1},
            102: {'utilization_rate': 0.3, 'variance': 0.2}  # Low utilization, high variance
        }
        
        class_utilization = {
            201: {'utilization_rate': 0.9, 'variance': 0.05}  # High utilization, low variance
        }
        
        slot_conflicts = {(0, 1): 5, (1, 2): 3}
        
        patterns = analyzer.analyze_utilization_patterns(
            teacher_utilization, class_utilization, slot_conflicts
        )
        
        assert len(patterns) == 3  # 2 teachers + 1 class
        
        # Should be sorted by efficiency score (lowest first)
        efficiency_scores = [p.efficiency_score for p in patterns if p is not None]
        assert efficiency_scores == sorted(efficiency_scores)

    def test_efficiency_score_calculation(self):
        """Test efficiency score calculation"""
        analyzer = BottleneckAnalyzer()
        
        # Ideal utilization (0.75) with low variance should have high efficiency
        efficiency_high = analyzer._calculate_efficiency_score(0.75, 0.05)
        
        # Poor utilization with high variance should have low efficiency
        efficiency_low = analyzer._calculate_efficiency_score(0.3, 0.4)
        
        assert efficiency_high > efficiency_low
        assert 0 <= efficiency_high <= 1
        assert 0 <= efficiency_low <= 1

    def test_analyze_resource_utilization_pattern(self):
        """Test individual resource utilization pattern analysis"""
        analyzer = BottleneckAnalyzer()
        
        utilization_data = {
            'utilization_rate': 0.8,
            'variance': 0.15
        }
        slot_conflicts = {(0, 1): 5, (1, 2): 3}
        
        pattern = analyzer._analyze_resource_utilization_pattern(
            'teacher', 101, utilization_data, slot_conflicts
        )
        
        assert pattern is not None
        assert pattern.resource_type == 'teacher'
        assert pattern.resource_id == 101
        assert pattern.average_utilization == 0.8
        assert pattern.variance == 0.15
        assert pattern.efficiency_score >= 0

    def test_analyze_empty_utilization_data(self):
        """Test analysis with empty utilization data"""
        analyzer = BottleneckAnalyzer()
        
        pattern = analyzer._analyze_resource_utilization_pattern(
            'teacher', 101, {}, {}
        )
        
        assert pattern is None


class TestTargetedImprovements:
    """Test targeted improvement generation"""

    def test_generate_targeted_improvements(self):
        """Test targeted improvement suggestion generation"""
        analyzer = BottleneckAnalyzer()
        
        # Create mock bottlenecks
        bottlenecks = [
            Mock(
                resource_type='teacher',
                resource_name='Teacher_101',
                bottleneck_score=8.5,
                affected_lessons=[1, 2, 3],
                peak_conflict_times=[(0, 1), (1, 2)],
                improvement_potential=0.8
            ),
            Mock(
                resource_type='class',
                resource_name='Class_201',
                bottleneck_score=6.2,
                affected_lessons=[4, 5],
                peak_conflict_times=[(2, 3)],
                improvement_potential=0.6
            )
        ]
        
        # Create mock constraint analyses
        constraint_analyses = [
            Mock(
                constraint_type='teacher_availability',
                frequency=15,
                severity_score=7.8
            )
        ]
        
        # Create mock utilization patterns
        utilization_patterns = [
            Mock(
                resource_type='teacher',
                resource_id=102,
                efficiency_score=0.4,  # Poor efficiency
                average_utilization=0.3,
                variance=0.25
            )
        ]
        
        improvements = analyzer.generate_targeted_improvements(
            bottlenecks, constraint_analyses, utilization_patterns
        )
        
        assert len(improvements) > 0
        
        # Should include critical bottleneck suggestion
        critical_suggestion = any('CRITICAL' in imp for imp in improvements)
        assert critical_suggestion
        
        # Should include constraint-specific suggestions
        constraint_suggestion = any('availability' in imp.lower() for imp in improvements)
        assert constraint_suggestion

    def test_generate_improvements_empty_data(self):
        """Test improvement generation with empty data"""
        analyzer = BottleneckAnalyzer()
        
        improvements = analyzer.generate_targeted_improvements([], [], [])
        
        # Should still return some general suggestions or empty list
        assert isinstance(improvements, list)

    def test_generate_improvements_time_based(self):
        """Test time-based improvement suggestions"""
        analyzer = BottleneckAnalyzer()
        
        # Create bottlenecks with overlapping peak times
        bottlenecks = [
            Mock(
                resource_type='teacher',
                resource_name='Teacher_101',
                bottleneck_score=7.0,
                peak_conflict_times=[(0, 1), (0, 2)],
                affected_lessons=[1, 2],
                improvement_potential=0.5
            ),
            Mock(
                resource_type='class',
                resource_name='Class_201',
                bottleneck_score=6.0,
                peak_conflict_times=[(0, 1), (1, 1)],  # Overlapping with (0, 1)
                affected_lessons=[3],
                improvement_potential=0.4
            )
        ]
        
        improvements = analyzer.generate_targeted_improvements(bottlenecks, [], [])
        
        # Should include time-based suggestions
        time_suggestion = any('slot' in imp.lower() or 'time' in imp.lower() for imp in improvements)
        assert time_suggestion

    def test_generate_improvements_high_potential(self):
        """Test improvement suggestions for high potential bottlenecks"""
        analyzer = BottleneckAnalyzer()
        
        bottlenecks = [
            Mock(
                resource_type='teacher',
                resource_name='Teacher_101',
                bottleneck_score=5.0,
                improvement_potential=0.8,  # High potential
                peak_conflict_times=[],
                affected_lessons=[]
            )
        ]
        
        improvements = analyzer.generate_targeted_improvements(bottlenecks, [], [])
        
        # Should include opportunity-based suggestions
        opportunity_suggestion = any('OPPORTUNITY' in imp for imp in improvements)
        assert opportunity_suggestion


class TestHelperMethods:
    """Test helper methods"""

    def test_calculate_slot_utilization(self):
        """Test slot utilization calculation"""
        analyzer = BottleneckAnalyzer()
        
        slot_conflicts = {
            (0, 1): 10,
            (1, 2): 5,
            (2, 3): 15
        }
        
        # Total conflicts = 30
        utilization = analyzer._calculate_slot_utilization(0, 1, slot_conflicts)
        assert utilization == 10/30  # 0.333...
        
        utilization = analyzer._calculate_slot_utilization(2, 3, slot_conflicts)
        assert utilization == 15/30  # 0.5
        
        # Non-existent slot should return 0
        utilization = analyzer._calculate_slot_utilization(4, 4, slot_conflicts)
        assert utilization == 0.0

    def test_calculate_slot_utilization_empty(self):
        """Test slot utilization with empty conflicts"""
        analyzer = BottleneckAnalyzer()
        
        utilization = analyzer._calculate_slot_utilization(0, 1, {})
        assert utilization == 0.0

    def test_estimate_lesson_improvement_potential(self):
        """Test lesson improvement potential estimation"""
        analyzer = BottleneckAnalyzer()
        
        # High failure count should have high potential (capped at 1.0)
        potential_high = analyzer._estimate_lesson_improvement_potential(10)
        assert potential_high == 1.0
        
        # Low failure count should have proportional potential
        potential_low = analyzer._estimate_lesson_improvement_potential(2)
        assert potential_low == 0.4  # 2/5
        
        # Zero failures should have zero potential
        potential_zero = analyzer._estimate_lesson_improvement_potential(0)
        assert potential_zero == 0.0


@pytest.fixture
def sample_conflicts():
    """Sample conflict data for testing"""
    return {
        'teacher_conflicts': {101: 5, 102: 3, 103: 8},
        'class_conflicts': {201: 4, 202: 6},
        'slot_conflicts': {(0, 1): 10, (1, 2): 5, (2, 3): 15},
        'lesson_failures': {1: 3, 2: 1, 3: 7}
    }


@pytest.fixture
def sample_utilization():
    """Sample utilization data for testing"""
    return {
        'teacher_utilization': {
            101: {'utilization_rate': 0.8, 'variance': 0.1},
            102: {'utilization_rate': 0.3, 'variance': 0.2},
            103: {'utilization_rate': 0.95, 'variance': 0.05}
        },
        'class_utilization': {
            201: {'utilization_rate': 0.7, 'variance': 0.15},
            202: {'utilization_rate': 0.9, 'variance': 0.08}
        }
    }