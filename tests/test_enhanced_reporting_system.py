# -*- coding: utf-8 -*-
"""
Tests for Enhanced Reporting System - Comprehensive reporting system testing

This module tests the enhanced reporting functionality including completion reports,
failure analysis reports, performance metrics, and various report formats.

Requirements tested: 5.1, 5.4, 5.5
"""

import json
import pytest
from unittest.mock import Mock, MagicMock
from algorithms.enhanced_reporting_system import (
    EnhancedReportingSystem, CompletionReport, FailureAnalysisReport, 
    PerformanceReport, ReportType, ReportFormat
)
from algorithms.optimized_curriculum_scheduler import (
    ScheduleResult, EnhancedScheduleEntry, WorkloadViolation, PlacementMethod, ConstraintLevel
)
from algorithms.solution_validator import ValidationReport, ValidationViolation, ViolationType
from algorithms.scheduling_diagnostics import SchedulingDiagnostics, FailureEntry, BottleneckReport


class TestEnhancedReportingSystem:
    """Test enhanced reporting system core functionality"""
    
    @pytest.fixture
    def reporting_system(self):
        """Create reporting system instance"""
        mock_db = Mock()
        return EnhancedReportingSystem(mock_db)
    
    @pytest.fixture
    def sample_schedule_result(self):
        """Create sample schedule result for testing"""
        entries = [
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
            )
        ]
        
        return ScheduleResult(
            entries=entries,
            completion_rate=85.5,
            total_hours=279,
            scheduled_hours=238,
            execution_time=45.2,
            success=False,
            performance_metrics={"phase_1": 20.1, "phase_2": 25.1},
            teacher_utilization={1: 75.0, 2: 60.0},
            class_utilization={1: 80.0, 2: 70.0},
            backtrack_statistics={
                "total_backtracks": 150,
                "successful_backtracks": 120,
                "max_depth_reached": 8,
                "constraint_relaxations": 5
            },
            alternative_block_usage={
                "standard_blocks": 200,
                "alternative_blocks": 30,
                "relaxed_blocks": 8,
                "backtracked_blocks": 0
            }
        )
    
    @pytest.fixture
    def sample_validation_report(self):
        """Create sample validation report"""
        return ValidationReport(
            is_valid=False,
            total_violations=5,
            critical_violations=[
                ValidationViolation(ViolationType.TEACHER_CONFLICT, "critical", "Teacher conflict", [])
            ],
            major_violations=[
                ValidationViolation(ViolationType.BLOCK_RULE_VIOLATION, "major", "Block violation", []),
                ValidationViolation(ViolationType.WORKLOAD_VIOLATION, "major", "Workload violation", [])
            ],
            minor_violations=[
                ValidationViolation(ViolationType.CURRICULUM_VIOLATION, "minor", "Minor curriculum issue", []),
                ValidationViolation(ViolationType.AVAILABILITY_VIOLATION, "minor", "Minor availability issue", [])
            ],
            validation_metrics={
                "quality_score": 78.5,
                "validation_passed": False,
                "total_entries_validated": 238
            },
            recommendations=["Fix teacher conflicts", "Improve block placement", "Balance workload"]
        )
    
    @pytest.fixture
    def sample_diagnostics(self):
        """Create sample diagnostics data"""
        diagnostics = Mock(spec=SchedulingDiagnostics)
        
        # Mock failure log
        diagnostics.failure_log = [
            FailureEntry(
                lesson_id=1, lesson_name="Mathematics", class_id=1, teacher_id=1,
                weekly_hours=3, reason="Teacher conflict", timestamp=1234567890.0,
                context={"attempted_slots": [(0, 0), (0, 1)]},
                attempted_slots=[(0, 0), (0, 1)], constraint_violations=["teacher_conflict"]
            ),
            FailureEntry(
                lesson_id=2, lesson_name="Physics", class_id=2, teacher_id=2,
                weekly_hours=2, reason="Block placement failed", timestamp=1234567891.0,
                context={"attempted_slots": [(1, 0)]},
                attempted_slots=[(1, 0)], constraint_violations=["block_rule"]
            )
        ]
        
        # Mock methods
        diagnostics.get_failure_summary.return_value = {
            "total_failures": 2,
            "failure_details": [
                {"reason": "Teacher conflict", "count": 1},
                {"reason": "Block placement failed", "count": 1}
            ]
        }
        
        diagnostics.analyze_bottlenecks.return_value = BottleneckReport(
            most_constrained_teachers=[(1, "Teacher 1", 5)],
            most_constrained_classes=[(1, "Class 1", 3)],
            peak_conflict_slots=[(0, 0, 8)],
            constraint_type_frequency={"teacher_conflict": 3, "block_rule": 2},
            resource_utilization={"teacher_conflict_rate": 0.15},
            critical_lessons=[(1, "Mathematics", 2)]
        )
        
        diagnostics.generate_improvement_suggestions.return_value = [
            "Increase teacher availability",
            "Review block placement rules"
        ]
        
        diagnostics.get_scheduling_health_score.return_value = {
            "overall_score": 72.5,
            "health_status": "FAIR"
        }
        
        return diagnostics
    
    def test_reporting_system_initialization(self, reporting_system):
        """Test reporting system initialization"""
        assert reporting_system is not None
        assert len(reporting_system.report_templates) == 7
        assert ReportType.COMPLETION_SUMMARY in reporting_system.report_templates
        assert ReportType.FAILURE_ANALYSIS in reporting_system.report_templates
        assert ReportType.PERFORMANCE_METRICS in reporting_system.report_templates


