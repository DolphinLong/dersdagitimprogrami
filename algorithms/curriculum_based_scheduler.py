"""
Curriculum-Based Full Schedule Generator
Generates complete schedule based on curriculum requirements instead of just existing assignments
"""
import logging
from typing import List, Dict, Any, Tuple
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
        
        # Final step: Apply teacher workload balancing rule
        self._apply_teacher_workload_balancing()
        
        return self.schedule_entries
    
    def _apply_teacher_workload_balancing(self):
        """
        Apply teacher workload balancing rule:
        No teacher should have more than 1 empty day per week (max 1 day off)
        """
        self.logger.info("\n🎯 Applying teacher workload balancing rule...")
        self.logger.info("   📋 Rule: Maximum 1 empty day per teacher per week")
        
        teachers = self.db_manager.get_all_teachers()
        violations = 0
        
        for teacher in teachers:
            teacher_days = self._get_teacher_working_days(teacher.teacher_id)
            empty_days = 5 - len(teacher_days)  # 5 days - working days = empty days
            
            if empty_days > 1:
                violations += 1
                self.logger.warning(f"   ⚠️  {teacher.name}: {empty_days} empty days (violation)")
                
                # Try to redistribute lessons to fill empty days
                self._redistribute_teacher_lessons(teacher.teacher_id, empty_days - 1)
            else:
                self.logger.info(f"   ✅ {teacher.name}: {empty_days} empty days (compliant)")
        
        if violations == 0:
            self.logger.info("   🎉 All teachers comply with workload balancing rule!")
        else:
            self.logger.warning(f"   ⚠️  {violations} teachers need workload redistribution")
    
    def _get_teacher_working_days(self, teacher_id: int) -> set:
        """Get the set of days a teacher is working"""
        working_days = set()
        for entry in self.schedule_entries:
            if entry['teacher_id'] == teacher_id:
                working_days.add(entry['day'])
        return working_days
    
    def _redistribute_teacher_lessons(self, teacher_id: int, days_to_fill: int):
        """
        Enhanced redistribution algorithm to fill empty days
        Uses multiple strategies to ensure better workload distribution
        """
        if days_to_fill <= 0:
            return
        
        teacher = self.db_manager.get_teacher_by_id(teacher_id)
        if not teacher:
            return
        
        self.logger.info(f"   🔄 Redistributing lessons for {teacher.name} to fill {days_to_fill} empty days")
        
        # Get empty days
        working_days = self._get_teacher_working_days(teacher_id)
        empty_days = [day for day in range(5) if day not in working_days]
        
        # Strategy 1: Try to move single lessons to empty days
        moved_lessons = self._move_single_lessons_to_empty_days(teacher_id, empty_days[:days_to_fill])
        
        # Strategy 2: If not enough moved, try to split blocks
        if moved_lessons < days_to_fill:
            remaining_days = days_to_fill - moved_lessons
            empty_days_remaining = empty_days[moved_lessons:moved_lessons + remaining_days]
            moved_lessons += self._split_blocks_to_fill_days(teacher_id, empty_days_remaining)
        
        # Strategy 3: If still not enough, try aggressive redistribution
        if moved_lessons < days_to_fill:
            remaining_days = days_to_fill - moved_lessons
            empty_days_remaining = empty_days[moved_lessons:moved_lessons + remaining_days]
            moved_lessons += self._aggressive_lesson_redistribution(teacher_id, empty_days_remaining)
        
        if moved_lessons > 0:
            self.logger.info(f"   ✅ Successfully redistributed {moved_lessons} lessons for {teacher.name}")
        else:
            self.logger.warning(f"   ⚠️  Could not redistribute lessons for {teacher.name}")
    
    def _move_single_lessons_to_empty_days(self, teacher_id: int, empty_days: List[int]) -> int:
        """Move single lessons (not part of blocks) to empty days"""
        moved_count = 0
        teacher_entries = [e for e in self.schedule_entries if e['teacher_id'] == teacher_id]
        
        for empty_day in empty_days:
            # Find single lessons that can be moved
            for entry in teacher_entries[:]:
                if self._is_single_lesson(entry) and self._can_move_lesson_to_day(entry, empty_day):
                    new_slot = self._find_available_slot_for_teacher_and_class(
                        teacher_id, entry['class_id'], empty_day)
                    
                    if new_slot is not None:
                        self._move_lesson_entry(entry, empty_day, new_slot)
                        moved_count += 1
                        self.logger.info(f"      ✅ Moved single lesson to Day {empty_day+1}")
                        break
        
        return moved_count
    
    def _split_blocks_to_fill_days(self, teacher_id: int, empty_days: List[int]) -> int:
        """Split lesson blocks to fill empty days while maintaining block rules"""
        moved_count = 0
        
        for empty_day in empty_days:
            # Find blocks that can be split
            lesson_blocks = self._find_splittable_blocks(teacher_id)
            
            for class_id, lesson_id, block_entries in lesson_blocks:
                if len(block_entries) >= 2:  # Can split blocks of 2+ hours
                    # Take one hour from the block and move to empty day
                    entry_to_move = block_entries[-1]  # Take last entry from block
                    
                    new_slot = self._find_available_slot_for_teacher_and_class(
                        teacher_id, class_id, empty_day)
                    
                    if new_slot is not None:
                        self._move_lesson_entry(entry_to_move, empty_day, new_slot)
                        moved_count += 1
                        self.logger.info(f"      ✅ Split block and moved 1 hour to Day {empty_day+1}")
                        break
        
        return moved_count
    
    def _aggressive_lesson_redistribution(self, teacher_id: int, empty_days: List[int]) -> int:
        """Aggressively redistribute lessons, even if it breaks some block rules"""
        moved_count = 0
        teacher_entries = [e for e in self.schedule_entries if e['teacher_id'] == teacher_id]
        
        for empty_day in empty_days:
            # Find any lesson that can be moved (more relaxed rules)
            for entry in teacher_entries[:]:
                new_slot = self._find_available_slot_for_teacher_and_class(
                    teacher_id, entry['class_id'], empty_day)
                
                if new_slot is not None:
                    self._move_lesson_entry(entry, empty_day, new_slot)
                    moved_count += 1
                    self.logger.info(f"      ⚡ Aggressively moved lesson to Day {empty_day+1}")
                    break
        
        return moved_count
    
    def _is_single_lesson(self, entry: Dict[str, Any]) -> bool:
        """Check if this entry is a single lesson (not part of a block)"""
        same_lesson_same_day = [
            e for e in self.schedule_entries 
            if (e['class_id'] == entry['class_id'] and 
                e['lesson_id'] == entry['lesson_id'] and 
                e['day'] == entry['day'])
        ]
        return len(same_lesson_same_day) == 1
    
    def _find_splittable_blocks(self, teacher_id: int) -> List[Tuple[int, int, List[Dict]]]:
        """Find lesson blocks that can be split"""
        teacher_entries = [e for e in self.schedule_entries if e['teacher_id'] == teacher_id]
        
        # Group by class and lesson
        lesson_groups = {}
        for entry in teacher_entries:
            key = (entry['class_id'], entry['lesson_id'])
            if key not in lesson_groups:
                lesson_groups[key] = []
            lesson_groups[key].append(entry)
        
        splittable_blocks = []
        for (class_id, lesson_id), entries in lesson_groups.items():
            # Group by day to find blocks
            day_groups = {}
            for entry in entries:
                day = entry['day']
                if day not in day_groups:
                    day_groups[day] = []
                day_groups[day].append(entry)
            
            # Find blocks with 2+ consecutive hours
            for day, day_entries in day_groups.items():
                if len(day_entries) >= 2:
                    # Sort by time slot
                    day_entries.sort(key=lambda x: x['time_slot'])
                    
                    # Check if consecutive
                    is_consecutive = True
                    for i in range(1, len(day_entries)):
                        if day_entries[i]['time_slot'] != day_entries[i-1]['time_slot'] + 1:
                            is_consecutive = False
                            break
                    
                    if is_consecutive:
                        splittable_blocks.append((class_id, lesson_id, day_entries))
        
        return splittable_blocks
    
    def _move_lesson_entry(self, entry: Dict[str, Any], new_day: int, new_slot: int):
        """Move a lesson entry to a new day and slot"""
        old_day = entry['day']
        old_slot = entry['time_slot']
        teacher_id = entry['teacher_id']
        class_id = entry['class_id']
        
        # Update entry
        entry['day'] = new_day
        entry['time_slot'] = new_slot
        
        # Update tracking
        self.teacher_slots[teacher_id].discard((old_day, old_slot))
        self.teacher_slots[teacher_id].add((new_day, new_slot))
        
        self.class_slots[class_id].discard((old_day, old_slot))
        self.class_slots[class_id].add((new_day, new_slot))
    
    def _find_available_slot_for_teacher_and_class(self, teacher_id: int, class_id: int, day: int) -> int:
        """Find an available time slot for both teacher and class on given day"""
        school_config = self.db_manager.get_school_type() or "Lise"
        time_slots_count = {
            "İlkokul": 7, "Ortaokul": 7, "Lise": 8,
            "Anadolu Lisesi": 8, "Fen Lisesi": 8, "Sosyal Bilimler Lisesi": 8,
        }.get(school_config, 8)
        
        for slot in range(time_slots_count):
            # Check teacher availability
            if (day, slot) in self.teacher_slots[teacher_id]:
                continue
            
            # Check class availability
            if (day, slot) in self.class_slots[class_id]:
                continue
            
            return slot
        
        return None  # No available slot found
    
    def _can_move_lesson_to_day(self, entry: Dict[str, Any], target_day: int) -> bool:
        """
        Check if a lesson can be moved to a target day
        Considers class conflicts and maintains block integrity
        """
        class_id = entry['class_id']
        lesson_id = entry['lesson_id']
        
        # Check if class has any lessons on target day
        class_lessons_on_day = [e for e in self.schedule_entries 
                               if e['class_id'] == class_id and e['day'] == target_day]
        
        # Check if moving this lesson would break block rules
        # For now, only move single-hour lessons or lessons that don't break blocks
        same_lesson_entries = [e for e in self.schedule_entries 
                              if e['class_id'] == class_id and e['lesson_id'] == lesson_id]
        
        # If this lesson has multiple entries (blocks), be more careful
        if len(same_lesson_entries) > 1:
            # Only move if it doesn't break consecutive blocks
            current_day_entries = [e for e in same_lesson_entries if e['day'] == entry['day']]
            if len(current_day_entries) > 1:
                # This is part of a block, don't move
                return False
        
        return True
    
    def _find_available_slot_for_teacher(self, teacher_id: int, day: int) -> int:
        """Find an available time slot for teacher on given day"""
        school_config = self.db_manager.get_school_type() or "Lise"
        time_slots_count = {
            "İlkokul": 7, "Ortaokul": 7, "Lise": 8,
            "Anadolu Lisesi": 8, "Fen Lisesi": 8, "Sosyal Bilimler Lisesi": 8,
        }.get(school_config, 8)
        
        for slot in range(time_slots_count):
            if (day, slot) not in self.teacher_slots[teacher_id]:
                # Check if any class is using this slot
                slot_occupied = any(
                    (day, slot) in class_slots 
                    for class_slots in self.class_slots.values()
                )
                if not slot_occupied:
                    return slot
        
        return None  # No available slot found
    
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
    Convenience function to generate complete schedule using optimized scheduler
    """
    try:
        from algorithms.optimized_curriculum_scheduler import OptimizedCurriculumScheduler
        scheduler = OptimizedCurriculumScheduler(db_manager)
        return scheduler.generate_schedule()
    except ImportError:
        # Fallback to original implementation
        generator = CurriculumBasedFullScheduleGenerator(db_manager)
        return generator.generate_full_schedule()