"""
Curriculum-Based Full Schedule Generator
Generates complete schedule based on curriculum requirements instead of just existing assignments
"""
import logging
from typing import List, Dict, Any
from database.db_manager import DatabaseManager


class CurriculumBasedFullScheduleGenerator:
    """
    Generates complete schedule based on curriculum requirements
    Instead of scheduling only 112 existing assignments, 
    this schedules the full 280-hour curriculum requirement
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        self.schedule_entries = []
        self.teacher_slots = {}  # {teacher_id: {(day, time_slot)}}
        self.class_slots = {}    # {class_id: {(day, time_slot)}}
        
        # Initialize slot tracking
        self._initialize_slot_tracking()
        
    def _initialize_slot_tracking(self):
        """Initialize slot tracking dictionaries"""
        classes = self.db_manager.get_all_classes()
        teachers = self.db_manager.get_all_teachers()
        
        for class_obj in classes:
            self.class_slots[class_obj.class_id] = set()
            
        for teacher in teachers:
            self.teacher_slots[teacher.teacher_id] = set()
    
    def generate_full_schedule(self) -> List[Dict[str, Any]]:
        """
        Generate complete schedule based on curriculum requirements
        This addresses the core issue of only scheduling 112 assignments instead of 280 hours
        """
        self.logger.info("=" * 80)
        self.logger.info("CURRICULUM-BASED FULL SCHEDULE GENERATOR")
        self.logger.info("=" * 80)
        
        # Get all required data
        classes = self.db_manager.get_all_classes()
        teachers = self.db_manager.get_all_teachers()
        lessons = self.db_manager.get_all_lessons()
        assignments = self.db_manager.get_schedule_by_school_type()
        
        self.logger.info(f"Classes: {len(classes)}")
        self.logger.info(f"Teachers: {len(teachers)}")
        self.logger.info(f"Lessons: {len(lessons)}")
        self.logger.info(f"Assignments: {len(assignments)}")
        
        # Get school configuration
        school_type = self.db_manager.get_school_type() or "Lise"
        time_slots_count = {
            "İlkokul": 7,
            "Ortaokul": 7,
            "Lise": 8,
            "Anadolu Lisesi": 8,
            "Fen Lisesi": 8,
            "Sosyal Bilimler Lisesi": 8,
        }.get(school_type, 8)
        
        self.logger.info(f"School type: {school_type} ({time_slots_count} hours/day)")
        
        # Clear existing schedule
        self.schedule_entries = []
        self._initialize_slot_tracking()
        
        total_required_hours = 0
        total_scheduled_hours = 0
        
        # For each class, schedule full curriculum
        for class_obj in classes:
            self.logger.info(f"\n📋 Scheduling curriculum for {class_obj.name} (Grade {class_obj.grade})")
            
            # Get all lessons assigned to this class
            class_assignments = [a for a in assignments if a.class_id == class_obj.class_id]
            self.logger.info(f"   Found {len(class_assignments)} lesson assignments")
            
            # Schedule each assignment for this class
            class_scheduled = 0
            for assignment in class_assignments:
                # Get weekly hours from curriculum
                weekly_hours = self.db_manager.get_weekly_hours_for_lesson(assignment.lesson_id, class_obj.grade)
                
                if weekly_hours and weekly_hours > 0:
                    teacher = self.db_manager.get_teacher_by_id(assignment.teacher_id)
                    lesson = self.db_manager.get_lesson_by_id(assignment.lesson_id)
                    
                    if teacher and lesson:
                        self.logger.info(f"   📚 {lesson.name}: {weekly_hours} hours ({teacher.name})")
                        total_required_hours += weekly_hours
                        
                        # Try to schedule all required hours
                        scheduled_for_this_lesson = self._schedule_lesson_for_class(
                            class_obj.class_id,
                            assignment.lesson_id,
                            assignment.teacher_id,
                            weekly_hours,
                            time_slots_count
                        )
                        
                        class_scheduled += scheduled_for_this_lesson
                        total_scheduled_hours += scheduled_for_this_lesson
                        self.logger.info(f"      ✅ {scheduled_for_this_lesson}/{weekly_hours} hours scheduled")
            
            self.logger.info(f"   📊 Class {class_obj.name}: {class_scheduled} hours scheduled")
        
        # Final summary
        self.logger.info(f"\n{'='*80}")
        self.logger.info("FINAL SCHEDULE SUMMARY")
        self.logger.info(f"{'='*80}")
        self.logger.info(f"Total required hours: {total_required_hours}")
        self.logger.info(f"Total scheduled hours: {total_scheduled_hours}")
        if total_required_hours > 0:
            fill_rate = (total_scheduled_hours / total_required_hours) * 100
            self.logger.info(f"Fill rate: {fill_rate:.1f}%")
        self.logger.info(f"Schedule entries: {len(self.schedule_entries)}")
        
        return self.schedule_entries
    
    def _schedule_lesson_for_class(self, class_id: int, lesson_id: int, teacher_id: int, 
                                 weekly_hours: int, time_slots_count: int) -> int:
        """
        Schedule a lesson for a specific class using BLOCK RULES
        
        BLOCK RULES (MANDATORY):
        - 1 hour: [1] - single slot
        - 2 hours: [2] - consecutive slots on same day
        - 3 hours: [2+1] - 2 consecutive + 1 single, different days
        - 4 hours: [2+2] - two 2-hour blocks, different days
        - 5 hours: [2+2+1] - two 2-hour blocks + 1 single, different days
        - 6 hours: [2+2+2] - three 2-hour blocks, different days
        """
        # Decompose weekly hours into blocks
        blocks = self._decompose_into_blocks(weekly_hours)
        self.logger.debug(f"         📦 {weekly_hours} hours → blocks: {blocks}")
        
        # Try to place all blocks using backtracking
        placed_blocks = []
        used_days = set()
        
        if self._place_blocks_with_backtracking(class_id, lesson_id, teacher_id, blocks, 
                                               placed_blocks, used_days, time_slots_count):
            scheduled_count = sum(blocks)
            self.logger.debug(f"         ✅ All blocks placed successfully")
            return scheduled_count
        else:
            # Rollback any partial placements
            self._rollback_placed_blocks(placed_blocks)
            
            # Try placing only 2-hour blocks (partial success)
            two_hour_blocks = [b for b in blocks if b == 2]
            if two_hour_blocks:
                placed_blocks = []
                used_days = set()
                if self._place_blocks_with_backtracking(class_id, lesson_id, teacher_id, two_hour_blocks,
                                                      placed_blocks, used_days, time_slots_count):
                    scheduled_count = sum(two_hour_blocks)
                    self.logger.warning(f"      ⚠️  Partial placement: {scheduled_count}/{weekly_hours} hours (only 2-hour blocks)")
                    return scheduled_count
                else:
                    self._rollback_placed_blocks(placed_blocks)
            
            # Complete failure
            self.logger.error(f"      ❌ Could not place any blocks for {weekly_hours} hours")
            return 0
    
    def _decompose_into_blocks(self, weekly_hours: int) -> List[int]:
        """
        Decompose weekly hours into blocks according to MEB rules
        
        Examples:
        - 1 hour: [1]
        - 2 hours: [2] 
        - 3 hours: [2, 1]
        - 4 hours: [2, 2]
        - 5 hours: [2, 2, 1]
        - 6 hours: [2, 2, 2]
        """
        if weekly_hours <= 0:
            return []
        elif weekly_hours == 1:
            return [1]
        elif weekly_hours == 2:
            return [2]
        elif weekly_hours == 3:
            return [2, 1]
        elif weekly_hours == 4:
            return [2, 2]
        elif weekly_hours == 5:
            return [2, 2, 1]
        elif weekly_hours == 6:
            return [2, 2, 2]
        else:
            # For more than 6 hours, use 2-hour blocks + remainder
            blocks = []
            remaining = weekly_hours
            while remaining >= 2:
                blocks.append(2)
                remaining -= 2
            if remaining == 1:
                blocks.append(1)
            return blocks
    
    def _place_blocks_with_backtracking(self, class_id: int, lesson_id: int, teacher_id: int,
                                       blocks: List[int], placed_blocks: List, used_days: set,
                                       time_slots_count: int) -> bool:
        """
        Place blocks using backtracking algorithm
        Each block must be on a different day and consecutive slots
        """
        if not blocks:
            return True  # All blocks placed successfully
        
        current_block_size = blocks[0]
        remaining_blocks = blocks[1:]
        
        # Try each day
        for day in range(5):
            if day in used_days:
                continue  # This day already used
            
            # Find consecutive slots for this block
            consecutive_slots = self._find_consecutive_slots(class_id, teacher_id, day, 
                                                           current_block_size, time_slots_count)
            
            for start_slot in consecutive_slots:
                slots = list(range(start_slot, start_slot + current_block_size))
                
                # Place this block
                block_entries = []
                for slot in slots:
                    classroom_id = 1  # Default classroom
                    entry = self._add_entry(class_id, teacher_id, lesson_id, classroom_id, day, slot)
                    block_entries.append((day, slot))
                
                placed_blocks.append(block_entries)
                used_days.add(day)
                
                # Recursively place remaining blocks
                if self._place_blocks_with_backtracking(class_id, lesson_id, teacher_id,
                                                       remaining_blocks, placed_blocks, 
                                                       used_days, time_slots_count):
                    return True
                
                # Backtrack: remove this block
                for day_slot, slot in block_entries:
                    self._remove_entry(class_id, teacher_id, lesson_id, day_slot, slot)
                placed_blocks.pop()
                used_days.remove(day)
        
        return False  # Could not place this block
    
    def _find_consecutive_slots(self, class_id: int, teacher_id: int, day: int, 
                               block_size: int, time_slots_count: int) -> List[int]:
        """
        Find all possible starting positions for consecutive slots of given size
        """
        possible_starts = []
        
        for start_slot in range(time_slots_count - block_size + 1):
            # Check if all slots in this block are available
            all_available = True
            for slot in range(start_slot, start_slot + block_size):
                if not self._can_place_lesson_strict(class_id, teacher_id, day, slot):
                    all_available = False
                    break
            
            if all_available:
                possible_starts.append(start_slot)
        
        return possible_starts
    
    def _rollback_placed_blocks(self, placed_blocks: List):
        """
        Remove all entries from placed blocks (rollback)
        """
        for block_entries in placed_blocks:
            for day, slot in block_entries:
                # Find and remove the entry
                for i, entry in enumerate(self.schedule_entries):
                    if entry['day'] == day and entry['time_slot'] == slot:
                        # Remove from schedule
                        removed_entry = self.schedule_entries.pop(i)
                        
                        # Remove from tracking
                        class_id = removed_entry['class_id']
                        teacher_id = removed_entry['teacher_id']
                        self.class_slots[class_id].discard((day, slot))
                        self.teacher_slots[teacher_id].discard((day, slot))
                        break
        
        placed_blocks.clear()
    
    def _can_place_lesson_relaxed(self, class_id: int, teacher_id: int, day: int, time_slot: int) -> bool:
        """
        Check if a lesson can be placed with relaxed constraints
        Only checks hard constraints (no class/teacher conflicts)
        """
        # Check class conflict
        if (day, time_slot) in self.class_slots[class_id]:
            return False
            
        # Check teacher conflict
        if (day, time_slot) in self.teacher_slots[teacher_id]:
            return False
            
        # Check teacher availability (but be more flexible)
        try:
            if not self.db_manager.is_teacher_available(teacher_id, day, time_slot):
                self.logger.debug(f"         ⚠️  Teacher not available, but allowing placement")
                # In relaxed mode, we still allow but log the warning
        except Exception as e:
            self.logger.warning(f"         ⚠️  Teacher availability check failed: {e}")
            # If check fails, assume teacher is available
            
        return True
    
    def _aggressive_placement_for_remaining_hours(self, class_id: int, lesson_id: int, teacher_id: int, 
                                               remaining_hours: int, time_slots_count: int) -> int:
        """
        Aggressively place remaining hours with relaxed constraints
        """
        placed_count = 0
        
        # Try each day and time slot with very relaxed constraints
        for day in range(5):
            if placed_count >= remaining_hours:
                break
                
            for time_slot in range(time_slots_count):
                if placed_count >= remaining_hours:
                    break
                    
                # Very relaxed check - only hard constraints (class/teacher conflicts)
                class_conflict = (day, time_slot) in self.class_slots[class_id]
                teacher_conflict = (day, time_slot) in self.teacher_slots[teacher_id]
                
                if not class_conflict and not teacher_conflict:
                    # Place the lesson
                    classroom_id = 1  # Default classroom
                    self._add_entry(class_id, teacher_id, lesson_id, classroom_id, day, time_slot)
                    placed_count += 1
                    self.logger.debug(f"         ⚡ Aggressively placed: Day {day+1}, Slot {time_slot+1}")
        
        return placed_count
    
    def _add_entry(self, class_id: int, teacher_id: int, lesson_id: int, 
                  classroom_id: int, day: int, time_slot: int):
        """
        Add a schedule entry
        """
        entry = {
            "class_id": class_id,
            "lesson_id": lesson_id,
            "teacher_id": teacher_id,
            "classroom_id": classroom_id,
            "day": day,
            "time_slot": time_slot,
        }
        
        self.schedule_entries.append(entry)
        self.class_slots[class_id].add((day, time_slot))
        self.teacher_slots[teacher_id].add((day, time_slot))
        
        self.logger.debug(f"Added entry: Class {class_id}, Teacher {teacher_id}, Lesson {lesson_id}, "
                         f"Day {day}, Slot {time_slot}")
    
    def _can_place_lesson_strict(self, class_id: int, teacher_id: int, day: int, time_slot: int) -> bool:
        """
        Check if a lesson can be placed with strict constraints
        Checks class conflicts, teacher conflicts, and teacher availability
        """
        # Check class conflict
        if (day, time_slot) in self.class_slots[class_id]:
            return False
            
        # Check teacher conflict
        if (day, time_slot) in self.teacher_slots[teacher_id]:
            return False
            
        # Check teacher availability (strict)
        try:
            if not self.db_manager.is_teacher_available(teacher_id, day, time_slot):
                return False
        except Exception as e:
            self.logger.debug(f"Teacher availability check failed: {e}, assuming available")
            # If check fails, assume teacher is available
            
        return True
    
    def _remove_entry(self, class_id: int, teacher_id: int, lesson_id: int, day: int, time_slot: int):
        """
        Remove a schedule entry (for backtracking)
        """
        # Find and remove the entry
        for i, entry in enumerate(self.schedule_entries):
            if (entry['class_id'] == class_id and 
                entry['teacher_id'] == teacher_id and 
                entry['lesson_id'] == lesson_id and
                entry['day'] == day and 
                entry['time_slot'] == time_slot):
                
                # Remove from schedule
                self.schedule_entries.pop(i)
                
                # Remove from tracking
                self.class_slots[class_id].discard((day, time_slot))
                self.teacher_slots[teacher_id].discard((day, time_slot))
                
                self.logger.debug(f"Removed entry: Class {class_id}, Teacher {teacher_id}, "
                                f"Lesson {lesson_id}, Day {day}, Slot {time_slot}")
                break


def generate_complete_schedule(db_manager: DatabaseManager) -> List[Dict[str, Any]]:
    """
    Convenience function to generate complete schedule
    """
    generator = CurriculumBasedFullScheduleGenerator(db_manager)
    return generator.generate_full_schedule()