class TestCompletionReporting:
    """Test completion report generation"""
    
    @pytest.fixture
    def reporting_system(self):
        """Create reporting system instance"""
        return EnhancedReportingSystem()
    
    def test_generate_comprehensive_report_text_format(self, reporting_system, sample_schedule_result, sample_validation_report):
        """Test comprehensive report generation in text format"""
        report = reporting_system.generate_comprehensive_report(
            sample_schedule_result, sample_validation_report, format=ReportFormat.TEXT
        )
        
        assert isinstance(report, str)
        assert "SCHEDULER OPTIMIZATION - COMPLETION REPORT" in report
        assert "85.5%" in report  # Completion rate
        assert "238/279" in report  # Scheduled/total hours
        assert "45.2" in report  # Execution time
        assert "RECOMMENDATIONS" in report
    
    def test_generate_comprehensive_report_json_format(self, reporting_system, sample_schedule_result):
        """Test comprehensive report generation in JSON format"""
        report = reporting_system.generate_comprehensive_report(
            sample_schedule_result, format=ReportFormat.JSON
        )
        
        assert isinstance(report, str)
        
        # Parse JSON to verify structure
        report_data = json.loads(report)
        assert "completion_rate" in report_data
        assert "scheduled_hours" in report_data
        assert "execution_time" in report_data
        assert report_data["completion_rate"] == 85.5
        assert report_data["scheduled_hours"] == 238
    
    def test_generate_comprehensive_report_html_format(self, reporting_system, sample_schedule_result):
        """Test comprehensive report generation in HTML format"""
        report = reporting_system.generate_comprehensive_report(
            sample_schedule_result, format=ReportFormat.HTML
        )
        
        assert isinstance(report, str)
        assert "<!DOCTYPE html>" in report
        assert "<title>Scheduler Optimization - Completion Report</title>" in report
        assert "85.5%" in report  # Completion rate
        assert "238/279" in report  # Scheduled/total hours
    
    def test_generate_comprehensive_report_markdown_format(self, reporting_system, sample_schedule_result):
        """Test comprehensive report generation in Markdown format"""
        report = reporting_system.generate_comprehensive_report(
            sample_schedule_result, format=ReportFormat.MARKDOWN
        )
        
        assert isinstance(report, str)
        assert "# Scheduler Optimization - Completion Report" in report
        assert "**Completion Rate:** 85.5%" in report
        assert "**Scheduled Hours:** 238/279" in report
        assert "## Summary" in report
    
    def test_create_completion_report(self, reporting_system, sample_schedule_result, sample_validation_report, sample_diagnostics):
        """Test completion report creation"""
        completion_report = reporting_system._create_completion_report(
            sample_schedule_result, sample_validation_report, sample_diagnostics
        )
        
        assert isinstance(completion_report, CompletionReport)
        assert completion_report.completion_rate == 85.5
        assert completion_report.scheduled_hours == 238
        assert completion_report.total_required_hours == 279
        assert not completion_report.success
        assert completion_report.execution_time == 45.2
        assert completion_report.quality_score > 0
        assert len(completion_report.recommendations) > 0
        assert len(completion_report.next_steps) > 0
    
    def test_calculate_quality_score_high_completion(self, reporting_system):
        """Test quality score calculation with high completion rate"""
        schedule_result = Mock()
        schedule_result.completion_rate = 95.0
        schedule_result.execution_time = 30.0  # Under 30 seconds
        
        validation_report = Mock()
        validation_report.critical_violations = []
        validation_report.major_violations = []
        validation_report.minor_violations = []
        
        quality_score = reporting_system._calculate_quality_score(schedule_result, validation_report)
        
        assert quality_score == 100.0  # 95 + 5 (performance bonus) = 100, capped at 100
    
    def test_calculate_quality_score_with_violations(self, reporting_system):
        """Test quality score calculation with violations"""
        schedule_result = Mock()
        schedule_result.completion_rate = 90.0
        schedule_result.execution_time = 45.0  # Normal time
        
        validation_report = Mock()
        validation_report.critical_violations = [Mock()]  # 1 critical = -10
        validation_report.major_violations = [Mock(), Mock()]  # 2 major = -10
        validation_report.minor_violations = [Mock()]  # 1 minor = -1
        
        quality_score = reporting_system._calculate_quality_score(schedule_result, validation_report)
        
        assert quality_score == 69.0  # 90 - 10 - 10 - 1 = 69
    
    def test_calculate_constraint_compliance(self, reporting_system, sample_validation_report):
        """Test constraint compliance calculation"""
        compliance = reporting_system._calculate_constraint_compliance(sample_validation_report)
        
        assert isinstance(compliance, dict)
        assert len(compliance) > 0
        
        # Should have compliance rates for each violation type
        for violation_type, rate in compliance.items():
            assert 0.0 <= rate <= 100.0
    
    def test_calculate_workload_balance_score(self, reporting_system, sample_schedule_result):
        """Test workload balance score calculation"""
        balance_score = reporting_system._calculate_workload_balance_score(sample_schedule_result)
        
        assert isinstance(balance_score, float)
        assert 0.0 <= balance_score <= 100.0
    
    def test_calculate_time_slot_utilization(self, reporting_system, sample_schedule_result):
        """Test time slot utilization calculation"""
        utilization = reporting_system._calculate_time_slot_utilization(sample_schedule_result.entries)
        
        assert isinstance(utilization, dict)
        assert len(utilization) > 0
        
        # Check that utilization values are percentages
        for slot, util in utilization.items():
            assert 0.0 <= util <= 100.0
            assert "Day_" in slot and "Slot_" in slot


