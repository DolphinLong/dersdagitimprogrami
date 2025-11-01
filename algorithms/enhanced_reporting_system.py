# -*- coding: utf-8 -*-
"""
Enhanced Reporting System - Comprehensive reporting for scheduler optimization

This module provides detailed completion reports with diagnostics, failure analysis
reports for unscheduled lessons, and performance metrics with improvement suggestions.
It generates comprehensive reports for stakeholders and provides actionable insights.

Key Features:
- Detailed completion reports with comprehensive diagnostics
- Failure analysis reports for unscheduled lessons
- Performance metrics and improvement suggestions
- Multiple report formats (text, JSON, HTML)
- Stakeholder-specific report views
- Historical trend analysis

Requirements addressed: 5.1, 5.4, 5.5
"""

import json
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum

from algorithms.optimized_curriculum_scheduler import ScheduleResult, EnhancedScheduleEntry, WorkloadViolation
from algorithms.solution_validator import ValidationReport, ValidationViolation
from algorithms.scheduling_diagnostics import SchedulingDiagnostics, FailureEntry, BottleneckReport, UtilizationReport


class ReportType(Enum):
    """Types of reports that can be generated"""
    COMPLETION_SUMMARY = "completion_summary"
    DETAILED_DIAGNOSTICS = "detailed_diagnostics"
    FAILURE_ANALYSIS = "failure_analysis"
    PERFORMANCE_METRICS = "performance_metrics"
    STAKEHOLDER_SUMMARY = "stakeholder_summary"
    TECHNICAL_DETAILS = "technical_details"
    IMPROVEMENT_RECOMMENDATIONS = "improvement_recommendations"


class ReportFormat(Enum):
    """Report output formats"""
    TEXT = "text"
    JSON = "json"
    HTML = "html"
    MARKDOWN = "markdown"


@dataclass
class CompletionReport:
    """Comprehensive completion report with diagnostics"""
    timestamp: str
    execution_time: float
    completion_rate: float
    scheduled_hours: int
    total_required_hours: int
    success: bool
    
    # Detailed metrics
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    validation_results: Optional[ValidationReport] = None
    diagnostics_summary: Dict[str, Any] = field(default_factory=dict)
    
    # Resource utilization
    teacher_utilization: Dict[int, float] = field(default_factory=dict)
    class_utilization: Dict[int, float] = field(default_factory=dict)
    time_slot_utilization: Dict[str, float] = field(default_factory=dict)
    
    # Quality metrics
    quality_score: float = 0.0
    constraint_compliance: Dict[str, float] = field(default_factory=dict)
    workload_balance_score: float = 0.0
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)


@dataclass
class FailureAnalysisReport:
    """Detailed analysis of scheduling failures"""
    timestamp: str
    total_failures: int
    unscheduled_hours: int
    
    # Failure breakdown
    failures_by_reason: Dict[str, int] = field(default_factory=dict)
    failures_by_lesson: Dict[str, int] = field(default_factory=dict)
    failures_by_teacher: Dict[str, int] = field(default_factory=dict)
    failures_by_class: Dict[str, int] = field(default_factory=dict)
    
    # Critical failures
    critical_failures: List[Dict[str, Any]] = field(default_factory=list)
    
    # Bottleneck analysis
    bottlenecks: Optional[BottleneckReport] = None
    
    # Improvement suggestions
    specific_fixes: List[Dict[str, Any]] = field(default_factory=list)
    systemic_improvements: List[str] = field(default_factory=list)


@dataclass
class PerformanceReport:
    """Performance metrics and analysis report"""
    timestamp: str
    execution_time: float
    target_time: float
    
    # Performance breakdown
    phase_timings: Dict[str, Dict[str, float]] = field(default_factory=dict)
    algorithm_metrics: Dict[str, Any] = field(default_factory=dict)
    resource_usage: Dict[str, Any] = field(default_factory=dict)
    
    # Efficiency metrics
    scheduling_rate: float = 0.0  # hours per second
    success_rate: float = 0.0
    backtrack_efficiency: float = 0.0
    constraint_relaxation_effectiveness: float = 0.0
    
    # Scalability analysis
    scalability_metrics: Dict[str, Any] = field(default_factory=dict)
    
    # Performance recommendations
    optimization_suggestions: List[str] = field(default_factory=list)


