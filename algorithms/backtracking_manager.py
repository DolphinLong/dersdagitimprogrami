"""
Backtracking Manager - Intelligent backtracking system for schedule optimization

This module implements an intelligent backtracking system that tracks placement decisions,
manages solution states, and provides alternative slot generation for optimal scheduling.

Key Features:
- Solution stack for tracking and restoring placement decisions
- Constraint ordering for optimal backtracking efficiency
- Depth limiting (max 10 levels) to prevent infinite recursion
- Alternative time slot generation with conflict detection
- Slot scoring for optimal selection
- Randomization to avoid local optima
"""

import logging
import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from database.db_manager import DatabaseManager
    from algorithms.optimized_curriculum_scheduler import EnhancedScheduleEntry


class ConstraintType(Enum):
    """Types of constraints for ordering"""
    TEACHER_AVAILABILITY = "teacher_availability"
    CLASS_CONFLICT = "class_conflict"
    TEACHER_CONFLICT = "teacher_conflict"
    WORKLOAD_DISTRIBUTION = "workload_distribution"
    BLOCK_RULES = "block_rules"


@dataclass
class PlacementDecision:
    """Represents a single placement decision that can be backtracked"""
    class_id: int
    lesson_id: int
    teacher_id: int
    day: int
    time_slot: int
    block_position: int
    block_id: str
    classroom_id: Optional[int] = None
    
    # Metadata for backtracking
    decision_id: int = 0
    depth: int = 0
    alternatives_tried: Set[Tuple[int, int]] = field(default_factory=set)  # (day, slot) pairs
    constraint_violations: Dict[str, Any] = field(default_factory=dict)
    
    def get_slot_key(self) -> Tuple[int, int]:
        """Get the (day, slot) key for this placement"""
        return (self.day, self.time_slot)


@dataclass
class SolutionState:
    """Represents the complete state of the scheduling solution at a point in time"""
    placements: List[PlacementDecision] = field(default_factory=list)
    teacher_slots: Dict[int, Set[Tuple[int, int]]] = field(default_factory=dict)
    class_slots: Dict[int, Set[Tuple[int, int]]] = field(default_factory=dict)
    depth: int = 0
    decision_count: int = 0
    
    def copy(self) -> 'SolutionState':
        """Create a deep copy of the solution state"""
        return SolutionState(
            placements=self.placements.copy(),
            teacher_slots={k: v.copy() for k, v in self.teacher_slots.items()},
            class_slots={k: v.copy() for k, v in self.class_slots.items()},
            depth=self.depth,
            decision_count=self.decision_count
        )


@dataclass
class TimeSlotScore:
    """Represents a time slot with its suitability score"""
    day: int
    slot: int
    score: float
    conflicts: List[str] = field(default_factory=list)
    
    def __lt__(self, other):
        return self.score > other.score  # Higher scores are better


