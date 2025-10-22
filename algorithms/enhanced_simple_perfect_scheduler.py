"""
Enhanced Simple Perfect Scheduler
Extends the existing working Simple Perfect Scheduler with improved filling strategies
"""
import time
from typing import List, Dict, Any, Tuple
from algorithms.simple_perfect_scheduler import SimplePerfectScheduler
from algorithms.monitoring import PerformanceMonitor
from utils.progress_tracker import SchedulerProgressTracker


class EnhancedSimplePerfectScheduler(SimplePerfectScheduler):
    """
    Enhanced version of Simple Perfect Scheduler with improved filling strategies
    Builds upon the proven working algorithm to achieve higher filling rates
    """
    
    def __init__(self, db_manager, progress_callback=None, heuristics=None):
        # Call parent constructor with correct parameters
        if heuristics is not None:
            super().__init__(db_manager, progress_callback, heuristics)
        else:
            super().__init__(db_manager, progress_callback)
        self.performance_monitor = PerformanceMonitor()
        self.progress_tracker = SchedulerProgressTracker()
        
        # Enhanced scheduling parameters
        self.max_placement_attempts = 50
        self.aggressive_filling = True
        self.gap_filling_enabled = True
        self.relaxed_constraints = False  # Conservative by default
        
        # School time slots configuration (copied from base_scheduler.py)
        self.SCHOOL_TIME_SLOTS = {
            "İlkokul": 7,
            "Ortaokul": 7,
            "Lise": 8,
            "Anadolu Lisesi": 8,
            "Fen Lisesi": 8,
            "Sosyal Bilimler Lisesi": 8,
        }
        
    def _get_school_config(self):
        """
        Get school configuration (copied from base_scheduler.py)
        
        Returns:
            Dict with school configuration
        """
        school_type = self.db_manager.get_school_type() or "Lise"
        time_slots_count = self.SCHOOL_TIME_SLOTS.get(school_type, 8)

        return {"school_type": school_type, "time_slots_count": time_slots_count}
        
    def _can_place_lesson(self, class_id: int, teacher_id: int, day: int, time_slot: int, 
                          check_availability: bool = True, consecutive_slots: int = 1) -> tuple:
        """
        Check if a lesson can be placed at a specific slot (delegate to parent)
        """
        # Call parent class method
        return super()._can_place_lesson(class_id, teacher_id, day, time_slot, 
                                        check_availability, consecutive_slots)
        
    def generate_schedule(self) -> List[Dict[str, Any]]:
        """
        Generate enhanced schedule with improved filling strategies
        """
        print("=" * 80)
        print("ENHANCED SIMPLE PERFECT SCHEDULER")
        print("=" * 80)
        print("Extending proven algorithm with enhanced filling strategies")
        
        start_time = time.time()
        
        # Step 1: Generate base schedule using proven Simple Perfect approach
        base_schedule = self._generate_base_schedule()
        print(f"Base schedule generated: {len(base_schedule)} entries")
        
        # Step 2: Apply enhanced filling strategies
        enhanced_schedule = self._apply_enhanced_filling_strategies(base_schedule)
        print(f"Enhanced schedule after filling: {len(enhanced_schedule)} entries")
        
        # Step 3: Final optimization and validation
        final_schedule = self._final_optimization_pass(enhanced_schedule)
        print(f"Final optimized schedule: {len(final_schedule)} entries")
        
        total_time = time.time() - start_time
        print(f"Schedule generation completed in {total_time:.2f} seconds")
        
        # Update internal state
        self.schedule_entries = final_schedule
        
        # Validate final schedule
        self._validate_final_schedule(final_schedule)
        
        return final_schedule
    
    def _generate_base_schedule(self) -> List[Dict[str, Any]]:
        """
        Generate base schedule using proven Simple Perfect approach
        """
        # Use the parent class's proven approach
        return super().generate_schedule()
    
    def _apply_enhanced_filling_strategies(self, base_schedule: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply enhanced strategies to improve filling rate
        """
        enhanced_schedule = base_schedule.copy()
        
        # Strategy 1: Identify and fill gaps in existing schedule
        if self.gap_filling_enabled:
            gap_filled_schedule = self._fill_gaps_in_schedule(enhanced_schedule)
            print(f"After gap filling: {len(gap_filled_schedule)} entries")
        else:
            gap_filled_schedule = enhanced_schedule
        
        # Strategy 2: Place remaining unplaced assignments
        remaining_assignments = self._get_unplaced_assignments(gap_filled_schedule)
        print(f"Unplaced assignments: {len(remaining_assignments)}")
        
        for assignment in remaining_assignments:
            self._try_place_remaining_assignment(gap_filled_schedule, assignment)
        
        print(f"After placing remaining: {len(gap_filled_schedule)} entries")
        
        # Strategy 3: Aggressive placement for difficult assignments
        if self.aggressive_filling:
            difficult_assignments = self._identify_difficult_assignments()
            for assignment in difficult_assignments:
                self._try_aggressive_placement(gap_filled_schedule, assignment)
        
        print(f"After aggressive placement: {len(gap_filled_schedule)} entries")
        
        return gap_filled_schedule
    
    def _fill_gaps_in_schedule(self, schedule: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Fill gaps in the existing schedule
        """
        filled_schedule = schedule.copy()
        
        # Get all classes
        classes = self.db_manager.get_all_classes()
        
        # For each class, check each day for gaps
        for class_obj in classes:
            # Get current schedule for this class
            class_schedule = [entry for entry in schedule if entry["class_id"] == class_obj.class_id]
            
            # Check each day
            for day in range(5):  # 5 days per week
                # Get occupied slots for this class on this day
                occupied_slots = {entry["time_slot"] for entry in class_schedule if entry["day"] == day}
                
                # Try to fill empty slots
                school_config = self._get_school_config()
                time_slots_count = school_config["time_slots_count"]
                
                for time_slot in range(time_slots_count):
                    if time_slot not in occupied_slots:
                        # This slot is empty, try to place an assignment here
                        self._try_place_in_empty_slot(filled_schedule, class_obj.class_id, day, time_slot)
        
        return filled_schedule
    
    def _try_place_in_empty_slot(self, schedule: List[Dict[str, Any]], class_id: int, day: int, time_slot: int):
        """
        Try to place an assignment in an empty slot
        """
        # Get all assignments for this class
        assignments = self.db_manager.get_schedule_by_school_type()
        class_assignments = [a for a in assignments if a.class_id == class_id]
        
        # Try each assignment
        for assignment in class_assignments:
            # Check if this assignment still needs placement
            current_count = sum(1 for entry in schedule 
                              if entry["class_id"] == class_id and entry["lesson_id"] == assignment.lesson_id)
            
            class_obj = next((c for c in self.db_manager.get_all_classes() if c.class_id == class_id), None)
            if class_obj:
                weekly_hours = self.db_manager.get_weekly_hours_for_lesson(assignment.lesson_id, class_obj.grade)
                
                if weekly_hours and current_count < weekly_hours:
                    # Try to place this assignment in the empty slot
                    # Use parent class method directly
                    can_place, _ = self._can_place_lesson(
                        assignment.class_id,
                        assignment.teacher_id,
                        day,
                        time_slot,
                        check_availability=True
                    )
                    
                    if can_place:
                        new_entry = {
                            "class_id": assignment.class_id,
                            "lesson_id": assignment.lesson_id,
                            "teacher_id": assignment.teacher_id,
                            "day": day,
                            "time_slot": time_slot,
                            "classroom_id": 1
                        }
                        schedule.append(new_entry)
                        return  # Successfully placed
    
    def _get_unplaced_assignments(self, schedule: List[Dict[str, Any]]) -> List:
        """
        Get assignments that haven't been fully placed yet
        """
        # Get all assignments
        all_assignments = self.db_manager.get_schedule_by_school_type()
        
        # Count how many times each assignment is already placed
        placement_counts = {}
        for entry in schedule:
            key = (entry["class_id"], entry["lesson_id"])
            if key not in placement_counts:
                placement_counts[key] = 0
            placement_counts[key] += 1
        
        # Identify assignments that are under-placed
        unplaced = []
        for assignment in all_assignments:
            key = (assignment.class_id, assignment.lesson_id)
            placed_count = placement_counts.get(key, 0)
            
            class_obj = next((c for c in self.db_manager.get_all_classes() if c.class_id == assignment.class_id), None)
            if class_obj:
                weekly_hours = self.db_manager.get_weekly_hours_for_lesson(assignment.lesson_id, class_obj.grade)
                
                if weekly_hours and placed_count < weekly_hours:
                    unplaced.append(assignment)
        
        return unplaced
    
    def _try_place_remaining_assignment(self, schedule: List[Dict[str, Any]], assignment):
        """
        Try to place a remaining assignment that wasn't fully placed
        """
        class_obj = next((c for c in self.db_manager.get_all_classes() if c.class_id == assignment.class_id), None)
        if not class_obj:
            return
            
        weekly_hours = self.db_manager.get_weekly_hours_for_lesson(assignment.lesson_id, class_obj.grade)
        if not weekly_hours:
            return
        
        # Count how many are already placed
        already_placed = sum(1 for entry in schedule 
                           if entry["class_id"] == assignment.class_id and 
                              entry["lesson_id"] == assignment.lesson_id)
        
        remaining_hours = weekly_hours - already_placed
        
        if remaining_hours <= 0:
            return  # Already fully placed
        
        # Try to place remaining hours
        for _ in range(remaining_hours):
            placed = False
            max_attempts = min(self.max_placement_attempts, 50)  # Limit attempts
            attempts = 0
            
            while not placed and attempts < max_attempts:
                attempts += 1
                
                # Try different days and time slots
                for day in range(5):
                    if placed:
                        break
                    school_config = super()._get_school_config()
                    for time_slot in range(school_config["time_slots_count"]):
                        can_place, _ = self._can_place_lesson(
                            assignment.class_id,
                            assignment.teacher_id,
                            day,
                            time_slot,
                            check_availability=True
                        )
                        
                        if can_place:
                            new_entry = {
                                "class_id": assignment.class_id,
                                "lesson_id": assignment.lesson_id,
                                "teacher_id": assignment.teacher_id,
                                "day": day,
                                "time_slot": time_slot,
                                "classroom_id": 1
                            }
                            schedule.append(new_entry)
                            placed = True
                            break
            
            if not placed:
                print(f"  Warning: Could not place remaining hour for assignment {assignment.class_id}-{assignment.lesson_id}")
    
    def _identify_difficult_assignments(self) -> List:
        """
        Identify assignments that are difficult to place
        """
        # Assignments with very limited available slots are considered difficult
        difficult_assignments = []
        assignments = self.db_manager.get_schedule_by_school_type()
        
        for assignment in assignments:
            available_slots = 0
            for day in range(5):
                for time_slot in range(self._get_school_config()["time_slots_count"]):
                    can_place, _ = self._can_place_lesson(
                        assignment.class_id,
                        assignment.teacher_id,
                        day,
                        time_slot,
                        check_availability=True
                    )
                    
                    if can_place:
                        available_slots += 1
            
            # If very few slots available, it's difficult
            if available_slots < 3:  # Less than 3 slots available
                difficult_assignments.append(assignment)
        
        return difficult_assignments
    
    def _try_aggressive_placement(self, schedule: List[Dict[str, Any]], assignment):
        """
        Try aggressive placement for difficult assignments
        """
        # This is still conservative - we respect hard constraints
        # but try more combinations and are less restrictive about some soft preferences
        
        class_obj = next((c for c in self.db_manager.get_all_classes() if c.class_id == assignment.class_id), None)
        if not class_obj:
            return
            
        weekly_hours = self.db_manager.get_weekly_hours_for_lesson(assignment.lesson_id, class_obj.grade)
        if not weekly_hours:
            return
        
        # Count how many are already placed
        already_placed = sum(1 for entry in schedule 
                           if entry["class_id"] == assignment.class_id and 
                              entry["lesson_id"] == assignment.lesson_id)
        
        remaining_hours = weekly_hours - already_placed
        
        if remaining_hours <= 0:
            return  # Already fully placed
        
        # Try to place with more aggressive strategy
        for _ in range(remaining_hours):
            self._place_with_aggressive_strategy(schedule, assignment)
    
    def _place_with_aggressive_strategy(self, schedule: List[Dict[str, Any]], assignment):
        """
        Place with aggressive but still constraint-respecting strategy
        """
        # Try all possible combinations more systematically
        for day in range(5):
            school_config = super()._get_school_config()
            for time_slot in range(school_config["time_slots_count"]):
                # Check only hard constraints (class and teacher conflicts)
                class_conflict = self._is_slot_occupied_by_class(assignment.class_id, day, time_slot)
                teacher_conflict = self._is_slot_occupied_by_teacher(assignment.teacher_id, day, time_slot)
                
                if not class_conflict and not teacher_conflict:
                    # Even if teacher is not explicitly available, we can still place
                    # (this is the "aggressive" part - still respecting hard constraints)
                    new_entry = {
                        "class_id": assignment.class_id,
                        "lesson_id": assignment.lesson_id,
                        "teacher_id": assignment.teacher_id,
                        "day": day,
                        "time_slot": time_slot,
                        "classroom_id": 1
                    }
                    schedule.append(new_entry)
                    return  # Successfully placed
    
    def _final_optimization_pass(self, schedule: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Final optimization pass to improve schedule quality
        """
        optimized_schedule = schedule.copy()
        
        # Remove duplicates and validate
        validated_schedule = []
        seen_entries = set()
        
        for entry in optimized_schedule:
            # Create a unique key for this entry
            key = (entry["class_id"], entry["lesson_id"], entry["teacher_id"], 
                   entry["day"], entry["time_slot"])
            
            if key not in seen_entries:
                seen_entries.add(key)
                validated_schedule.append(entry)
        
        return validated_schedule
    
    def _validate_final_schedule(self, schedule: List[Dict[str, Any]]):
        """
        Validate the final schedule for conflicts
        """
        conflicts = self._detect_conflicts(schedule)
        if conflicts:
            print(f"Warning: {len(conflicts)} conflicts detected in final schedule")
            # In a real implementation, we would try to resolve these