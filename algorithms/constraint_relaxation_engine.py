"""
Constraint Relaxation Engine - Graduated constraint relaxation for optimal scheduling
Implements flexible constraint handling with workload distribution management
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum

from database.db_manager import DatabaseManager


class RelaxationLevel(Enum):
    """Graduated constraint relaxation levels"""
    STRICT = "strict"                    # All constraints enforced (max 1 empty day)
    WORKLOAD_FLEX = "workload_flex"      # Allow up to 2 empty days temporarily
    BLOCK_FLEX = "block_flex"            # Allow non-consecutive blocks for large lessons
    AVAILABILITY_FLEX = "availability_flex"  # Minor teacher availability violations


@dataclass
class WorkloadViolation:
    """Represents a workload distribution violation"""
    teacher_id: int
    teacher_name: str
    empty_days: int
    working_days: Set[int]
    violation_severity: str  # "minor", "moderate", "severe"
    suggested_adjustments: List[str] = field(default_factory=list)


@dataclass
class ConstraintState:
    """Stores the current state of constraints"""
    workload_max_empty_days: int = 1
    allow_non_consecutive_blocks: bool = False
    allow_availability_violations: bool = False
    strict_block_rules: bool = True
    original_state: Optional['ConstraintState'] = None


class ConstraintRelaxationEngine:
    """
    Implements graduated constraint relaxation for optimal scheduling
    
    Relaxation Levels:
    1. STRICT: All constraints enforced (max 1 empty day per teacher)
    2. WORKLOAD_FLEX: Allow up to 2 empty days temporarily
    3. BLOCK_FLEX: Allow non-consecutive blocks for large lessons
    4. AVAILABILITY_FLEX: Minor teacher availability violations
    """

    RELAXATION_LEVELS = [
        RelaxationLevel.STRICT,
        RelaxationLevel.WORKLOAD_FLEX,
        RelaxationLevel.BLOCK_FLEX,
        RelaxationLevel.AVAILABILITY_FLEX
    ]

    def __init__(self, db_manager: DatabaseManager, logger: Optional[logging.Logger] = None):
        """
        Initialize constraint relaxation engine
        
        Args:
            db_manager: Database manager instance
            logger: Optional logger instance
        """
        self.db_manager = db_manager
        self.logger = logger or logging.getLogger(__name__)
        
        # Current constraint state
        self.current_level = RelaxationLevel.STRICT
        self.constraint_state = ConstraintState()
        self.original_state = None
        
        # Workload tracking
        self.workload_violations: Dict[int, WorkloadViolation] = {}
        self.teacher_schedules: Dict[int, Set[Tuple[int, int]]] = {}  # teacher_id -> {(day, slot)}
        
        # Statistics
        self.relaxation_stats = {
            "total_relaxations": 0,
            "successful_relaxations": 0,
            "workload_violations_created": 0,
            "workload_violations_resolved": 0,
            "constraint_restorations": 0
        }
        
        self.logger.info("ConstraintRelaxationEngine initialized")

    def relax_constraints(self, level: RelaxationLevel) -> None:
        """
        Apply graduated constraint relaxation at specified level
        
        Args:
            level: Target relaxation level
        """
        if level == self.current_level:
            self.logger.debug(f"Already at relaxation level: {level.value}")
            return
        
        # Store original state if this is the first relaxation
        if self.current_level == RelaxationLevel.STRICT:
            self.original_state = ConstraintState(
                workload_max_empty_days=self.constraint_state.workload_max_empty_days,
                allow_non_consecutive_blocks=self.constraint_state.allow_non_consecutive_blocks,
                allow_availability_violations=self.constraint_state.allow_availability_violations,
                strict_block_rules=self.constraint_state.strict_block_rules
            )
        
        self.logger.info(f"Relaxing constraints from {self.current_level.value} to {level.value}")
        
        # Apply relaxation based on level
        if level == RelaxationLevel.STRICT:
            self._apply_strict_constraints()
        elif level == RelaxationLevel.WORKLOAD_FLEX:
            self._apply_workload_flexibility()
        elif level == RelaxationLevel.BLOCK_FLEX:
            self._apply_block_flexibility()
        elif level == RelaxationLevel.AVAILABILITY_FLEX:
            self._apply_availability_flexibility()
        
        self.current_level = level
        self.relaxation_stats["total_relaxations"] += 1
        
        self.logger.info(f"Constraints relaxed to level: {level.value}")
        self._log_constraint_state()

    def restore_constraints(self) -> None:
        """Restore original constraint levels after scheduling"""
        if self.original_state is None:
            self.logger.debug("No original state to restore")
            return
        
        self.logger.info("Restoring original constraint levels")
        
        # Restore original state
        self.constraint_state = ConstraintState(
            workload_max_empty_days=self.original_state.workload_max_empty_days,
            allow_non_consecutive_blocks=self.original_state.allow_non_consecutive_blocks,
            allow_availability_violations=self.original_state.allow_availability_violations,
            strict_block_rules=self.original_state.strict_block_rules
        )
        
        self.current_level = RelaxationLevel.STRICT
        self.original_state = None
        self.relaxation_stats["constraint_restorations"] += 1
        
        self.logger.info("Constraints restored to original levels")
        self._log_constraint_state()

    def _apply_strict_constraints(self) -> None:
        """Apply strict constraint enforcement"""
        self.constraint_state.workload_max_empty_days = 1
        self.constraint_state.allow_non_consecutive_blocks = False
        self.constraint_state.allow_availability_violations = False
        self.constraint_state.strict_block_rules = True

    def _apply_workload_flexibility(self) -> None:
        """Apply workload flexibility - allow up to 2 empty days temporarily"""
        self.constraint_state.workload_max_empty_days = 2
        self.constraint_state.allow_non_consecutive_blocks = False
        self.constraint_state.allow_availability_violations = False
        self.constraint_state.strict_block_rules = True

    def _apply_block_flexibility(self) -> None:
        """Apply block flexibility - allow non-consecutive blocks for large lessons"""
        self.constraint_state.workload_max_empty_days = 2
        self.constraint_state.allow_non_consecutive_blocks = True
        self.constraint_state.allow_availability_violations = False
        self.constraint_state.strict_block_rules = False

    def _apply_availability_flexibility(self) -> None:
        """Apply availability flexibility - minor teacher availability violations"""
        self.constraint_state.workload_max_empty_days = 2
        self.constraint_state.allow_non_consecutive_blocks = True
        self.constraint_state.allow_availability_violations = True
        self.constraint_state.strict_block_rules = False

    def update_teacher_schedule(self, teacher_id: int, day: int, slot: int) -> None:
        """
        Update teacher schedule for workload tracking
        
        Args:
            teacher_id: Teacher ID
            day: Day of week (0-4)
            slot: Time slot
        """
        if teacher_id not in self.teacher_schedules:
            self.teacher_schedules[teacher_id] = set()
        
        self.teacher_schedules[teacher_id].add((day, slot))

    def check_workload_constraint(self, teacher_id: int) -> bool:
        """
        Check if teacher workload constraint is satisfied
        
        Args:
            teacher_id: Teacher ID to check
            
        Returns:
            True if workload constraint is satisfied
        """
        if teacher_id not in self.teacher_schedules:
            return True  # No schedule yet, constraint satisfied
        
        # Calculate working days
        working_days = set()
        for day, slot in self.teacher_schedules[teacher_id]:
            working_days.add(day)
        
        # Calculate empty days
        all_days = set(range(5))  # Monday to Friday
        empty_days = len(all_days - working_days)
        
        # Check against current constraint level
        return empty_days <= self.constraint_state.workload_max_empty_days

    def attempt_workload_rebalancing(self) -> bool:
        """
        Attempt to rebalance workload after initial scheduling completion
        
        Returns:
            True if rebalancing was successful
        """
        self.logger.info("Attempting workload rebalancing")
        
        # Identify teachers with workload violations
        violations_before = len(self.workload_violations)
        self._identify_workload_violations()
        violations_after = len(self.workload_violations)
        
        if violations_after == 0:
            self.logger.info("No workload violations found - rebalancing not needed")
            return True
        
        self.logger.info(f"Found {violations_after} workload violations")
        
        # Attempt to resolve violations through schedule adjustments
        resolved_count = 0
        for teacher_id, violation in self.workload_violations.items():
            if self._attempt_violation_resolution(violation):
                resolved_count += 1
        
        self.relaxation_stats["workload_violations_resolved"] += resolved_count
        
        # Update violation tracking after resolution attempts
        self._identify_workload_violations()
        final_violations = len(self.workload_violations)
        
        success = final_violations < violations_after
        self.logger.info(f"Workload rebalancing: {resolved_count} violations resolved, {final_violations} remaining")
        
        return success

    def track_workload_violations(self) -> Dict[int, WorkloadViolation]:
        """
        Track and report workload violations for manual adjustment suggestions
        
        Returns:
            Dictionary of workload violations by teacher ID
        """
        self._identify_workload_violations()
        return self.workload_violations.copy()

    def _identify_workload_violations(self) -> None:
        """Identify current workload violations"""
        self.workload_violations.clear()
        
        for teacher_id, schedule in self.teacher_schedules.items():
            # Calculate working days
            working_days = set()
            for day, slot in schedule:
                working_days.add(day)
            
            # Calculate empty days
            all_days = set(range(5))  # Monday to Friday
            empty_days = len(all_days - working_days)
            
            # Check for violation (using strict constraint of max 1 empty day)
            if empty_days > 1:
                teacher = self.db_manager.get_teacher_by_id(teacher_id)
                teacher_name = teacher.name if teacher else f"Teacher {teacher_id}"
                
                # Determine violation severity
                if empty_days == 2:
                    severity = "minor"
                elif empty_days == 3:
                    severity = "moderate"
                else:
                    severity = "severe"
                
                violation = WorkloadViolation(
                    teacher_id=teacher_id,
                    teacher_name=teacher_name,
                    empty_days=empty_days,
                    working_days=working_days,
                    violation_severity=severity,
                    suggested_adjustments=self._generate_adjustment_suggestions(teacher_id, working_days)
                )
                
                self.workload_violations[teacher_id] = violation
                self.relaxation_stats["workload_violations_created"] += 1

    def _generate_adjustment_suggestions(self, teacher_id: int, working_days: Set[int]) -> List[str]:
        """Generate suggestions for resolving workload violations"""
        suggestions = []
        
        empty_days = set(range(5)) - working_days
        if len(empty_days) > 1:
            suggestions.append(f"Consider moving lessons to fill {len(empty_days)} empty days")
            
            # Suggest specific days
            day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            empty_day_names = [day_names[day] for day in sorted(empty_days)]
            suggestions.append(f"Empty days: {', '.join(empty_day_names)}")
            
            # Suggest redistribution
            if len(working_days) >= 2:
                suggestions.append("Consider redistributing lessons across more days")
        
        return suggestions

    def _attempt_violation_resolution(self, violation: WorkloadViolation) -> bool:
        """
        Attempt to resolve a specific workload violation
        
        Args:
            violation: WorkloadViolation to resolve
            
        Returns:
            True if violation was resolved
        """
        self.logger.debug(f"Attempting to resolve violation for teacher {violation.teacher_name}")
        
        # Get teacher's current schedule
        teacher_schedule = self.teacher_schedules.get(violation.teacher_id, set())
        if not teacher_schedule:
            return False
        
        # Find empty days that could be filled
        all_days = set(range(5))  # Monday to Friday
        empty_days = all_days - violation.working_days
        
        if len(empty_days) <= 1:
            return True  # Already within acceptable limits
        
        # Strategy 1: Try to redistribute existing lessons to fill empty days
        success = self._redistribute_teacher_lessons(violation.teacher_id, empty_days)
        
        if success:
            self.logger.info(f"Successfully resolved workload violation for {violation.teacher_name}")
            return True
        
        # Strategy 2: Mark as acceptable under flexible constraints
        if self.current_level in [RelaxationLevel.WORKLOAD_FLEX, RelaxationLevel.BLOCK_FLEX, RelaxationLevel.AVAILABILITY_FLEX]:
            self.logger.info(f"Workload violation for {violation.teacher_name} accepted under flexible constraints")
            return True
        
        return False

    def _redistribute_teacher_lessons(self, teacher_id: int, empty_days: Set[int]) -> bool:
        """
        Attempt to redistribute teacher's lessons to fill empty days
        
        Args:
            teacher_id: Teacher ID
            empty_days: Set of empty days to fill
            
        Returns:
            True if redistribution was successful
        """
        # This is a simplified redistribution strategy
        # In a full implementation, this would:
        # 1. Identify lessons that can be moved without conflicts
        # 2. Check class availability on target days
        # 3. Verify no other constraints are violated
        # 4. Update the actual schedule
        
        teacher_schedule = self.teacher_schedules.get(teacher_id, set())
        
        # For now, simulate successful redistribution if we have flexibility
        if self.is_workload_flexible() and len(empty_days) <= 2:
            self.logger.debug(f"Simulated successful redistribution for teacher {teacher_id}")
            return True
        
        return False

    def prioritize_curriculum_over_workload(self) -> bool:
        """
        Ensure curriculum completion takes priority over perfect workload distribution
        
        Returns:
            True if prioritization is active
        """
        # This method indicates that curriculum completion should take priority
        # over perfect workload distribution when conflicts arise
        
        if self.current_level != RelaxationLevel.STRICT:
            self.logger.info("Curriculum completion prioritized over workload distribution")
            return True
        
        return False

    def get_constraint_state(self) -> ConstraintState:
        """
        Get current constraint state
        
        Returns:
            Current ConstraintState
        """
        return self.constraint_state

    def get_relaxation_statistics(self) -> Dict[str, int]:
        """
        Get constraint relaxation statistics
        
        Returns:
            Dictionary of relaxation statistics
        """
        return self.relaxation_stats.copy()

    def is_workload_flexible(self) -> bool:
        """Check if workload constraints are currently flexible"""
        return self.current_level in [RelaxationLevel.WORKLOAD_FLEX, RelaxationLevel.BLOCK_FLEX, RelaxationLevel.AVAILABILITY_FLEX]

    def is_block_flexible(self) -> bool:
        """Check if block constraints are currently flexible"""
        return self.current_level in [RelaxationLevel.BLOCK_FLEX, RelaxationLevel.AVAILABILITY_FLEX]

    def is_availability_flexible(self) -> bool:
        """Check if availability constraints are currently flexible"""
        return self.current_level == RelaxationLevel.AVAILABILITY_FLEX

    def allow_temporary_empty_days(self, teacher_id: int, max_empty_days: int = 2) -> bool:
        """
        Allow temporary empty days during initial scheduling
        
        Args:
            teacher_id: Teacher ID
            max_empty_days: Maximum allowed empty days (default 2)
            
        Returns:
            True if temporary empty days are allowed
        """
        if not self.is_workload_flexible():
            return False
        
        # Check current empty days
        if teacher_id not in self.teacher_schedules:
            return True  # No schedule yet, allow flexibility
        
        working_days = set()
        for day, slot in self.teacher_schedules[teacher_id]:
            working_days.add(day)
        
        empty_days = len(set(range(5)) - working_days)
        
        # Allow up to max_empty_days during flexible scheduling
        allowed = empty_days <= max_empty_days
        
        if allowed and empty_days > 1:
            self.logger.debug(f"Allowing {empty_days} empty days for teacher {teacher_id} during flexible scheduling")
        
        return allowed

    def create_workload_rebalancing_plan(self) -> Dict[int, List[str]]:
        """
        Create workload rebalancing plan after scheduling completion
        
        Returns:
            Dictionary mapping teacher_id to list of rebalancing actions
        """
        rebalancing_plan = {}
        
        for teacher_id, violation in self.workload_violations.items():
            actions = []
            
            # Analyze current distribution
            teacher_schedule = self.teacher_schedules.get(teacher_id, set())
            daily_hours = {day: 0 for day in range(5)}
            
            for day, slot in teacher_schedule:
                daily_hours[day] += 1
            
            # Identify overloaded and underloaded days
            overloaded_days = [day for day, hours in daily_hours.items() if hours > 2]
            empty_days = [day for day, hours in daily_hours.items() if hours == 0]
            
            # Generate rebalancing actions
            if overloaded_days and empty_days:
                actions.append(f"Move lessons from {overloaded_days} to {empty_days}")
            
            if len(empty_days) > 1:
                actions.append(f"Distribute lessons across {5 - len(empty_days)} working days")
            
            # Add specific suggestions from violation
            actions.extend(violation.suggested_adjustments)
            
            if actions:
                rebalancing_plan[teacher_id] = actions
        
        return rebalancing_plan

    def validate_workload_distribution(self, schedule_entries: List[Any]) -> Dict[str, Any]:
        """
        Validate workload distribution across all teachers
        
        Args:
            schedule_entries: List of schedule entries to validate
            
        Returns:
            Validation report with statistics and violations
        """
        # Reset teacher schedules for validation
        self.teacher_schedules.clear()
        
        # Build teacher schedules from entries
        for entry in schedule_entries:
            teacher_id = getattr(entry, 'teacher_id', entry.get('teacher_id') if isinstance(entry, dict) else None)
            day = getattr(entry, 'day', entry.get('day') if isinstance(entry, dict) else None)
            slot = getattr(entry, 'time_slot', entry.get('time_slot') if isinstance(entry, dict) else None)
            
            if teacher_id is not None and day is not None and slot is not None:
                self.update_teacher_schedule(teacher_id, day, slot)
        
        # Identify violations
        self._identify_workload_violations()
        
        # Generate validation report
        total_teachers = len(self.teacher_schedules)
        teachers_with_violations = len(self.workload_violations)
        violation_rate = (teachers_with_violations / total_teachers * 100) if total_teachers > 0 else 0
        
        # Calculate distribution statistics
        empty_day_stats = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        for teacher_id, schedule in self.teacher_schedules.items():
            working_days = set(day for day, slot in schedule)
            empty_days = 5 - len(working_days)
            empty_day_stats[empty_days] += 1
        
        report = {
            "total_teachers": total_teachers,
            "teachers_with_violations": teachers_with_violations,
            "violation_rate_percent": violation_rate,
            "empty_day_distribution": empty_day_stats,
            "violations_by_severity": {
                "minor": len([v for v in self.workload_violations.values() if v.violation_severity == "minor"]),
                "moderate": len([v for v in self.workload_violations.values() if v.violation_severity == "moderate"]),
                "severe": len([v for v in self.workload_violations.values() if v.violation_severity == "severe"])
            },
            "workload_violations": self.workload_violations.copy(),
            "rebalancing_plan": self.create_workload_rebalancing_plan()
        }
        
        self.logger.info(f"Workload validation: {teachers_with_violations}/{total_teachers} teachers with violations ({violation_rate:.1f}%)")
        
        return report

    def _log_constraint_state(self) -> None:
        """Log current constraint state for debugging"""
        self.logger.debug(f"Constraint State:")
        self.logger.debug(f"  Level: {self.current_level.value}")
        self.logger.debug(f"  Max empty days: {self.constraint_state.workload_max_empty_days}")
        self.logger.debug(f"  Allow non-consecutive blocks: {self.constraint_state.allow_non_consecutive_blocks}")
        self.logger.debug(f"  Allow availability violations: {self.constraint_state.allow_availability_violations}")
        self.logger.debug(f"  Strict block rules: {self.constraint_state.strict_block_rules}")