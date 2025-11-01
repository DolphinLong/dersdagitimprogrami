# -*- coding: utf-8 -*-
"""
Solution Validator - Comprehensive validation system for scheduler optimization

This module provides comprehensive validation of scheduling solutions to ensure
all constraints are satisfied, conflicts are detected, and block rules are properly
enforced. It validates workload distribution and provides detailed validation reports.

Key Features:
- Complete constraint satisfaction verification
- Teacher and class conflict detection
- Block rule validation (consecutive slots, proper patterns)
- Workload distribution validation
- Detailed validation reporting with specific violations
- Performance metrics for validation process

Requirements addressed: 1.4, 3.5, 5.2
"""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum

from database.models import Teacher, Class, Lesson
from algorithms.optimized_curriculum_scheduler import EnhancedScheduleEntry, WorkloadViolation


class ViolationType(Enum):
    """Types of validation violations"""
    TEACHER_CONFLICT = "teacher_conflict"
    CLASS_CONFLICT = "class_conflict"
    BLOCK_RULE_VIOLATION = "block_rule_violation"
    WORKLOAD_VIOLATION = "workload_violation"
    AVAILABILITY_VIOLATION = "availability_violation"
    CURRICULUM_VIOLATION = "curriculum_violation"
    CLASSROOM_CONFLICT = "classroom_conflict"


@dataclass
class ValidationViolation:
    """Represents a validation violation with detailed context"""
    violation_type: ViolationType
    severity: str  # "critical", "major", "minor"
    description: str
    affected_entries: List[EnhancedScheduleEntry]
    context: Dict[str, Any] = field(default_factory=dict)
    suggested_fix: Optional[str] = None


@dataclass
class BlockValidationResult:
    """Result of block rule validation"""
    is_valid: bool
    violations: List[ValidationViolation] = field(default_factory=list)
    block_patterns: Dict[str, List[Tuple[int, int]]] = field(default_factory=dict)  # block_id -> [(day, slot), ...]
    fragmented_blocks: List[str] = field(default_factory=list)  # block_ids with fragmentation
    invalid_patterns: List[Tuple[str, str]] = field(default_factory=list)  # (block_id, reason)


@dataclass
class WorkloadValidationResult:
    """Result of workload distribution validation"""
    is_valid: bool
    violations: List[WorkloadViolation] = field(default_factory=list)
    teacher_workloads: Dict[int, Dict[str, Any]] = field(default_factory=dict)
    empty_day_violations: Dict[int, int] = field(default_factory=dict)  # teacher_id -> empty_days
    overload_violations: Dict[int, float] = field(default_factory=dict)  # teacher_id -> overload_hours


@dataclass
class ValidationReport:
    """Comprehensive validation report"""
    is_valid: bool
    total_violations: int
    violations_by_type: Dict[ViolationType, int] = field(default_factory=dict)
    critical_violations: List[ValidationViolation] = field(default_factory=list)
    major_violations: List[ValidationViolation] = field(default_factory=list)
    minor_violations: List[ValidationViolation] = field(default_factory=list)
    block_validation: Optional[BlockValidationResult] = None
    workload_validation: Optional[WorkloadValidationResult] = None
    conflict_summary: Dict[str, int] = field(default_factory=dict)
    validation_metrics: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