class EnhancedReportingSystem:
    """
    Comprehensive reporting system for scheduler optimization
    
    Generates detailed reports with diagnostics, failure analysis, and performance
    metrics to provide stakeholders with actionable insights for achieving 100%
    schedule completion.
    """
    
    def __init__(self, db_manager=None):
        """
        Initialize enhanced reporting system
        
        Args:
            db_manager: Database manager for accessing additional data
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.db_manager = db_manager
        
        # Report configuration - placeholder for future template system
        self.report_templates = {
            ReportType.COMPLETION_SUMMARY: "completion_summary",
            ReportType.DETAILED_DIAGNOSTICS: "detailed_diagnostics",
            ReportType.FAILURE_ANALYSIS: "failure_analysis",
            ReportType.PERFORMANCE_METRICS: "performance_metrics",
            ReportType.STAKEHOLDER_SUMMARY: "stakeholder_summary",
            ReportType.TECHNICAL_DETAILS: "technical_details",
            ReportType.IMPROVEMENT_RECOMMENDATIONS: "improvement_recommendations"
        }
        
        self.logger.info("EnhancedReportingSystem initialized")
    
    def generate_comprehensive_report(self, schedule_result: ScheduleResult, 
                                    validation_report: Optional[ValidationReport] = None,
                                    diagnostics: Optional[SchedulingDiagnostics] = None,
                                    report_format: ReportFormat = ReportFormat.TEXT) -> str:
        """
        Generate comprehensive completion report with diagnostics
        
        Args:
            schedule_result: Scheduling result to report on
            validation_report: Optional validation results
            diagnostics: Optional diagnostics data
            report_format: Output format for the report
            
        Returns:
            Formatted comprehensive report
        """
        self.logger.info("Generating comprehensive completion report")
        
        # Create completion report
        completion_report = self._create_completion_report(schedule_result, validation_report, diagnostics)
        
        # Format report based on requested format
        if report_format == ReportFormat.JSON:
            return self._format_as_json(completion_report)
        elif report_format == ReportFormat.HTML:
            return self._format_as_html(completion_report)
        elif report_format == ReportFormat.MARKDOWN:
            return self._format_as_markdown(completion_report)
        else:
            return self._format_as_text(completion_report)
    
    def generate_failure_analysis_report(self, schedule_result: ScheduleResult,
                                       diagnostics: SchedulingDiagnostics,
                                       report_format: ReportFormat = ReportFormat.TEXT) -> str:
        """
        Create failure analysis reports for unscheduled lessons
        
        Args:
            schedule_result: Scheduling result with failures
            diagnostics: Diagnostics data with failure details
            report_format: Output format for the report
            
        Returns:
            Formatted failure analysis report
        """
        self.logger.info("Generating failure analysis report")
        
        # Create failure analysis report
        failure_report = self._create_failure_analysis_report(schedule_result, diagnostics)
        
        # Format report based on requested format
        if report_format == ReportFormat.JSON:
            return self._format_failure_report_as_json(failure_report)
        elif report_format == ReportFormat.HTML:
            return self._format_failure_report_as_html(failure_report)
        elif report_format == ReportFormat.MARKDOWN:
            return self._format_failure_report_as_markdown(failure_report)
        else:
            return self._format_failure_report_as_text(failure_report)
    
    def generate_performance_report(self, schedule_result: ScheduleResult,
                                  diagnostics: Optional[SchedulingDiagnostics] = None,
                                  report_format: ReportFormat = ReportFormat.TEXT) -> str:
        """
        Add performance metrics and improvement suggestions
        
        Args:
            schedule_result: Scheduling result with performance data
            diagnostics: Optional diagnostics data
            report_format: Output format for the report
            
        Returns:
            Formatted performance report
        """
        self.logger.info("Generating performance metrics report")
        
        # Create performance report
        performance_report = self._create_performance_report(schedule_result, diagnostics)
        
        # Format report based on requested format
        if report_format == ReportFormat.JSON:
            return self._format_performance_report_as_json(performance_report)
        elif report_format == ReportFormat.HTML:
            return self._format_performance_report_as_html(performance_report)
        elif report_format == ReportFormat.MARKDOWN:
            return self._format_performance_report_as_markdown(performance_report)
        else:
            return self._format_performance_report_as_text(performance_report)
    
    def generate_stakeholder_summary(self, schedule_result: ScheduleResult,
                                   validation_report: Optional[ValidationReport] = None,
                                   stakeholder_type: str = "administrator") -> str:
        """
        Generate stakeholder-specific summary report
        
        Args:
            schedule_result: Scheduling result
            validation_report: Optional validation results
            stakeholder_type: Type of stakeholder (administrator, teacher, coordinator)
            
        Returns:
            Stakeholder-specific summary report
        """
        self.logger.info(f"Generating stakeholder summary for {stakeholder_type}")
        
        if stakeholder_type == "administrator":
            return self._generate_administrator_summary(schedule_result, validation_report)
        elif stakeholder_type == "teacher":
            return self._generate_teacher_summary(schedule_result, validation_report)
        elif stakeholder_type == "coordinator":
            return self._generate_coordinator_summary(schedule_result, validation_report)
        else:
            return self._generate_general_summary(schedule_result, validation_report)
    
    def _create_completion_report(self, schedule_result: ScheduleResult,
                                validation_report: Optional[ValidationReport],
                                diagnostics: Optional[SchedulingDiagnostics]) -> CompletionReport:
        """Create comprehensive completion report"""
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(schedule_result, validation_report)
        
        # Calculate constraint compliance
        constraint_compliance = self._calculate_constraint_compliance(validation_report)
        
        # Calculate workload balance score
        workload_balance_score = self._calculate_workload_balance_score(schedule_result)
        
        # Generate recommendations
        recommendations = self._generate_completion_recommendations(schedule_result, validation_report, diagnostics)
        
        # Generate next steps
        next_steps = self._generate_next_steps(schedule_result, validation_report)
        
        return CompletionReport(
            timestamp=datetime.now().isoformat(),
            execution_time=schedule_result.execution_time,
            completion_rate=schedule_result.completion_rate,
            scheduled_hours=schedule_result.scheduled_hours,
            total_required_hours=schedule_result.total_hours,
            success=schedule_result.success,
            performance_metrics=schedule_result.performance_metrics,
            validation_results=validation_report,
            diagnostics_summary=diagnostics.get_scheduling_health_score() if diagnostics else {},
            teacher_utilization=schedule_result.teacher_utilization,
            class_utilization=schedule_result.class_utilization,
            time_slot_utilization=self._calculate_time_slot_utilization(schedule_result.entries),
            quality_score=quality_score,
            constraint_compliance=constraint_compliance,
            workload_balance_score=workload_balance_score,
            recommendations=recommendations,
            next_steps=next_steps
        )
    
    def _create_failure_analysis_report(self, schedule_result: ScheduleResult,
                                      diagnostics: SchedulingDiagnostics) -> FailureAnalysisReport:
        """Create detailed failure analysis report"""
        
        # Get failure summary
        failure_summary = diagnostics.get_failure_summary()
        
        # Analyze bottlenecks
        bottlenecks = diagnostics.analyze_bottlenecks()
        
        # Generate specific fixes
        specific_fixes = self._generate_specific_fixes(schedule_result, diagnostics)
        
        # Generate systemic improvements
        systemic_improvements = diagnostics.generate_improvement_suggestions()
        
        return FailureAnalysisReport(
            timestamp=datetime.now().isoformat(),
            total_failures=failure_summary.get('total_failures', 0),
            unscheduled_hours=schedule_result.total_hours - schedule_result.scheduled_hours,
            failures_by_reason=self._analyze_failures_by_reason(diagnostics.failure_log),
            failures_by_lesson=self._analyze_failures_by_lesson(diagnostics.failure_log),
            failures_by_teacher=self._analyze_failures_by_teacher(diagnostics.failure_log),
            failures_by_class=self._analyze_failures_by_class(diagnostics.failure_log),
            critical_failures=self._identify_critical_failures(diagnostics.failure_log),
            bottlenecks=bottlenecks,
            specific_fixes=specific_fixes,
            systemic_improvements=systemic_improvements
        )
    
    def _create_performance_report(self, schedule_result: ScheduleResult,
                                 diagnostics: Optional[SchedulingDiagnostics]) -> PerformanceReport:
        """Create comprehensive performance report"""
        
        # Calculate performance metrics
        scheduling_rate = schedule_result.scheduled_hours / schedule_result.execution_time if schedule_result.execution_time > 0 else 0
        success_rate = schedule_result.completion_rate / 100.0
        
        # Calculate efficiency metrics
        backtrack_efficiency = self._calculate_backtrack_efficiency(schedule_result)
        constraint_relaxation_effectiveness = self._calculate_constraint_relaxation_effectiveness(schedule_result)
        
        # Generate optimization suggestions
        optimization_suggestions = self._generate_optimization_suggestions(schedule_result, diagnostics)
        
        return PerformanceReport(
            timestamp=datetime.now().isoformat(),
            execution_time=schedule_result.execution_time,
            target_time=60.0,  # 60-second target
            phase_timings=self._extract_phase_timings(schedule_result.performance_metrics),
            algorithm_metrics=schedule_result.backtrack_statistics,
            resource_usage=self._calculate_resource_usage(schedule_result),
            scheduling_rate=scheduling_rate,
            success_rate=success_rate,
            backtrack_efficiency=backtrack_efficiency,
            constraint_relaxation_effectiveness=constraint_relaxation_effectiveness,
            scalability_metrics=self._calculate_scalability_metrics(schedule_result),
            optimization_suggestions=optimization_suggestions
        )
    
    def _calculate_quality_score(self, schedule_result: ScheduleResult,
                               validation_report: Optional[ValidationReport]) -> float:
        """Calculate overall quality score (0-100)"""
        
        # Base score from completion rate
        completion_score = schedule_result.completion_rate
        
        # Penalty for validation violations
        validation_penalty = 0.0
        if validation_report:
            critical_penalty = len(validation_report.critical_violations) * 10
            major_penalty = len(validation_report.major_violations) * 5
            minor_penalty = len(validation_report.minor_violations) * 1
            validation_penalty = critical_penalty + major_penalty + minor_penalty
        
        # Performance bonus/penalty
        performance_bonus = 0.0
        if schedule_result.execution_time < 30:  # Under 30 seconds
            performance_bonus = 5.0
        elif schedule_result.execution_time > 60:  # Over 60 seconds
            performance_bonus = -5.0
        
        # Calculate final score
        quality_score = completion_score - validation_penalty + performance_bonus
        return max(0.0, min(100.0, quality_score))
    
    def _calculate_constraint_compliance(self, validation_report: Optional[ValidationReport]) -> Dict[str, float]:
        """Calculate constraint compliance percentages"""
        
        if not validation_report:
            return {}
        
        total_checks = validation_report.validation_metrics.get("total_entries_validated", 1)
        
        compliance = {}
        for violation_type, count in validation_report.violations_by_type.items():
            compliance_rate = max(0.0, 100.0 - (count / total_checks * 100))
            compliance[violation_type.value] = round(compliance_rate, 1)
        
        return compliance
    
    def _calculate_workload_balance_score(self, schedule_result: ScheduleResult) -> float:
        """Calculate workload balance score (0-100)"""
        
        if not schedule_result.teacher_utilization:
            return 0.0
        
        utilizations = list(schedule_result.teacher_utilization.values())
        
        # Calculate variance in utilization
        mean_utilization = sum(utilizations) / len(utilizations)
        variance = sum((u - mean_utilization) ** 2 for u in utilizations) / len(utilizations)
        
        # Convert variance to balance score (lower variance = higher score)
        balance_score = max(0.0, 100.0 - variance)
        
        return round(balance_score, 1)
    
    def _calculate_time_slot_utilization(self, entries: List[EnhancedScheduleEntry]) -> Dict[str, float]:
        """Calculate utilization by time slot"""
        
        slot_counts = defaultdict(int)
        total_entries = len(entries)
        
        for entry in entries:
            slot_key = f"Day_{entry.day}_Slot_{entry.time_slot}"
            slot_counts[slot_key] += 1
        
        # Calculate utilization percentages
        utilization = {}
        for slot_key, count in slot_counts.items():
            utilization[slot_key] = round((count / total_entries * 100), 1) if total_entries > 0 else 0.0
        
        return utilization
    
    def _generate_completion_recommendations(self, schedule_result: ScheduleResult,
                                          validation_report: Optional[ValidationReport],
                                          diagnostics: Optional[SchedulingDiagnostics]) -> List[str]:
        """Generate recommendations based on completion results"""
        
        recommendations = []
        
        # Completion rate recommendations
        if schedule_result.completion_rate < 100:
            missing_hours = schedule_result.total_hours - schedule_result.scheduled_hours
            recommendations.append(f"Schedule the remaining {missing_hours} hours to achieve 100% completion")
        
        # Performance recommendations
        if schedule_result.execution_time > 60:
            recommendations.append(f"Optimize performance - execution took {schedule_result.execution_time:.1f}s (target: 60s)")
        
        # Validation recommendations
        if validation_report and not validation_report.is_valid:
            recommendations.extend(validation_report.recommendations[:3])  # Top 3 validation recommendations
        
        # Diagnostics recommendations
        if diagnostics:
            diagnostic_recommendations = diagnostics.generate_improvement_suggestions()
            recommendations.extend(diagnostic_recommendations[:2])  # Top 2 diagnostic recommendations
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _generate_next_steps(self, schedule_result: ScheduleResult,
                           validation_report: Optional[ValidationReport]) -> List[str]:
        """Generate next steps based on results"""
        
        next_steps = []
        
        if schedule_result.success:
            next_steps.append("✅ Schedule is ready for implementation")
            next_steps.append("📋 Review schedule with stakeholders")
            next_steps.append("📅 Prepare for schedule deployment")
        else:
            next_steps.append("🔧 Address scheduling failures before implementation")
            next_steps.append("📊 Analyze failure patterns and constraints")
            next_steps.append("⚙️ Adjust scheduling parameters and retry")
        
        if validation_report and validation_report.critical_violations:
            next_steps.insert(0, "🚨 URGENT: Fix critical validation violations")
        
        return next_steps
    
    def _analyze_failures_by_reason(self, failure_log: List[FailureEntry]) -> Dict[str, int]:
        """Analyze failures by reason"""
        
        reason_counts = defaultdict(int)
        for failure in failure_log:
            reason_counts[failure.reason] += 1
        
        return dict(reason_counts)
    
    def _analyze_failures_by_lesson(self, failure_log: List[FailureEntry]) -> Dict[str, int]:
        """Analyze failures by lesson"""
        
        lesson_counts = defaultdict(int)
        for failure in failure_log:
            lesson_counts[failure.lesson_name] += 1
        
        return dict(lesson_counts)
    
    def _analyze_failures_by_teacher(self, failure_log: List[FailureEntry]) -> Dict[str, int]:
        """Analyze failures by teacher"""
        
        teacher_counts = defaultdict(int)
        for failure in failure_log:
            teacher_key = f"Teacher_{failure.teacher_id}"
            teacher_counts[teacher_key] += 1
        
        return dict(teacher_counts)
    
    def _analyze_failures_by_class(self, failure_log: List[FailureEntry]) -> Dict[str, int]:
        """Analyze failures by class"""
        
        class_counts = defaultdict(int)
        for failure in failure_log:
            class_key = f"Class_{failure.class_id}"
            class_counts[class_key] += 1
        
        return dict(class_counts)
    
    def _identify_critical_failures(self, failure_log: List[FailureEntry]) -> List[Dict[str, Any]]:
        """Identify critical failures that need immediate attention"""
        
        critical_failures = []
        
        # Group failures by lesson to identify repeated failures
        lesson_failures = defaultdict(list)
        for failure in failure_log:
            lesson_failures[failure.lesson_id].append(failure)
        
        # Identify lessons with multiple failures
        for lesson_id, failures in lesson_failures.items():
            if len(failures) >= 3:  # 3 or more failures = critical
                critical_failures.append({
                    "lesson_id": lesson_id,
                    "lesson_name": failures[0].lesson_name,
                    "failure_count": len(failures),
                    "primary_reason": failures[-1].reason,  # Most recent reason
                    "total_hours": failures[0].weekly_hours,
                    "severity": "critical"
                })
        
        # Sort by failure count (most critical first)
        critical_failures.sort(key=lambda x: x["failure_count"], reverse=True)
        
        return critical_failures[:10]  # Top 10 critical failures
    
    def _generate_specific_fixes(self, schedule_result: ScheduleResult,
                               diagnostics: SchedulingDiagnostics) -> List[Dict[str, Any]]:
        """Generate specific fixes for identified problems"""
        
        fixes = []
        
        # Analyze bottlenecks for specific fixes
        bottlenecks = diagnostics.analyze_bottlenecks()
        
        # Teacher constraint fixes
        for teacher_id, teacher_name, conflict_count in bottlenecks.most_constrained_teachers[:3]:
            fixes.append({
                "type": "teacher_constraint",
                "resource": f"Teacher {teacher_name}",
                "problem": f"{conflict_count} scheduling conflicts",
                "fix": "Review teacher availability and redistribute lessons",
                "priority": "high" if conflict_count > 5 else "medium"
            })
        
        # Class constraint fixes
        for class_id, class_name, conflict_count in bottlenecks.most_constrained_classes[:3]:
            fixes.append({
                "type": "class_constraint",
                "resource": f"Class {class_name}",
                "problem": f"{conflict_count} scheduling conflicts",
                "fix": "Review curriculum requirements and lesson distribution",
                "priority": "high" if conflict_count > 5 else "medium"
            })
        
        # Time slot fixes
        for day, slot, conflict_count in bottlenecks.peak_conflict_slots[:2]:
            day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            day_name = day_names[day] if day < 5 else f"Day {day}"
            fixes.append({
                "type": "time_slot_constraint",
                "resource": f"{day_name} Slot {slot}",
                "problem": f"{conflict_count} scheduling conflicts",
                "fix": "Spread lessons more evenly across available time slots",
                "priority": "medium"
            })
        
        return fixes
    
    def _calculate_backtrack_efficiency(self, schedule_result: ScheduleResult) -> float:
        """Calculate backtracking efficiency"""
        
        backtrack_stats = schedule_result.backtrack_statistics
        total_backtracks = backtrack_stats.get("total_backtracks", 0)
        successful_backtracks = backtrack_stats.get("successful_backtracks", 0)
        
        if total_backtracks == 0:
            return 100.0  # No backtracking needed = perfect efficiency
        
        efficiency = (successful_backtracks / total_backtracks) * 100
        return round(efficiency, 1)
    
    def _calculate_constraint_relaxation_effectiveness(self, schedule_result: ScheduleResult) -> float:
        """Calculate constraint relaxation effectiveness"""
        
        # This would be enhanced with actual constraint relaxation data
        # For now, estimate based on completion rate and alternative block usage
        
        completion_rate = schedule_result.completion_rate
        alternative_usage = schedule_result.alternative_block_usage
        
        total_alternatives = sum(alternative_usage.values()) - alternative_usage.get("standard_blocks", 0)
        total_entries = sum(alternative_usage.values())
        
        if total_entries == 0:
            return 0.0
        
        alternative_rate = (total_alternatives / total_entries) * 100
        
        # Effectiveness is combination of completion rate and alternative usage
        effectiveness = (completion_rate + alternative_rate) / 2
        return round(effectiveness, 1)
    
    def _extract_phase_timings(self, performance_metrics: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        """Extract phase timing information"""
        
        # This would extract actual phase timings from performance metrics
        # For now, provide a placeholder structure
        
        return {
            "initialization": {"total_time": 0.5, "percentage": 5.0},
            "strict_scheduling": {"total_time": 15.0, "percentage": 60.0},
            "flexible_scheduling": {"total_time": 7.5, "percentage": 30.0},
            "validation": {"total_time": 1.25, "percentage": 5.0}
        }
    
    def _calculate_resource_usage(self, schedule_result: ScheduleResult) -> Dict[str, Any]:
        """Calculate resource usage metrics"""
        
        return {
            "memory_usage_mb": 128,  # Placeholder - would be actual memory usage
            "cpu_utilization_percent": 75,  # Placeholder
            "entries_processed": len(schedule_result.entries),
            "backtrack_operations": schedule_result.backtrack_statistics.get("total_backtracks", 0),
            "constraint_relaxations": schedule_result.backtrack_statistics.get("constraint_relaxations", 0)
        }
    
    def _calculate_scalability_metrics(self, schedule_result: ScheduleResult) -> Dict[str, Any]:
        """Calculate scalability metrics"""
        
        entries_count = len(schedule_result.entries)
        execution_time = schedule_result.execution_time
        
        return {
            "entries_per_second": round(entries_count / execution_time, 1) if execution_time > 0 else 0,
            "estimated_capacity": round(entries_count * (60 / execution_time), 0) if execution_time > 0 else 0,
            "scalability_rating": "Good" if execution_time < 60 else "Needs Optimization"
        }
    
    def _generate_optimization_suggestions(self, schedule_result: ScheduleResult,
                                         diagnostics: Optional[SchedulingDiagnostics]) -> List[str]:
        """Generate performance optimization suggestions"""
        
        suggestions = []
        
        # Time-based suggestions
        if schedule_result.execution_time > 60:
            suggestions.append("Implement more aggressive early termination conditions")
            suggestions.append("Optimize constraint checking algorithms")
        
        # Backtracking suggestions
        backtrack_stats = schedule_result.backtrack_statistics
        if backtrack_stats.get("total_backtracks", 0) > 1000:
            suggestions.append("Improve initial placement heuristics to reduce backtracking")
            suggestions.append("Implement better constraint ordering")
        
        # Memory suggestions
        if backtrack_stats.get("max_depth_reached", 0) >= 10:
            suggestions.append("Consider increasing backtrack depth limit for better solutions")
        
        # Alternative block suggestions
        alternative_usage = schedule_result.alternative_block_usage
        if alternative_usage.get("alternative_blocks", 0) > alternative_usage.get("standard_blocks", 0):
            suggestions.append("Review block patterns - high alternative usage indicates constraint issues")
        
        return suggestions[:5]  # Top 5 suggestions
    
    def _format_as_text(self, report: CompletionReport) -> str:
        """Format completion report as text"""
        
        lines = []
        lines.append("=" * 80)
        lines.append("SCHEDULER OPTIMIZATION - COMPLETION REPORT")
        lines.append("=" * 80)
        lines.append(f"Generated: {report.timestamp}")
        lines.append(f"Execution Time: {report.execution_time:.2f} seconds")
        lines.append("")
        
        # Summary
        lines.append("SUMMARY")
        lines.append("-" * 40)
        lines.append(f"Completion Rate: {report.completion_rate:.1f}%")
        lines.append(f"Scheduled Hours: {report.scheduled_hours}/{report.total_required_hours}")
        lines.append(f"Success: {'✅ YES' if report.success else '❌ NO'}")
        lines.append(f"Quality Score: {report.quality_score:.1f}/100")
        lines.append("")
        
        # Performance
        lines.append("PERFORMANCE METRICS")
        lines.append("-" * 40)
        lines.append(f"Execution Time: {report.execution_time:.2f}s (Target: 60s)")
        lines.append(f"Scheduling Rate: {report.scheduled_hours/report.execution_time:.1f} hours/second")
        lines.append(f"Workload Balance: {report.workload_balance_score:.1f}/100")
        lines.append("")
        
        # Validation Results
        if report.validation_results:
            lines.append("VALIDATION RESULTS")
            lines.append("-" * 40)
            lines.append(f"Valid: {'✅ YES' if report.validation_results.is_valid else '❌ NO'}")
            lines.append(f"Total Violations: {report.validation_results.total_violations}")
            lines.append(f"Critical: {len(report.validation_results.critical_violations)}")
            lines.append(f"Major: {len(report.validation_results.major_violations)}")
            lines.append(f"Minor: {len(report.validation_results.minor_violations)}")
            lines.append("")
        
        # Recommendations
        if report.recommendations:
            lines.append("RECOMMENDATIONS")
            lines.append("-" * 40)
            for i, rec in enumerate(report.recommendations, 1):
                lines.append(f"{i}. {rec}")
            lines.append("")
        
        # Next Steps
        if report.next_steps:
            lines.append("NEXT STEPS")
            lines.append("-" * 40)
            for step in report.next_steps:
                lines.append(f"• {step}")
            lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def _format_as_json(self, report: CompletionReport) -> str:
        """Format completion report as JSON"""
        
        # Convert dataclass to dict, handling special types
        report_dict = asdict(report)
        
        # Handle ValidationReport if present
        if report_dict.get('validation_results'):
            validation_dict = asdict(report.validation_results)
            report_dict['validation_results'] = validation_dict
        
        return json.dumps(report_dict, indent=2, default=str)
    
    def _format_as_html(self, report: CompletionReport) -> str:
        """Format completion report as HTML"""
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Scheduler Optimization - Completion Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
                .success {{ color: green; }}
                .failure {{ color: red; }}
                .warning {{ color: orange; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Scheduler Optimization - Completion Report</h1>
                <p>Generated: {report.timestamp}</p>
                <p>Execution Time: {report.execution_time:.2f} seconds</p>
            </div>
            
            <div class="section">
                <h2>Summary</h2>
                <div class="metric">
                    <strong>Completion Rate:</strong> {report.completion_rate:.1f}%
                </div>
                <div class="metric">
                    <strong>Scheduled Hours:</strong> {report.scheduled_hours}/{report.total_required_hours}
                </div>
                <div class="metric {'success' if report.success else 'failure'}">
                    <strong>Success:</strong> {'✅ YES' if report.success else '❌ NO'}
                </div>
                <div class="metric">
                    <strong>Quality Score:</strong> {report.quality_score:.1f}/100
                </div>
            </div>
            
            <div class="section">
                <h2>Recommendations</h2>
                <ul>
        """
        
        for rec in report.recommendations:
            html += f"<li>{rec}</li>"
        
        html += """
                </ul>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _format_as_markdown(self, report: CompletionReport) -> str:
        """Format completion report as Markdown"""
        
        md = f"""# Scheduler Optimization - Completion Report