class TestFailureAnalysisReporting:
    """Test failure analysis report generation"""
    
    @pytest.fixture
    def reporting_system(self):
        """Create reporting system instance"""
        return EnhancedReportingSystem()
    
    def test_generate_failure_analysis_report_text(self, reporting_system, sample_schedule_result, sample_diagnostics):
        """Test failure analysis report generation in text format"""
        report = reporting_system.generate_failure_analysis_report(
            sample_schedule_result, sample_diagnostics, ReportFormat.TEXT
        )
        
        assert isinstance(report, str)
        assert "FAILURE ANALYSIS REPORT" in report
        assert "Total Failures: 2" in report
        assert "Unscheduled Hours: 41" in report  # 279 - 238
        assert "FAILURES BY REASON" in report
        assert "CRITICAL FAILURES" in report
    
    def test_generate_failure_analysis_report_json(self, reporting_system, sample_schedule_result, sample_diagnostics):
        """Test failure analysis report generation in JSON format"""
        report = reporting_system.generate_failure_analysis_report(
            sample_schedule_result, sample_diagnostics, ReportFormat.JSON
        )
        
        assert isinstance(report, str)
        
        # Parse JSON to verify structure
        report_data = json.loads(report)
        assert "total_failures" in report_data
        assert "unscheduled_hours" in report_data
        assert "failures_by_reason" in report_data
        assert report_data["total_failures"] == 2
        assert report_data["unscheduled_hours"] == 41
    
    def test_create_failure_analysis_report(self, reporting_system, sample_schedule_result, sample_diagnostics):
        """Test failure analysis report creation"""
        failure_report = reporting_system._create_failure_analysis_report(
            sample_schedule_result, sample_diagnostics
        )
        
        assert isinstance(failure_report, FailureAnalysisReport)
        assert failure_report.total_failures == 2
        assert failure_report.unscheduled_hours == 41
        assert len(failure_report.failures_by_reason) > 0
        assert len(failure_report.failures_by_lesson) > 0
        assert failure_report.bottlenecks is not None
        assert len(failure_report.systemic_improvements) > 0
    
    def test_analyze_failures_by_reason(self, reporting_system, sample_diagnostics):
        """Test failure analysis by reason"""
        failures_by_reason = reporting_system._analyze_failures_by_reason(sample_diagnostics.failure_log)
        
        assert isinstance(failures_by_reason, dict)
        assert "Teacher conflict" in failures_by_reason
        assert "Block placement failed" in failures_by_reason
        assert failures_by_reason["Teacher conflict"] == 1
        assert failures_by_reason["Block placement failed"] == 1
    
    def test_analyze_failures_by_lesson(self, reporting_system, sample_diagnostics):
        """Test failure analysis by lesson"""
        failures_by_lesson = reporting_system._analyze_failures_by_lesson(sample_diagnostics.failure_log)
        
        assert isinstance(failures_by_lesson, dict)
        assert "Mathematics" in failures_by_lesson
        assert "Physics" in failures_by_lesson
        assert failures_by_lesson["Mathematics"] == 1
        assert failures_by_lesson["Physics"] == 1
    
    def test_identify_critical_failures(self, reporting_system):
        """Test critical failure identification"""
        # Create failure log with repeated failures
        failure_log = [
            FailureEntry(1, "Mathematics", 1, 1, 3, "Teacher conflict", 123.0, {}, [], []),
            FailureEntry(1, "Mathematics", 1, 1, 3, "Block placement", 124.0, {}, [], []),
            FailureEntry(1, "Mathematics", 1, 1, 3, "Availability", 125.0, {}, [], []),
            FailureEntry(2, "Physics", 2, 2, 2, "Teacher conflict", 126.0, {}, [], []),
        ]
        
        critical_failures = reporting_system._identify_critical_failures(failure_log)
        
        assert isinstance(critical_failures, list)
        assert len(critical_failures) == 1  # Only Mathematics has 3+ failures
        assert critical_failures[0]["lesson_name"] == "Mathematics"
        assert critical_failures[0]["failure_count"] == 3
        assert critical_failures[0]["severity"] == "critical"
    
    def test_generate_specific_fixes(self, reporting_system, sample_schedule_result, sample_diagnostics):
        """Test specific fix generation"""
        fixes = reporting_system._generate_specific_fixes(sample_schedule_result, sample_diagnostics)
        
        assert isinstance(fixes, list)
        assert len(fixes) > 0
        
        # Check fix structure
        for fix in fixes:
            assert "type" in fix
            assert "resource" in fix
            assert "problem" in fix
            assert "fix" in fix
            assert "priority" in fix