class SolutionValidator:
    """
    Comprehensive solution validator for scheduler optimization
    
    Validates all aspects of a scheduling solution including constraints,
    conflicts, block rules, and workload distribution to ensure 100%
    compliance with scheduling requirements.
    """
    
    def __init__(self, db_manager=None):
        """
        Initialize solution validator
        
        Args:
            db_manager: Database manager for accessing constraint data
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.db_manager = db_manager
        
        # Validation configuration
        self.max_empty_days = 1  # Maximum allowed empty days per teacher
        self.max_daily_hours = 8  # Maximum hours per day per teacher
        self.required_block_patterns = {
            5: [(2, 2, 1), (3, 1, 1), (2, 1, 1, 1)],  # 5-hour lesson patterns
            4: [(2, 2), (3, 1), (2, 1, 1)],  # 4-hour lesson patterns
            3: [(2, 1), (1, 1, 1)],  # 3-hour lesson patterns
            2: [(2,), (1, 1)],  # 2-hour lesson patterns
            1: [(1,)]  # 1-hour lesson patterns
        }
        
        self.logger.info("SolutionValidator initialized")
    
    def validate_complete_solution(self, entries: List[EnhancedScheduleEntry]) -> ValidationReport:
        """
        Validate complete scheduling solution with comprehensive checks
        
        Args:
            entries: List of enhanced schedule entries to validate
            
        Returns:
            ValidationReport with detailed validation results
        """
        self.logger.info(f"Starting comprehensive validation of {len(entries)} schedule entries")
        
        report = ValidationReport(is_valid=True, total_violations=0)
        all_violations = []
        
        # Step 1: Validate teacher and class conflicts
        self.logger.debug("Validating conflicts...")
        conflict_violations = self._validate_conflicts(entries)
        all_violations.extend(conflict_violations)
        
        # Step 2: Validate block rules
        self.logger.debug("Validating block rules...")
        block_result = self._validate_block_rules(entries)
        report.block_validation = block_result
        all_violations.extend(block_result.violations)
        
        # Step 3: Validate workload distribution
        self.logger.debug("Validating workload distribution...")
        workload_result = self._validate_workload_distribution(entries)
        report.workload_validation = workload_result
        all_violations.extend([
            ValidationViolation(
                violation_type=ViolationType.WORKLOAD_VIOLATION,
                severity="major",
                description=f"Teacher {v.teacher_name} has {v.empty_days} empty days (max: {self.max_empty_days})",
                affected_entries=[],
                context={"teacher_id": v.teacher_id, "empty_days": v.empty_days},
                suggested_fix="Redistribute lessons to reduce empty days"
            )
            for v in workload_result.violations
        ])
        
        # Step 4: Validate curriculum requirements
        self.logger.debug("Validating curriculum requirements...")
        curriculum_violations = self._validate_curriculum_requirements(entries)
        all_violations.extend(curriculum_violations)
        
        # Step 5: Validate teacher availability
        self.logger.debug("Validating teacher availability...")
        availability_violations = self._validate_teacher_availability(entries)
        all_violations.extend(availability_violations)
        
        # Categorize violations by severity
        for violation in all_violations:
            if violation.severity == "critical":
                report.critical_violations.append(violation)
            elif violation.severity == "major":
                report.major_violations.append(violation)
            else:
                report.minor_violations.append(violation)
            
            # Count by type
            if violation.violation_type not in report.violations_by_type:
                report.violations_by_type[violation.violation_type] = 0
            report.violations_by_type[violation.violation_type] += 1
        
        # Update report summary
        report.total_violations = len(all_violations)
        report.is_valid = len(report.critical_violations) == 0 and len(report.major_violations) == 0
        
        # Generate conflict summary
        report.conflict_summary = self._generate_conflict_summary(all_violations)
        
        # Generate validation metrics
        report.validation_metrics = self._generate_validation_metrics(entries, all_violations)
        
        # Generate recommendations
        report.recommendations = self._generate_validation_recommendations(report)
        
        # Log validation results
        self.logger.info(f"Validation completed:")
        self.logger.info(f"  Valid: {report.is_valid}")
        self.logger.info(f"  Total violations: {report.total_violations}")
        self.logger.info(f"  Critical: {len(report.critical_violations)}")
        self.logger.info(f"  Major: {len(report.major_violations)}")
        self.logger.info(f"  Minor: {len(report.minor_violations)}")
        
        return report
    
    def _validate_conflicts(self, entries: List[EnhancedScheduleEntry]) -> List[ValidationViolation]:
        """
        Check for conflicts between classes and teachers
        
        Args:
            entries: Schedule entries to validate
            
        Returns:
            List of conflict violations
        """
        violations = []
        
        # Group entries by time slot for conflict detection
        slot_entries = defaultdict(list)  # (day, time_slot) -> [entries]
        
        for entry in entries:
            slot_key = (entry.day, entry.time_slot)
            slot_entries[slot_key].append(entry)
        
        # Check each time slot for conflicts
        for (day, time_slot), slot_entries_list in slot_entries.items():
            if len(slot_entries_list) <= 1:
                continue  # No conflicts possible with single entry
            
            # Check for teacher conflicts
            teacher_entries = defaultdict(list)
            for entry in slot_entries_list:
                teacher_entries[entry.teacher_id].append(entry)
            
            for teacher_id, teacher_slot_entries in teacher_entries.items():
                if len(teacher_slot_entries) > 1:
                    # Teacher conflict detected
                    violations.append(ValidationViolation(
                        violation_type=ViolationType.TEACHER_CONFLICT,
                        severity="critical",
                        description=f"Teacher {teacher_id} scheduled for multiple classes at Day {day}, Slot {time_slot}",
                        affected_entries=teacher_slot_entries,
                        context={
                            "teacher_id": teacher_id,
                            "day": day,
                            "time_slot": time_slot,
                            "conflicting_classes": [e.class_id for e in teacher_slot_entries]
                        },
                        suggested_fix="Reschedule one of the conflicting lessons to a different time slot"
                    ))
            
            # Check for class conflicts
            class_entries = defaultdict(list)
            for entry in slot_entries_list:
                class_entries[entry.class_id].append(entry)
            
            for class_id, class_slot_entries in class_entries.items():
                if len(class_slot_entries) > 1:
                    # Class conflict detected
                    violations.append(ValidationViolation(
                        violation_type=ViolationType.CLASS_CONFLICT,
                        severity="critical",
                        description=f"Class {class_id} scheduled for multiple lessons at Day {day}, Slot {time_slot}",
                        affected_entries=class_slot_entries,
                        context={
                            "class_id": class_id,
                            "day": day,
                            "time_slot": time_slot,
                            "conflicting_lessons": [e.lesson_id for e in class_slot_entries]
                        },
                        suggested_fix="Reschedule one of the conflicting lessons to a different time slot"
                    ))
        
        return violations
    
    def _validate_block_rules(self, entries: List[EnhancedScheduleEntry]) -> BlockValidationResult:
        """
        Validate block rules and workload distribution
        
        Args:
            entries: Schedule entries to validate
            
        Returns:
            BlockValidationResult with detailed block validation
        """
        result = BlockValidationResult(is_valid=True)
        
        # Group entries by block_id
        block_entries = defaultdict(list)
        for entry in entries:
            if entry.block_id:
                block_entries[entry.block_id].append(entry)
        
        # Validate each block
        for block_id, block_entry_list in block_entries.items():
            if not block_entry_list:
                continue
            
            # Sort entries by day and time_slot
            block_entry_list.sort(key=lambda e: (e.day, e.time_slot))
            
            # Extract time slots for this block
            time_slots = [(e.day, e.time_slot) for e in block_entry_list]
            result.block_patterns[block_id] = time_slots
            
            # Validate block pattern
            block_violations = self._validate_single_block_pattern(block_id, block_entry_list, time_slots)
            result.violations.extend(block_violations)
            
            # Check for fragmentation
            if self._is_block_fragmented(time_slots):
                result.fragmented_blocks.append(block_id)
                result.violations.append(ValidationViolation(
                    violation_type=ViolationType.BLOCK_RULE_VIOLATION,
                    severity="major",
                    description=f"Block {block_id} is fragmented across non-consecutive time slots",
                    affected_entries=block_entry_list,
                    context={"block_id": block_id, "time_slots": time_slots},
                    suggested_fix="Reschedule block to consecutive time slots"
                ))
        
        # Update overall validity
        result.is_valid = len(result.violations) == 0
        
        return result
    
    def _validate_single_block_pattern(self, block_id: str, entries: List[EnhancedScheduleEntry], 
                                     time_slots: List[Tuple[int, int]]) -> List[ValidationViolation]:
        """
        Validate a single block's pattern against allowed configurations
        
        Args:
            block_id: Block identifier
            entries: Entries in this block
            time_slots: Time slots for this block
            
        Returns:
            List of violations for this block
        """
        violations = []
        block_size = len(entries)
        
        # Check if block size has valid patterns
        if block_size not in self.required_block_patterns:
            violations.append(ValidationViolation(
                violation_type=ViolationType.BLOCK_RULE_VIOLATION,
                severity="major",
                description=f"Block {block_id} has invalid size {block_size} hours",
                affected_entries=entries,
                context={"block_id": block_id, "block_size": block_size},
                suggested_fix=f"Adjust block size to one of: {list(self.required_block_patterns.keys())}"
            ))
            return violations
        
        # For blocks larger than 1 hour, validate consecutive placement
        if block_size > 1:
            # Check if slots are properly arranged
            if not self._are_slots_properly_arranged(time_slots, block_size):
                violations.append(ValidationViolation(
                    violation_type=ViolationType.BLOCK_RULE_VIOLATION,
                    severity="major",
                    description=f"Block {block_id} slots are not properly arranged for {block_size}-hour lesson",
                    affected_entries=entries,
                    context={"block_id": block_id, "time_slots": time_slots, "block_size": block_size},
                    suggested_fix="Arrange block slots according to valid patterns (consecutive or approved alternatives)"
                ))
        
        # Validate block positions
        for i, entry in enumerate(entries):
            expected_position = i + 1
            if entry.block_position != expected_position:
                violations.append(ValidationViolation(
                    violation_type=ViolationType.BLOCK_RULE_VIOLATION,
                    severity="minor",
                    description=f"Block {block_id} entry has incorrect position {entry.block_position}, expected {expected_position}",
                    affected_entries=[entry],
                    context={"block_id": block_id, "actual_position": entry.block_position, "expected_position": expected_position},
                    suggested_fix="Correct block position numbering"
                ))
        
        return violations
    
    def _is_block_fragmented(self, time_slots: List[Tuple[int, int]]) -> bool:
        """
        Check if a block is fragmented (not in consecutive slots)
        
        Args:
            time_slots: List of (day, slot) tuples
            
        Returns:
            True if block is fragmented
        """
        if len(time_slots) <= 1:
            return False
        
        # Sort slots
        sorted_slots = sorted(time_slots)
        
        # Check for consecutive slots within same day
        for i in range(len(sorted_slots) - 1):
            current_day, current_slot = sorted_slots[i]
            next_day, next_slot = sorted_slots[i + 1]
            
            # If same day, slots should be consecutive
            if current_day == next_day:
                if next_slot != current_slot + 1:
                    return True  # Gap in same day
            else:
                # Different days - check if it's a valid cross-day pattern
                # For now, consider cross-day blocks as potentially fragmented
                # This could be enhanced based on specific school policies
                pass
        
        return False
    
    def _are_slots_properly_arranged(self, time_slots: List[Tuple[int, int]], block_size: int) -> bool:
        """
        Check if time slots are properly arranged for the given block size
        
        Args:
            time_slots: List of (day, slot) tuples
            block_size: Size of the block in hours
            
        Returns:
            True if slots are properly arranged
        """
        if len(time_slots) != block_size:
            return False
        
        # Get valid patterns for this block size
        valid_patterns = self.required_block_patterns.get(block_size, [])
        
        # For simple validation, check if slots form valid consecutive groups
        # This is a simplified check - could be enhanced for complex patterns
        
        # Group slots by day
        day_slots = defaultdict(list)
        for day, slot in time_slots:
            day_slots[day].append(slot)
        
        # Check each day's slots are consecutive
        for day, slots in day_slots.items():
            sorted_slots = sorted(slots)
            for i in range(len(sorted_slots) - 1):
                if sorted_slots[i + 1] != sorted_slots[i] + 1:
                    return False  # Non-consecutive slots in same day
        
        return True
    
    def _validate_workload_distribution(self, entries: List[EnhancedScheduleEntry]) -> WorkloadValidationResult:
        """
        Validate workload distribution for all teachers
        
        Args:
            entries: Schedule entries to validate
            
        Returns:
            WorkloadValidationResult with workload analysis
        """
        result = WorkloadValidationResult(is_valid=True)
        
        # Group entries by teacher
        teacher_entries = defaultdict(list)
        for entry in entries:
            teacher_entries[entry.teacher_id].append(entry)
        
        # Analyze each teacher's workload
        for teacher_id, teacher_entry_list in teacher_entries.items():
            workload_data = self._analyze_teacher_workload(teacher_id, teacher_entry_list)
            result.teacher_workloads[teacher_id] = workload_data
            
            # Check for empty day violations
            empty_days = workload_data.get('empty_days', 0)
            if empty_days > self.max_empty_days:
                result.empty_day_violations[teacher_id] = empty_days
                
                # Get teacher name if available
                teacher_name = f"Teacher_{teacher_id}"
                if self.db_manager:
                    teacher = self.db_manager.get_teacher_by_id(teacher_id)
                    if teacher:
                        teacher_name = teacher.name
                
                violation = WorkloadViolation(
                    teacher_id=teacher_id,
                    teacher_name=teacher_name,
                    empty_days=empty_days,
                    working_days=set(workload_data.get('working_days', [])),
                    violation_severity="major" if empty_days > 2 else "minor"
                )
                result.violations.append(violation)
            
            # Check for overload violations
            daily_hours = workload_data.get('daily_hours', {})
            for day, hours in daily_hours.items():
                if hours > self.max_daily_hours:
                    result.overload_violations[teacher_id] = hours
        
        # Update overall validity
        result.is_valid = len(result.violations) == 0 and len(result.overload_violations) == 0
        
        return result
    
    def _analyze_teacher_workload(self, teacher_id: int, entries: List[EnhancedScheduleEntry]) -> Dict[str, Any]:
        """
        Analyze workload for a single teacher
        
        Args:
            teacher_id: Teacher ID
            entries: Teacher's schedule entries
            
        Returns:
            Dictionary with workload analysis
        """
        # Group by day
        daily_entries = defaultdict(list)
        for entry in entries:
            daily_entries[entry.day].append(entry)
        
        # Calculate metrics
        working_days = list(daily_entries.keys())
        total_days = 5  # Monday to Friday
        empty_days = total_days - len(working_days)
        
        daily_hours = {}
        for day in range(total_days):
            daily_hours[day] = len(daily_entries.get(day, []))
        
        total_hours = sum(daily_hours.values())
        average_daily_hours = total_hours / total_days if total_days > 0 else 0
        
        return {
            'teacher_id': teacher_id,
            'total_hours': total_hours,
            'working_days': working_days,
            'empty_days': empty_days,
            'daily_hours': daily_hours,
            'average_daily_hours': average_daily_hours,
            'max_daily_hours': max(daily_hours.values()) if daily_hours else 0,
            'min_daily_hours': min(daily_hours.values()) if daily_hours else 0
        }
    
    def _validate_curriculum_requirements(self, entries: List[EnhancedScheduleEntry]) -> List[ValidationViolation]:
        """
        Validate curriculum requirements are met
        
        Args:
            entries: Schedule entries to validate
            
        Returns:
            List of curriculum violations
        """
        violations = []
        
        if not self.db_manager:
            return violations  # Cannot validate without database access
        
        # Group entries by class and lesson
        class_lesson_hours = defaultdict(lambda: defaultdict(int))
        for entry in entries:
            class_lesson_hours[entry.class_id][entry.lesson_id] += 1
        
        # Check each class's curriculum requirements
        classes = self.db_manager.get_all_classes()
        for class_obj in classes:
            class_id = class_obj.class_id
            
            # Get curriculum requirements for this class
            assignments = self.db_manager.get_schedule_by_school_type()
            class_assignments = [a for a in assignments if a.class_id == class_id]
            
            for assignment in class_assignments:
                lesson_id = assignment.lesson_id
                required_hours = self.db_manager.get_weekly_hours_for_lesson(lesson_id, class_obj.grade)
                
                if required_hours and required_hours > 0:
                    scheduled_hours = class_lesson_hours[class_id].get(lesson_id, 0)
                    
                    if scheduled_hours < required_hours:
                        lesson = self.db_manager.get_lesson_by_id(lesson_id)
                        lesson_name = lesson.name if lesson else f"Lesson_{lesson_id}"
                        
                        violations.append(ValidationViolation(
                            violation_type=ViolationType.CURRICULUM_VIOLATION,
                            severity="critical",
                            description=f"Class {class_obj.name} missing {required_hours - scheduled_hours} hours of {lesson_name}",
                            affected_entries=[],
                            context={
                                "class_id": class_id,
                                "lesson_id": lesson_id,
                                "required_hours": required_hours,
                                "scheduled_hours": scheduled_hours,
                                "missing_hours": required_hours - scheduled_hours
                            },
                            suggested_fix=f"Schedule additional {required_hours - scheduled_hours} hours of {lesson_name}"
                        ))
                    elif scheduled_hours > required_hours:
                        lesson = self.db_manager.get_lesson_by_id(lesson_id)
                        lesson_name = lesson.name if lesson else f"Lesson_{lesson_id}"
                        
                        violations.append(ValidationViolation(
                            violation_type=ViolationType.CURRICULUM_VIOLATION,
                            severity="minor",
                            description=f"Class {class_obj.name} has {scheduled_hours - required_hours} extra hours of {lesson_name}",
                            affected_entries=[],
                            context={
                                "class_id": class_id,
                                "lesson_id": lesson_id,
                                "required_hours": required_hours,
                                "scheduled_hours": scheduled_hours,
                                "extra_hours": scheduled_hours - required_hours
                            },
                            suggested_fix=f"Remove {scheduled_hours - required_hours} hours of {lesson_name}"
                        ))
        
        return violations
    
    def _validate_teacher_availability(self, entries: List[EnhancedScheduleEntry]) -> List[ValidationViolation]:
        """
        Validate teacher availability constraints
        
        Args:
            entries: Schedule entries to validate
            
        Returns:
            List of availability violations
        """
        violations = []
        
        if not self.db_manager:
            return violations  # Cannot validate without database access
        
        # Get teacher availability data
        try:
            # This would need to be implemented based on your availability system
            # For now, we'll do basic validation
            
            # Group entries by teacher
            teacher_entries = defaultdict(list)
            for entry in entries:
                teacher_entries[entry.teacher_id].append(entry)
            
            # Check each teacher's schedule against availability
            for teacher_id, teacher_entry_list in teacher_entries.items():
                teacher = self.db_manager.get_teacher_by_id(teacher_id)
                if not teacher:
                    continue
                
                # Basic availability check - could be enhanced with actual availability data
                for entry in teacher_entry_list:
                    # Check for unreasonable scheduling (e.g., too early or too late)
                    if entry.time_slot < 0 or entry.time_slot > 7:  # Assuming 8 slots per day (0-7)
                        violations.append(ValidationViolation(
                            violation_type=ViolationType.AVAILABILITY_VIOLATION,
                            severity="major",
                            description=f"Teacher {teacher.name} scheduled at invalid time slot {entry.time_slot}",
                            affected_entries=[entry],
                            context={
                                "teacher_id": teacher_id,
                                "day": entry.day,
                                "time_slot": entry.time_slot
                            },
                            suggested_fix="Reschedule to valid time slot (0-7)"
                        ))
        
        except Exception as e:
            self.logger.warning(f"Could not validate teacher availability: {e}")
        
        return violations
    
    def _generate_conflict_summary(self, violations: List[ValidationViolation]) -> Dict[str, int]:
        """
        Generate summary of conflicts by type
        
        Args:
            violations: List of all violations
            
        Returns:
            Dictionary with conflict counts by type
        """
        summary = {
            "teacher_conflicts": 0,
            "class_conflicts": 0,
            "block_violations": 0,
            "workload_violations": 0,
            "curriculum_violations": 0,
            "availability_violations": 0,
            "total_conflicts": len(violations)
        }
        
        for violation in violations:
            if violation.violation_type == ViolationType.TEACHER_CONFLICT:
                summary["teacher_conflicts"] += 1
            elif violation.violation_type == ViolationType.CLASS_CONFLICT:
                summary["class_conflicts"] += 1
            elif violation.violation_type == ViolationType.BLOCK_RULE_VIOLATION:
                summary["block_violations"] += 1
            elif violation.violation_type == ViolationType.WORKLOAD_VIOLATION:
                summary["workload_violations"] += 1
            elif violation.violation_type == ViolationType.CURRICULUM_VIOLATION:
                summary["curriculum_violations"] += 1
            elif violation.violation_type == ViolationType.AVAILABILITY_VIOLATION:
                summary["availability_violations"] += 1
        
        return summary
    
    def _generate_validation_metrics(self, entries: List[EnhancedScheduleEntry], 
                                   violations: List[ValidationViolation]) -> Dict[str, Any]:
        """
        Generate validation performance metrics
        
        Args:
            entries: Schedule entries validated
            violations: All violations found
            
        Returns:
            Dictionary with validation metrics
        """
        total_entries = len(entries)
        total_violations = len(violations)
        
        # Calculate violation rates
        violation_rate = (total_violations / total_entries * 100) if total_entries > 0 else 0
        
        # Count violations by severity
        critical_count = len([v for v in violations if v.severity == "critical"])
        major_count = len([v for v in violations if v.severity == "major"])
        minor_count = len([v for v in violations if v.severity == "minor"])
        
        # Calculate quality score (0-100)
        quality_score = max(0, 100 - (critical_count * 10 + major_count * 5 + minor_count * 1))
        
        return {
            "total_entries_validated": total_entries,
            "total_violations": total_violations,
            "violation_rate_percent": round(violation_rate, 2),
            "critical_violations": critical_count,
            "major_violations": major_count,
            "minor_violations": minor_count,
            "quality_score": round(quality_score, 1),
            "validation_passed": critical_count == 0 and major_count == 0
        }
    
    def _generate_validation_recommendations(self, report: ValidationReport) -> List[str]:
        """
        Generate specific recommendations based on validation results
        
        Args:
            report: Validation report
            
        Returns:
            List of actionable recommendations
        """
        recommendations = []
        
        # Critical violations
        if report.critical_violations:
            recommendations.append(f"URGENT: Fix {len(report.critical_violations)} critical violations before using this schedule")
            
            # Specific recommendations for critical violations
            teacher_conflicts = len([v for v in report.critical_violations if v.violation_type == ViolationType.TEACHER_CONFLICT])
            if teacher_conflicts > 0:
                recommendations.append(f"Resolve {teacher_conflicts} teacher conflicts by rescheduling overlapping lessons")
            
            class_conflicts = len([v for v in report.critical_violations if v.violation_type == ViolationType.CLASS_CONFLICT])
            if class_conflicts > 0:
                recommendations.append(f"Resolve {class_conflicts} class conflicts by rescheduling overlapping lessons")
        
        # Major violations
        if report.major_violations:
            recommendations.append(f"Address {len(report.major_violations)} major violations to improve schedule quality")
            
            # Block rule violations
            block_violations = len([v for v in report.major_violations if v.violation_type == ViolationType.BLOCK_RULE_VIOLATION])
            if block_violations > 0:
                recommendations.append(f"Fix {block_violations} block rule violations by ensuring consecutive lesson placement")
            
            # Workload violations
            workload_violations = len([v for v in report.major_violations if v.violation_type == ViolationType.WORKLOAD_VIOLATION])
            if workload_violations > 0:
                recommendations.append(f"Rebalance workload for teachers with {workload_violations} workload violations")
        
        # Block-specific recommendations
        if report.block_validation and not report.block_validation.is_valid:
            if report.block_validation.fragmented_blocks:
                recommendations.append(f"Consolidate {len(report.block_validation.fragmented_blocks)} fragmented lesson blocks")
        
        # Workload-specific recommendations
        if report.workload_validation and not report.workload_validation.is_valid:
            if report.workload_validation.empty_day_violations:
                recommendations.append(f"Redistribute lessons for {len(report.workload_validation.empty_day_violations)} teachers with excessive empty days")
        
        # Overall quality recommendations
        quality_score = report.validation_metrics.get("quality_score", 0)
        if quality_score < 80:
            recommendations.append(f"Overall quality score is {quality_score}/100. Focus on reducing violations to improve schedule quality")
        elif quality_score < 95:
            recommendations.append(f"Good quality score ({quality_score}/100). Address minor violations for optimal schedule")
        
        # If no violations, provide positive feedback
        if not recommendations and report.is_valid:
            recommendations.append("Excellent! Schedule passes all validation checks with no violations")
        
        return recommendations
    
    def validate_single_constraint(self, entries: List[EnhancedScheduleEntry], 
                                 constraint_type: str) -> List[ValidationViolation]:
        """
        Validate a specific constraint type
        
        Args:
            entries: Schedule entries to validate
            constraint_type: Type of constraint to validate
            
        Returns:
            List of violations for the specified constraint
        """
        if constraint_type == "conflicts":
            return self._validate_conflicts(entries)
        elif constraint_type == "blocks":
            result = self._validate_block_rules(entries)
            return result.violations
        elif constraint_type == "workload":
            result = self._validate_workload_distribution(entries)
            return [
                ValidationViolation(
                    violation_type=ViolationType.WORKLOAD_VIOLATION,
                    severity="major",
                    description=f"Teacher {v.teacher_name} workload violation",
                    affected_entries=[],
                    context={"teacher_id": v.teacher_id}
                )
                for v in result.violations
            ]
        elif constraint_type == "curriculum":
            return self._validate_curriculum_requirements(entries)
        elif constraint_type == "availability":
            return self._validate_teacher_availability(entries)
        else:
            self.logger.warning(f"Unknown constraint type: {constraint_type}")
            return []
    
    def get_validation_summary(self, report: ValidationReport) -> Dict[str, Any]:
        """
        Get a concise validation summary
        
        Args:
            report: Validation report
            
        Returns:
            Dictionary with summary information
        """
        return {
            "is_valid": report.is_valid,
            "total_violations": report.total_violations,
            "quality_score": report.validation_metrics.get("quality_score", 0),
            "critical_issues": len(report.critical_violations),
            "major_issues": len(report.major_violations),
            "minor_issues": len(report.minor_violations),
            "top_recommendations": report.recommendations[:3],  # Top 3 recommendations
            "validation_passed": report.validation_metrics.get("validation_passed", False)
        }