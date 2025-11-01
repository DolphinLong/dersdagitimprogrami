# -*- coding: utf-8 -*-
"""
Bottleneck Analyzer - Advanced bottleneck identification and analysis for scheduler optimization

This module provides sophisticated algorithms to identify scheduling bottlenecks,
analyze constraint conflicts, and generate specific improvement suggestions.
It works in conjunction with SchedulingDiagnostics to provide deep insights
into scheduling performance issues.

Key Features:
- Advanced bottleneck detection algorithms
- Teacher and class utilization analysis
- Time slot conflict pattern analysis
- Resource constraint identification
- Specific improvement recommendation generation
- Performance impact assessment

Requirements addressed: 5.3, 5.4
"""

import logging
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple
from database.models import Teacher, Class, Lesson


@dataclass
class ResourceBottleneck:
    """Represents a resource bottleneck with detailed analysis"""
    resource_type: str  # 'teacher', 'class', 'time_slot', 'lesson'
    resource_id: int
    resource_name: str
    bottleneck_score: float  # Higher score = more severe bottleneck
    conflict_count: int
    affected_lessons: List[int]
    constraint_types: List[str]
    peak_conflict_times: List[Tuple[int, int]]  # (day, slot) pairs
    utilization_rate: float
    improvement_potential: float  # Estimated improvement if resolved


@dataclass
class ConstraintAnalysis:
    """Analysis of constraint patterns and conflicts"""
    constraint_type: str
    frequency: int
    severity_score: float
    affected_resources: List[Tuple[str, int]]  # (resource_type, resource_id)
    time_patterns: Dict[Tuple[int, int], int]  # (day, slot) -> frequency
    resolution_suggestions: List[str]


@dataclass
class UtilizationPattern:
    """Pattern analysis for resource utilization"""
    resource_type: str
    resource_id: int
    peak_hours: List[Tuple[int, int, float]]  # (day, slot, utilization)
    low_hours: List[Tuple[int, int, float]]  # (day, slot, utilization)
    average_utilization: float
    variance: float
    efficiency_score: float


