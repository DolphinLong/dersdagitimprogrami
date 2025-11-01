# -*- coding: utf-8 -*-
"""
Unit tests for SchedulingDiagnostics

Tests cover:
- Failure logging accuracy with detailed context
- Performance metrics collection and calculation
- Constraint violation statistics tracking
- Bottleneck analysis algorithms
- Teacher and class utilization analysis
- Health score calculation and recommendations
- Advanced bottleneck analysis integration
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from collections import defaultdict

from algorithms.scheduling_diagnostics import (
    SchedulingDiagnostics,
    FailureEntry,
    BottleneckReport,
    UtilizationReport
)
from algorithms.bottleneck_analyzer import ResourceBottleneck, ConstraintAnalysis, UtilizationPattern
from database.models import Lesson


class TestSchedulingDiagnosticsInitialization:
    """Test SchedulingDiagnostics initialization"""

    def test_initialization_default(self):
        """Test default initialization"""
        diagnostics = SchedulingDiagnostics()
        
        assert len(diagnostics.failure_log) == 0
        assert len(diagnostics.performance_metrics) == 0
        assert len(diagnostics.constraint_violations) == 0
        assert len(diagnostics.teacher_utilization) == 0
        assert len(diagnostics.class_utilization) == 0
        assert diagnostics.start_time is None
        assert diagnostics.total_attempts == 0
        assert diagnostics.successful_placements == 0
        assert diagnostics.backtrack_attempts == 0
        assert diagnostics.constraint_relaxations == 0
        assert diagnostics.bottleneck_analyzer is not None

    def test_initialization_with_db_manager(self):
        """Test initialization with database manager"""
        mock_db = Mock()
        diagnostics = SchedulingDiagnostics(mock_db)
        
        assert diagnostics.bottleneck_analyzer.db_manager == mock_db

    def test_start_session(self):
        """Test starting a new diagnostics session"""
        diagnostics = SchedulingDiagnostics()
        
        # Add some data first
        diagnostics.total_attempts = 5
        diagnostics.failure_log.append(Mock())
        diagnostics.constraint_violations['test'] = 3
        
        # Start new session
        diagnostics.start_session()
        
        assert diagnostics.start_time is not None
        assert len(diagnostics.failure_log) == 0
        assert len(diagnostics.constraint_violations) == 0
        assert diagnostics.total_attempts == 0
        assert diagnostics.successful_placements == 0


class TestFailureLogging:
    """Test failure logging functionality"""

    def test_log_failure_basic(self):
        """Test basic failure logging"""
        diagnostics = SchedulingDiagnostics()
        lesson = Lesson(1, "Math", 5)
        reason = "Teacher conflict"
        context = {
            'class_id': 101,
            'teacher_id': 201,
            'attempted_slots': [(0, 1), (0, 2)],
            'constraint_violations': ['teacher_availability'],
            'backtrack_depth': 2
        }
        
        diagnostics.log_failure(lesson, reason, context)
        
        assert len(diagnostics.failure_log) == 1
        failure = diagnostics.failure_log[0]
        
        assert failure.lesson_id == 1
        assert failure.lesson_name == "Math"
        assert failure.reason == reason
        assert failure.class_id == 101
        assert failure.teacher_id == 201
        assert failure.weekly_hours == 5
        assert failure.attempted_slots == [(0, 1), (0, 2)]
        assert failure.constraint_violations == ['teacher_availability']
        assert failure.backtrack_depth == 2

    def test_log_failure_updates_statistics(self):
        """Test that failure logging updates internal statistics"""
        diagnostics = SchedulingDiagnostics()
        lesson = Lesson(1, "Math", 5)
        context = {
            'class_id': 101,
            'teacher_id': 201,
            'attempted_slots': [(0, 1), (1, 2)],
            'constraint_violations': ['teacher_availability', 'workload_distribution']
        }
        
        diagnostics.log_failure(lesson, "Teacher conflict", context)
        
        # Check constraint violations tracking
        assert diagnostics.constraint_violations['teacher_availability'] == 1
        assert diagnostics.constraint_violations['workload_distribution'] == 1
        
        # Check lesson failures tracking
        assert diagnostics.lesson_failures[1] == 1
        
        # Check teacher conflicts tracking
        assert diagnostics.teacher_conflicts[201] == 1
        
        # Check slot conflicts tracking
        assert diagnostics.slot_conflicts[(0, 1)] == 1
        assert diagnostics.slot_conflicts[(1, 2)] == 1

    def test_log_multiple_failures(self):
        """Test logging multiple failures"""
        diagnostics = SchedulingDiagnostics()
        
        # Log first failure
        lesson1 = Lesson(1, "Math", 5)
        diagnostics.log_failure(lesson1, "Teacher conflict", {
            'teacher_id': 201,
            'constraint_violations': ['teacher_availability']
        })
        
        # Log second failure for same lesson
        diagnostics.log_failure(lesson1, "Class conflict", {
            'class_id': 101,
            'constraint_violations': ['class_scheduling']
        })
        
        assert len(diagnostics.failure_log) == 2
        assert diagnostics.lesson_failures[1] == 2
        assert diagnostics.constraint_violations['teacher_availability'] == 1
        assert diagnostics.constraint_violations['class_scheduling'] == 1


class TestPerformanceMetrics:
    """Test performance metrics collection"""

    def test_log_phase_timing(self):
        """Test phase timing logging"""
        diagnostics = SchedulingDiagnostics()
        
        diagnostics.log_phase_timing("initialization", 1.5)
        diagnostics.log_phase_timing("scheduling", 10.2)
        diagnostics.log_phase_timing("initialization", 1.8)  # Second call to same phase
        
        assert len(diagnostics.phase_timings["initialization"]) == 2
        assert diagnostics.phase_timings["initialization"] == [1.5, 1.8]
        assert len(diagnostics.phase_timings["scheduling"]) == 1
        assert diagnostics.phase_timings["scheduling"] == [10.2]

    def test_record_attempt(self):
        """Test attempt recording"""
        diagnostics = SchedulingDiagnostics()
        
        diagnostics.record_attempt(successful=True)
        diagnostics.record_attempt(successful=False)
        diagnostics.record_attempt(successful=True)
        
        assert diagnostics.total_attempts == 3
        assert diagnostics.successful_placements == 2

    def test_record_backtrack(self):
        """Test backtrack recording"""
        diagnostics = SchedulingDiagnostics()
        
        diagnostics.record_backtrack()
        diagnostics.record_backtrack()
        
        assert diagnostics.backtrack_attempts == 2

    def test_record_constraint_relaxation(self):
        """Test constraint relaxation recording"""
        diagnostics = SchedulingDiagnostics()
        
        diagnostics.record_constraint_relaxation()
        diagnostics.record_constraint_relaxation()
        diagnostics.record_constraint_relaxation()
        
        assert diagnostics.constraint_relaxations == 3

    def test_generate_performance_metrics(self):
        """Test comprehensive performance metrics generation"""
        diagnostics = SchedulingDiagnostics()
        diagnostics.start_session()
        
        # Add some test data
        diagnostics.record_attempt(successful=True)
        diagnostics.record_attempt(successful=False)
        diagnostics.record_attempt(successful=True)
        diagnostics.record_backtrack()
        diagnostics.record_constraint_relaxation()
        diagnostics.log_phase_timing("test_phase", 2.5)
        diagnostics.constraint_violations['test_constraint'] = 3
        
        # Wait a bit to ensure duration > 0
        time.sleep(0.01)
        
        metrics = diagnostics.generate_performance_metrics()
        
        assert metrics['total_attempts'] == 3
        assert metrics['successful_placements'] == 2
        assert metrics['failed_attempts'] == 0  # No failures logged
        assert metrics['success_rate'] == 2/3
        assert metrics['backtrack_attempts'] == 1
        assert metrics['backtrack_rate'] == 1/3
        assert metrics['constraint_relaxations'] == 1
        assert metrics['session_duration'] > 0
        assert 'test_phase' in metrics['phase_timings']
        assert metrics['phase_timings']['test_phase']['total_time'] == 2.5
        assert metrics['constraint_violations_total'] == 3


class TestUtilizationTracking:
    """Test teacher and class utilization tracking"""

    def test_update_teacher_utilization(self):
        """Test teacher utilization updates"""
        diagnostics = SchedulingDiagnostics()
        
        utilization_data = {
            'scheduled_hours': 20,
            'available_hours': 25,
            'utilization_rate': 0.8,
            'empty_days': 1
        }
        
        diagnostics.update_teacher_utilization(101, utilization_data)
        
        assert diagnostics.teacher_utilization[101] == utilization_data

    def test_update_class_utilization(self):
        """Test class utilization updates"""
        diagnostics = SchedulingDiagnostics()
        
        utilization_data = {
            'scheduled_hours': 30,
            'total_slots': 35,
            'utilization_rate': 0.857,
            'curriculum_completion': 0.95
        }
        
        diagnostics.update_class_utilization(201, utilization_data)
        
        assert diagnostics.class_utilization[201] == utilization_data

    def test_analyze_teacher_class_utilization(self):
        """Test teacher and class utilization analysis"""
        diagnostics = SchedulingDiagnostics()
        
        # Add some utilization data
        diagnostics.update_teacher_utilization(101, {'utilization_rate': 0.3})  # Underutilized
        diagnostics.update_teacher_utilization(102, {'utilization_rate': 0.95})  # Overutilized
        diagnostics.update_class_utilization(201, {'utilization_rate': 0.4})  # Underutilized
        
        # Add some slot conflicts
        diagnostics.slot_conflicts[(0, 1)] = 5
        diagnostics.slot_conflicts[(1, 2)] = 3
        diagnostics.slot_conflicts[(2, 3)] = 8
        
        report = diagnostics.analyze_teacher_class_utilization()
        
        assert isinstance(report, UtilizationReport)
        assert len(report.teacher_utilization) == 2
        assert len(report.class_utilization) == 1
        assert len(report.peak_usage_times) > 0
        
        # Check underutilized resources
        underutilized = report.underutilized_resources
        assert len(underutilized) == 2  # One teacher and one class
        assert ('teacher', 101, 0.3) in underutilized
        assert ('class', 201, 0.4) in underutilized
        
        # Check overutilized resources
        overutilized = report.overutilized_resources
        assert len(overutilized) == 1
        assert ('teacher', 102, 0.95) in overutilized


class TestBottleneckAnalysis:
    """Test bottleneck analysis functionality"""

    def test_analyze_bottlenecks_basic(self):
        """Test basic bottleneck analysis"""
        diagnostics = SchedulingDiagnostics()
        
        # Add some conflict data
        diagnostics.teacher_conflicts[101] = 5
        diagnostics.teacher_conflicts[102] = 3
        diagnostics.class_conflicts[201] = 4
        diagnostics.slot_conflicts[(0, 1)] = 7
        diagnostics.lesson_failures[301] = 2
        
        report = diagnostics.analyze_bottlenecks()
        
        assert isinstance(report, BottleneckReport)
        assert len(report.most_constrained_teachers) <= 10
        assert len(report.most_constrained_classes) <= 10
        assert len(report.peak_conflict_slots) <= 20
        
        # Check that teachers are sorted by conflict count
        if len(report.most_constrained_teachers) > 1:
            assert report.most_constrained_teachers[0][2] >= report.most_constrained_teachers[1][2]

    @patch('algorithms.scheduling_diagnostics.BottleneckAnalyzer')
    def test_analyze_bottlenecks_uses_advanced_analyzer(self, mock_analyzer_class):
        """Test that bottleneck analysis uses the advanced analyzer"""
        mock_analyzer = Mock()
        mock_analyzer_class.return_value = mock_analyzer
        
        # Mock the analyzer methods
        mock_bottlenecks = [
            Mock(resource_type='teacher', resource_id=101, resource_name='Teacher_101', conflict_count=5),
            Mock(resource_type='class', resource_id=201, resource_name='Class_201', conflict_count=3)
        ]
        mock_analyzer.identify_resource_bottlenecks.return_value = mock_bottlenecks
        
        diagnostics = SchedulingDiagnostics()
        diagnostics.bottleneck_analyzer = mock_analyzer
        
        report = diagnostics.analyze_bottlenecks()
        
        # Verify the analyzer was called
        mock_analyzer.identify_resource_bottlenecks.assert_called_once()

    def test_get_advanced_bottleneck_analysis(self):
        """Test advanced bottleneck analysis integration"""
        diagnostics = SchedulingDiagnostics()
        
        # Mock the bottleneck analyzer
        mock_analyzer = Mock()
        diagnostics.bottleneck_analyzer = mock_analyzer
        
        # Mock return values
        mock_bottlenecks = [
            Mock(
                resource_type='teacher',
                resource_id=101,
                resource_name='Teacher_101',
                bottleneck_score=8.5,
                conflict_count=5,
                utilization_rate=0.9,
                improvement_potential=0.7,
                affected_lessons=[1, 2, 3],
                peak_conflict_times=[(0, 1), (1, 2)]
            )
        ]
        mock_constraints = [
            Mock(
                constraint_type='teacher_availability',
                frequency=10,
                severity_score=7.2,
                affected_resources=[('teacher', 101)],
                resolution_suggestions=['Adjust availability windows']
            )
        ]
        mock_patterns = [
            Mock(
                resource_type='teacher',
                resource_id=101,
                average_utilization=0.85,
                efficiency_score=0.6,
                variance=0.15
            )
        ]
        
        mock_analyzer.identify_resource_bottlenecks.return_value = mock_bottlenecks
        mock_analyzer.analyze_constraint_patterns.return_value = mock_constraints
        mock_analyzer.analyze_utilization_patterns.return_value = mock_patterns
        mock_analyzer.generate_targeted_improvements.return_value = ['Improve teacher scheduling']
        
        analysis = diagnostics.get_advanced_bottleneck_analysis()
        
        assert 'resource_bottlenecks' in analysis
        assert 'constraint_analyses' in analysis
        assert 'utilization_patterns' in analysis
        assert 'targeted_improvements' in analysis
        
        # Check resource bottlenecks structure
        bottleneck = analysis['resource_bottlenecks'][0]
        assert bottleneck['type'] == 'teacher'
        assert bottleneck['id'] == 101
        assert bottleneck['score'] == 8.5
        assert bottleneck['conflicts'] == 5


class TestHealthScoring:
    """Test scheduling health score calculation"""

    def test_get_scheduling_health_score_excellent(self):
        """Test health score calculation for excellent performance"""
        diagnostics = SchedulingDiagnostics()
        
        # Set up excellent performance metrics
        diagnostics.total_attempts = 100
        diagnostics.successful_placements = 95
        diagnostics.backtrack_attempts = 5
        diagnostics.constraint_relaxations = 2
        
        health = diagnostics.get_scheduling_health_score()
        
        assert health['overall_score'] >= 90
        assert health['health_status'] == 'EXCELLENT'
        assert health['component_scores']['success_rate'] >= 90
        assert 'recommendations' in health

    def test_get_scheduling_health_score_poor(self):
        """Test health score calculation for poor performance"""
        diagnostics = SchedulingDiagnostics()
        
        # Set up poor performance metrics
        diagnostics.total_attempts = 100
        diagnostics.successful_placements = 30
        diagnostics.backtrack_attempts = 60
        diagnostics.constraint_relaxations = 40
        diagnostics.teacher_conflicts[101] = 20
        diagnostics.class_conflicts[201] = 15
        diagnostics.constraint_violations['teacher_availability'] = 25
        
        health = diagnostics.get_scheduling_health_score()
        
        assert health['overall_score'] < 60
        assert health['health_status'] in ['POOR', 'CRITICAL']
        assert len(health['recommendations']) > 0

    def test_health_recommendations(self):
        """Test health-based recommendations"""
        diagnostics = SchedulingDiagnostics()
        
        # Set up scenario with specific issues
        diagnostics.total_attempts = 100
        diagnostics.successful_placements = 50  # Low success rate
        diagnostics.teacher_conflicts[101] = 30  # High conflicts
        
        health = diagnostics.get_scheduling_health_score()
        recommendations = health['recommendations']
        
        assert len(recommendations) > 0
        # Should include success rate improvement recommendation
        success_rec = any('success rate' in rec.lower() for rec in recommendations)
        assert success_rec


class TestConstraintViolationTracking:
    """Test constraint violation statistics tracking"""

    def test_track_constraint_violations_by_type(self):
        """Test constraint violation tracking by type"""
        diagnostics = SchedulingDiagnostics()
        
        # Add some violations
        diagnostics.constraint_violations['teacher_availability'] = 5
        diagnostics.constraint_violations['block_rules'] = 3
        diagnostics.constraint_violations['workload_distribution'] = 2
        
        violations = diagnostics.track_constraint_violations_by_type()
        
        assert violations['teacher_availability'] == 5
        assert violations['block_rules'] == 3
        assert violations['workload_distribution'] == 2
        assert len(violations) == 3

    def test_constraint_violations_from_failures(self):
        """Test that constraint violations are tracked from failure logs"""
        diagnostics = SchedulingDiagnostics()
        lesson = Lesson(1, "Math", 5)
        
        # Log failure with multiple constraint violations
        context = {
            'constraint_violations': ['teacher_availability', 'block_rules', 'teacher_availability']
        }
        diagnostics.log_failure(lesson, "Multiple constraints", context)
        
        violations = diagnostics.track_constraint_violations_by_type()
        
        assert violations['teacher_availability'] == 2  # Appears twice
        assert violations['block_rules'] == 1


class TestFailureSummary:
    """Test failure summary functionality"""

    def test_get_failure_summary_empty(self):
        """Test failure summary with no failures"""
        diagnostics = SchedulingDiagnostics()
        
        summary = diagnostics.get_failure_summary()
        
        assert summary['total_failures'] == 0
        assert summary['failure_details'] == []

    def test_get_failure_summary_with_failures(self):
        """Test failure summary with multiple failures"""
        diagnostics = SchedulingDiagnostics()
        
        # Add some failures
        lesson1 = Lesson(1, "Math", 5)
        lesson2 = Lesson(2, "Science", 3)
        
        diagnostics.log_failure(lesson1, "Teacher conflict", {
            'backtrack_depth': 2,
            'attempted_slots': [(0, 1), (0, 2)]
        })
        diagnostics.log_failure(lesson2, "Teacher conflict", {
            'backtrack_depth': 1,
            'attempted_slots': [(1, 1)]
        })
        diagnostics.log_failure(lesson1, "Block rules", {
            'backtrack_depth': 3,
            'attempted_slots': [(2, 1), (2, 2), (2, 3)]
        })
        
        summary = diagnostics.get_failure_summary()
        
        assert summary['total_failures'] == 3
        assert summary['unique_failure_reasons'] == 2
        
        # Check failure details
        details = summary['failure_details']
        assert len(details) == 2
        
        # Should be sorted by count (Teacher conflict appears twice)
        assert details[0]['reason'] == 'Teacher conflict'
        assert details[0]['count'] == 2
        assert details[1]['reason'] == 'Block rules'
        assert details[1]['count'] == 1


@pytest.fixture
def db_manager():
    """Mock database manager for testing"""
    mock_db = Mock()
    mock_db.get_school_type.return_value = "Lise"
    return mock_db


@pytest.fixture
def sample_lesson():
    """Sample lesson for testing"""
    return Lesson(1, "Mathematics", 5)


@pytest.fixture
def sample_context():
    """Sample context for failure logging"""
    return {
        'class_id': 101,
        'teacher_id': 201,
        'attempted_slots': [(0, 1), (0, 2), (1, 1)],
        'constraint_violations': ['teacher_availability', 'workload_distribution'],
        'backtrack_depth': 2,
        'alternative_blocks_tried': [(2, 2, 1), (3, 1, 1)]
    }