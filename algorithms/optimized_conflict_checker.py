# -*- coding: utf-8 -*-
"""
Optimized Conflict Checker - Performance Optimization
Uses set-based lookups for O(1) conflict detection
"""

from typing import Dict, Set, Tuple, List, Optional
from collections import defaultdict
import logging


class OptimizedConflictChecker:
    """
    Optimized conflict checker using set-based lookups
    
    Performance: O(1) conflict detection vs O(n) in original
    Expected speedup: 20-30% faster scheduling
    """
    
    def __init__(self):
        """Initialize conflict checker with empty state"""
        self.logger = logging.getLogger(__name__)
        
        # Set-based lookups for O(1) conflict detection
        self.class_slots: Dict[int, Set[Tuple[int, int]]] = defaultdict(set)
        self.teacher_slots: Dict[int, Set[Tuple[int, int]]] = defaultdict(set)
        self.classroom_slots: Dict[int, Set[Tuple[int, int]]] = defaultdict(set)
        
        # Track all entries for validation
        self.entries: List[Dict] = []
    
    def add_entry(self, entry: Dict):
        """
        Add an entry to the conflict checker
        
        Args:
            entry: Schedule entry dict with keys:
                - class_id, teacher_id, lesson_id, classroom_id, day, time_slot
        """
        class_id = entry['class_id']
        teacher_id = entry['teacher_id']
        classroom_id = entry.get('classroom_id')
        day = entry['day']
        slot = entry['time_slot']
        
        # Add to lookup sets
        self.class_slots[class_id].add((day, slot))
        self.teacher_slots[teacher_id].add((day, slot))
        
        if classroom_id:
            self.classroom_slots[classroom_id].add((day, slot))
        
        # Track entry
        self.entries.append(entry)
    
    def remove_entry(self, entry: Dict):
        """
        Remove an entry from the conflict checker
        
        Args:
            entry: Schedule entry to remove
        """
        class_id = entry['class_id']
        teacher_id = entry['teacher_id']
        classroom_id = entry.get('classroom_id')
        day = entry['day']
        slot = entry['time_slot']
        
        # Remove from lookup sets
        self.class_slots[class_id].discard((day, slot))
        self.teacher_slots[teacher_id].discard((day, slot))
        
        if classroom_id:
            self.classroom_slots[classroom_id].discard((day, slot))
        
        # Remove from entries
        if entry in self.entries:
            self.entries.remove(entry)
    
    def has_class_conflict(self, class_id: int, day: int, slot: int) -> bool:
        """
        Check if class has conflict at specific time
        
        O(1) lookup time
        
        Args:
            class_id: Class ID
            day: Day (0-4)
            slot: Time slot (0-7)
        
        Returns:
            True if conflict exists, False otherwise
        """
        return (day, slot) in self.class_slots[class_id]
    
    def has_teacher_conflict(self, teacher_id: int, day: int, slot: int) -> bool:
        """
        Check if teacher has conflict at specific time
        
        O(1) lookup time
        
        Args:
            teacher_id: Teacher ID
            day: Day (0-4)
            slot: Time slot (0-7)
        
        Returns:
            True if conflict exists, False otherwise
        """
        return (day, slot) in self.teacher_slots[teacher_id]
    
    def has_classroom_conflict(self, classroom_id: int, day: int, slot: int) -> bool:
        """
        Check if classroom has conflict at specific time
        
        O(1) lookup time
        
        Args:
            classroom_id: Classroom ID
            day: Day (0-4)
            slot: Time slot (0-7)
        
        Returns:
            True if conflict exists, False otherwise
        """
        return (day, slot) in self.classroom_slots[classroom_id]
    
    def has_any_conflict(self, class_id: int, teacher_id: int, 
                        day: int, slot: int, 
                        classroom_id: Optional[int] = None) -> bool:
        """
        Check if any conflict exists for given parameters
        
        O(1) lookup time
        
        Args:
            class_id: Class ID
            teacher_id: Teacher ID
            day: Day (0-4)
            slot: Time slot (0-7)
            classroom_id: Optional classroom ID
        
        Returns:
            True if any conflict exists, False otherwise
        """
        # Check class conflict
        if self.has_class_conflict(class_id, day, slot):
            return True
        
        # Check teacher conflict
        if self.has_teacher_conflict(teacher_id, day, slot):
            return True
        
        # Check classroom conflict if provided
        if classroom_id and self.has_classroom_conflict(classroom_id, day, slot):
            return True
        
        return False
    
    def detect_all_conflicts(self) -> List[Dict]:
        """
        Detect all conflicts in current state
        
        Returns:
            List of conflict dicts with 'type', 'entry1', 'entry2' keys
        """
        conflicts = []
        
        # Check for duplicate entries in class slots
        class_slot_entries = defaultdict(list)
        for entry in self.entries:
            key = (entry['class_id'], entry['day'], entry['time_slot'])
            class_slot_entries[key].append(entry)
        
        for key, entries in class_slot_entries.items():
            if len(entries) > 1:
                for i in range(len(entries) - 1):
                    conflicts.append({
                        'type': 'class_conflict',
                        'entry1': entries[i],
                        'entry2': entries[i + 1],
                        'day': key[1],
                        'slot': key[2]
                    })
        
        # Check for duplicate entries in teacher slots
        teacher_slot_entries = defaultdict(list)
        for entry in self.entries:
            key = (entry['teacher_id'], entry['day'], entry['time_slot'])
            teacher_slot_entries[key].append(entry)
        
        for key, entries in teacher_slot_entries.items():
            if len(entries) > 1:
                for i in range(len(entries) - 1):
                    conflicts.append({
                        'type': 'teacher_conflict',
                        'entry1': entries[i],
                        'entry2': entries[i + 1],
                        'day': key[1],
                        'slot': key[2]
                    })
        
        return conflicts
    
    def clear(self):
        """Clear all state"""
        self.class_slots.clear()
        self.teacher_slots.clear()
        self.classroom_slots.clear()
        self.entries.clear()
    
    def get_stats(self) -> Dict:
        """
        Get conflict checker statistics
        
        Returns:
            Dict with statistics
        """
        return {
            'total_entries': len(self.entries),
            'classes_with_entries': len(self.class_slots),
            'teachers_with_entries': len(self.teacher_slots),
            'classrooms_with_entries': len(self.classroom_slots),
            'total_class_slots': sum(len(slots) for slots in self.class_slots.values()),
            'total_teacher_slots': sum(len(slots) for slots in self.teacher_slots.values())
        }