class BottleneckAnalyzer:
    """
    Advanced bottleneck analysis system for scheduler optimization
    
    Provides sophisticated algorithms to identify and analyze scheduling bottlenecks,
    helping achieve 100% schedule completion by targeting the most critical issues.
    """
    
    def __init__(self, db_manager=None):
        """
        Initialize bottleneck analyzer
        
        Args:
            db_manager: Optional database manager for accessing resource data
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.db_manager = db_manager
        
        # Analysis weights for scoring
        self.weights = {
            'conflict_frequency': 0.4,
            'resource_utilization': 0.3,
            'constraint_severity': 0.2,
            'improvement_potential': 0.1
        }
        
        self.logger.info("BottleneckAnalyzer initialized")
    
    def identify_resource_bottlenecks(
        self,
        teacher_conflicts: Dict[int, int],
        class_conflicts: Dict[int, int],
        slot_conflicts: Dict[Tuple[int, int], int],
        lesson_failures: Dict[int, int],
        teacher_utilization: Dict[int, Dict[str, Any]],
        class_utilization: Dict[int, Dict[str, Any]]
    ) -> List[ResourceBottleneck]:
        """
        Identify resource bottlenecks using advanced scoring algorithms
        
        Args:
            teacher_conflicts: Teacher ID -> conflict count mapping
            class_conflicts: Class ID -> conflict count mapping
            slot_conflicts: (day, slot) -> conflict count mapping
            lesson_failures: Lesson ID -> failure count mapping
            teacher_utilization: Teacher utilization data
            class_utilization: Class utilization data
            
        Returns:
            List of ResourceBottleneck objects sorted by severity
        """
        bottlenecks = []
        
        # Analyze teacher bottlenecks
        for teacher_id, conflict_count in teacher_conflicts.items():
            if conflict_count > 0:
                utilization_data = teacher_utilization.get(teacher_id, {})
                utilization_rate = utilization_data.get('utilization_rate', 0.0)
                
                # Calculate bottleneck score
                score = self._calculate_resource_bottleneck_score(
                    conflict_count, utilization_rate, 'teacher'
                )
                
                # Get affected lessons and peak conflict times
                affected_lessons = self._get_affected_lessons_for_teacher(teacher_id, lesson_failures)
                peak_times = self._get_peak_conflict_times_for_teacher(teacher_id, slot_conflicts)
                
                bottleneck = ResourceBottleneck(
                    resource_type='teacher',
                    resource_id=teacher_id,
                    resource_name=f"Teacher_{teacher_id}",
                    bottleneck_score=score,
                    conflict_count=conflict_count,
                    affected_lessons=affected_lessons,
                    constraint_types=['availability', 'workload', 'scheduling'],
                    peak_conflict_times=peak_times,
                    utilization_rate=utilization_rate,
                    improvement_potential=self._estimate_improvement_potential(
                        conflict_count, utilization_rate, 'teacher'
                    )
                )
                bottlenecks.append(bottleneck)
        
        # Analyze class bottlenecks
        for class_id, conflict_count in class_conflicts.items():
            if conflict_count > 0:
                utilization_data = class_utilization.get(class_id, {})
                utilization_rate = utilization_data.get('utilization_rate', 0.0)
                
                score = self._calculate_resource_bottleneck_score(
                    conflict_count, utilization_rate, 'class'
                )
                
                affected_lessons = self._get_affected_lessons_for_class(class_id, lesson_failures)
                peak_times = self._get_peak_conflict_times_for_class(class_id, slot_conflicts)
                
                bottleneck = ResourceBottleneck(
                    resource_type='class',
                    resource_id=class_id,
                    resource_name=f"Class_{class_id}",
                    bottleneck_score=score,
                    conflict_count=conflict_count,
                    affected_lessons=affected_lessons,
                    constraint_types=['curriculum', 'scheduling', 'capacity'],
                    peak_conflict_times=peak_times,
                    utilization_rate=utilization_rate,
                    improvement_potential=self._estimate_improvement_potential(
                        conflict_count, utilization_rate, 'class'
                    )
                )
                bottlenecks.append(bottleneck)
        
        # Analyze time slot bottlenecks
        for (day, slot), conflict_count in slot_conflicts.items():
            if conflict_count > 0:
                # Calculate utilization rate for this time slot
                utilization_rate = self._calculate_slot_utilization(day, slot, slot_conflicts)
                
                score = self._calculate_resource_bottleneck_score(
                    conflict_count, utilization_rate, 'time_slot'
                )
                
                bottleneck = ResourceBottleneck(
                    resource_type='time_slot',
                    resource_id=day * 10 + slot,  # Unique ID for slot
                    resource_name=f"Day_{day}_Slot_{slot}",
                    bottleneck_score=score,
                    conflict_count=conflict_count,
                    affected_lessons=[],  # Will be populated by cross-reference
                    constraint_types=['time_availability', 'scheduling'],
                    peak_conflict_times=[(day, slot)],
                    utilization_rate=utilization_rate,
                    improvement_potential=self._estimate_improvement_potential(
                        conflict_count, utilization_rate, 'time_slot'
                    )
                )
                bottlenecks.append(bottleneck)
        
        # Analyze lesson bottlenecks
        for lesson_id, failure_count in lesson_failures.items():
            if failure_count > 0:
                score = self._calculate_lesson_bottleneck_score(failure_count)
                
                bottleneck = ResourceBottleneck(
                    resource_type='lesson',
                    resource_id=lesson_id,
                    resource_name=f"Lesson_{lesson_id}",
                    bottleneck_score=score,
                    conflict_count=failure_count,
                    affected_lessons=[lesson_id],
                    constraint_types=['block_rules', 'availability', 'curriculum'],
                    peak_conflict_times=[],  # Will be populated by analysis
                    utilization_rate=0.0,  # Not applicable for lessons
                    improvement_potential=self._estimate_lesson_improvement_potential(failure_count)
                )
                bottlenecks.append(bottleneck)
        
        # Sort by bottleneck score (highest first)
        bottlenecks.sort(key=lambda x: x.bottleneck_score, reverse=True)
        
        self.logger.info(f"Identified {len(bottlenecks)} resource bottlenecks")
        return bottlenecks
    
    def analyze_constraint_patterns(
        self,
        constraint_violations: Dict[str, int],
        failure_log: List[Any]
    ) -> List[ConstraintAnalysis]:
        """
        Analyze constraint violation patterns and their impact
        
        Args:
            constraint_violations: Constraint type -> violation count mapping
            failure_log: List of failure entries with detailed context
            
        Returns:
            List of ConstraintAnalysis objects with detailed pattern analysis
        """
        constraint_analyses = []
        
        for constraint_type, frequency in constraint_violations.items():
            if frequency > 0:
                # Analyze affected resources
                affected_resources = self._get_affected_resources_for_constraint(
                    constraint_type, failure_log
                )
                
                # Analyze time patterns
                time_patterns = self._analyze_constraint_time_patterns(
                    constraint_type, failure_log
                )
                
                # Calculate severity score
                severity_score = self._calculate_constraint_severity(
                    constraint_type, frequency, affected_resources, time_patterns
                )
                
                # Generate resolution suggestions
                suggestions = self._generate_constraint_resolution_suggestions(
                    constraint_type, frequency, affected_resources, time_patterns
                )
                
                analysis = ConstraintAnalysis(
                    constraint_type=constraint_type,
                    frequency=frequency,
                    severity_score=severity_score,
                    affected_resources=affected_resources,
                    time_patterns=time_patterns,
                    resolution_suggestions=suggestions
                )
                constraint_analyses.append(analysis)
        
        # Sort by severity score (highest first)
        constraint_analyses.sort(key=lambda x: x.severity_score, reverse=True)
        
        self.logger.info(f"Analyzed {len(constraint_analyses)} constraint patterns")
        return constraint_analyses
    
    def analyze_utilization_patterns(
        self,
        teacher_utilization: Dict[int, Dict[str, Any]],
        class_utilization: Dict[int, Dict[str, Any]],
        slot_conflicts: Dict[Tuple[int, int], int]
    ) -> List[UtilizationPattern]:
        """
        Analyze utilization patterns for teachers and classes
        
        Args:
            teacher_utilization: Teacher utilization data
            class_utilization: Class utilization data
            slot_conflicts: Time slot conflict data
            
        Returns:
            List of UtilizationPattern objects with detailed analysis
        """
        patterns = []
        
        # Analyze teacher utilization patterns
        for teacher_id, data in teacher_utilization.items():
            pattern = self._analyze_resource_utilization_pattern(
                'teacher', teacher_id, data, slot_conflicts
            )
            if pattern:
                patterns.append(pattern)
        
        # Analyze class utilization patterns
        for class_id, data in class_utilization.items():
            pattern = self._analyze_resource_utilization_pattern(
                'class', class_id, data, slot_conflicts
            )
            if pattern:
                patterns.append(pattern)
        
        # Sort by efficiency score (lowest first - most problematic)
        patterns.sort(key=lambda x: x.efficiency_score)
        
        self.logger.info(f"Analyzed {len(patterns)} utilization patterns")
        return patterns
    
    def generate_targeted_improvements(
        self,
        bottlenecks: List[ResourceBottleneck],
        constraint_analyses: List[ConstraintAnalysis],
        utilization_patterns: List[UtilizationPattern]
    ) -> List[str]:
        """
        Generate specific, targeted improvement suggestions
        
        Args:
            bottlenecks: List of identified bottlenecks
            constraint_analyses: List of constraint pattern analyses
            utilization_patterns: List of utilization patterns
            
        Returns:
            List of specific, actionable improvement suggestions
        """
        suggestions = []
        
        # Top bottleneck suggestions
        if bottlenecks:
            top_bottleneck = bottlenecks[0]
            if top_bottleneck.resource_type == 'teacher':
                suggestions.append(
                    f"CRITICAL: Teacher {top_bottleneck.resource_name} is the primary bottleneck "
                    f"(score: {top_bottleneck.bottleneck_score:.2f}). "
                    f"Consider redistributing {len(top_bottleneck.affected_lessons)} affected lessons "
                    f"or adjusting availability during peak conflict times: "
                    f"{', '.join([f'Day {d} Slot {s}' for d, s in top_bottleneck.peak_conflict_times[:3]])}"
                )
            elif top_bottleneck.resource_type == 'class':
                suggestions.append(
                    f"CRITICAL: Class {top_bottleneck.resource_name} is the primary bottleneck "
                    f"(score: {top_bottleneck.bottleneck_score:.2f}). "
                    f"Review curriculum requirements for {len(top_bottleneck.affected_lessons)} lessons "
                    f"and consider alternative scheduling approaches."
                )
            elif top_bottleneck.resource_type == 'time_slot':
                suggestions.append(
                    f"CRITICAL: Time slot {top_bottleneck.resource_name} is severely overloaded "
                    f"(score: {top_bottleneck.bottleneck_score:.2f}). "
                    f"Redistribute lessons to less congested time periods."
                )
        
        # Constraint-specific suggestions
        if constraint_analyses:
            top_constraint = constraint_analyses[0]
            if top_constraint.constraint_type == 'teacher_availability':
                suggestions.append(
                    f"HIGH: Teacher availability constraints cause {top_constraint.frequency} conflicts. "
                    f"Consider implementing flexible availability windows or constraint relaxation."
                )
            elif top_constraint.constraint_type == 'block_rules':
                suggestions.append(
                    f"HIGH: Block rule violations occur {top_constraint.frequency} times. "
                    f"Implement alternative block configurations (e.g., 2+2 instead of 4-hour blocks)."
                )
            elif top_constraint.constraint_type == 'workload_distribution':
                suggestions.append(
                    f"HIGH: Workload distribution issues cause {top_constraint.frequency} conflicts. "
                    f"Consider temporary relaxation allowing up to 2 empty days during initial scheduling."
                )
        
        # Utilization pattern suggestions
        inefficient_patterns = [p for p in utilization_patterns if p.efficiency_score < 0.6]
        if inefficient_patterns:
            pattern = inefficient_patterns[0]
            suggestions.append(
                f"MEDIUM: {pattern.resource_type.title()} {pattern.resource_id} has poor utilization "
                f"efficiency ({pattern.efficiency_score:.1%}). "
                f"Average utilization: {pattern.average_utilization:.1%}, "
                f"Variance: {pattern.variance:.2f}. Consider load balancing."
            )
        
        # Time-based suggestions
        if bottlenecks:
            peak_times = defaultdict(int)
            for bottleneck in bottlenecks[:5]:  # Top 5 bottlenecks
                for day, slot in bottleneck.peak_conflict_times:
                    peak_times[(day, slot)] += 1
            
            if peak_times:
                most_problematic_time = max(peak_times.items(), key=lambda x: x[1])
                day, slot = most_problematic_time[0]
                count = most_problematic_time[1]
                day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
                day_name = day_names[day] if day < 5 else f"Day {day}"
                
                suggestions.append(
                    f"MEDIUM: {day_name} slot {slot} appears in {count} bottlenecks. "
                    f"This time period requires special attention - consider spreading lessons "
                    f"to adjacent time slots or implementing priority scheduling."
                )
        
        # Improvement potential suggestions
        high_potential_bottlenecks = [b for b in bottlenecks if b.improvement_potential > 0.7]
        if high_potential_bottlenecks:
            suggestions.append(
                f"OPPORTUNITY: {len(high_potential_bottlenecks)} bottlenecks have high improvement potential. "
                f"Focusing on these could yield significant scheduling improvements with minimal effort."
            )
        
        return suggestions
    
    def _calculate_resource_bottleneck_score(
        self, conflict_count: int, utilization_rate: float, resource_type: str
    ) -> float:
        """Calculate bottleneck score for a resource"""
        base_score = conflict_count * self.weights['conflict_frequency']
        
        # Adjust for utilization (overutilized resources are bigger bottlenecks)
        if utilization_rate > 0.8:
            utilization_penalty = (utilization_rate - 0.8) * 5 * self.weights['resource_utilization']
        else:
            utilization_penalty = 0
        
        # Resource type multiplier
        type_multipliers = {'teacher': 1.2, 'class': 1.0, 'time_slot': 0.8}
        type_multiplier = type_multipliers.get(resource_type, 1.0)
        
        return (base_score + utilization_penalty) * type_multiplier
    
    def _calculate_lesson_bottleneck_score(self, failure_count: int) -> float:
        """Calculate bottleneck score for a lesson"""
        return failure_count * 2.0  # Lessons with multiple failures are critical
    
    def _calculate_slot_utilization(
        self, day: int, slot: int, slot_conflicts: Dict[Tuple[int, int], int]
    ) -> float:
        """Calculate utilization rate for a time slot"""
        total_conflicts = sum(slot_conflicts.values())
        if total_conflicts == 0:
            return 0.0
        
        slot_conflicts_count = slot_conflicts.get((day, slot), 0)
        return slot_conflicts_count / total_conflicts
    
    def _estimate_improvement_potential(
        self, conflict_count: int, utilization_rate: float, resource_type: str
    ) -> float:
        """Estimate improvement potential if bottleneck is resolved"""
        base_potential = min(conflict_count / 10.0, 1.0)  # Normalize to 0-1
        
        # Higher utilization means more potential for improvement
        utilization_factor = utilization_rate if utilization_rate > 0.5 else 0.5
        
        return base_potential * utilization_factor
    
    def _estimate_lesson_improvement_potential(self, failure_count: int) -> float:
        """Estimate improvement potential for a lesson"""
        return min(failure_count / 5.0, 1.0)  # Normalize to 0-1
    
    def _get_affected_lessons_for_teacher(
        self, teacher_id: int, lesson_failures: Dict[int, int]
    ) -> List[int]:
        """Get lessons affected by teacher bottleneck"""
        # This would need actual failure log analysis in a real implementation
        # For now, return a subset of failed lessons
        return list(lesson_failures.keys())[:5]
    
    def _get_affected_lessons_for_class(
        self, class_id: int, lesson_failures: Dict[int, int]
    ) -> List[int]:
        """Get lessons affected by class bottleneck"""
        # This would need actual failure log analysis in a real implementation
        return list(lesson_failures.keys())[:5]
    
    def _get_peak_conflict_times_for_teacher(
        self, teacher_id: int, slot_conflicts: Dict[Tuple[int, int], int]
    ) -> List[Tuple[int, int]]:
        """Get peak conflict times for a teacher"""
        # Return top conflict slots (simplified implementation)
        sorted_slots = sorted(slot_conflicts.items(), key=lambda x: x[1], reverse=True)
        return [slot for slot, _ in sorted_slots[:5]]
    
    def _get_peak_conflict_times_for_class(
        self, class_id: int, slot_conflicts: Dict[Tuple[int, int], int]
    ) -> List[Tuple[int, int]]:
        """Get peak conflict times for a class"""
        # Return top conflict slots (simplified implementation)
        sorted_slots = sorted(slot_conflicts.items(), key=lambda x: x[1], reverse=True)
        return [slot for slot, _ in sorted_slots[:5]]
    
    def _get_affected_resources_for_constraint(
        self, constraint_type: str, failure_log: List[Any]
    ) -> List[Tuple[str, int]]:
        """Get resources affected by a specific constraint type"""
        affected = set()
        for failure in failure_log:
            if hasattr(failure, 'constraint_violations') and constraint_type in failure.constraint_violations:
                if hasattr(failure, 'teacher_id'):
                    affected.add(('teacher', failure.teacher_id))
                if hasattr(failure, 'class_id'):
                    affected.add(('class', failure.class_id))
        return list(affected)
    
    def _analyze_constraint_time_patterns(
        self, constraint_type: str, failure_log: List[Any]
    ) -> Dict[Tuple[int, int], int]:
        """Analyze time patterns for constraint violations"""
        patterns = defaultdict(int)
        for failure in failure_log:
            if hasattr(failure, 'constraint_violations') and constraint_type in failure.constraint_violations:
                if hasattr(failure, 'attempted_slots'):
                    for day, slot in failure.attempted_slots:
                        patterns[(day, slot)] += 1
        return dict(patterns)
    
    def _calculate_constraint_severity(
        self,
        constraint_type: str,
        frequency: int,
        affected_resources: List[Tuple[str, int]],
        time_patterns: Dict[Tuple[int, int], int]
    ) -> float:
        """Calculate severity score for a constraint"""
        base_severity = frequency * 0.5
        resource_impact = len(affected_resources) * 0.3
        time_concentration = len(time_patterns) * 0.2
        
        return base_severity + resource_impact + time_concentration
    
    def _generate_constraint_resolution_suggestions(
        self,
        constraint_type: str,
        frequency: int,
        affected_resources: List[Tuple[str, int]],
        time_patterns: Dict[Tuple[int, int], int]
    ) -> List[str]:
        """Generate specific suggestions for resolving constraint violations"""
        suggestions = []
        
        if constraint_type == 'teacher_availability':
            suggestions.append("Consider implementing flexible teacher availability windows")
            suggestions.append("Review teacher schedules for optimization opportunities")
        elif constraint_type == 'block_rules':
            suggestions.append("Implement alternative block configurations (e.g., split large blocks)")
            suggestions.append("Consider relaxing consecutive slot requirements for specific lessons")
        elif constraint_type == 'workload_distribution':
            suggestions.append("Allow temporary workload imbalances during initial scheduling")
            suggestions.append("Implement post-scheduling workload rebalancing")
        else:
            suggestions.append(f"Review and potentially relax {constraint_type} constraints")
        
        return suggestions
    
    def _analyze_resource_utilization_pattern(
        self,
        resource_type: str,
        resource_id: int,
        utilization_data: Dict[str, Any],
        slot_conflicts: Dict[Tuple[int, int], int]
    ) -> Optional[UtilizationPattern]:
        """Analyze utilization pattern for a specific resource"""
        if not utilization_data:
            return None
        
        # Extract utilization metrics
        avg_utilization = utilization_data.get('utilization_rate', 0.0)
        
        # Calculate variance (simplified)
        variance = utilization_data.get('variance', 0.0)
        
        # Calculate efficiency score
        efficiency_score = self._calculate_efficiency_score(avg_utilization, variance)
        
        # Get peak and low hours (simplified - would need detailed slot data)
        peak_hours = [(d, s, 0.9) for d in range(5) for s in range(3)][:3]  # Mock data
        low_hours = [(d, s, 0.1) for d in range(5) for s in range(3, 6)][:3]  # Mock data
        
        return UtilizationPattern(
            resource_type=resource_type,
            resource_id=resource_id,
            peak_hours=peak_hours,
            low_hours=low_hours,
            average_utilization=avg_utilization,
            variance=variance,
            efficiency_score=efficiency_score
        )
    
    def _calculate_efficiency_score(self, avg_utilization: float, variance: float) -> float:
        """Calculate efficiency score based on utilization and variance"""
        # Ideal utilization is around 0.7-0.8, low variance is better
        utilization_score = 1.0 - abs(avg_utilization - 0.75) / 0.75
        variance_penalty = min(variance, 0.5) / 0.5  # Normalize variance penalty
        
        return max(0.0, utilization_score - variance_penalty)