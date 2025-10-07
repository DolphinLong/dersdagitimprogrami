# -*- coding: utf-8 -*-
"""
Base Scheduler - Common functionality for all schedulers
DRY (Don't Repeat Yourself) principle

This module provides the base class for all scheduling algorithms in the system.
It consolidates common scheduling functionality to eliminate code duplication
and provide a consistent interface for all scheduler implementations.

Key Features:
- State management for schedule entries, teacher slots, and class slots
- Conflict detection and validation
- Lesson placement and removal operations
- Common utility methods (slot finding, availability checking, etc.)
- Template methods for subclass customization
- Abstract interface for schedule generation

All scheduler implementations should inherit from this class and implement
the generate_schedule() method. Subclasses can override template methods
like _create_lesson_blocks() to customize behavior.
"""

from typing import List, Dict, Tuple, Optional, Set
from collections import defaultdict
from abc import ABC, abstractmethod
import logging

from exceptions import (
    ConflictError, TeacherConflictError, ClassConflictError,
    AvailabilityError, ScheduleGenerationError
)


class BaseScheduler(ABC):
    """
    Base class for all scheduling algorithms
    Contains common functionality to avoid code duplication
    
    This class provides:
    - State management (schedule_entries, teacher_slots, class_slots)
    - Conflict detection and validation
    - Lesson placement and removal
    - Common utility methods for scheduling
    - Template methods for subclass customization
    
    Subclasses must implement:
    - generate_schedule(): Main scheduling algorithm
    
    Subclasses can override:
    - _create_lesson_blocks(): Custom block distribution logic
    - _load_scheduler_weights(): Custom weight loading
    """
    
    SCHOOL_TIME_SLOTS = {
        "İlkokul": 7,
        "Ortaokul": 7,
        "Lise": 8,
        "Anadolu Lisesi": 8,
        "Fen Lisesi": 8,
        "Sosyal Bilimler Lisesi": 8
    }
    
    DAYS = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
    
    def __init__(self, db_manager, progress_callback=None):
        """
        Initialize base scheduler
        
        Args:
            db_manager: Database manager instance
            progress_callback: Optional callback for progress updates
        """
        self.db_manager = db_manager
        self.progress_callback = progress_callback
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # State
        self.schedule_entries = []
        self.teacher_slots = defaultdict(set)  # {teacher_id: {(day, slot)}}
        self.class_slots = defaultdict(set)    # {class_id: {(day, slot)}}
    
    @abstractmethod
    def generate_schedule(self) -> List[Dict]:
        """
        Generate schedule - must be implemented by subclasses
        
        Returns:
            List of schedule entries
        """
        pass
    
    def _update_progress(self, message: str, percentage: int = 0):
        """
        Update progress callback
        
        Args:
            message: Progress message
            percentage: Progress percentage (0-100)
        """
        if self.progress_callback:
            self.progress_callback(message, percentage)
        self.logger.info(f"Progress: {percentage}% - {message}")
    
    def _get_school_config(self) -> Dict:
        """
        Get school configuration
        
        Returns:
            Dict with school configuration
        """
        school_type = self.db_manager.get_school_type() or "Lise"
        time_slots_count = self.SCHOOL_TIME_SLOTS.get(school_type, 8)
        
        return {
            'school_type': school_type,
            'time_slots_count': time_slots_count
        }
    
    def _is_slot_occupied_by_class(self, class_id: int, day: int, slot: int) -> bool:
        """
        Check if a slot is occupied by a class
        
        Args:
            class_id: Class ID
            day: Day (0-4)
            slot: Time slot (0-7)
        
        Returns:
            True if occupied, False otherwise
        """
        return (day, slot) in self.class_slots[class_id]
    
    def _is_slot_occupied_by_teacher(self, teacher_id: int, day: int, slot: int) -> bool:
        """
        Check if a slot is occupied by a teacher
        
        Args:
            teacher_id: Teacher ID
            day: Day (0-4)
            slot: Time slot (0-7)
        
        Returns:
            True if occupied, False otherwise
        """
        return (day, slot) in self.teacher_slots[teacher_id]
    
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
        teacher = self.db_manager.get_teacher_by_id(teacher_id)
        if not teacher or not teacher.availability:
            return True  # If no availability set, assume available
        
        day_name = self.DAYS[day]
        available_slots = teacher.availability.get(day_name, [])
        
        return slot in available_slots
    
    def _can_place_lesson(
        self,
        class_id: int,
        teacher_id: int,
        day: int,
        slot: int,
        check_availability: bool = True,
        consecutive_slots: int = 1
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if a lesson can be placed at a specific slot
        Enhanced to support consecutive slot checking
        
        Args:
            class_id: Class ID
            teacher_id: Teacher ID
            day: Day (0-4)
            slot: Time slot (0-7)
            check_availability: Whether to check teacher availability
            consecutive_slots: Number of consecutive slots to check (default 1)
        
        Returns:
            (can_place, reason) tuple
        """
        # Check all consecutive slots
        for i in range(consecutive_slots):
            current_slot = slot + i
            
            # Check class conflict
            if self._is_slot_occupied_by_class(class_id, day, current_slot):
                return False, f"Class already has a lesson at slot {current_slot}"
            
            # Check teacher conflict
            if self._is_slot_occupied_by_teacher(teacher_id, day, current_slot):
                return False, f"Teacher already teaching another class at slot {current_slot}"
            
            # Check teacher availability
            if check_availability and not self._is_teacher_available(teacher_id, day, current_slot):
                return False, f"Teacher not available at slot {current_slot}"
        
        return True, None
    
    def _is_placement_valid_advanced(
        self,
        class_id: int,
        teacher_id: int,
        day: int,
        slots: List[int],
        check_availability: bool = True
    ) -> bool:
        """
        Advanced placement validation supporting multiple slot validation
        
        Args:
            class_id: Class ID
            teacher_id: Teacher ID
            day: Day (0-4)
            slots: List of time slots to check
            check_availability: Whether to check teacher availability
        
        Returns:
            True if all slots are valid for placement, False otherwise
        """
        for slot in slots:
            can_place, _ = self._can_place_lesson(
                class_id, teacher_id, day, slot, check_availability, consecutive_slots=1
            )
            if not can_place:
                return False
        
        return True
    
    def _place_lesson(
        self,
        class_id: int,
        lesson_id: int,
        teacher_id: int,
        day: int,
        slot: int,
        classroom_id: Optional[int] = None
    ):
        """
        Place a lesson in the schedule
        
        Args:
            class_id: Class ID
            lesson_id: Lesson ID
            teacher_id: Teacher ID
            day: Day (0-4)
            slot: Time slot (0-7)
            classroom_id: Optional classroom ID
        """
        entry = {
            'class_id': class_id,
            'lesson_id': lesson_id,
            'teacher_id': teacher_id,
            'day': day,
            'time_slot': slot,
            'classroom_id': classroom_id
        }
        
        self.schedule_entries.append(entry)
        self.class_slots[class_id].add((day, slot))
        self.teacher_slots[teacher_id].add((day, slot))
        
        self.logger.debug(f"Placed lesson {lesson_id} for class {class_id} on day {day} slot {slot}")
    
    def _remove_lesson(self, entry: Dict):
        """
        Remove a lesson from the schedule
        
        Args:
            entry: Schedule entry to remove
        """
        if entry in self.schedule_entries:
            self.schedule_entries.remove(entry)
            
            class_id = entry['class_id']
            teacher_id = entry['teacher_id']
            day = entry['day']
            slot = entry['time_slot']
            
            self.class_slots[class_id].discard((day, slot))
            self.teacher_slots[teacher_id].discard((day, slot))
            
            self.logger.debug(f"Removed lesson {entry['lesson_id']} from day {day} slot {slot}")
    
    def _find_available_slots(
        self,
        class_id: int,
        teacher_id: int,
        day: Optional[int] = None,
        check_availability: bool = True
    ) -> List[Tuple[int, int]]:
        """
        Find available slots for a class-teacher combination
        
        Args:
            class_id: Class ID
            teacher_id: Teacher ID
            day: Optional specific day (0-4)
            check_availability: Whether to check teacher availability
        
        Returns:
            List of (day, slot) tuples
        """
        config = self._get_school_config()
        time_slots_count = config['time_slots_count']
        
        available_slots = []
        days_to_check = [day] if day is not None else range(5)
        
        for d in days_to_check:
            for s in range(time_slots_count):
                can_place, _ = self._can_place_lesson(
                    class_id, teacher_id, d, s, check_availability
                )
                if can_place:
                    available_slots.append((d, s))
        
        return available_slots
    
    def _get_lesson_blocks(self, weekly_hours: int, strategy: str = 'default') -> List[int]:
        """
        Determine optimal lesson blocks for weekly hours
        Enhanced to support advanced block strategies
        
        Args:
            weekly_hours: Weekly hours for the lesson
            strategy: Block distribution strategy ('default', 'advanced', 'custom')
        
        Returns:
            List of block sizes (e.g., [2, 2, 1] for 5 hours)
        """
        if strategy == 'advanced':
            # Use advanced block creation (can be overridden by subclasses)
            return self._create_lesson_blocks(weekly_hours)
        
        # Default strategy
        if weekly_hours >= 6:
            return [2, 2, 2]
        elif weekly_hours == 5:
            return [2, 2, 1]
        elif weekly_hours == 4:
            return [2, 2]
        elif weekly_hours == 3:
            return [2, 1]
        elif weekly_hours == 2:
            return [2]
        elif weekly_hours == 1:
            return [1]
        else:
            return []
    
    def _create_lesson_blocks(self, total_hours: int) -> List[int]:
        """
        Template method for scheduler-specific block creation
        Subclasses can override this to provide custom block distribution logic
        
        Default implementation creates smart blocks with optimal distribution:
        - Prioritizes 2-hour blocks
        - Adds single hour for odd numbers
        
        Examples:
        - 1 hour: [1]
        - 2 hours: [2]
        - 3 hours: [2, 1]
        - 4 hours: [2, 2]
        - 5 hours: [2, 2, 1]
        - 6 hours: [2, 2, 2]
        - 7 hours: [2, 2, 2, 1]
        - 8 hours: [2, 2, 2, 2]
        
        Args:
            total_hours: Total weekly hours for the lesson
        
        Returns:
            List of block sizes
        """
        if total_hours <= 0:
            return []
        
        blocks = []
        remaining = total_hours
        
        # Fill with 2-hour blocks first
        while remaining >= 2:
            blocks.append(2)
            remaining -= 2
        
        # Add remaining single hour if any
        if remaining == 1:
            blocks.append(1)
        
        return blocks
    
    def _detect_conflicts(self) -> List[Dict]:
        """
        Detect conflicts in the schedule
        Enhanced to return List[Dict] format matching AdvancedScheduler
        
        Returns:
            List of conflict dicts with 'type', 'entry1', 'entry2' keys
        """
        conflicts = []
        
        # Check teacher conflicts
        teacher_slots = {}
        for entry in self.schedule_entries:
            key = (entry['teacher_id'], entry['day'], entry['time_slot'])
            if key in teacher_slots:
                conflicts.append({
                    'type': 'teacher_conflict',
                    'entry1': teacher_slots[key],
                    'entry2': entry,
                    'day': entry['day'],
                    'slot': entry['time_slot']
                })
            else:
                teacher_slots[key] = entry
        
        # Check class conflicts
        class_slots = {}
        for entry in self.schedule_entries:
            key = (entry['class_id'], entry['day'], entry['time_slot'])
            if key in class_slots:
                conflicts.append({
                    'type': 'class_conflict',
                    'entry1': class_slots[key],
                    'entry2': entry,
                    'day': entry['day'],
                    'slot': entry['time_slot']
                })
            else:
                class_slots[key] = entry
        
        return conflicts
    
    def _validate_schedule(self) -> bool:
        """
        Validate the generated schedule
        
        Returns:
            True if valid, False otherwise
        
        Raises:
            ConflictError: If conflicts are detected
        """
        conflicts = self._detect_conflicts()
        
        if len(conflicts) > 0:
            # Count conflicts by type
            class_conflicts = [c for c in conflicts if c['type'] == 'class_conflict']
            teacher_conflicts = [c for c in conflicts if c['type'] == 'teacher_conflict']
            
            self.logger.error(f"Schedule validation failed: {len(conflicts)} conflicts found")
            
            if class_conflicts:
                self.logger.error(f"Class conflicts: {len(class_conflicts)}")
            
            if teacher_conflicts:
                self.logger.error(f"Teacher conflicts: {len(teacher_conflicts)}")
            
            raise ConflictError(
                f"Schedule has {len(conflicts)} conflicts",
                conflicts=conflicts
            )
        
        self.logger.info("Schedule validation passed - no conflicts found")
        return True
    
    def _save_schedule(self) -> bool:
        """
        Save schedule to database
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Saving schedule: {len(self.schedule_entries)} entries")
            
            # Clear existing schedule
            self.db_manager.clear_schedule()
            
            # Save new schedule
            for entry in self.schedule_entries:
                self.db_manager.add_schedule_program(
                    class_id=entry['class_id'],
                    lesson_id=entry['lesson_id'],
                    teacher_id=entry['teacher_id'],
                    day=entry['day'],
                    time_slot=entry['time_slot'],
                    classroom_id=entry.get('classroom_id')
                )
            
            self.logger.info("Schedule saved successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save schedule: {e}", exc_info=True)
            return False
    
    def _calculate_coverage(self) -> Dict:
        """
        Calculate schedule coverage statistics
        
        Returns:
            Dict with coverage information
        """
        config = self._get_school_config()
        classes = self.db_manager.get_all_classes()
        
        total_slots = len(classes) * 5 * config['time_slots_count']
        total_scheduled = len(self.schedule_entries)
        
        coverage_percentage = (total_scheduled / total_slots * 100) if total_slots > 0 else 0
        
        return {
            'total_slots': total_slots,
            'total_scheduled': total_scheduled,
            'empty_slots': total_slots - total_scheduled,
            'coverage_percentage': coverage_percentage
        }
    
    def _get_class_lessons(self, class_obj, lessons: List, assignment_map: Dict, teachers: List) -> List[Dict]:
        """
        Get all lessons assigned to a class with their details
        
        Args:
            class_obj: Class object
            lessons: List of all lessons
            assignment_map: Dict mapping (class_id, lesson_id) to teacher_id
            teachers: List of all teachers
        
        Returns:
            List of dicts with lesson information including:
            - lesson_id, lesson_name, teacher_id, teacher_name, weekly_hours
        """
        class_lessons = []
        
        for lesson in lessons:
            assignment_key = (class_obj.class_id, lesson.lesson_id)
            if assignment_key in assignment_map:
                # Get weekly hours from curriculum
                weekly_hours = self.db_manager.get_weekly_hours_for_lesson(
                    lesson.lesson_id, class_obj.grade
                )
                
                if weekly_hours and weekly_hours > 0:
                    teacher_id = assignment_map[assignment_key]
                    teacher = self.db_manager.get_teacher_by_id(teacher_id)
                    
                    if teacher:
                        class_lessons.append({
                            'lesson_id': lesson.lesson_id,
                            'lesson_name': lesson.name,
                            'teacher_id': teacher.teacher_id,
                            'teacher_name': teacher.name,
                            'weekly_hours': weekly_hours,
                        })
        
        return class_lessons
    
    def _find_available_classroom(self, classrooms: List, day: int, time_slot: int) -> Optional[object]:
        """
        Find an available classroom for a specific day and time slot
        
        Args:
            classrooms: List of classroom objects
            day: Day (0-4)
            time_slot: Time slot (0-7)
        
        Returns:
            Available classroom object or None if no classroom available
        """
        for classroom in classrooms:
            # Check if classroom is already scheduled at this time
            classroom_scheduled = False
            for entry in self.schedule_entries:
                if (entry.get('classroom_id') == classroom.classroom_id and
                    entry['day'] == day and entry['time_slot'] == time_slot):
                    classroom_scheduled = True
                    break
            
            if not classroom_scheduled:
                return classroom
        
        return None
    
    def _load_scheduler_weights(self) -> Dict[str, float]:
        """
        Template method for loading scheduler-specific weights
        Subclasses can override this to provide custom weight loading logic
        
        Returns:
            Dict of weight names to values
        """
        # Default implementation returns empty dict
        # Subclasses should override to provide actual weights
        return {}
