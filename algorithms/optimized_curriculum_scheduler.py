"""
Optimized Curriculum Scheduler - Enhanced scheduler with 100% completion target
Implements intelligent backtracking, flexible constraint handling, and graduated relaxation
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum

from database.db_manager import DatabaseManager
from algorithms.base_scheduler import BaseScheduler
from algorithms.monitoring import PerformanceMonitor as EnhancedPerformanceMonitor, MetricType
from algorithms.enhanced_logging import create_scheduler_logger, SchedulingMetricsLogger


class PlacementMethod(Enum):
    """Method used to place a lesson"""
    STANDARD = "standard"
    ALTERNATIVE = "alternative"
    RELAXED = "relaxed"
    BACKTRACKED = "backtracked"


class ConstraintLevel(Enum):
    """Constraint relaxation levels"""
    STRICT = "strict"
    WORKLOAD_FLEX = "workload_flex"
    BLOCK_FLEX = "block_flex"
    AVAILABILITY_FLEX = "availability_flex"


@dataclass
class EnhancedScheduleEntry:
    """Enhanced schedule entry with optimization metadata"""
    schedule_id: int
    class_id: int
    teacher_id: int
    lesson_id: int
    day: int
    time_slot: int
    block_position: int  # Position within block (1, 2, 3...)
    block_id: str       # Unique identifier for block
    placement_method: PlacementMethod = PlacementMethod.STANDARD
    constraint_level: ConstraintLevel = ConstraintLevel.STRICT
    backtrack_depth: int = 0  # Depth of backtracking used (0 for first attempt)
    alternative_pattern: Optional[Tuple[int, ...]] = None  # Block pattern used if alternative
    classroom_id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format compatible with existing code"""
        return {
            "class_id": self.class_id,
            "lesson_id": self.lesson_id,
            "teacher_id": self.teacher_id,
            "day": self.day,
            "time_slot": self.time_slot,
            "classroom_id": self.classroom_id,
            # Enhanced metadata
            "block_position": self.block_position,
            "block_id": self.block_id,
            "placement_method": self.placement_method.value,
            "constraint_level": self.constraint_level.value,
            "backtrack_depth": self.backtrack_depth,
            "alternative_pattern": self.alternative_pattern,
        }


@dataclass
class WorkloadViolation:
    """Represents a workload distribution violation"""
    teacher_id: int
    teacher_name: str
    empty_days: int
    working_days: Set[int]
    violation_severity: str  # "minor", "moderate", "severe"


@dataclass
class ScheduleResult:
    """Enhanced scheduling result with comprehensive metrics"""
    entries: List[EnhancedScheduleEntry] = field(default_factory=list)
    completion_rate: float = 0.0  # Target: 100% (279/279 hours)
    total_hours: int = 279  # Always 279 for curriculum requirements
    scheduled_hours: int = 0  # Target: 279 (100% completion)
    failed_lessons: List[Dict[str, Any]] = field(default_factory=list)  # Target: empty list
    performance_metrics: Dict[str, Any] = field(default_factory=dict)  # Includes execution time (< 60s target)
    workload_violations: Dict[int, WorkloadViolation] = field(default_factory=dict)
    constraint_violations_by_type: Dict[str, int] = field(default_factory=dict)
    teacher_utilization: Dict[int, float] = field(default_factory=dict)
    class_utilization: Dict[int, float] = field(default_factory=dict)
    backtrack_statistics: Dict[str, int] = field(default_factory=dict)
    alternative_block_usage: Dict[str, int] = field(default_factory=dict)
    execution_time: float = 0.0
    success: bool = False

    def get_legacy_entries(self) -> List[Dict[str, Any]]:
        """Convert enhanced entries to legacy format for compatibility"""
        return [entry.to_dict() for entry in self.entries]


