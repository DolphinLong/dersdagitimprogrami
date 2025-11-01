# -*- coding: utf-8 -*-
"""
Scheduling Diagnostics - Comprehensive analysis and failure reporting for scheduler optimization

This module provides detailed diagnostics, bottleneck analysis, and performance metrics
for the enhanced scheduling system. It tracks failures, analyzes constraints, and
generates improvement suggestions to achieve 100% schedule completion.

Key Features:
- Detailed failure logging with comprehensive context
- Performance metrics collection and analysis
- Constraint violation statistics tracking
- Bottleneck identification and analysis
- Teacher and class utilization analysis
- Specific improvement suggestions generation

Requirements addressed: 5.1, 5.2, 5.3, 5.4, 5.5
"""

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from database.models import Lesson
from algorithms.bottleneck_analyzer import BottleneckAnalyzer, ResourceBottleneck, ConstraintAnalysis, UtilizationPattern


@dataclass
class FailureEntry:
    """Represents a scheduling failure with detailed context"""
    lesson_id: int
    lesson_name: str
    class_id: int
    teacher_id: int
    weekly_hours: int
    reason: str
    timestamp: float
    context: Dict[str, Any]
    attempted_slots: List[Tuple[int, int]]  # (day, slot) pairs attempted
    constraint_violations: List[str]
    backtrack_depth: int = 0
    alternative_blocks_tried: List[Tuple[int, ...]] = field(default_factory=list)


@dataclass
class BottleneckReport:
    """Report identifying scheduling bottlenecks and constraint conflicts"""
    most_constrained_teachers: List[Tuple[int, str, int]]  # (teacher_id, name, conflict_count)
    most_constrained_classes: List[Tuple[int, str, int]]  # (class_id, name, conflict_count)
    peak_conflict_slots: List[Tuple[int, int, int]]  # (day, slot, conflict_count)
    constraint_type_frequency: Dict[str, int]
    resource_utilization: Dict[str, float]
    critical_lessons: List[Tuple[int, str, int]]  # (lesson_id, name, failure_count)


@dataclass
class UtilizationReport:
    """Report on teacher and class utilization patterns"""
    teacher_utilization: Dict[int, Dict[str, Any]]  # teacher_id -> utilization data
    class_utilization: Dict[int, Dict[str, Any]]  # class_id -> utilization data
    peak_usage_times: List[Tuple[int, int, float]]  # (day, slot, utilization_percentage)
    underutilized_resources: List[Tuple[str, int, float]]  # (resource_type, id, utilization)
    overutilized_resources: List[Tuple[str, int, float]]  # (resource_type, id, utilization)