**Generated:** {report.timestamp}  
**Execution Time:** {report.execution_time:.2f} seconds

## Summary

- **Completion Rate:** {report.completion_rate:.1f}%
- **Scheduled Hours:** {report.scheduled_hours}/{report.total_required_hours}
- **Success:** {'✅ YES' if report.success else '❌ NO'}
- **Quality Score:** {report.quality_score:.1f}/100

## Performance Metrics

- **Execution Time:** {report.execution_time:.2f}s (Target: 60s)
- **Scheduling Rate:** {report.scheduled_hours/report.execution_time:.1f} hours/second
- **Workload Balance:** {report.workload_balance_score:.1f}/100

"""
        
        if report.validation_results:
            md += f"""## Validation Results

- **Valid:** {'✅ YES' if report.validation_results.is_valid else '❌ NO'}
- **Total Violations:** {report.validation_results.total_violations}
- **Critical:** {len(report.validation_results.critical_violations)}
- **Major:** {len(report.validation_results.major_violations)}
- **Minor:** {len(report.validation_results.minor_violations)}

"""
        
        if report.recommendations:
            md += "## Recommendations\n\n"
            for i, rec in enumerate(report.recommendations, 1):
                md += f"{i}. {rec}\n"
            md += "\n"
        
        if report.next_steps:
            md += "## Next Steps\n\n"
            for step in report.next_steps:
                md += f"- {step}\n"
        
        return md
    
    def _format_failure_report_as_text(self, report: FailureAnalysisReport) -> str:
        """Format failure analysis report as text"""
        
        lines = []
        lines.append("=" * 80)
        lines.append("SCHEDULER OPTIMIZATION - FAILURE ANALYSIS REPORT")
        lines.append("=" * 80)
        lines.append(f"Generated: {report.timestamp}")
        lines.append("")
        
        # Summary
        lines.append("FAILURE SUMMARY")
        lines.append("-" * 40)
        lines.append(f"Total Failures: {report.total_failures}")
        lines.append(f"Unscheduled Hours: {report.unscheduled_hours}")
        lines.append("")
        
        # Failures by reason
        if report.failures_by_reason:
            lines.append("FAILURES BY REASON")
            lines.append("-" * 40)
            for reason, count in sorted(report.failures_by_reason.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"{reason}: {count}")
            lines.append("")
        
        # Critical failures
        if report.critical_failures:
            lines.append("CRITICAL FAILURES")
            lines.append("-" * 40)
            for failure in report.critical_failures[:5]:  # Top 5
                lines.append(f"• {failure['lesson_name']}: {failure['failure_count']} failures ({failure['primary_reason']})")
            lines.append("")
        
        # Specific fixes
        if report.specific_fixes:
            lines.append("SPECIFIC FIXES")
            lines.append("-" * 40)
            for fix in report.specific_fixes[:5]:  # Top 5
                lines.append(f"• {fix['resource']}: {fix['fix']} (Priority: {fix['priority']})")
            lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def _format_failure_report_as_json(self, report: FailureAnalysisReport) -> str:
        """Format failure analysis report as JSON"""
        return json.dumps(asdict(report), indent=2, default=str)
    
    def _format_failure_report_as_html(self, report: FailureAnalysisReport) -> str:
        """Format failure analysis report as HTML"""
        # Similar to completion report HTML formatting
        return f"<html><body><h1>Failure Analysis Report</h1><p>Total Failures: {report.total_failures}</p></body></html>"
    
    def _format_failure_report_as_markdown(self, report: FailureAnalysisReport) -> str:
        """Format failure analysis report as Markdown"""
        return f"# Failure Analysis Report\n\n**Total Failures:** {report.total_failures}\n**Unscheduled Hours:** {report.unscheduled_hours}"
    
    def _format_performance_report_as_text(self, report: PerformanceReport) -> str:
        """Format performance report as text"""
        
        lines = []
        lines.append("=" * 80)
        lines.append("SCHEDULER OPTIMIZATION - PERFORMANCE REPORT")
        lines.append("=" * 80)
        lines.append(f"Generated: {report.timestamp}")
        lines.append(f"Execution Time: {report.execution_time:.2f}s (Target: {report.target_time}s)")
        lines.append("")
        
        # Performance metrics
        lines.append("PERFORMANCE METRICS")
        lines.append("-" * 40)
        lines.append(f"Scheduling Rate: {report.scheduling_rate:.2f} hours/second")
        lines.append(f"Success Rate: {report.success_rate:.1%}")
        lines.append(f"Backtrack Efficiency: {report.backtrack_efficiency:.1f}%")
        lines.append("")
        
        # Optimization suggestions
        if report.optimization_suggestions:
            lines.append("OPTIMIZATION SUGGESTIONS")
            lines.append("-" * 40)
            for i, suggestion in enumerate(report.optimization_suggestions, 1):
                lines.append(f"{i}. {suggestion}")
            lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def _format_performance_report_as_json(self, report: PerformanceReport) -> str:
        """Format performance report as JSON"""
        return json.dumps(asdict(report), indent=2, default=str)
    
    def _format_performance_report_as_html(self, report: PerformanceReport) -> str:
        """Format performance report as HTML"""
        return f"<html><body><h1>Performance Report</h1><p>Execution Time: {report.execution_time:.2f}s</p></body></html>"
    
    def _format_performance_report_as_markdown(self, report: PerformanceReport) -> str:
        """Format performance report as Markdown"""
        return f"# Performance Report\n\n**Execution Time:** {report.execution_time:.2f}s\n**Success Rate:** {report.success_rate:.1%}"
    
    def _generate_administrator_summary(self, schedule_result: ScheduleResult,
                                      validation_report: Optional[ValidationReport]) -> str:
        """Generate administrator-focused summary"""
        
        summary = f"""