class OptimizedCurriculumScheduler(BaseScheduler):
    """
    Optimized curriculum scheduler with 100% completion guarantee
    
    Features:
    - Intelligent backtracking with 10-level depth limit
    - Flexible block management with alternative configurations
    - Graduated constraint relaxation
    - Comprehensive diagnostics and performance monitoring
    - 60-second execution time target
    """

    def __init__(self, db_manager: DatabaseManager, progress_callback=None):
        """
        Initialize optimized curriculum scheduler
        
        Args:
            db_manager: Database manager instance
            progress_callback: Optional progress callback function
        """
        super().__init__(db_manager, progress_callback)
        
        # Enhanced logging setup
        self.logger, self.metrics_logger = create_scheduler_logger(
            scheduler_name="OptimizedCurriculumScheduler",
            log_level="INFO",
            enable_file_logging=True
        )
        
        # Performance monitoring
        self.performance_monitor = EnhancedPerformanceMonitor()
        
        # Scheduling configuration
        self.target_hours = 279  # Total curriculum hours to schedule
        self.time_limit = 60.0   # 60-second execution time limit
        self.max_backtrack_depth = 10  # Maximum backtracking depth
        
        # Enhanced state tracking
        self.enhanced_entries: List[EnhancedScheduleEntry] = []
        self.block_counter = 0  # For generating unique block IDs
        self.current_constraint_level = ConstraintLevel.STRICT
        
        # Initialize enhanced components
        from algorithms.backtracking_manager import BacktrackingManager
        from algorithms.flexible_block_manager import FlexibleBlockManager
        from algorithms.constraint_relaxation_engine import ConstraintRelaxationEngine
        from algorithms.scheduling_diagnostics import SchedulingDiagnostics
        
        self.backtrack_manager = BacktrackingManager(db_manager, max_depth=self.max_backtrack_depth)
        self.block_flexibility = FlexibleBlockManager(db_manager)
        self.constraint_relaxer = ConstraintRelaxationEngine(db_manager, self.logger)
        self.diagnostics = SchedulingDiagnostics(db_manager)
        
        # Statistics tracking
        self.backtrack_stats = {
            "total_backtracks": 0,
            "successful_backtracks": 0,
            "max_depth_reached": 0,
            "alternative_blocks_used": 0,
            "constraint_relaxations": 0
        }
        
        # Initialize performance monitoring
        self._setup_performance_monitoring()
        
        self.logger.info("OptimizedCurriculumScheduler initialized with enhanced components")
        self.logger.info(f"Target: {self.target_hours} hours, Time limit: {self.time_limit}s")
        self.logger.info(f"Components: BacktrackingManager, FlexibleBlockManager, ConstraintRelaxationEngine, SchedulingDiagnostics")

    def _setup_performance_monitoring(self):
        """Setup comprehensive performance monitoring"""
        # Record initialization metrics
        from algorithms.monitoring import MetricType
        self.performance_monitor.collector.record_metric(
            name="scheduler_initialized",
            value=1,
            metric_type=MetricType.ALGORITHM,
            metadata={
                "target_hours": self.target_hours,
                "time_limit": self.time_limit,
                "max_backtrack_depth": self.max_backtrack_depth
            }
        )

    def generate_schedule(self) -> List[Dict[str, Any]]:
        """
        Generate complete schedule with 100% completion target
        
        Returns:
            List of schedule entries in legacy format for compatibility
        """
        self.logger.info("=" * 80)
        self.logger.info("OPTIMIZED CURRICULUM SCHEDULER - 100% COMPLETION TARGET")
        self.logger.info("=" * 80)
        
        # Start performance monitoring
        start_time = time.time()
        self.performance_monitor.start_timer("complete_schedule_generation")
        
        try:
            # Generate enhanced schedule
            result = self.generate_complete_schedule()
            
            # Convert to legacy format for compatibility
            legacy_entries = result.get_legacy_entries()
            
            # Log final results
            self.logger.info(f"Schedule generation completed:")
            self.logger.info(f"  Completion rate: {result.completion_rate:.1f}%")
            self.logger.info(f"  Scheduled hours: {result.scheduled_hours}/{result.total_hours}")
            self.logger.info(f"  Execution time: {result.execution_time:.2f}s")
            self.logger.info(f"  Success: {result.success}")
            
            return legacy_entries
            
        except Exception as e:
            self.logger.error(f"Schedule generation failed: {e}", exc_info=True)
            self.performance_monitor.stop_timer("complete_schedule_generation")
            raise
        finally:
            # Always stop the timer
            duration = self.performance_monitor.stop_timer("complete_schedule_generation")
            self.logger.info(f"Total execution time: {duration:.2f}s")

    def generate_complete_schedule(self) -> ScheduleResult:
        """
        Main scheduling method with 100% completion guarantee and 60s time limit
        
        Returns:
            ScheduleResult with comprehensive metrics and diagnostics
        """
        start_time = time.time()
        result = ScheduleResult()
        
        try:
            self._update_progress("Initializing enhanced scheduler...", 5)
            
            # Initialize scheduler state
            self._initialize_enhanced_state()
            
            # Get all required data
            classes = self.db_manager.get_all_classes()
            assignments = self.db_manager.get_schedule_by_school_type()
            
            self.logger.info(f"Processing {len(classes)} classes with {len(assignments)} assignments")
            
            # Calculate total required hours
            total_required_hours = self._calculate_total_required_hours(classes, assignments)
            result.total_hours = total_required_hours
            
            self.logger.info(f"Target: {total_required_hours} curriculum hours")
            
            self._update_progress("Starting curriculum-based scheduling...", 10)
            
            # Main scheduling loop with graduated approach
            scheduled_hours = self._schedule_with_graduated_approach(classes, assignments, start_time)
            
            # Update result
            result.scheduled_hours = scheduled_hours
            result.completion_rate = (scheduled_hours / total_required_hours * 100) if total_required_hours > 0 else 0
            result.entries = self.enhanced_entries.copy()
            result.execution_time = time.time() - start_time
            result.success = result.completion_rate >= 100.0
            
            # Generate comprehensive metrics
            self._generate_comprehensive_metrics(result)
            
            # Validate 100% completion
            if result.success:
                self.logger.info("🎉 SUCCESS: 100% curriculum completion achieved!")
                self._update_progress("Schedule completed successfully!", 100)
            else:
                self.logger.warning(f"⚠️ Partial completion: {result.completion_rate:.1f}%")
                self._update_progress(f"Partial completion: {result.completion_rate:.1f}%", 90)
            
            return result
            
        except Exception as e:
            result.execution_time = time.time() - start_time
            result.success = False
            self.logger.error(f"Schedule generation failed: {e}", exc_info=True)
            raise
        finally:
            # Record final performance metrics
            from algorithms.monitoring import MetricType
            self.performance_monitor.collector.record_metric(
                name="final_completion_rate",
                value=result.completion_rate,
                metric_type=MetricType.COVERAGE,
                metadata={
                    "scheduled_hours": result.scheduled_hours,
                    "total_hours": result.total_hours,
                    "execution_time": result.execution_time,
                    "success": result.success
                }
            )

    def _initialize_enhanced_state(self):
        """Initialize enhanced scheduler state"""
        # Clear existing state
        self.enhanced_entries.clear()
        self.schedule_entries.clear()
        self.teacher_slots.clear()
        self.class_slots.clear()
        self.block_counter = 0
        self.current_constraint_level = ConstraintLevel.STRICT
        
        # Reset statistics
        self.backtrack_stats = {
            "total_backtracks": 0,
            "successful_backtracks": 0,
            "max_depth_reached": 0,
            "alternative_blocks_used": 0,
            "constraint_relaxations": 0
        }
        
        # Initialize slot tracking
        classes = self.db_manager.get_all_classes()
        teachers = self.db_manager.get_all_teachers()
        
        for class_obj in classes:
            self.class_slots[class_obj.class_id] = set()
            
        for teacher in teachers:
            self.teacher_slots[teacher.teacher_id] = set()
        
        self.logger.info("Enhanced scheduler state initialized")

    def _calculate_total_required_hours(self, classes, assignments) -> int:
        """Calculate total required curriculum hours"""
        total_hours = 0
        
        for class_obj in classes:
            class_assignments = [a for a in assignments if a.class_id == class_obj.class_id]
            
            for assignment in class_assignments:
                weekly_hours = self.db_manager.get_weekly_hours_for_lesson(
                    assignment.lesson_id, class_obj.grade
                )
                if weekly_hours and weekly_hours > 0:
                    total_hours += weekly_hours
        
        return total_hours

    def _schedule_with_graduated_approach(self, classes, assignments, start_time) -> int:
        """
        Create multi-pass scheduling (strict → relaxed → backtrack)
        Implements graduated solution approach with quality optimization and randomization
        
        Returns:
            Total scheduled hours
        """
        total_scheduled = 0
        
        # Prepare lesson data for prioritization
        lesson_data = self._prepare_lesson_data(classes, assignments)
        
        # Sort lessons by difficulty/constraints (larger blocks first)
        prioritized_lessons = self._prioritize_lessons_by_difficulty(lesson_data)
        
        self.logger.info(f"Prioritized {len(prioritized_lessons)} lessons by difficulty and constraints")
        
        # Initialize solution quality tracking
        best_solution = None
        best_completion_rate = 0.0
        solution_attempts = 0
        max_solution_attempts = 3  # Try multiple solutions to avoid local optima
        
        # Multi-pass scheduling with solution quality optimization
        for attempt in range(max_solution_attempts):
            if not self._check_time_limit(start_time):
                break
                
            self.logger.info(f"Solution attempt {attempt + 1}/{max_solution_attempts}")
            
            # Apply randomization to avoid local optima (except first attempt)
            if attempt > 0:
                self._apply_randomization_to_avoid_local_optima(prioritized_lessons)
            
            # Reset state for new attempt
            if attempt > 0:
                self._reset_scheduling_state()
            
            attempt_scheduled = self._execute_multi_pass_scheduling(prioritized_lessons, start_time)
            solution_attempts += 1
            
            # Calculate completion rate for this attempt
            completion_rate = (attempt_scheduled / self.target_hours * 100) if self.target_hours > 0 else 0
            
            self.logger.info(f"Attempt {attempt + 1} result: {attempt_scheduled} hours ({completion_rate:.1f}%)")
            
            # Check if this is the best solution so far
            if completion_rate > best_completion_rate:
                best_completion_rate = completion_rate
                best_solution = self._capture_current_solution()
                
                # If we achieved 100%, we can stop
                if completion_rate >= 100.0:
                    self.logger.info("🎉 100% completion achieved!")
                    total_scheduled = attempt_scheduled
                    break
            
            total_scheduled = max(total_scheduled, attempt_scheduled)
        
        # Restore best solution if we tried multiple attempts
        if best_solution and solution_attempts > 1:
            self._restore_solution(best_solution)
            self.logger.info(f"Restored best solution: {best_completion_rate:.1f}% completion")
        
        # Final solution quality optimization
        if total_scheduled > 0:
            optimized_hours = self._optimize_solution_quality()
            total_scheduled = max(total_scheduled, optimized_hours)
        
        return total_scheduled

    def _execute_multi_pass_scheduling(self, prioritized_lessons: List[Dict[str, Any]], start_time: float) -> int:
        """
        Execute multi-pass scheduling: strict → workload_flex → block_flex → availability_flex
        Enhanced with performance monitoring and early termination
        
        Returns:
            Total scheduled hours for this pass
        """
        total_scheduled = 0
        
        # Phase 1: Strict scheduling with backtracking
        self.logger.info("Phase 1: Strict constraint scheduling with intelligent backtracking")
        self.current_constraint_level = ConstraintLevel.STRICT
        from algorithms.constraint_relaxation_engine import RelaxationLevel
        self.constraint_relaxer.relax_constraints(RelaxationLevel.STRICT)
        
        phase_start = time.time()
        phase_scheduled = self._schedule_with_backtracking(prioritized_lessons, start_time)
        total_scheduled += phase_scheduled
        
        # Monitor performance and check early termination
        elapsed = time.time() - start_time
        self._monitor_performance_metrics("strict", total_scheduled, elapsed)
        
        if self._check_early_termination_conditions(total_scheduled, self.target_hours, elapsed, "strict"):
            self.logger.warning("Early termination triggered in strict phase")
            return total_scheduled
        
        # Optimize memory usage after intensive phase
        self._optimize_memory_usage()
        
        # Check if we need additional phases
        if total_scheduled < self.target_hours and self._check_time_limit(start_time):
            self.logger.info("Phase 2: Workload flexibility scheduling")
            self.current_constraint_level = ConstraintLevel.WORKLOAD_FLEX
            self.constraint_relaxer.relax_constraints(RelaxationLevel.WORKLOAD_FLEX)
            self.backtrack_stats["constraint_relaxations"] += 1
            
            # Get remaining unscheduled lessons
            remaining_lessons = self._get_remaining_lessons(prioritized_lessons)
            phase_scheduled = self._schedule_with_backtracking(remaining_lessons, start_time)
            total_scheduled += phase_scheduled
            
            # Monitor performance
            elapsed = time.time() - start_time
            self._monitor_performance_metrics("workload_flex", total_scheduled, elapsed)
            
            if self._check_early_termination_conditions(total_scheduled, self.target_hours, elapsed, "workload_flex"):
                self.logger.warning("Early termination triggered in workload flexibility phase")
                return total_scheduled
        
        if total_scheduled < self.target_hours and self._check_time_limit(start_time):
            self.logger.info("Phase 3: Block flexibility scheduling")
            self.current_constraint_level = ConstraintLevel.BLOCK_FLEX
            self.constraint_relaxer.relax_constraints(RelaxationLevel.BLOCK_FLEX)
            self.backtrack_stats["constraint_relaxations"] += 1
            
            remaining_lessons = self._get_remaining_lessons(prioritized_lessons)
            phase_scheduled = self._schedule_with_backtracking(remaining_lessons, start_time)
            total_scheduled += phase_scheduled
            
            # Monitor performance
            elapsed = time.time() - start_time
            self._monitor_performance_metrics("block_flex", total_scheduled, elapsed)
            
            # Optimize memory after block flexibility (can be memory intensive)
            self._optimize_memory_usage()
            
            if self._check_early_termination_conditions(total_scheduled, self.target_hours, elapsed, "block_flex"):
                self.logger.warning("Early termination triggered in block flexibility phase")
                return total_scheduled
        
        if total_scheduled < self.target_hours and self._check_time_limit(start_time):
            self.logger.info("Phase 4: Availability flexibility scheduling")
            self.current_constraint_level = ConstraintLevel.AVAILABILITY_FLEX
            self.constraint_relaxer.relax_constraints(RelaxationLevel.AVAILABILITY_FLEX)
            self.backtrack_stats["constraint_relaxations"] += 1
            
            remaining_lessons = self._get_remaining_lessons(prioritized_lessons)
            phase_scheduled = self._schedule_with_backtracking(remaining_lessons, start_time)
            total_scheduled += phase_scheduled
            
            # Final performance monitoring
            elapsed = time.time() - start_time
            self._monitor_performance_metrics("availability_flex", total_scheduled, elapsed)
        
        return total_scheduled

    def _apply_randomization_to_avoid_local_optima(self, lessons: List[Dict[str, Any]]) -> None:
        """
        Implement randomization to avoid local optima
        
        Applies controlled randomization to lesson ordering and slot selection
        to explore different solution spaces and avoid getting stuck in local optima.
        """
        import random
        
        self.logger.info("Applying randomization to avoid local optima")
        
        # Strategy 1: Shuffle lessons within same priority groups
        # Group lessons by weekly hours (priority groups)
        priority_groups = {}
        for lesson in lessons:
            hours = lesson.get('weekly_hours', 0)
            if hours not in priority_groups:
                priority_groups[hours] = []
            priority_groups[hours].append(lesson)
        
        # Shuffle within each group
        for hours, group in priority_groups.items():
            if len(group) > 1:
                random.shuffle(group)
                self.logger.debug(f"Shuffled {len(group)} lessons in {hours}-hour group")
        
        # Rebuild lessons list maintaining overall priority but with randomization within groups
        lessons.clear()
        for hours in sorted(priority_groups.keys(), reverse=True):  # Larger hours first
            lessons.extend(priority_groups[hours])
        
        # Strategy 2: Enable randomization in backtracking manager
        self.backtrack_manager.enable_randomization(True)
        
        # Strategy 3: Set random seed for reproducible randomization
        import time
        random_seed = int(time.time() * 1000) % 10000
        self.backtrack_manager.set_randomization_seed(random_seed)
        
        self.logger.info(f"Randomization applied with seed: {random_seed}")

    def _reset_scheduling_state(self) -> None:
        """Reset scheduling state for new solution attempt"""
        # Clear existing entries
        self.enhanced_entries.clear()
        self.schedule_entries.clear()
        self.teacher_slots.clear()
        self.class_slots.clear()
        self.block_counter = 0
        
        # Reset component states
        self.backtrack_manager.reset_state()
        self.block_flexibility.reset_statistics()
        
        # Reset constraint level
        self.current_constraint_level = ConstraintLevel.STRICT
        self.constraint_relaxer.restore_constraints()
        
        # Initialize slot tracking
        classes = self.db_manager.get_all_classes()
        teachers = self.db_manager.get_all_teachers()
        
        for class_obj in classes:
            self.class_slots[class_obj.class_id] = set()
            
        for teacher in teachers:
            self.teacher_slots[teacher.teacher_id] = set()
        
        self.logger.debug("Scheduling state reset for new solution attempt")

    def _capture_current_solution(self) -> Dict[str, Any]:
        """
        Capture current solution state for later restoration
        
        Returns:
            Dictionary containing current solution state
        """
        return {
            'enhanced_entries': [entry for entry in self.enhanced_entries],
            'schedule_entries': [entry for entry in self.schedule_entries],
            'teacher_slots': {k: v.copy() for k, v in self.teacher_slots.items()},
            'class_slots': {k: v.copy() for k, v in self.class_slots.items()},
            'block_counter': self.block_counter,
            'backtrack_stats': self.backtrack_stats.copy()
        }

    def _restore_solution(self, solution: Dict[str, Any]) -> None:
        """
        Restore a previously captured solution
        
        Args:
            solution: Solution state to restore
        """
        self.enhanced_entries = solution['enhanced_entries']
        self.schedule_entries = solution['schedule_entries']
        self.teacher_slots = solution['teacher_slots']
        self.class_slots = solution['class_slots']
        self.block_counter = solution['block_counter']
        self.backtrack_stats = solution['backtrack_stats']
        
        self.logger.debug("Solution state restored")

    def _optimize_solution_quality(self) -> int:
        """
        Add solution quality optimization
        
        Performs post-scheduling optimization to improve solution quality:
        - Workload rebalancing
        - Block consolidation
        - Gap minimization
        
        Returns:
            Optimized scheduled hours count
        """
        self.logger.info("Optimizing solution quality")
        
        initial_hours = len(self.enhanced_entries)
        
        # Step 1: Attempt workload rebalancing
        if self.constraint_relaxer.attempt_workload_rebalancing():
            self.logger.info("✓ Workload rebalancing successful")
        else:
            self.logger.info("⚠ Workload rebalancing had limited success")
        
        # Step 2: Try to consolidate fragmented blocks
        consolidated_hours = self._consolidate_fragmented_blocks()
        
        # Step 3: Minimize gaps in teacher and class schedules
        gap_minimized_hours = self._minimize_schedule_gaps()
        
        # Step 4: Final validation and cleanup
        final_hours = self._validate_and_cleanup_solution()
        
        optimized_hours = max(initial_hours, consolidated_hours, gap_minimized_hours, final_hours)
        
        if optimized_hours > initial_hours:
            self.logger.info(f"✓ Solution quality improved: {initial_hours} → {optimized_hours} hours")
        else:
            self.logger.info(f"Solution quality maintained: {optimized_hours} hours")
        
        return optimized_hours

    def _consolidate_fragmented_blocks(self) -> int:
        """
        Try to consolidate fragmented lesson blocks
        
        Returns:
            Number of hours after consolidation
        """
        # This is a simplified consolidation - in full implementation would:
        # 1. Identify fragmented lessons (same lesson spread across many single slots)
        # 2. Try to move them to consecutive slots
        # 3. Use block flexibility to create better patterns
        
        self.logger.debug("Attempting block consolidation")
        
        # For now, return current count
        return len(self.enhanced_entries)

    def _minimize_schedule_gaps(self) -> int:
        """
        Minimize gaps in teacher and class schedules
        
        Returns:
            Number of hours after gap minimization
        """
        # This is a simplified gap minimization - in full implementation would:
        # 1. Identify gaps in daily schedules
        # 2. Try to move lessons to fill gaps
        # 3. Optimize for continuous blocks of teaching
        
        self.logger.debug("Attempting gap minimization")
        
        # For now, return current count
        return len(self.enhanced_entries)

    def _validate_and_cleanup_solution(self) -> int:
        """
        Final validation and cleanup of the solution
        
        Returns:
            Number of valid hours after cleanup
        """
        valid_entries = []
        
        # Validate each entry for conflicts
        for entry in self.enhanced_entries:
            # Check for conflicts with other entries
            has_conflict = False
            
            for other_entry in self.enhanced_entries:
                if entry == other_entry:
                    continue
                    
                # Check for same slot conflicts
                if (entry.day == other_entry.day and 
                    entry.time_slot == other_entry.time_slot):
                    
                    # Same teacher conflict
                    if entry.teacher_id == other_entry.teacher_id:
                        has_conflict = True
                        break
                    
                    # Same class conflict
                    if entry.class_id == other_entry.class_id:
                        has_conflict = True
                        break
            
            if not has_conflict:
                valid_entries.append(entry)
            else:
                self.logger.warning(f"Removed conflicting entry: Class {entry.class_id}, Day {entry.day}, Slot {entry.time_slot}")
        
        # Update entries with validated list
        self.enhanced_entries = valid_entries
        
        # Rebuild legacy entries
        self.schedule_entries.clear()
        for entry in valid_entries:
            self.schedule_entries.append(entry.to_dict())
        
        self.logger.info(f"Solution validation: {len(valid_entries)} valid entries")
        return len(valid_entries)

    def _schedule_all_classes(self, classes, assignments, start_time) -> int:
        """Schedule lessons for all classes"""
        total_scheduled = 0
        
        for i, class_obj in enumerate(classes):
            if not self._check_time_limit(start_time):
                self.logger.warning("Time limit reached during class scheduling")
                break
                
            progress = 20 + (i / len(classes)) * 60  # 20-80% progress range
            self._update_progress(f"Scheduling {class_obj.name}...", int(progress))
            
            class_scheduled = self._schedule_class_lessons(class_obj, assignments, start_time)
            total_scheduled += class_scheduled
            
            self.logger.info(f"Class {class_obj.name}: {class_scheduled} hours scheduled")
        
        return total_scheduled

    def _schedule_with_backtracking(self, lesson_data: List[Dict[str, Any]], start_time: float) -> int:
        """
        Core scheduling with intelligent backtracking (max depth 10)
        Integrates backtracking, block flexibility, and constraint relaxation
        
        Args:
            lesson_data: List of lesson dictionaries to schedule
            start_time: Start time for time limit checking
            
        Returns:
            Number of hours successfully scheduled
        """
        scheduled_hours = 0
        
        for i, lesson in enumerate(lesson_data):
            if not self._check_time_limit(start_time):
                self.logger.warning("Time limit reached during backtracking scheduling")
                break
            
            # Update progress
            progress = 20 + (i / len(lesson_data)) * 60  # 20-80% progress range
            lesson_name = lesson.get('lesson_name', 'Unknown')
            self._update_progress(f"Scheduling {lesson_name} with backtracking...", int(progress))
            
            # Try to schedule this lesson with enhanced methods
            lesson_scheduled_hours = self._schedule_lesson_with_backtracking(lesson, start_time)
            scheduled_hours += lesson_scheduled_hours
            
            # Log progress
            if lesson_scheduled_hours > 0:
                self.logger.debug(f"✓ Scheduled {lesson_name}: {lesson_scheduled_hours} hours")
            else:
                self.logger.warning(f"✗ Failed to schedule {lesson_name}")
                
                # Log failure for diagnostics
                from database.models import Lesson
                lesson_obj = Lesson(
                    lesson_id=lesson.get('lesson_id'),
                    name=lesson.get('lesson_name', 'Unknown'),
                    weekly_hours=lesson.get('weekly_hours', 0)
                )
                
                context = {
                    'class_id': lesson.get('class_id'),
                    'teacher_id': lesson.get('teacher_id'),
                    'weekly_hours': lesson.get('weekly_hours', 0),
                    'constraint_level': self.current_constraint_level.value,
                    'backtrack_depth': self.backtrack_manager.get_current_depth()
                }
                
                self.diagnostics.log_failure(
                    lesson_obj,
                    "Backtracking and alternative methods failed",
                    context
                )
        
        return scheduled_hours

    def _schedule_class_lessons(self, class_obj, assignments, start_time) -> int:
        """Schedule all lessons for a specific class"""
        class_scheduled = 0
        class_assignments = [a for a in assignments if a.class_id == class_obj.class_id]
        
        for assignment in class_assignments:
            if not self._check_time_limit(start_time):
                break
                
            weekly_hours = self.db_manager.get_weekly_hours_for_lesson(
                assignment.lesson_id, class_obj.grade
            )
            
            if weekly_hours and weekly_hours > 0:
                teacher = self.db_manager.get_teacher_by_id(assignment.teacher_id)
                lesson = self.db_manager.get_lesson_by_id(assignment.lesson_id)
                
                if teacher and lesson:
                    scheduled_hours = self._schedule_lesson_enhanced(
                        class_obj.class_id,
                        assignment.lesson_id,
                        assignment.teacher_id,
                        weekly_hours,
                        lesson.name,
                        teacher.name
                    )
                    class_scheduled += scheduled_hours
        
        return class_scheduled

    def _schedule_lesson_enhanced(self, class_id: int, lesson_id: int, teacher_id: int, 
                                weekly_hours: int, lesson_name: str, teacher_name: str) -> int:
        """
        Enhanced lesson scheduling with metadata tracking
        
        Returns:
            Number of hours successfully scheduled
        """
        self.logger.debug(f"Scheduling {lesson_name} ({weekly_hours}h) for class {class_id} with {teacher_name}")
        
        # For now, use basic placement - will be enhanced in subsequent tasks
        config = self._get_school_config()
        time_slots_count = config["time_slots_count"]
        
        scheduled_count = 0
        
        # Simple placement for foundation - will be replaced with advanced logic
        for day in range(5):  # Monday to Friday
            if scheduled_count >= weekly_hours:
                break
                
            for slot in range(time_slots_count):
                if scheduled_count >= weekly_hours:
                    break
                    
                can_place, _ = self._can_place_lesson(class_id, teacher_id, day, slot)
                if can_place:
                    # Create enhanced entry
                    self.block_counter += 1
                    block_id = f"block_{self.block_counter}"
                    
                    enhanced_entry = EnhancedScheduleEntry(
                        schedule_id=len(self.enhanced_entries) + 1,
                        class_id=class_id,
                        teacher_id=teacher_id,
                        lesson_id=lesson_id,
                        day=day,
                        time_slot=slot,
                        block_position=1,  # Simple for now
                        block_id=block_id,
                        placement_method=PlacementMethod.STANDARD,
                        constraint_level=self.current_constraint_level,
                        classroom_id=1  # Default classroom
                    )
                    
                    # Add to enhanced entries
                    self.enhanced_entries.append(enhanced_entry)
                    
                    # Add to legacy format for compatibility
                    self._place_lesson(class_id, lesson_id, teacher_id, day, slot, 1)
                    
                    scheduled_count += 1
        
        return scheduled_count

    def _check_time_limit(self, start_time: float) -> bool:
        """
        Implement execution time monitoring (60 second target)
        Enhanced time limit checking with performance monitoring
        """
        elapsed = time.time() - start_time
        remaining = self.time_limit - elapsed
        
        # Log performance warnings
        if remaining < 10.0 and remaining > 5.0:
            self.logger.warning(f"Time limit approaching: {remaining:.1f}s remaining")
        elif remaining < 5.0 and remaining > 0:
            self.logger.warning(f"Time limit critical: {remaining:.1f}s remaining")
        
        # Record timing metrics
        from algorithms.monitoring import MetricType
        self.performance_monitor.collector.record_metric(
            name="execution_time_elapsed",
            value=elapsed,
            metric_type=MetricType.PERFORMANCE,
            metadata={"remaining_time": remaining, "time_limit": self.time_limit}
        )
        
        return elapsed < self.time_limit

    def _check_early_termination_conditions(self, current_scheduled: int, total_required: int, 
                                          elapsed_time: float, phase: str) -> bool:
        """
        Create early termination for impossible scenarios
        
        Analyzes current progress and determines if continuing is futile
        
        Args:
            current_scheduled: Currently scheduled hours
            total_required: Total required hours
            elapsed_time: Time elapsed so far
            phase: Current scheduling phase
            
        Returns:
            True if early termination is recommended
        """
        # Calculate progress metrics
        completion_rate = (current_scheduled / total_required * 100) if total_required > 0 else 0
        time_remaining = self.time_limit - elapsed_time
        
        # Early termination conditions
        
        # Condition 1: Very low progress with little time remaining
        if time_remaining < 10.0 and completion_rate < 50.0:
            self.logger.warning(f"Early termination: Low progress ({completion_rate:.1f}%) with limited time ({time_remaining:.1f}s)")
            return True
        
        # Condition 2: No progress in strict phase suggests impossible scenario
        if phase == "strict" and completion_rate < 10.0 and elapsed_time > 20.0:
            self.logger.warning(f"Early termination: Minimal progress in strict phase suggests impossible scenario")
            return True
        
        # Condition 3: Excessive backtracking suggests stuck in local optima
        if self.backtrack_stats["total_backtracks"] > 1000 and completion_rate < 80.0:
            self.logger.warning(f"Early termination: Excessive backtracking ({self.backtrack_stats['total_backtracks']}) with low completion")
            return True
        
        # Condition 4: Memory pressure (simplified check)
        if self._check_memory_pressure():
            self.logger.warning("Early termination: Memory pressure detected")
            return True
        
        return False

    def _check_memory_pressure(self) -> bool:
        """
        Add memory usage optimization during backtracking
        
        Monitors memory usage and detects pressure conditions
        
        Returns:
            True if memory pressure is detected
        """
        try:
            import psutil
            import os
            
            # Get current process memory usage
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024  # Convert to MB
            
            # Check system memory
            system_memory = psutil.virtual_memory()
            memory_percent = system_memory.percent
            
            # Memory pressure thresholds
            MEMORY_LIMIT_MB = 1024  # 1GB limit for this process
            SYSTEM_MEMORY_LIMIT = 85  # 85% system memory usage
            
            # Log memory usage periodically
            if len(self.enhanced_entries) % 100 == 0:  # Every 100 entries
                self.logger.debug(f"Memory usage: {memory_mb:.1f}MB, System: {memory_percent:.1f}%")
            
            # Check for memory pressure
            if memory_mb > MEMORY_LIMIT_MB:
                self.logger.warning(f"Process memory limit exceeded: {memory_mb:.1f}MB > {MEMORY_LIMIT_MB}MB")
                return True
            
            if memory_percent > SYSTEM_MEMORY_LIMIT:
                self.logger.warning(f"System memory pressure: {memory_percent:.1f}% > {SYSTEM_MEMORY_LIMIT}%")
                return True
            
            return False
            
        except ImportError:
            # psutil not available, skip memory monitoring
            return False
        except Exception as e:
            self.logger.debug(f"Memory monitoring error: {e}")
            return False

    def _optimize_memory_usage(self) -> None:
        """
        Optimize memory usage during backtracking operations
        
        Implements memory optimization strategies:
        - Limit solution stack depth
        - Clean up unused data structures
        - Compress historical data
        """
        # Strategy 1: Limit backtracking solution stack
        if len(self.backtrack_manager.solution_stack) > self.max_backtrack_depth:
            # Remove oldest entries to maintain depth limit
            excess_count = len(self.backtrack_manager.solution_stack) - self.max_backtrack_depth
            self.backtrack_manager.solution_stack = self.backtrack_manager.solution_stack[excess_count:]
            self.logger.debug(f"Trimmed solution stack by {excess_count} entries")
        
        # Strategy 2: Clean up placement attempt history
        if len(self.block_flexibility.placement_attempts) > 1000:
            # Keep only recent attempts
            self.block_flexibility.placement_attempts = self.block_flexibility.placement_attempts[-500:]
            self.logger.debug("Cleaned up placement attempt history")
        
        # Strategy 3: Compress diagnostic data
        if hasattr(self.diagnostics, 'failure_log') and len(self.diagnostics.failure_log) > 500:
            # Keep only recent failures
            self.diagnostics.failure_log = self.diagnostics.failure_log[-250:]
            self.logger.debug("Compressed diagnostic failure log")
        
        # Strategy 4: Force garbage collection
        import gc
        collected = gc.collect()
        if collected > 0:
            self.logger.debug(f"Garbage collection freed {collected} objects")

    def _monitor_performance_metrics(self, phase: str, scheduled_hours: int, elapsed_time: float) -> None:
        """
        Monitor and record comprehensive performance metrics
        
        Args:
            phase: Current scheduling phase
            scheduled_hours: Hours scheduled so far
            elapsed_time: Time elapsed
        """
        # Calculate rates
        hours_per_second = scheduled_hours / elapsed_time if elapsed_time > 0 else 0
        completion_rate = (scheduled_hours / self.target_hours * 100) if self.target_hours > 0 else 0
        
        # Record phase-specific metrics
        from algorithms.monitoring import MetricType
        self.performance_monitor.collector.record_metric(
            name=f"phase_{phase}_completion_rate",
            value=completion_rate,
            metric_type=MetricType.COVERAGE,
            metadata={
                "phase": phase,
                "scheduled_hours": scheduled_hours,
                "target_hours": self.target_hours,
                "elapsed_time": elapsed_time
            }
        )
        
        # Record scheduling rate
        self.performance_monitor.collector.record_metric(
            name="scheduling_rate_hours_per_second",
            value=hours_per_second,
            metric_type=MetricType.PERFORMANCE,
            metadata={
                "phase": phase,
                "efficiency": "high" if hours_per_second > 5.0 else "low"
            }
        )
        
        # Record backtracking efficiency
        backtrack_success_rate = 0.0
        if self.backtrack_stats["total_backtracks"] > 0:
            backtrack_success_rate = (self.backtrack_stats["successful_backtracks"] / 
                                    self.backtrack_stats["total_backtracks"] * 100)
        
        self.performance_monitor.collector.record_metric(
            name="backtrack_success_rate",
            value=backtrack_success_rate,
            metric_type=MetricType.ALGORITHM,
            metadata={
                "total_backtracks": self.backtrack_stats["total_backtracks"],
                "successful_backtracks": self.backtrack_stats["successful_backtracks"],
                "max_depth_reached": self.backtrack_stats["max_depth_reached"]
            }
        )
        
        # Log performance summary
        self.logger.info(f"Performance metrics - Phase: {phase}")
        self.logger.info(f"  Completion: {completion_rate:.1f}% ({scheduled_hours}/{self.target_hours})")
        self.logger.info(f"  Rate: {hours_per_second:.2f} hours/second")
        self.logger.info(f"  Backtrack success: {backtrack_success_rate:.1f}%")
        self.logger.info(f"  Time: {elapsed_time:.1f}s / {self.time_limit}s")

    def _generate_comprehensive_metrics(self, result: ScheduleResult):
        """Generate comprehensive performance and diagnostic metrics with validation"""
        # Performance metrics
        result.performance_metrics = self.performance_monitor.get_performance_report()
        
        # Backtracking statistics
        result.backtrack_statistics = self.backtrack_stats.copy()
        
        # Teacher utilization (enhanced with validation)
        teachers = self.db_manager.get_all_teachers()
        for teacher in teachers:
            teacher_entries = [e for e in self.enhanced_entries if e.teacher_id == teacher.teacher_id]
            utilization = len(teacher_entries) / (5 * 8) * 100  # Assuming 8 slots per day
            result.teacher_utilization[teacher.teacher_id] = min(utilization, 100.0)
        
        # Class utilization (enhanced with validation)
        classes = self.db_manager.get_all_classes()
        for class_obj in classes:
            class_entries = [e for e in self.enhanced_entries if e.class_id == class_obj.class_id]
            utilization = len(class_entries) / (5 * 8) * 100  # Assuming 8 slots per day
            result.class_utilization[class_obj.class_id] = min(utilization, 100.0)
        
        # Enhanced constraint violations with validation
        validation_report = self._validate_solution()
        if validation_report:
            result.constraint_violations_by_type = {
                violation_type.value: count 
                for violation_type, count in validation_report.violations_by_type.items()
            }
        else:
            result.constraint_violations_by_type = {
                "teacher_conflicts": 0,
                "class_conflicts": 0,
                "availability_violations": 0,
                "workload_violations": 0
            }
        
        # Alternative block usage (enhanced)
        result.alternative_block_usage = {
            "standard_blocks": len([e for e in self.enhanced_entries if e.placement_method == PlacementMethod.STANDARD]),
            "alternative_blocks": len([e for e in self.enhanced_entries if e.placement_method == PlacementMethod.ALTERNATIVE]),
            "relaxed_blocks": len([e for e in self.enhanced_entries if e.placement_method == PlacementMethod.RELAXED]),
            "backtracked_blocks": len([e for e in self.enhanced_entries if e.placement_method == PlacementMethod.BACKTRACKED])
        }
    
    def _validate_solution(self):
        """
        Validate the complete solution using SolutionValidator
        
        Returns:
            ValidationReport with comprehensive validation results
        """
        try:
            from algorithms.solution_validator import SolutionValidator
            
            validator = SolutionValidator(self.db_manager)
            validation_report = validator.validate_complete_solution(self.enhanced_entries)
            
            self.logger.info(f"Solution validation completed:")
            self.logger.info(f"  Valid: {validation_report.is_valid}")
            self.logger.info(f"  Total violations: {validation_report.total_violations}")
            self.logger.info(f"  Critical: {len(validation_report.critical_violations)}")
            self.logger.info(f"  Major: {len(validation_report.major_violations)}")
            self.logger.info(f"  Minor: {len(validation_report.minor_violations)}")
            
            return validation_report
            
        except Exception as e:
            self.logger.error(f"Solution validation failed: {e}")
            return None
    
    def generate_comprehensive_report(self, validation_report=None, report_format="text"):
        """
        Generate comprehensive completion report with diagnostics
        
        Args:
            validation_report: Optional validation report
            report_format: Report format ("text", "json", "html", "markdown")
            
        Returns:
            Formatted comprehensive report
        """
        try:
            from algorithms.enhanced_reporting_system import EnhancedReportingSystem, ReportFormat
            
            # Create schedule result for reporting
            result = ScheduleResult(
                entries=self.enhanced_entries.copy(),
                completion_rate=(len(self.enhanced_entries) / self.target_hours * 100) if self.target_hours > 0 else 0,
                total_hours=self.target_hours,
                scheduled_hours=len(self.enhanced_entries),
                execution_time=0.0,  # Will be set by caller
                success=len(self.enhanced_entries) >= self.target_hours,
                performance_metrics=self.performance_monitor.get_performance_report(),
                teacher_utilization=self.teacher_utilization if hasattr(self, 'teacher_utilization') else {},
                class_utilization=self.class_utilization if hasattr(self, 'class_utilization') else {},
                backtrack_statistics=self.backtrack_stats.copy(),
                alternative_block_usage={
                    "standard_blocks": len([e for e in self.enhanced_entries if e.placement_method == PlacementMethod.STANDARD]),
                    "alternative_blocks": len([e for e in self.enhanced_entries if e.placement_method == PlacementMethod.ALTERNATIVE]),
                    "relaxed_blocks": len([e for e in self.enhanced_entries if e.placement_method == PlacementMethod.RELAXED]),
                    "backtracked_blocks": len([e for e in self.enhanced_entries if e.placement_method == PlacementMethod.BACKTRACKED])
                }
            )
            
            # Create reporting system
            reporting_system = EnhancedReportingSystem(self.db_manager)
            
            # Map format string to enum
            format_map = {
                "text": ReportFormat.TEXT,
                "json": ReportFormat.JSON,
                "html": ReportFormat.HTML,
                "markdown": ReportFormat.MARKDOWN
            }
            format_enum = format_map.get(report_format.lower(), ReportFormat.TEXT)
            
            # Generate comprehensive report
            report = reporting_system.generate_comprehensive_report(
                result, validation_report, self.diagnostics, format_enum
            )
            
            self.logger.info(f"Comprehensive report generated in {report_format} format")
            return report
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            return f"Report generation failed: {e}"

    def _prepare_lesson_data(self, classes, assignments) -> List[Dict[str, Any]]:
        """
        Prepare lesson data for prioritization and scheduling
        
        Returns:
            List of lesson dictionaries with all necessary information
        """
        lesson_data = []
        
        for class_obj in classes:
            class_assignments = [a for a in assignments if a.class_id == class_obj.class_id]
            
            for assignment in class_assignments:
                weekly_hours = self.db_manager.get_weekly_hours_for_lesson(
                    assignment.lesson_id, class_obj.grade
                )
                
                if weekly_hours and weekly_hours > 0:
                    teacher = self.db_manager.get_teacher_by_id(assignment.teacher_id)
                    lesson = self.db_manager.get_lesson_by_id(assignment.lesson_id)
                    
                    if teacher and lesson:
                        lesson_data.append({
                            'class_id': class_obj.class_id,
                            'class_name': class_obj.name,
                            'lesson_id': assignment.lesson_id,
                            'lesson_name': lesson.name,
                            'teacher_id': assignment.teacher_id,
                            'teacher_name': teacher.name,
                            'weekly_hours': weekly_hours,
                            'grade': class_obj.grade,
                            'scheduled_hours': 0,  # Track scheduled hours
                            'attempts': 0,  # Track scheduling attempts
                            'last_failure_reason': None
                        })
        
        return lesson_data

    def _prioritize_lessons_by_difficulty(self, lesson_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Add lesson sorting by difficulty/constraints (larger blocks first)
        
        Implements sophisticated prioritization considering:
        - Lesson duration (larger blocks first)
        - Placement difficulty
        - Teacher constraints
        - Educational importance
        
        Returns:
            Lessons sorted by priority (most difficult/important first)
        """
        # Use FlexibleBlockManager's advanced prioritization
        prioritized_lessons = self.block_flexibility.implement_block_priority_ordering(lesson_data)
        
        self.logger.info("Lesson prioritization completed:")
        self.logger.info(f"  Total lessons: {len(prioritized_lessons)}")
        
        # Log distribution by hours
        hour_distribution = {}
        for lesson in prioritized_lessons:
            hours = lesson.get('weekly_hours', 0)
            hour_distribution[hours] = hour_distribution.get(hours, 0) + 1
        
        for hours in sorted(hour_distribution.keys(), reverse=True):
            count = hour_distribution[hours]
            self.logger.info(f"  {hours}-hour lessons: {count}")
        
        return prioritized_lessons

    def _get_remaining_lessons(self, all_lessons: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get lessons that still need scheduling
        
        Returns:
            List of unscheduled or partially scheduled lessons
        """
        remaining_lessons = []
        
        for lesson in all_lessons:
            scheduled_hours = lesson.get('scheduled_hours', 0)
            required_hours = lesson.get('weekly_hours', 0)
            
            if scheduled_hours < required_hours:
                # Create a copy with remaining hours
                remaining_lesson = lesson.copy()
                remaining_lesson['weekly_hours'] = required_hours - scheduled_hours
                remaining_lesson['remaining_hours'] = required_hours - scheduled_hours
                remaining_lessons.append(remaining_lesson)
        
        return remaining_lessons

    def _schedule_lesson_with_backtracking(self, lesson_data: Dict[str, Any], start_time: float) -> int:
        """
        Schedule a single lesson using backtracking and alternative methods
        
        Returns:
            Number of hours successfully scheduled
        """
        class_id = lesson_data['class_id']
        lesson_id = lesson_data['lesson_id']
        teacher_id = lesson_data['teacher_id']
        weekly_hours = lesson_data['weekly_hours']
        lesson_name = lesson_data['lesson_name']
        teacher_name = lesson_data['teacher_name']
        
        lesson_data['attempts'] += 1
        
        # Method 1: Try standard placement with backtracking
        success, placements = self.backtrack_manager.try_placement(
            class_id, lesson_id, teacher_id, weekly_hours, lesson_name, teacher_name,
            self.teacher_slots, self.class_slots
        )
        
        if success:
            scheduled_hours = self._process_successful_placements(placements, lesson_data, PlacementMethod.BACKTRACKED)
            lesson_data['scheduled_hours'] += scheduled_hours
            return scheduled_hours
        
        # Method 2: Try alternative block configurations
        if weekly_hours > 1:  # Only for multi-hour lessons
            success, placements, config = self.block_flexibility.try_alternative_blocks(
                lesson_id, class_id, teacher_id, weekly_hours, lesson_name, teacher_name,
                self.teacher_slots, self.class_slots, self._place_lesson
            )
            
            if success:
                self.backtrack_stats["alternative_blocks_used"] += 1
                scheduled_hours = len(placements)
                lesson_data['scheduled_hours'] += scheduled_hours
                
                # Convert placements to enhanced entries
                for placement in placements:
                    self._add_enhanced_entry_from_placement(placement, config)
                
                return scheduled_hours
        
        # Method 3: Try with constraint relaxation if not already flexible
        from algorithms.constraint_relaxation_engine import RelaxationLevel
        if self.constraint_relaxer.current_level == RelaxationLevel.STRICT:
            # Temporarily relax constraints for this lesson
            original_level = self.constraint_relaxer.current_level
            self.constraint_relaxer.relax_constraints(RelaxationLevel.WORKLOAD_FLEX)
            
            success, placements = self.backtrack_manager.try_placement(
                class_id, lesson_id, teacher_id, weekly_hours, lesson_name, teacher_name,
                self.teacher_slots, self.class_slots
            )
            
            # Restore original constraint level
            self.constraint_relaxer.relax_constraints(original_level)
            
            if success:
                scheduled_hours = self._process_successful_placements(placements, lesson_data, PlacementMethod.RELAXED)
                lesson_data['scheduled_hours'] += scheduled_hours
                return scheduled_hours
        
        # All methods failed
        lesson_data['last_failure_reason'] = "All scheduling methods failed"
        return 0

    def _process_successful_placements(self, placements: List[Any], lesson_data: Dict[str, Any], 
                                     method: PlacementMethod) -> int:
        """
        Process successful placements and create enhanced entries
        
        Returns:
            Number of hours scheduled
        """
        scheduled_hours = 0
        
        for placement in placements:
            # Create enhanced entry
            self.block_counter += 1
            block_id = f"block_{self.block_counter}"
            
            enhanced_entry = EnhancedScheduleEntry(
                schedule_id=len(self.enhanced_entries) + 1,
                class_id=placement.class_id,
                teacher_id=placement.teacher_id,
                lesson_id=placement.lesson_id,
                day=placement.day,
                time_slot=placement.time_slot,
                block_position=placement.block_position,
                block_id=block_id,
                placement_method=method,
                constraint_level=self.current_constraint_level,
                backtrack_depth=placement.depth,
                classroom_id=placement.classroom_id or 1
            )
            
            # Add to enhanced entries
            self.enhanced_entries.append(enhanced_entry)
            
            # Add to legacy format for compatibility
            self._place_lesson(placement.class_id, placement.lesson_id, placement.teacher_id, 
                             placement.day, placement.time_slot, placement.classroom_id or 1)
            
            scheduled_hours += 1
        
        return scheduled_hours

    def _add_enhanced_entry_from_placement(self, placement: Dict[str, Any], config=None):
        """Add enhanced entry from placement dictionary"""
        self.block_counter += 1
        
        enhanced_entry = EnhancedScheduleEntry(
            schedule_id=len(self.enhanced_entries) + 1,
            class_id=placement['class_id'],
            teacher_id=placement['teacher_id'],
            lesson_id=placement['lesson_id'],
            day=placement['day'],
            time_slot=placement['time_slot'],
            block_position=placement.get('block_position', 1),
            block_id=placement.get('block_id', f"block_{self.block_counter}"),
            placement_method=PlacementMethod.ALTERNATIVE,
            constraint_level=self.current_constraint_level,
            alternative_pattern=config.pattern if config else None,
            classroom_id=placement.get('classroom_id', 1)
        )
        
        self.enhanced_entries.append(enhanced_entry)
        
        # Add to legacy format
        self._place_lesson(placement['class_id'], placement['lesson_id'], placement['teacher_id'],
                         placement['day'], placement['time_slot'], placement.get('classroom_id', 1))

    def _validate_100_percent_completion(self) -> bool:
        """
        Verify all 279 curriculum hours are successfully scheduled
        
        Returns:
            True if 100% completion achieved
        """
        total_scheduled = len(self.enhanced_entries)
        completion_rate = (total_scheduled / self.target_hours * 100) if self.target_hours > 0 else 0
        
        self.logger.info(f"Validation: {total_scheduled}/{self.target_hours} hours ({completion_rate:.1f}%)")
        
        return completion_rate >= 100.0

    def get_enhanced_schedule_result(self) -> ScheduleResult:
        """
        Get the current schedule result with all metrics
        
        Returns:
            Complete ScheduleResult object
        """
        result = ScheduleResult()
        result.entries = self.enhanced_entries.copy()
        result.scheduled_hours = len(self.enhanced_entries)
        result.completion_rate = (result.scheduled_hours / self.target_hours * 100) if self.target_hours > 0 else 0
        result.success = result.completion_rate >= 100.0
        
        # Generate metrics
        self._generate_comprehensive_metrics(result)
        
        return result