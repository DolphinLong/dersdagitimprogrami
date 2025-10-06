# -*- coding: utf-8 -*-
"""
Base Scheduler - Common functionality for all schedulers
DRY (Don't Repeat Yourself) principle
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
        check_availability: bool = True
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if a lesson can be placed at a specific slot
        
        Args:
            class_id: Class ID
            teacher_id: Teacher ID
            day: Day (0-4)
            slot: Time slot (0-7)
            check_availability: Whether to check teacher availability
        
        Returns:
            (can_place, reason) tuple
        """
        # Check class conflict
        if self._is_slot_occupied_by_class(class_id, day, slot):
            return False, "Class already has a lesson at this time"
        
        # Check teacher conflict
        if self._is_slot_occupied_by_teacher(teacher_id, day, slot):
            return False, "Teacher already teaching another class at this time"
        
        # Check teacher availability
        if check_availability and not self._is_teacher_available(teacher_id, day, slot):
            return False, "Teacher not available at this time"
        
        return True, None
    
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
    
    def _get_lesson_blocks(self, weekly_hours: int) -> List[int]:
        """
        Determine optimal lesson blocks for weekly hours
        
        Args:
            weekly_hours: Weekly hours for the lesson
        
        Returns:
            List of block sizes (e.g., [2, 2, 1] for 5 hours)
        """
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
    
    def _detect_conflicts(self) -> Dict:
        """
        Detect conflicts in the schedule
        
        Returns:
            Dict with conflict information
        """
        class_conflicts = []
        teacher_conflicts = []
        
        # Check class conflicts
        class_slot_map = defaultdict(list)
        for entry in self.schedule_entries:
            key = (entry['class_id'], entry['day'], entry['time_slot'])
            class_slot_map[key].append(entry)
        
        for key, entries in class_slot_map.items():
            if len(entries) > 1:
                class_conflicts.append({
                    'class_id': key[0],
                    'day': key[1],
                    'slot': key[2],
                    'count': len(entries),
                    'entries': entries
                })
        
        # Check teacher conflicts
        teacher_slot_map = defaultdict(list)
        for entry in self.schedule_entries:
            key = (entry['teacher_id'], entry['day'], entry['time_slot'])
            teacher_slot_map[key].append(entry)
        
        for key, entries in teacher_slot_map.items():
            if len(entries) > 1:
                teacher_conflicts.append({
                    'teacher_id': key[0],
                    'day': key[1],
                    'slot': key[2],
                    'count': len(entries),
                    'entries': entries
                })
        
        return {
            'class_conflicts': class_conflicts,
            'teacher_conflicts': teacher_conflicts,
            'total_conflicts': len(class_conflicts) + len(teacher_conflicts)
        }
    
    def _validate_schedule(self) -> bool:
        """
        Validate the generated schedule
        
        Returns:
            True if valid, False otherwise
        
        Raises:
            ConflictError: If conflicts are detected
        """
        conflicts = self._detect_conflicts()
        
        if conflicts['total_conflicts'] > 0:
            self.logger.error(f"Schedule validation failed: {conflicts['total_conflicts']} conflicts found")
            
            if conflicts['class_conflicts']:
                self.logger.error(f"Class conflicts: {len(conflicts['class_conflicts'])}")
            
            if conflicts['teacher_conflicts']:
                self.logger.error(f"Teacher conflicts: {len(conflicts['teacher_conflicts'])}")
            
            raise ConflictError(
                f"Schedule has {conflicts['total_conflicts']} conflicts",
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