class TestPerformanceReporting:
    """Test performance report generation"""
    
    @pytest.fixture
    def reporting_system(self):
        """Create reporting system instance"""
        return EnhancedReportingSystem()
    
    def test_generate_performance_report_text(self, reporting_system, sample_schedule_result):
        """Test performance report generation in text format"""
        report = reporting_system.generate_performance_report(
            sample_schedule_result, format=ReportFormat.TEXT
        )
        
        assert isinstance(report, str)
        assert "PERFORMANCE REPORT" in report
        assert "45.2s" in report  # Execution time
        assert "Scheduling Rate:" in report
        assert "Success Rate:" in report
        assert "OPTIMIZATION SUGGESTIONS" in report
    
    def test_generate_performance_report_json(self, reporting_system, sample_schedule_result):
        """Test performance report generation in JSON format"""
        report = reporting_system.generate_performance_report(
            sample_schedule_result, format=ReportFormat.JSON
        )
        
        assert isinstance(report, str)
        
        # Parse JSON to verify structure
        report_data = json.loads(report)
        assert "execution_time" in report_data
        assert "scheduling_rate" in report_data
        assert "success_rate" in report_data
        assert report_data["execution_time"] == 45.2
    
    def test_create_performance_report(self, reporting_system, sample_schedule_result):
        """Test performance report creation"""
        performance_report = reporting_system._create_performance_report(
            sample_schedule_result, None
        )
        
        assert isinstance(performance_report, PerformanceReport)
        assert performance_report.execution_time == 45.2
        assert performance_report.target_time == 60.0
        assert performance_report.scheduling_rate > 0
        assert 0.0 <= performance_report.success_rate <= 1.0
        assert performance_report.backtrack_efficiency >= 0
        assert len(performance_report.optimization_suggestions) > 0
    
    def test_calculate_backtrack_efficiency(self, reporting_system, sample_schedule_result):
        """Test backtracking efficiency calculation"""
        efficiency = reporting_system._calculate_backtrack_efficiency(sample_schedule_result)
        
        assert isinstance(efficiency, float)
        assert 0.0 <= efficiency <= 100.0
        # With 120 successful out of 150 total: (120/150)*100 = 80.0
        assert efficiency == 80.0
    
    def test_calculate_constraint_relaxation_effectiveness(self, reporting_system, sample_schedule_result):
        """Test constraint relaxation effectiveness calculation"""
        effectiveness = reporting_system._calculate_constraint_relaxation_effectiveness(sample_schedule_result)
        
        assert isinstance(effectiveness, float)
        assert 0.0 <= effectiveness <= 100.0
    
    def test_calculate_scalability_metrics(self, reporting_system, sample_schedule_result):
        """Test scalability metrics calculation"""
        metrics = reporting_system._calculate_scalability_metrics(sample_schedule_result)
        
        assert isinstance(metrics, dict)
        assert "entries_per_second" in metrics
        assert "estimated_capacity" in metrics
        assert "scalability_rating" in metrics
        assert metrics["entries_per_second"] > 0
    
    def test_generate_optimization_suggestions(self, reporting_system, sample_schedule_result):
        """Test optimization suggestions generation"""
        suggestions = reporting_system._generate_optimization_suggestions(sample_schedule_result, None)
        
        assert isinstance(suggestions, list)
        assert len(suggestions) <= 5  # Should limit to top 5
        
        # Should not suggest time optimization since execution time < 60s
        time_suggestions = [s for s in suggestions if "time" in s.lower() or "termination" in s.lower()]
        assert len(time_suggestions) == 0