ADMINISTRATOR SUMMARY - SCHEDULE OPTIMIZATION

Completion Status: {'✅ COMPLETE' if schedule_result.success else '⚠️ PARTIAL'}
Completion Rate: {schedule_result.completion_rate:.1f}%
Execution Time: {schedule_result.execution_time:.1f} seconds

KEY METRICS:
• Total Hours Scheduled: {schedule_result.scheduled_hours}/{schedule_result.total_hours}
• Teacher Utilization: {len(schedule_result.teacher_utilization)} teachers scheduled
• Class Coverage: {len(schedule_result.class_utilization)} classes scheduled

VALIDATION STATUS:
"""
        
        if validation_report:
            summary += f"• Critical Issues: {len(validation_report.critical_violations)}\n"
            summary += f"• Major Issues: {len(validation_report.major_violations)}\n"
            summary += f"• Ready for Implementation: {'YES' if validation_report.is_valid else 'NO'}\n"
        
        return summary
    
    def _generate_teacher_summary(self, schedule_result: ScheduleResult,
                                validation_report: Optional[ValidationReport]) -> str:
        """Generate teacher-focused summary"""
        
        return f"""
TEACHER SUMMARY - SCHEDULE OPTIMIZATION

Your schedule has been optimized with {schedule_result.completion_rate:.1f}% completion rate.

