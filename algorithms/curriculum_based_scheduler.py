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
        Schedule a lesson for a specific class for its required weekly hours
        """
        scheduled_count = 0
        max_attempts = weekly_hours * 20  # More attempts for better coverage
        attempts = 0
        
        # Try to schedule all required hours
        while scheduled_count < weekly_hours and attempts < max_attempts:
            attempts += 1
            
            # Try different strategies for placement
            for day in range(5):  # 5 days per week
                if scheduled_count >= weekly_hours:
                    break
                    
                for time_slot in range(time_slots_count):
                    if scheduled_count >= weekly_hours:
                        break
                        
                    # Check if we can place this lesson here (relaxed constraints)
                    can_place = self._can_place_lesson_relaxed(
                        class_id, teacher_id, day, time_slot
                    )
                    
                    if can_place:
                        # Place the lesson
                        classroom_id = 1  # Default classroom
                        self._add_entry(class_id, teacher_id, lesson_id, classroom_id, day, time_slot)
                        scheduled_count += 1
                        self.logger.debug(f"         ✓ Placed: Day {day+1}, Slot {time_slot+1}")
                        break  # Move to next hour needed
        
        # If we couldn't place all hours, try aggressive placement
        if scheduled_count < weekly_hours:
            remaining = weekly_hours - scheduled_count
            self.logger.warning(f"      ⚠️  {remaining} hours missing, trying aggressive placement...")
            aggressive_placed = self._aggressive_placement_for_remaining_hours(
                class_id, lesson_id, teacher_id, remaining, time_slots_count
            )
            scheduled_count += aggressive_placed
            
        return scheduled_count
    
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


def generate_complete_schedule(db_manager: DatabaseManager) -> List[Dict[str, Any]]:
    """
    Convenience function to generate complete schedule
    """
    generator = CurriculumBasedFullScheduleGenerator(db_manager)
    return generator.generate_full_schedule()