class TestStakeholderReporting:
    """Test stakeholder-specific reporting"""
    
    @pytest.fixture
    def reporting_system(self):
        """Create reporting system instance"""
        return EnhancedReportingSystem()
    
    def test_generate_administrator_summary(self, reporting_system, sample_schedule_result, sample_validation_report):
        """Test administrator summary generation"""
        summary = reporting_system.generate_stakeholder_summary(
            sample_schedule_result, sample_validation_report, "administrator"
        )
        
        assert isinstance(summary, str)
        assert "ADMINISTRATOR SUMMARY" in summary
        assert "85.5%" in summary  # Completion rate
        assert "238/279" in summary  # Hours scheduled
        assert "VALIDATION STATUS" in summary
        assert "Critical Issues:" in summary
    
    def test_generate_teacher_summary(self, reporting_system, sample_schedule_result, sample_validation_report):
        """Test teacher summary generation"""
        summary = reporting_system.generate_stakeholder_summary(
            sample_schedule_result, sample_validation_report, "teacher"
        )
        
        assert isinstance(summary, str)
        assert "TEACHER SUMMARY" in summary
        assert "85.5%" in summary  # Completion rate
        assert "WORKLOAD DISTRIBUTION" in summary
        assert "SCHEDULE QUALITY" in summary
    
    def test_generate_coordinator_summary(self, reporting_system, sample_schedule_result, sample_validation_report):
        """Test coordinator summary generation"""
        summary = reporting_system.generate_stakeholder_summary(
            sample_schedule_result, sample_validation_report, "coordinator"
        )
        
        assert isinstance(summary, str)
        assert "COORDINATOR SUMMARY" in summary
        assert "CURRICULUM COVERAGE" in summary
        assert "OPTIMIZATION RESULTS" in summary
        assert "85.5%" in summary  # Completion rate
    
    def test_generate_general_summary(self, reporting_system, sample_schedule_result, sample_validation_report):
        """Test general summary generation"""
        summary = reporting_system.generate_stakeholder_summary(
            sample_schedule_result, sample_validation_report, "unknown_type"
        )
        
        assert isinstance(summary, str)
        assert "SCHEDULE OPTIMIZATION SUMMARY" in summary
        assert "85.5%" in summary  # Completion rate
        assert "238/279" in summary  # Hours scheduled