class SchedulingDiagnostics:
    """
    Comprehensive diagnostics system for scheduler optimization
    
    Provides detailed failure analysis, performance metrics, constraint violation tracking,
    and bottleneck identification to achieve 100% schedule completion.
    """
    
    def __init__(self, db_manager=None):
        """
        Initialize diagnostics system
        
        Args:
            db_manager: Optional database manager for enhanced analysis
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Core data structures
        self.failure_log: List[FailureEntry] = []
        self.performance_metrics: Dict[str, Any] = {}
        self.constraint_violations: Dict[str, int] = defaultdict(int)
        self.teacher_utilization: Dict[int, Dict[str, Any]] = defaultdict(dict)
        self.class_utilization: Dict[int, Dict[str, Any]] = defaultdict(dict)
        
        # Tracking data
        self.phase_timings: Dict[str, List[float]] = defaultdict(list)
        self.slot_conflicts: Dict[Tuple[int, int], int] = defaultdict(int)  # (day, slot) -> conflict_count
        self.teacher_conflicts: Dict[int, int] = defaultdict(int)  # teacher_id -> conflict_count
        self.class_conflicts: Dict[int, int] = defaultdict(int)  # class_id -> conflict_count
        self.lesson_failures: Dict[int, int] = defaultdict(int)  # lesson_id -> failure_count
        
        # Performance tracking
        self.start_time: Optional[float] = None
        self.total_attempts: int = 0
        self.successful_placements: int = 0
        self.backtrack_attempts: int = 0
        self.constraint_relaxations: int = 0
        
        # Initialize bottleneck analyzer
        self.bottleneck_analyzer = BottleneckAnalyzer(db_manager)
        
        self.logger.info("SchedulingDiagnostics initialized")
    
    def start_session(self) -> None:
        """Start a new diagnostics session"""
        self.start_time = time.time()
        self.failure_log.clear()
        self.constraint_violations.clear()
        self.teacher_utilization.clear()
        self.class_utilization.clear()
        self.phase_timings.clear()
        self.slot_conflicts.clear()
        self.teacher_conflicts.clear()
        self.class_conflicts.clear()
        self.lesson_failures.clear()
        
        self.total_attempts = 0
        self.successful_placements = 0
        self.backtrack_attempts = 0
        self.constraint_relaxations = 0
        
        self.logger.info("Started new diagnostics session")
    
    def log_failure(self, lesson: Lesson, reason: str, context: Dict[str, Any]) -> None:
        """
        Log detailed scheduling failure with comprehensive context
        
        Args:
            lesson: Lesson object that failed to be scheduled
            reason: Primary reason for failure
            context: Additional context including attempted slots, constraints, etc.
        """
        failure_entry = FailureEntry(
            lesson_id=lesson.lesson_id,
            lesson_name=lesson.name,
            class_id=context.get('class_id', 0),
            teacher_id=context.get('teacher_id', 0),
            weekly_hours=lesson.weekly_hours,
            reason=reason,
            timestamp=time.time(),
            context=context.copy(),
            attempted_slots=context.get('attempted_slots', []),
            constraint_violations=context.get('constraint_violations', []),
            backtrack_depth=context.get('backtrack_depth', 0),
            alternative_blocks_tried=context.get('alternative_blocks_tried', [])
        )
        
        self.failure_log.append(failure_entry)
        self.lesson_failures[lesson.lesson_id] += 1
        
        # Track constraint violations
        for violation in failure_entry.constraint_violations:
            self.constraint_violations[violation] += 1
        
        # Track conflicts by resource
        if 'teacher' in reason.lower() and 'conflict' in reason.lower():
            self.teacher_conflicts[context.get('teacher_id', 0)] += 1
        if 'class' in reason.lower() and 'conflict' in reason.lower():
            self.class_conflicts[context.get('class_id', 0)] += 1
        
        # Track slot conflicts
        for day, slot in failure_entry.attempted_slots:
            self.slot_conflicts[(day, slot)] += 1
        
        self.logger.warning(
            f"Logged failure for lesson {lesson.name} (ID: {lesson.lesson_id}): {reason}"
        )
    
    def log_phase_timing(self, phase: str, duration: float) -> None:
        """
        Log timing for each scheduling phase
        
        Args:
            phase: Name of the scheduling phase
            duration: Duration in seconds
        """
        self.phase_timings[phase].append(duration)
        self.logger.debug(f"Phase '{phase}' completed in {duration:.3f} seconds")
    
    def record_attempt(self, successful: bool = False) -> None:
        """
        Record a scheduling attempt
        
        Args:
            successful: Whether the attempt was successful
        """
        self.total_attempts += 1
        if successful:
            self.successful_placements += 1
    
    def record_backtrack(self) -> None:
        """Record a backtracking attempt"""
        self.backtrack_attempts += 1
    
    def record_constraint_relaxation(self) -> None:
        """Record a constraint relaxation event"""
        self.constraint_relaxations += 1
    
    def update_teacher_utilization(self, teacher_id: int, utilization_data: Dict[str, Any]) -> None:
        """
        Update teacher utilization data
        
        Args:
            teacher_id: Teacher ID
            utilization_data: Utilization metrics (scheduled_hours, available_hours, etc.)
        """
        self.teacher_utilization[teacher_id].update(utilization_data)
    
    def update_class_utilization(self, class_id: int, utilization_data: Dict[str, Any]) -> None:
        """
        Update class utilization data
        
        Args:
            class_id: Class ID
            utilization_data: Utilization metrics (scheduled_hours, total_slots, etc.)
        """
        self.class_utilization[class_id].update(utilization_data)
    
    def analyze_bottlenecks(self) -> BottleneckReport:
        """
        Identify scheduling bottlenecks and constraint conflicts using advanced analysis
        
        Returns:
            BottleneckReport with detailed analysis
        """
        # Use advanced bottleneck analyzer for detailed analysis
        resource_bottlenecks = self.bottleneck_analyzer.identify_resource_bottlenecks(
            self.teacher_conflicts,
            self.class_conflicts,
            self.slot_conflicts,
            self.lesson_failures,
            self.teacher_utilization,
            self.class_utilization
        )
        
        # Convert to legacy format for backward compatibility
        most_constrained_teachers = [
            (b.resource_id, b.resource_name, b.conflict_count)
            for b in resource_bottlenecks if b.resource_type == 'teacher'
        ][:10]
        
        most_constrained_classes = [
            (b.resource_id, b.resource_name, b.conflict_count)
            for b in resource_bottlenecks if b.resource_type == 'class'
        ][:10]
        
        # Peak conflict slots
        peak_conflict_slots = sorted(
            [(day, slot, count) for (day, slot), count in self.slot_conflicts.items()],
            key=lambda x: x[2],
            reverse=True
        )[:20]
        
        # Constraint type frequency
        constraint_type_frequency = dict(self.constraint_violations)
        
        # Resource utilization
        total_teachers = len(self.teacher_utilization) if self.teacher_utilization else 1
        total_classes = len(self.class_utilization) if self.class_utilization else 1
        
        resource_utilization = {
            'teacher_conflict_rate': sum(self.teacher_conflicts.values()) / total_teachers,
            'class_conflict_rate': sum(self.class_conflicts.values()) / total_classes,
            'slot_conflict_rate': sum(self.slot_conflicts.values()) / max(len(self.slot_conflicts), 1),
            'overall_success_rate': self.successful_placements / max(self.total_attempts, 1)
        }
        
        # Critical lessons (most failed)
        critical_lessons = sorted(
            [(lid, f"Lesson_{lid}", count) for lid, count in self.lesson_failures.items()],
            key=lambda x: x[2],
            reverse=True
        )[:10]
        
        return BottleneckReport(
            most_constrained_teachers=most_constrained_teachers,
            most_constrained_classes=most_constrained_classes,
            peak_conflict_slots=peak_conflict_slots,
            constraint_type_frequency=constraint_type_frequency,
            resource_utilization=resource_utilization,
            critical_lessons=critical_lessons
        )
    
    def generate_improvement_suggestions(self) -> List[str]:
        """
        Generate specific improvement recommendations for failed attempts
        
        Returns:
            List of actionable improvement suggestions
        """
        suggestions = []
        bottlenecks = self.analyze_bottlenecks()
        
        # Analyze failure patterns
        if self.failure_log:
            # Most common failure reasons
            failure_reasons = defaultdict(int)
            for failure in self.failure_log:
                failure_reasons[failure.reason] += 1
            
            most_common_failure = max(failure_reasons.items(), key=lambda x: x[1])
            suggestions.append(
                f"Most common failure: '{most_common_failure[0]}' ({most_common_failure[1]} occurrences). "
                f"Focus optimization efforts on resolving this constraint type."
            )
        
        # Teacher constraint suggestions
        if bottlenecks.most_constrained_teachers:
            top_teacher = bottlenecks.most_constrained_teachers[0]
            suggestions.append(
                f"Teacher {top_teacher[1]} has {top_teacher[2]} conflicts. "
                f"Consider adjusting their availability or redistributing their lessons."
            )
        
        # Class constraint suggestions
        if bottlenecks.most_constrained_classes:
            top_class = bottlenecks.most_constrained_classes[0]
            suggestions.append(
                f"Class {top_class[1]} has {top_class[2]} conflicts. "
                f"Review curriculum requirements and consider lesson redistribution."
            )
        
        # Time slot suggestions
        if bottlenecks.peak_conflict_slots:
            peak_slot = bottlenecks.peak_conflict_slots[0]
            day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            day_name = day_names[peak_slot[0]] if peak_slot[0] < 5 else f"Day {peak_slot[0]}"
            suggestions.append(
                f"Time slot {day_name} slot {peak_slot[1]} has {peak_slot[2]} conflicts. "
                f"Consider spreading lessons more evenly across time slots."
            )
        
        # Success rate suggestions
        success_rate = bottlenecks.resource_utilization.get('overall_success_rate', 0)
        if success_rate < 0.8:
            suggestions.append(
                f"Overall success rate is {success_rate:.1%}. "
                f"Consider implementing more aggressive constraint relaxation or backtracking."
            )
        
        # Backtracking suggestions
        if self.backtrack_attempts > 0:
            backtrack_rate = self.backtrack_attempts / max(self.total_attempts, 1)
            if backtrack_rate > 0.3:
                suggestions.append(
                    f"High backtracking rate ({backtrack_rate:.1%}). "
                    f"Consider improving initial placement heuristics or constraint ordering."
                )
        
        # Critical lesson suggestions
        if bottlenecks.critical_lessons:
            critical_lesson = bottlenecks.critical_lessons[0]
            suggestions.append(
                f"Lesson {critical_lesson[1]} failed {critical_lesson[2]} times. "
                f"Review its constraints and consider alternative block configurations."
            )
        
        # Constraint violation suggestions
        if bottlenecks.constraint_type_frequency:
            top_violation = max(bottlenecks.constraint_type_frequency.items(), key=lambda x: x[1])
            suggestions.append(
                f"Most frequent constraint violation: '{top_violation[0]}' ({top_violation[1]} times). "
                f"Focus on relaxing or optimizing this constraint type."
            )
        
        return suggestions
    
    def track_constraint_violations_by_type(self) -> Dict[str, int]:
        """
        Report constraint violation statistics by category
        
        Returns:
            Dictionary mapping constraint types to violation counts
        """
        return dict(self.constraint_violations)
    
    def analyze_teacher_class_utilization(self) -> UtilizationReport:
        """
        Identify teacher and class utilization patterns
        
        Returns:
            UtilizationReport with detailed utilization analysis
        """
        # Calculate peak usage times
        peak_usage_times = []
        if self.slot_conflicts:
            total_conflicts = sum(self.slot_conflicts.values())
            for (day, slot), conflicts in self.slot_conflicts.items():
                utilization_percentage = (conflicts / total_conflicts) * 100
                peak_usage_times.append((day, slot, utilization_percentage))
        
        peak_usage_times.sort(key=lambda x: x[2], reverse=True)
        
        # Identify underutilized and overutilized resources
        underutilized_resources = []
        overutilized_resources = []
        
        # Analyze teacher utilization
        if self.teacher_utilization:
            for teacher_id, data in self.teacher_utilization.items():
                utilization = data.get('utilization_rate', 0.0)
                if utilization < 0.5:  # Less than 50% utilized
                    underutilized_resources.append(('teacher', teacher_id, utilization))
                elif utilization > 0.9:  # More than 90% utilized
                    overutilized_resources.append(('teacher', teacher_id, utilization))
        
        # Analyze class utilization
        if self.class_utilization:
            for class_id, data in self.class_utilization.items():
                utilization = data.get('utilization_rate', 0.0)
                if utilization < 0.5:  # Less than 50% utilized
                    underutilized_resources.append(('class', class_id, utilization))
                elif utilization > 0.9:  # More than 90% utilized
                    overutilized_resources.append(('class', class_id, utilization))
        
        return UtilizationReport(
            teacher_utilization=dict(self.teacher_utilization),
            class_utilization=dict(self.class_utilization),
            peak_usage_times=peak_usage_times[:10],  # Top 10 peak times
            underutilized_resources=sorted(underutilized_resources, key=lambda x: x[2]),
            overutilized_resources=sorted(overutilized_resources, key=lambda x: x[2], reverse=True)
        )
    
    def generate_performance_metrics(self) -> Dict[str, Any]:
        """
        Generate comprehensive performance metrics including phase timing
        
        Returns:
            Dictionary with detailed performance metrics
        """
        current_time = time.time()
        total_duration = current_time - self.start_time if self.start_time else 0
        
        # Calculate phase timing statistics
        phase_stats = {}
        for phase, timings in self.phase_timings.items():
            if timings:
                phase_stats[phase] = {
                    'total_time': sum(timings),
                    'average_time': sum(timings) / len(timings),
                    'min_time': min(timings),
                    'max_time': max(timings),
                    'call_count': len(timings)
                }
        
        # Calculate success rates
        success_rate = self.successful_placements / max(self.total_attempts, 1)
        backtrack_rate = self.backtrack_attempts / max(self.total_attempts, 1)
        
        return {
            'session_duration': total_duration,
            'total_attempts': self.total_attempts,
            'successful_placements': self.successful_placements,
            'failed_attempts': len(self.failure_log),
            'success_rate': success_rate,
            'backtrack_attempts': self.backtrack_attempts,
            'backtrack_rate': backtrack_rate,
            'constraint_relaxations': self.constraint_relaxations,
            'phase_timings': phase_stats,
            'constraint_violations_total': sum(self.constraint_violations.values()),
            'unique_constraint_types': len(self.constraint_violations),
            'teacher_conflicts_total': sum(self.teacher_conflicts.values()),
            'class_conflicts_total': sum(self.class_conflicts.values()),
            'slot_conflicts_total': sum(self.slot_conflicts.values()),
            'critical_lessons_count': len([count for count in self.lesson_failures.values() if count > 1])
        }
    
    def get_failure_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all failures for reporting
        
        Returns:
            Dictionary with failure summary statistics
        """
        if not self.failure_log:
            return {'total_failures': 0, 'failure_details': []}
        
        # Group failures by reason
        failure_by_reason = defaultdict(list)
        for failure in self.failure_log:
            failure_by_reason[failure.reason].append(failure)
        
        failure_details = []
        for reason, failures in failure_by_reason.items():
            failure_details.append({
                'reason': reason,
                'count': len(failures),
                'lessons_affected': list(set(f.lesson_id for f in failures)),
                'average_backtrack_depth': sum(f.backtrack_depth for f in failures) / len(failures),
                'total_slots_attempted': sum(len(f.attempted_slots) for f in failures)
            })
        
        return {
            'total_failures': len(self.failure_log),
            'unique_failure_reasons': len(failure_by_reason),
            'failure_details': sorted(failure_details, key=lambda x: x['count'], reverse=True)
        }
    
    def get_advanced_bottleneck_analysis(self) -> Dict[str, Any]:
        """
        Get comprehensive bottleneck analysis using advanced algorithms
        
        Returns:
            Dictionary with detailed bottleneck analysis results
        """
        # Get resource bottlenecks
        resource_bottlenecks = self.bottleneck_analyzer.identify_resource_bottlenecks(
            self.teacher_conflicts,
            self.class_conflicts,
            self.slot_conflicts,
            self.lesson_failures,
            self.teacher_utilization,
            self.class_utilization
        )
        
        # Get constraint pattern analysis
        constraint_analyses = self.bottleneck_analyzer.analyze_constraint_patterns(
            self.constraint_violations,
            self.failure_log
        )
        
        # Get utilization patterns
        utilization_patterns = self.bottleneck_analyzer.analyze_utilization_patterns(
            self.teacher_utilization,
            self.class_utilization,
            self.slot_conflicts
        )
        
        # Get targeted improvement suggestions
        targeted_improvements = self.bottleneck_analyzer.generate_targeted_improvements(
            resource_bottlenecks,
            constraint_analyses,
            utilization_patterns
        )
        
        return {
            'resource_bottlenecks': [
                {
                    'type': b.resource_type,
                    'id': b.resource_id,
                    'name': b.resource_name,
                    'score': b.bottleneck_score,
                    'conflicts': b.conflict_count,
                    'utilization': b.utilization_rate,
                    'improvement_potential': b.improvement_potential,
                    'affected_lessons': b.affected_lessons,
                    'peak_conflict_times': b.peak_conflict_times
                }
                for b in resource_bottlenecks[:10]
            ],
            'constraint_analyses': [
                {
                    'type': c.constraint_type,
                    'frequency': c.frequency,
                    'severity': c.severity_score,
                    'affected_resources': c.affected_resources,
                    'suggestions': c.resolution_suggestions
                }
                for c in constraint_analyses[:5]
            ],
            'utilization_patterns': [
                {
                    'resource_type': u.resource_type,
                    'resource_id': u.resource_id,
                    'average_utilization': u.average_utilization,
                    'efficiency_score': u.efficiency_score,
                    'variance': u.variance
                }
                for u in utilization_patterns[:10]
            ],
            'targeted_improvements': targeted_improvements
        }
    
    def get_scheduling_health_score(self) -> Dict[str, Any]:
        """
        Calculate overall scheduling health score and metrics
        
        Returns:
            Dictionary with health score and component metrics
        """
        # Calculate component scores (0-100 scale)
        success_rate = self.successful_placements / max(self.total_attempts, 1)
        success_score = success_rate * 100
        
        # Conflict score (lower conflicts = higher score)
        total_conflicts = (
            sum(self.teacher_conflicts.values()) +
            sum(self.class_conflicts.values()) +
            sum(self.slot_conflicts.values())
        )
        max_possible_conflicts = max(self.total_attempts, 1)
        conflict_rate = total_conflicts / max_possible_conflicts
        conflict_score = max(0, 100 - (conflict_rate * 100))
        
        # Efficiency score (based on backtracking and relaxations)
        total_interventions = self.backtrack_attempts + self.constraint_relaxations
        intervention_rate = total_interventions / max(self.total_attempts, 1)
        efficiency_score = max(0, 100 - (intervention_rate * 50))
        
        # Constraint compliance score
        total_violations = sum(self.constraint_violations.values())
        violation_rate = total_violations / max(self.total_attempts, 1)
        compliance_score = max(0, 100 - (violation_rate * 100))
        
        # Overall health score (weighted average)
        weights = {
            'success': 0.4,
            'conflict': 0.3,
            'efficiency': 0.2,
            'compliance': 0.1
        }
        
        overall_score = (
            success_score * weights['success'] +
            conflict_score * weights['conflict'] +
            efficiency_score * weights['efficiency'] +
            compliance_score * weights['compliance']
        )
        
        # Determine health status
        if overall_score >= 90:
            health_status = "EXCELLENT"
        elif overall_score >= 75:
            health_status = "GOOD"
        elif overall_score >= 60:
            health_status = "FAIR"
        elif overall_score >= 40:
            health_status = "POOR"
        else:
            health_status = "CRITICAL"
        
        return {
            'overall_score': round(overall_score, 1),
            'health_status': health_status,
            'component_scores': {
                'success_rate': round(success_score, 1),
                'conflict_management': round(conflict_score, 1),
                'efficiency': round(efficiency_score, 1),
                'constraint_compliance': round(compliance_score, 1)
            },
            'raw_metrics': {
                'success_rate': success_rate,
                'conflict_rate': conflict_rate,
                'intervention_rate': intervention_rate,
                'violation_rate': violation_rate
            },
            'recommendations': self._get_health_recommendations(overall_score, {
                'success': success_score,
                'conflict': conflict_score,
                'efficiency': efficiency_score,
                'compliance': compliance_score
            })
        }
    
    def _get_health_recommendations(self, overall_score: float, component_scores: Dict[str, float]) -> List[str]:
        """
        Get health-based recommendations for improvement
        
        Args:
            overall_score: Overall health score
            component_scores: Individual component scores
            
        Returns:
            List of specific recommendations
        """
        recommendations = []
        
        if overall_score < 60:
            recommendations.append("URGENT: Overall scheduling health is poor. Immediate optimization required.")
        
        # Component-specific recommendations
        if component_scores['success'] < 70:
            recommendations.append("Improve success rate by implementing more aggressive backtracking and constraint relaxation.")
        
        if component_scores['conflict'] < 70:
            recommendations.append("Reduce conflicts by improving resource allocation and availability management.")
        
        if component_scores['efficiency'] < 70:
            recommendations.append("Optimize efficiency by improving initial placement heuristics and reducing backtracking needs.")
        
        if component_scores['compliance'] < 70:
            recommendations.append("Improve constraint compliance by reviewing and potentially relaxing overly restrictive constraints.")
        
        # Find the weakest component
        weakest_component = min(component_scores.items(), key=lambda x: x[1])
        if weakest_component[1] < 50:
            recommendations.append(f"Focus immediate attention on {weakest_component[0]} - it's the primary limiting factor.")
        
        return recommendations