class BacktrackingManager:
    """
    Intelligent backtracking manager for schedule optimization
    
    Implements backtracking with constraint ordering, depth limiting,
    and alternative slot generation for optimal scheduling results.
    """
    
    def __init__(self, db_manager: 'DatabaseManager', max_depth: int = 10):
        """
        Initialize backtracking manager
        
        Args:
            db_manager: Database manager instance
            max_depth: Maximum backtracking depth (default 10)
        """
        self.db_manager = db_manager
        self.max_depth = max_depth
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Solution stack for backtracking
        self.solution_stack: List[SolutionState] = []
        self.current_state = SolutionState()
        
        # Constraint ordering for optimal backtracking
        self.constraint_order = [
            ConstraintType.TEACHER_AVAILABILITY,
            ConstraintType.CLASS_CONFLICT,
            ConstraintType.TEACHER_CONFLICT,
            ConstraintType.BLOCK_RULES,
            ConstraintType.WORKLOAD_DISTRIBUTION
        ]
        
        # Statistics tracking
        self.stats = {
            "total_backtracks": 0,
            "successful_backtracks": 0,
            "max_depth_reached": 0,
            "alternative_slots_generated": 0,
            "constraint_violations_detected": 0,
            "randomizations_applied": 0
        }
        
        # Randomization seed for avoiding local optima
        self.randomization_seed = None
        self.randomization_enabled = True
        
        # School configuration
        self.school_config = self._get_school_config()
        
        self.logger.info(f"BacktrackingManager initialized with max_depth={max_depth}")
    
    def _get_school_config(self) -> Dict[str, Any]:
        """Get school configuration for slot limits"""
        school_type = self.db_manager.get_school_type() or "Lise"
        time_slots_count = {
            "İlkokul": 7,
            "Ortaokul": 7,
            "Lise": 8,
            "Anadolu Lisesi": 8,
            "Fen Lisesi": 8,
            "Sosyal Bilimler Lisesi": 8,
        }.get(school_type, 8)
        
        return {
            "school_type": school_type,
            "time_slots_count": time_slots_count,
            "days_per_week": 5
        }
    
    def push_solution_state(self) -> None:
        """Push current solution state onto the stack"""
        if len(self.solution_stack) >= self.max_depth:
            self.logger.warning(f"Maximum backtrack depth ({self.max_depth}) reached")
            return
        
        state_copy = self.current_state.copy()
        self.solution_stack.append(state_copy)
        self.current_state.depth = len(self.solution_stack)
        
        self.logger.debug(f"Pushed solution state at depth {self.current_state.depth}")
    
    def pop_solution_state(self) -> bool:
        """
        Pop and restore previous solution state
        
        Returns:
            True if state was restored, False if stack is empty
        """
        if not self.solution_stack:
            self.logger.debug("Cannot backtrack: solution stack is empty")
            return False
        
        # Restore previous state
        self.current_state = self.solution_stack.pop()
        self.stats["total_backtracks"] += 1
        
        # Update max depth reached
        current_depth = len(self.solution_stack)
        if current_depth > self.stats["max_depth_reached"]:
            self.stats["max_depth_reached"] = current_depth
        
        self.logger.debug(f"Backtracked to depth {current_depth}")
        return True
    
    def try_placement(self, class_id: int, lesson_id: int, teacher_id: int, 
                     weekly_hours: int, lesson_name: str, teacher_name: str,
                     existing_teacher_slots: Dict[int, Set[Tuple[int, int]]],
                     existing_class_slots: Dict[int, Set[Tuple[int, int]]]) -> Tuple[bool, List[PlacementDecision]]:
        """
        Try lesson placement with backtracking support and depth tracking
        
        Args:
            class_id: Class ID
            lesson_id: Lesson ID  
            teacher_id: Teacher ID
            weekly_hours: Number of hours to schedule
            lesson_name: Name of the lesson
            teacher_name: Name of the teacher
            existing_teacher_slots: Current teacher slot occupancy
            existing_class_slots: Current class slot occupancy
            
        Returns:
            (success, placements) tuple
        """
        self.logger.debug(f"Trying placement: {lesson_name} ({weekly_hours}h) for class {class_id} with {teacher_name}")
        
        # Update current state with existing slots
        self.current_state.teacher_slots = {k: v.copy() for k, v in existing_teacher_slots.items()}
        self.current_state.class_slots = {k: v.copy() for k, v in existing_class_slots.items()}
        
        # Push current state for potential backtracking
        self.push_solution_state()
        
        placements = []
        
        try:
            # Try to place all hours for this lesson
            for hour in range(weekly_hours):
                # Get alternative slots for this placement
                alternative_slots = self.get_alternative_slots(
                    class_id, teacher_id, lesson_id, existing_teacher_slots, existing_class_slots
                )
                
                if not alternative_slots:
                    self.logger.debug(f"No alternative slots found for hour {hour + 1}/{weekly_hours}")
                    raise Exception("No available slots")
                
                # Try the best scored slot
                best_slot = alternative_slots[0]
                
                # Create placement decision
                decision = PlacementDecision(
                    class_id=class_id,
                    lesson_id=lesson_id,
                    teacher_id=teacher_id,
                    day=best_slot.day,
                    time_slot=best_slot.slot,
                    block_position=hour + 1,
                    block_id=f"block_{self.current_state.decision_count + 1}",
                    decision_id=self.current_state.decision_count + 1,
                    depth=self.current_state.depth,
                    classroom_id=1  # Default classroom
                )
                
                # Update state
                self.current_state.placements.append(decision)
                self.current_state.teacher_slots.setdefault(teacher_id, set()).add((best_slot.day, best_slot.slot))
                self.current_state.class_slots.setdefault(class_id, set()).add((best_slot.day, best_slot.slot))
                self.current_state.decision_count += 1
                
                placements.append(decision)
                
                # Update existing slots for next iteration
                existing_teacher_slots.setdefault(teacher_id, set()).add((best_slot.day, best_slot.slot))
                existing_class_slots.setdefault(class_id, set()).add((best_slot.day, best_slot.slot))
            
            self.stats["successful_backtracks"] += 1
            self.logger.debug(f"Successfully placed {weekly_hours} hours for {lesson_name}")
            return True, placements
            
        except Exception as e:
            self.logger.debug(f"Placement failed: {e}")
            # Backtrack on failure
            if self.pop_solution_state():
                self.logger.debug("Backtracked due to placement failure")
            return False, []
    
    def backtrack(self) -> bool:
        """
        Undo last placement and try alternatives (respects 10-level depth limit)
        
        Returns:
            True if backtrack was successful, False if no more options
        """
        # Check if we can backtrack (need at least one state on stack)
        if not self.solution_stack:
            self.logger.debug("Cannot backtrack: solution stack is empty")
            return False
            
        # Allow backtracking even at max depth - the limit is for pushing new states
        return self.pop_solution_state()
    
    def get_alternative_slots(self, class_id: int, teacher_id: int, lesson_id: int,
                            existing_teacher_slots: Dict[int, Set[Tuple[int, int]]],
                            existing_class_slots: Dict[int, Set[Tuple[int, int]]]) -> List[TimeSlotScore]:
        """
        Generate alternative time slot options with intelligent conflict detection and scoring
        
        Uses multiple strategies:
        1. Optimal slots (no conflicts, high scores)
        2. Continuity-based slots (adjacent to existing lessons)
        3. Workload-balanced slots (distribute across days)
        4. Fallback slots (any available slot)
        
        Args:
            class_id: Class ID
            teacher_id: Teacher ID
            lesson_id: Lesson ID
            existing_teacher_slots: Current teacher slot occupancy
            existing_class_slots: Current class slot occupancy
            
        Returns:
            List of TimeSlotScore objects sorted by suitability (best first)
        """
        self.stats["alternative_slots_generated"] += 1
        
        # Try different strategies in order of preference
        alternative_slots = []
        
        # Strategy 1: Find optimal slots (high-scoring, no conflicts)
        optimal_slots = self._find_optimal_slots(
            class_id, teacher_id, existing_teacher_slots, existing_class_slots
        )
        alternative_slots.extend(optimal_slots)
        
        # Strategy 2: Find continuity-based slots (adjacent to existing lessons)
        if len(alternative_slots) < 5:  # Need more options
            continuity_slots = self._find_continuity_slots(
                class_id, teacher_id, existing_teacher_slots, existing_class_slots
            )
            # Add only if not already in list
            for slot in continuity_slots:
                if not any(s.day == slot.day and s.slot == slot.slot for s in alternative_slots):
                    alternative_slots.append(slot)
        
        # Strategy 3: Find workload-balanced slots
        if len(alternative_slots) < 10:  # Need more options
            balanced_slots = self._find_workload_balanced_slots(
                class_id, teacher_id, existing_teacher_slots, existing_class_slots
            )
            # Add only if not already in list
            for slot in balanced_slots:
                if not any(s.day == slot.day and s.slot == slot.slot for s in alternative_slots):
                    alternative_slots.append(slot)
        
        # Strategy 4: Fallback - any available slot
        if len(alternative_slots) < 15:  # Need more options
            fallback_slots = self._find_fallback_slots(
                class_id, teacher_id, existing_teacher_slots, existing_class_slots
            )
            # Add only if not already in list
            for slot in fallback_slots:
                if not any(s.day == slot.day and s.slot == slot.slot for s in alternative_slots):
                    alternative_slots.append(slot)
        
        # Sort by score (best first)
        alternative_slots.sort()
        
        # Apply randomization if enabled to avoid local optima
        if self.randomization_enabled and len(alternative_slots) > 1:
            self.apply_randomization(alternative_slots)
        
        self.logger.debug(f"Generated {len(alternative_slots)} alternative slots for class {class_id}, teacher {teacher_id}")
        return alternative_slots
    
    def _find_optimal_slots(self, class_id: int, teacher_id: int,
                          existing_teacher_slots: Dict[int, Set[Tuple[int, int]]],
                          existing_class_slots: Dict[int, Set[Tuple[int, int]]]) -> List[TimeSlotScore]:
        """Find optimal slots with high scores and no conflicts"""
        optimal_slots = []
        days_per_week = self.school_config["days_per_week"]
        time_slots_count = self.school_config["time_slots_count"]
        
        # Focus on morning slots (0-3) first
        for day in range(days_per_week):
            for slot in range(min(4, time_slots_count)):  # Morning slots
                conflicts = self._detect_slot_conflicts(
                    class_id, teacher_id, day, slot, 
                    existing_teacher_slots, existing_class_slots
                )
                
                if not conflicts:
                    score = self._calculate_slot_score(
                        class_id, teacher_id, day, slot,
                        existing_teacher_slots, existing_class_slots
                    )
                    
                    # Only include high-scoring slots
                    if score >= 10.0:
                        optimal_slots.append(TimeSlotScore(
                            day=day, slot=slot, score=score, conflicts=[]
                        ))
        
        return optimal_slots
    
    def _find_continuity_slots(self, class_id: int, teacher_id: int,
                             existing_teacher_slots: Dict[int, Set[Tuple[int, int]]],
                             existing_class_slots: Dict[int, Set[Tuple[int, int]]]) -> List[TimeSlotScore]:
        """Find slots that create continuity with existing lessons"""
        continuity_slots = []
        teacher_slots = existing_teacher_slots.get(teacher_id, set())
        class_slots = existing_class_slots.get(class_id, set())
        
        # Find slots adjacent to existing teacher lessons
        for day, slot in teacher_slots:
            # Check adjacent slots
            for adjacent_slot in [slot - 1, slot + 1]:
                if 0 <= adjacent_slot < self.school_config["time_slots_count"]:
                    conflicts = self._detect_slot_conflicts(
                        class_id, teacher_id, day, adjacent_slot,
                        existing_teacher_slots, existing_class_slots
                    )
                    
                    if not conflicts:
                        score = self._calculate_slot_score(
                            class_id, teacher_id, day, adjacent_slot,
                            existing_teacher_slots, existing_class_slots
                        )
                        
                        continuity_slots.append(TimeSlotScore(
                            day=day, slot=adjacent_slot, score=score + 5.0,  # Bonus for continuity
                            conflicts=[]
                        ))
        
        # Find slots adjacent to existing class lessons
        for day, slot in class_slots:
            for adjacent_slot in [slot - 1, slot + 1]:
                if 0 <= adjacent_slot < self.school_config["time_slots_count"]:
                    conflicts = self._detect_slot_conflicts(
                        class_id, teacher_id, day, adjacent_slot,
                        existing_teacher_slots, existing_class_slots
                    )
                    
                    if not conflicts:
                        score = self._calculate_slot_score(
                            class_id, teacher_id, day, adjacent_slot,
                            existing_teacher_slots, existing_class_slots
                        )
                        
                        continuity_slots.append(TimeSlotScore(
                            day=day, slot=adjacent_slot, score=score + 3.0,  # Bonus for class continuity
                            conflicts=[]
                        ))
        
        return continuity_slots
    
    def _find_workload_balanced_slots(self, class_id: int, teacher_id: int,
                                    existing_teacher_slots: Dict[int, Set[Tuple[int, int]]],
                                    existing_class_slots: Dict[int, Set[Tuple[int, int]]]) -> List[TimeSlotScore]:
        """Find slots that improve workload distribution"""
        balanced_slots = []
        teacher_slots = existing_teacher_slots.get(teacher_id, set())
        
        # Get days where teacher doesn't have lessons yet
        teacher_days = set(d for d, s in teacher_slots)
        available_days = set(range(self.school_config["days_per_week"])) - teacher_days
        
        # Prefer slots on days without lessons
        for day in available_days:
            for slot in range(self.school_config["time_slots_count"]):
                conflicts = self._detect_slot_conflicts(
                    class_id, teacher_id, day, slot,
                    existing_teacher_slots, existing_class_slots
                )
                
                if not conflicts:
                    score = self._calculate_slot_score(
                        class_id, teacher_id, day, slot,
                        existing_teacher_slots, existing_class_slots
                    )
                    
                    balanced_slots.append(TimeSlotScore(
                        day=day, slot=slot, score=score + 4.0,  # Bonus for workload balance
                        conflicts=[]
                    ))
        
        return balanced_slots
    
    def _find_fallback_slots(self, class_id: int, teacher_id: int,
                           existing_teacher_slots: Dict[int, Set[Tuple[int, int]]],
                           existing_class_slots: Dict[int, Set[Tuple[int, int]]]) -> List[TimeSlotScore]:
        """Find any available slots as fallback options"""
        fallback_slots = []
        days_per_week = self.school_config["days_per_week"]
        time_slots_count = self.school_config["time_slots_count"]
        
        # Check all remaining slots
        for day in range(days_per_week):
            for slot in range(time_slots_count):
                conflicts = self._detect_slot_conflicts(
                    class_id, teacher_id, day, slot,
                    existing_teacher_slots, existing_class_slots
                )
                
                if not conflicts:
                    score = self._calculate_slot_score(
                        class_id, teacher_id, day, slot,
                        existing_teacher_slots, existing_class_slots
                    )
                    
                    fallback_slots.append(TimeSlotScore(
                        day=day, slot=slot, score=score, conflicts=[]
                    ))
        
        return fallback_slots
    
    def _detect_slot_conflicts(self, class_id: int, teacher_id: int, day: int, slot: int,
                             existing_teacher_slots: Dict[int, Set[Tuple[int, int]]],
                             existing_class_slots: Dict[int, Set[Tuple[int, int]]]) -> List[str]:
        """
        Detect conflicts for a specific slot
        
        Returns:
            List of conflict descriptions (empty if no conflicts)
        """
        conflicts = []
        
        # Check class conflict
        if (day, slot) in existing_class_slots.get(class_id, set()):
            conflicts.append(f"Class {class_id} already has lesson at day {day}, slot {slot}")
        
        # Check teacher conflict
        if (day, slot) in existing_teacher_slots.get(teacher_id, set()):
            conflicts.append(f"Teacher {teacher_id} already teaching at day {day}, slot {slot}")
        
        # Check teacher availability
        if not self._is_teacher_available(teacher_id, day, slot):
            conflicts.append(f"Teacher {teacher_id} not available at day {day}, slot {slot}")
        
        if conflicts:
            self.stats["constraint_violations_detected"] += 1
        
        return conflicts
    
    def _is_teacher_available(self, teacher_id: int, day: int, slot: int) -> bool:
        """
        Check if teacher is available for a specific slot
        
        Args:
            teacher_id: Teacher ID
            day: Day (0-4)
            slot: Time slot (0-7)
            
        Returns:
            True if available, False otherwise
        """
        try:
            # Query teacher availability from database
            availability = self.db_manager.get_teacher_availability(teacher_id, day, slot)
            return availability is not None
        except Exception as e:
            self.logger.debug(f"Error checking teacher availability: {e}")
            # Default to available if we can't check
            return True
    
    def _calculate_slot_score(self, class_id: int, teacher_id: int, day: int, slot: int,
                            existing_teacher_slots: Dict[int, Set[Tuple[int, int]]],
                            existing_class_slots: Dict[int, Set[Tuple[int, int]]]) -> float:
        """
        Calculate suitability score for a time slot with advanced optimization
        
        Higher scores indicate better slots. Scoring factors:
        - Morning slots preferred (higher score)
        - Avoid creating gaps in teacher schedule
        - Avoid creating gaps in class schedule
        - Prefer slots that maintain workload distribution
        - Block formation potential
        - Teacher workload balance
        
        Returns:
            Slot score (higher is better)
        """
        score = 0.0
        
        # Base time preference scoring
        score += self._calculate_time_preference_score(slot)
        
        # Teacher schedule optimization
        score += self._calculate_teacher_schedule_score(
            teacher_id, day, slot, existing_teacher_slots
        )
        
        # Class schedule optimization  
        score += self._calculate_class_schedule_score(
            class_id, day, slot, existing_class_slots
        )
        
        # Workload distribution scoring
        score += self._calculate_workload_distribution_score(
            teacher_id, day, existing_teacher_slots
        )
        
        # Block formation potential
        score += self._calculate_block_formation_score(
            class_id, teacher_id, day, slot, existing_teacher_slots, existing_class_slots
        )
        
        return score
    
    def _calculate_time_preference_score(self, slot: int) -> float:
        """Calculate score based on time slot preference"""
        # Morning slots (0-3) are preferred
        if slot < 2:
            return 15.0 - (slot * 3)  # Slot 0 = 15, slot 1 = 12
        elif slot < 4:
            return 10.0 - (slot * 2)  # Slot 2 = 6, slot 3 = 4
        elif slot < 6:
            return 3.0  # Mid-day slots
        else:
            return 1.0  # Late afternoon slots
    
    def _calculate_teacher_schedule_score(self, teacher_id: int, day: int, slot: int,
                                        existing_teacher_slots: Dict[int, Set[Tuple[int, int]]]) -> float:
        """Calculate score based on teacher schedule optimization"""
        score = 0.0
        teacher_slots = existing_teacher_slots.get(teacher_id, set())
        
        if not teacher_slots:
            return 2.0  # Bonus for first lesson
        
        # Continuity bonus - adjacent slots on same day
        adjacent_slots = [
            (day, slot - 1) in teacher_slots,
            (day, slot + 1) in teacher_slots
        ]
        
        if any(adjacent_slots):
            score += 8.0  # Strong bonus for continuity
            
        # Check for creating blocks
        if (day, slot - 1) in teacher_slots and (day, slot + 1) in teacher_slots:
            score += 5.0  # Extra bonus for filling gaps
        
        # Avoid isolated slots (gaps)
        same_day_teacher_slots = [s for d, s in teacher_slots if d == day]
        if same_day_teacher_slots:
            min_slot = min(same_day_teacher_slots)
            max_slot = max(same_day_teacher_slots)
            
            # Penalty for creating gaps
            if min_slot < slot < max_slot and slot not in same_day_teacher_slots:
                score -= 3.0
        
        return score
    
    def _calculate_class_schedule_score(self, class_id: int, day: int, slot: int,
                                      existing_class_slots: Dict[int, Set[Tuple[int, int]]]) -> float:
        """Calculate score based on class schedule optimization"""
        score = 0.0
        class_slots = existing_class_slots.get(class_id, set())
        
        if not class_slots:
            return 1.0  # Small bonus for first lesson
        
        # Continuity bonus for class schedule
        adjacent_slots = [
            (day, slot - 1) in class_slots,
            (day, slot + 1) in class_slots
        ]
        
        if any(adjacent_slots):
            score += 5.0  # Bonus for class continuity
        
        # Avoid overloading class on single day
        same_day_class_slots = len([s for d, s in class_slots if d == day])
        if same_day_class_slots >= 6:  # Already 6+ lessons on this day
            score -= 8.0  # Strong penalty
        elif same_day_class_slots >= 4:  # Already 4+ lessons on this day
            score -= 3.0  # Moderate penalty
        
        return score
    
    def _calculate_workload_distribution_score(self, teacher_id: int, day: int,
                                             existing_teacher_slots: Dict[int, Set[Tuple[int, int]]]) -> float:
        """Calculate score based on workload distribution"""
        score = 0.0
        teacher_slots = existing_teacher_slots.get(teacher_id, set())
        
        if not teacher_slots:
            return 0.0
        
        # Get days where teacher already has lessons
        teacher_days = set(d for d, s in teacher_slots)
        
        # Bonus for spreading across days (avoid empty days)
        if day not in teacher_days:
            if len(teacher_days) < 4:  # Encourage spreading if not already on 4+ days
                score += 4.0
        
        # Penalty for overloading single day
        same_day_slots = len([s for d, s in teacher_slots if d == day])
        if same_day_slots >= 5:  # Already 5+ slots on this day
            score -= 10.0  # Strong penalty for overloading
        elif same_day_slots >= 3:  # Already 3+ slots on this day
            score -= 2.0  # Moderate penalty
        
        return score
    
    def _calculate_block_formation_score(self, class_id: int, teacher_id: int, day: int, slot: int,
                                       existing_teacher_slots: Dict[int, Set[Tuple[int, int]]],
                                       existing_class_slots: Dict[int, Set[Tuple[int, int]]]) -> float:
        """Calculate score based on potential for forming lesson blocks"""
        score = 0.0
        
        # Check potential for 2-hour blocks
        can_form_2hour_block = (
            self._is_slot_available_for_block(class_id, teacher_id, day, slot + 1, 
                                            existing_teacher_slots, existing_class_slots) or
            self._is_slot_available_for_block(class_id, teacher_id, day, slot - 1,
                                            existing_teacher_slots, existing_class_slots)
        )
        
        if can_form_2hour_block:
            score += 3.0
        
        # Check potential for 3-hour blocks
        can_form_3hour_block = (
            self._is_slot_available_for_block(class_id, teacher_id, day, slot + 1,
                                            existing_teacher_slots, existing_class_slots) and
            self._is_slot_available_for_block(class_id, teacher_id, day, slot + 2,
                                            existing_teacher_slots, existing_class_slots)
        )
        
        if can_form_3hour_block:
            score += 5.0
        
        return score
    
    def _is_slot_available_for_block(self, class_id: int, teacher_id: int, day: int, slot: int,
                                   existing_teacher_slots: Dict[int, Set[Tuple[int, int]]],
                                   existing_class_slots: Dict[int, Set[Tuple[int, int]]]) -> bool:
        """Check if a slot is available for block formation"""
        # Check bounds
        if slot < 0 or slot >= self.school_config["time_slots_count"]:
            return False
        
        # Check conflicts
        conflicts = self._detect_slot_conflicts(
            class_id, teacher_id, day, slot, existing_teacher_slots, existing_class_slots
        )
        
        return len(conflicts) == 0
    
    def apply_randomization(self, alternative_slots: List[TimeSlotScore]) -> None:
        """
        Apply randomization to avoid getting stuck in local optima
        
        Randomly shuffles the top-scored slots to introduce variation
        """
        if not self.randomization_enabled or len(alternative_slots) <= 1:
            return
        
        # Apply randomization to top 20% of slots or at least top 3
        randomize_count = max(3, len(alternative_slots) // 5)
        randomize_count = min(randomize_count, len(alternative_slots))
        
        # Shuffle the top slots
        top_slots = alternative_slots[:randomize_count]
        random.shuffle(top_slots)
        alternative_slots[:randomize_count] = top_slots
        
        self.stats["randomizations_applied"] += 1
        self.logger.debug(f"Applied randomization to top {randomize_count} slots")
    
    def is_depth_limit_reached(self) -> bool:
        """
        Check if maximum backtrack depth (10) has been reached
        
        Returns:
            True if at maximum depth, False otherwise
        """
        return len(self.solution_stack) >= self.max_depth
    
    def get_current_depth(self) -> int:
        """
        Get current backtracking depth
        
        Returns:
            Current depth level
        """
        return len(self.solution_stack)
    
    def reset_state(self) -> None:
        """Reset backtracking manager to initial state"""
        self.solution_stack.clear()
        self.current_state = SolutionState()
        
        # Reset statistics
        self.stats = {
            "total_backtracks": 0,
            "successful_backtracks": 0,
            "max_depth_reached": 0,
            "alternative_slots_generated": 0,
            "constraint_violations_detected": 0,
            "randomizations_applied": 0
        }
        
        self.logger.info("BacktrackingManager state reset")
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get backtracking statistics
        
        Returns:
            Dictionary with backtracking statistics
        """
        return self.stats.copy()
    
    def set_randomization_seed(self, seed: Optional[int]) -> None:
        """
        Set randomization seed for reproducible results
        
        Args:
            seed: Random seed (None for random seed)
        """
        self.randomization_seed = seed
        if seed is not None:
            random.seed(seed)
        self.logger.info(f"Randomization seed set to: {seed}")
    
    def enable_randomization(self, enabled: bool = True) -> None:
        """
        Enable or disable randomization
        
        Args:
            enabled: Whether to enable randomization
        """
        self.randomization_enabled = enabled
        self.logger.info(f"Randomization {'enabled' if enabled else 'disabled'}")