class TestReportFormatting:
    """Test report formatting functionality"""
    
    @pytest.fixture
    def reporting_system(self):
        """Create reporting system instance"""
        return EnhancedReportingSystem()
    
    @pytest.fixture
    def sample_completion_report(self):
        """Create sample completion report"""
        return CompletionReport(
            timestamp="2023-10-25T10:30:00",
            execution_time=45.2,
            completion_rate=85.5,
            scheduled_hours=238,
            total_required_hours=279,
            success=False,
            quality_score=78.5,
            workload_balance_score=82.0,
            recommendations=["Fix conflicts", "Improve blocks"],
            next_steps=["Review schedule", "Deploy when ready"]
        )
    
    def test_format_as_text(self, reporting_system, sample_completion_report):
        """Test text formatting"""
        text_report = reporting_system._format_as_text(sample_completion_report)
        
        assert isinstance(text_report, str)
        assert "SCHEDULER OPTIMIZATION - COMPLETION REPORT" in text_report
        assert "85.5%" in text_report
        assert "238/279" in text_report
        assert "45.2 seconds" in text_report
        assert "RECOMMENDATIONS" in text_report
        assert "NEXT STEPS" in text_report
    
    def test_format_as_json(self, reporting_system, sample_completion_report):
        """Test JSON formatting"""
        json_report = reporting_system._format_as_json(sample_completion_report)
        
        assert isinstance(json_report, str)
        
        # Parse to verify valid JSON
        report_data = json.loads(json_report)
        assert report_data["completion_rate"] == 85.5
        assert report_data["scheduled_hours"] == 238
        assert report_data["execution_time"] == 45.2
    
    def test_format_as_html(self, reporting_system, sample_completion_report):
        """Test HTML formatting"""
        html_report = reporting_system._format_as_html(sample_completion_report)
        
        assert isinstance(html_report, str)
        assert "<!DOCTYPE html>" in html_report
        assert "<title>Scheduler Optimization - Completion Report</title>" in html_report
        assert "85.5%" in html_report
        assert "238/279" in html_report
        assert "<h1>Scheduler Optimization - Completion Report</h1>" in html_report
    
    def test_format_as_markdown(self, reporting_system, sample_completion_report):
        """Test Markdown formatting"""
        md_report = reporting_system._format_as_markdown(sample_completion_report)
        
        assert isinstance(md_report, str)
        assert "# Scheduler Optimization - Completion Report" in md_report
        assert "**Completion Rate:** 85.5%" in md_report
        assert "**Scheduled Hours:** 238/279" in md_report
        assert "## Summary" in md_report
        assert "## Recommendations" in md_report