WORKLOAD DISTRIBUTION:
• Teachers scheduled: {len(schedule_result.teacher_utilization)}
• Average utilization: {sum(schedule_result.teacher_utilization.values())/len(schedule_result.teacher_utilization):.1f}%

SCHEDULE QUALITY:
• Conflicts resolved: {'YES' if not validation_report or validation_report.is_valid else 'SOME REMAIN'}
• Block rules followed: {'YES' if not validation_report or len([v for v in validation_report.major_violations if 'block' in str(v.violation_type)]) == 0 else 'MOSTLY'}
"""
    
    def _generate_coordinator_summary(self, schedule_result: ScheduleResult,
                                    validation_report: Optional[ValidationReport]) -> str:
        """Generate coordinator-focused summary"""
        
        return f"""
COORDINATOR SUMMARY - SCHEDULE OPTIMIZATION

CURRICULUM COVERAGE:
• Completion Rate: {schedule_result.completion_rate:.1f}%
• Hours Scheduled: {schedule_result.scheduled_hours}/{schedule_result.total_hours}
• Classes Covered: {len(schedule_result.class_utilization)}

OPTIMIZATION RESULTS:
• Backtracking Used: {schedule_result.backtrack_statistics.get('total_backtracks', 0)} times
• Alternative Blocks: {schedule_result.alternative_block_usage.get('alternative_blocks', 0)}
• Constraint Relaxations: {schedule_result.backtrack_statistics.get('constraint_relaxations', 0)}
"""
    
    def _generate_general_summary(self, schedule_result: ScheduleResult,
                                validation_report: Optional[ValidationReport]) -> str:
        """Generate general summary"""
        
        return f"""
SCHEDULE OPTIMIZATION SUMMARY

Status: {'✅ SUCCESS' if schedule_result.success else '⚠️ PARTIAL SUCCESS'}
Completion: {schedule_result.completion_rate:.1f}% ({schedule_result.scheduled_hours}/{schedule_result.total_hours} hours)
Time: {schedule_result.execution_time:.1f} seconds

Quality: {'HIGH' if not validation_report or validation_report.is_valid else 'NEEDS IMPROVEMENT'}
"""