class TestReportingIntegration:
    """Test reporting system integration"""
    
    @pytest.fixture
    def reporting_system(self):
        """Create reporting system with mocked database"""
        mock_db = Mock()
        return EnhancedReportingSystem(mock_db)
    
    def test_complete_reporting_workflow(self, reporting_system, sample_schedule_result, sample_validation_report, sample_diagnostics):
        """Test complete reporting workflow"""
        # Test comprehensive report
        comprehensive_report = reporting_system.generate_comprehensive_report(
            sample_schedule_result, sample_validation_report, sample_diagnostics
        )
        assert isinstance(comprehensive_report, str)
        assert len(comprehensive_report) > 0
        
        # Test failure analysis report
        failure_report = reporting_system.generate_failure_analysis_report(
            sample_schedule_result, sample_diagnostics
        )
        assert isinstance(failure_report, str)
        assert len(failure_report) > 0
        
        # Test performance report
        performance_report = reporting_system.generate_performance_report(
            sample_schedule_result, sample_diagnostics
        )
        assert isinstance(performance_report, str)
        assert len(performance_report) > 0
    
    def test_multiple_report_formats(self, reporting_system, sample_schedule_result):
        """Test generating reports in multiple formats"""
        formats = [ReportFormat.TEXT, ReportFormat.JSON, ReportFormat.HTML, ReportFormat.MARKDOWN]
        
        for format_type in formats:
            report = reporting_system.generate_comprehensive_report(
                sample_schedule_result, format=format_type
            )
            assert isinstance(report, str)
            assert len(report) > 0
    
    def test_report_consistency_across_formats(self, reporting_system, sample_schedule_result):
        """Test that key information is consistent across formats"""
        text_report = reporting_system.generate_comprehensive_report(
            sample_schedule_result, format=ReportFormat.TEXT
        )
        json_report = reporting_system.generate_comprehensive_report(
            sample_schedule_result, format=ReportFormat.JSON
        )
        
        # Parse JSON to check consistency
        json_data = json.loads(json_report)
        
        # Key metrics should be consistent
        assert "85.5" in text_report  # Completion rate
        assert json_data["completion_rate"] == 85.5
        
        assert "238" in text_report  # Scheduled hours
        assert json_data["scheduled_hours"] == 238
        
        assert "45.2" in text_report  # Execution time
        assert json_data["execution_time"] == 45.2
    
    def test_error_handling_missing_data(self, reporting_system):
        """Test error handling with missing data"""
        # Create minimal schedule result
        minimal_result = ScheduleResult()
        
        # Should not crash with minimal data
        report = reporting_system.generate_comprehensive_report(minimal_result)
        assert isinstance(report, str)
        assert len(report) > 0
    
    def test_report_generation_performance(self, reporting_system, sample_schedule_result):
        """Test report generation performance"""
        import time
        
        start_time = time.time()
        report = reporting_system.generate_comprehensive_report(sample_schedule_result)
        end_time = time.time()
        
        # Report generation should be fast (< 1 second)
        assert (end_time - start_time) < 1.0
        assert isinstance(report, str)
        assert len(report) > 0