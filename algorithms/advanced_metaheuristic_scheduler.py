"""
Advanced scheduling algorithm using metaheuristics
Implements Large Neighborhood Search to improve schedule filling
"""
import random
import time
from typing import List, Dict, Any, Tuple
from algorithms.base_scheduler import BaseScheduler
from algorithms.monitoring import PerformanceMonitor
from utils.progress_tracker import SchedulerProgressTracker

class AdvancedMetaheuristicScheduler(BaseScheduler):
    """
    Advanced scheduler using Large Neighborhood Search and other metaheuristics
    to achieve higher filling rates while respecting all constraints
    """
    
    def __init__(self, db_manager, progress_callback=None, max_iterations=500, neighborhood_size=20):
        super().__init__(db_manager, progress_callback)
        self.max_iterations = max_iterations
        self.neighborhood_size = neighborhood_size
        self.performance_monitor = PerformanceMonitor()
        self.progress_tracker = SchedulerProgressTracker()
        
    def generate_schedule(self) -> List[Dict[str, Any]]:
        """
        Generate schedule using advanced metaheuristics
        """
        print("=" * 80)
        print("ADVANCED METAHEURISTIC SCHEDULER")
        print("=" * 80)
        print(f"Max iterations: {self.max_iterations}")
        print(f"Neighborhood size: {self.neighborhood_size}")
        
        # Start with an initial solution (use simple perfect scheduler)
        initial_scheduler = self._get_simple_perfect_scheduler()
        initial_schedule = initial_scheduler.generate_schedule()
        
        self.schedule_entries = initial_schedule.copy()
        print(f"Initial solution: {len(initial_schedule)} entries")
        
        # Track best solution
        best_schedule = self.schedule_entries.copy()
        best_score = self._calculate_fitness(self.schedule_entries)
        
        print(f"Initial score: {best_score}")
        
        # Large Neighborhood Search
        iteration = 0
        no_improvement_count = 0
        max_no_improvement = 50  # Stop if no improvement for 50 iterations
        
        start_time = time.time()
        
        for iteration in range(self.max_iterations):
            # Report progress
            if iteration % 10 == 0:
                progress_percent = int((iteration / self.max_iterations) * 100)
                self._update_progress(f"Metaheuristic iteration {iteration}/{self.max_iterations}", progress_percent)
                
                # Report current status
                current_score = self._calculate_fitness(self.schedule_entries)
                print(f"Iteration {iteration}: Score = {current_score}, "
                      f"Schedule size = {len(self.schedule_entries)}")
            
            # Create a destroyed version of current solution (LNS destroy phase)
            destroyed_schedule = self._destroy_solution(self.schedule_entries.copy())
            
            # Repair the destroyed solution (LNS repair phase)
            repaired_schedule = self._repair_solution(destroyed_schedule)
            
            # Calculate new score
            new_score = self._calculate_fitness(repaired_schedule)
            
            # Accept new solution based on simulated annealing criteria
            if self._should_accept_solution(best_score, new_score, iteration):
                self.schedule_entries = repaired_schedule.copy()
                
                # Update best solution if improved
                if new_score > best_score:
                    best_schedule = repaired_schedule.copy()
                    best_score = new_score
                    no_improvement_count = 0
                    print(f"  IMPROVEMENT: New best score = {best_score}")
                else:
                    no_improvement_count += 1
            else:
                no_improvement_count += 1
            
            # Early termination if no improvement for too long
            if no_improvement_count >= max_no_improvement:
                print(f"  No improvement for {max_no_improvement} iterations, stopping...")
                break
        
        total_time = time.time() - start_time
        print(f"Optimization completed in {total_time:.2f} seconds")
        print(f"Final best score: {best_score}")
        print(f"Schedule entries: {len(best_schedule)}")
        
        # Return the best schedule found
        self.schedule_entries = best_schedule
        return best_schedule
    
    def _get_simple_perfect_scheduler(self):
        """Get simple perfect scheduler for initial solution"""
        from algorithms.simple_perfect_scheduler import SimplePerfectScheduler
        return SimplePerfectScheduler(self.db_manager, self.progress_callback)
    
    def _calculate_fitness(self, schedule: List[Dict[str, Any]]) -> float:
        """
        Calculate fitness score based on:
        - Coverage percentage
        - Constraint violations
        - Soft constraint satisfaction
        - Teacher preference satisfaction
        """
        if not schedule:
            return 0.0
        
        # Calculate coverage
        classes = self.db_manager.get_all_classes()
        school_config = self._get_school_config()
        daily_hours = school_config["time_slots_count"]
        total_days = 5
        
        theoretical_capacity = len(classes) * total_days * daily_hours
        coverage = len(schedule) / theoretical_capacity if theoretical_capacity > 0 else 0
        
        # Check conflicts (penalize violations)
        conflicts = self._detect_conflicts_in_schedule(schedule)
        conflict_penalty = len(conflicts) * 100  # Heavy penalty for each conflict
        
        # Calculate soft constraint satisfaction
        soft_score = self._calculate_soft_constraints_score(schedule)
        
        # Final fitness: prioritize coverage but penalize conflicts heavily
        fitness = coverage * 1000 - conflict_penalty + soft_score
        
        return max(0, fitness)  # Ensure non-negative
    
    def _detect_conflicts_in_schedule(self, schedule: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect conflicts in a given schedule"""
        conflicts = []
        
        # Check teacher conflicts
        teacher_slots = {}
        for entry in schedule:
            key = (entry["teacher_id"], entry["day"], entry["time_slot"])
            if key in teacher_slots:
                conflicts.append({
                    "type": "teacher_conflict",
                    "entries": [teacher_slots[key], entry]
                })
            else:
                teacher_slots[key] = entry
        
        # Check class conflicts
        class_slots = {}
        for entry in schedule:
            key = (entry["class_id"], entry["day"], entry["time_slot"])
            if key in class_slots:
                conflicts.append({
                    "type": "class_conflict", 
                    "entries": [class_slots[key], entry]
                })
            else:
                class_slots[key] = entry
        
        return conflicts
    
    def _calculate_soft_constraints_score(self, schedule: List[Dict[str, Any]]) -> float:
        """Calculate score based on soft constraints satisfaction"""
        score = 0.0
        
        # Add points for teachers having their preferred hours
        for entry in schedule:
            teacher_id = entry["teacher_id"]
            day = entry["day"]
            time_slot = entry["time_slot"]
            
            if self.db_manager.is_teacher_available(teacher_id, day, time_slot):
                score += 1.0  # Small bonus for preferred time
        
        # Add points for balanced distribution
        class_daily_hours = {}
        for entry in schedule:
            class_day_key = (entry["class_id"], entry["day"])
            if class_day_key not in class_daily_hours:
                class_daily_hours[class_day_key] = 0
            class_daily_hours[class_day_key] += 1
        
        # Penalize days with too many hours (more than 6 hours per day is problematic)
        for _, daily_hours in class_daily_hours.items():
            if daily_hours > 6:
                score -= (daily_hours - 6) * 2  # Penalty for overcrowded days
        
        return score
    
    def _destroy_solution(self, schedule: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Destroy a random portion of the schedule (LNS destroy phase)
        """
        if not schedule:
            return schedule
        
        # Determine how many entries to remove (10-30% of schedule)
        min_destroy = max(1, len(schedule) // 10)  # At least 10%
        max_destroy = min(len(schedule) - 1, len(schedule) // 3)  # At most 33%
        
        num_to_remove = random.randint(min_destroy, max_destroy)
        
        # Randomly select entries to remove
        entries_to_remove = random.sample(schedule, num_to_remove)
        
        # Create new schedule without these entries
        remaining_schedule = [entry for entry in schedule if entry not in entries_to_remove]
        
        # Clear internal state and rebuild from remaining schedule
        self.schedule_entries = []
        self.teacher_slots.clear()
        self.class_slots.clear()
        
        # Add back the remaining entries to internal state
        for entry in remaining_schedule:
            self.schedule_entries.append(entry)
            self.class_slots[entry["class_id"]].add((entry["day"], entry["time_slot"]))
            self.teacher_slots[entry["teacher_id"]].add((entry["day"], entry["time_slot"]))
        
        return remaining_schedule
    
    def _repair_solution(self, partial_schedule: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Repair the partial schedule by adding back missing assignments (LNS repair phase)
        """
        # Get all assignments that need to be scheduled
        assignments = self.db_manager.get_schedule_by_school_type()
        
        # Find which assignments are missing from the partial schedule
        scheduled_entries = set()
        for entry in partial_schedule:
            key = (entry["class_id"], entry["lesson_id"], entry["teacher_id"])
            scheduled_entries.add(key)
        
        missing_assignments = []
        for assignment in assignments:
            key = (assignment.class_id, assignment.lesson_id, assignment.teacher_id)
            if key not in scheduled_entries:
                missing_assignments.append(assignment)
        
        # Try to place the missing assignments
        repaired_schedule = partial_schedule.copy()
        
        # Rebuild state for the partial schedule
        self.schedule_entries = partial_schedule.copy()
        self.teacher_slots.clear()
        self.class_slots.clear()
        
        for entry in partial_schedule:
            self.class_slots[entry["class_id"]].add((entry["day"], entry["time_slot"]))
            self.teacher_slots[entry["teacher_id"]].add((entry["day"], entry["time_slot"]))
        
        # Sort missing assignments by priority (difficult lessons first)
        missing_assignments.sort(key=lambda x: self._get_assignment_priority(x), reverse=True)
        
        # Place each missing assignment using the best available slot
        placed_count = 0
        for assignment in missing_assignments:
            if self._try_place_assignment(assignment, repaired_schedule):
                placed_count += 1
        
        print(f"  Repair: Placed {placed_count}/{len(missing_assignments)} missing assignments")
        
        return repaired_schedule
    
    def _get_assignment_priority(self, assignment) -> int:
        """
        Get priority for assignment placement (higher priority items are placed first)
        """
        # Get lesson info to determine priority
        lesson = None
        lessons = self.db_manager.get_all_lessons()
        for l in lessons:
            if l.lesson_id == assignment.lesson_id:
                lesson = l
                break
        
        if lesson is None:
            return 1
        
        # Higher priority for core subjects
        if lesson.name in ["Türkçe", "Matematik", "Fen Bilimleri"]:
            return 10
        elif lesson.name in ["Sosyal Bilgiler", "İngilizce"]:
            return 8
        elif lesson.name in ["Din Kültürü ve Ahlak Bilgisi"]:
            return 6
        else:
            return 5  # Lower priority for electives
    
    def _try_place_assignment(self, assignment, schedule: List[Dict[str, Any]]) -> bool:
        """
        Try to place a single assignment in the best available slot
        """
        # Get weekly hours for this assignment
        weekly_hours = self.db_manager.get_weekly_hours_for_lesson(assignment.lesson_id, 
                                                                  assignment.class_id)  # This isn't a complete class object
        if not weekly_hours:
            # Get class object to get grade
            classes = self.db_manager.get_all_classes()
            class_obj = next((c for c in classes if c.class_id == assignment.class_id), None)
            if class_obj:
                weekly_hours = self.db_manager.get_weekly_hours_for_lesson(assignment.lesson_id, 
                                                                          class_obj.grade)
            else:
                # As a fallback, try to get some default value
                weekly_hours = 2  # Default to 2 hours if we can't determine
        
        if not weekly_hours:
            return False  # Can't place without knowing hours needed
        
        # Get how many hours are already placed for this assignment
        already_placed = sum(1 for entry in schedule 
                           if entry["class_id"] == assignment.class_id and 
                              entry["lesson_id"] == assignment.lesson_id)
        
        remaining_hours = weekly_hours - already_placed
        
        if remaining_hours <= 0:
            return True  # Already placed enough
        
        # Find best available slots for remaining hours
        for day in range(5):
            for time_slot in range(self._get_school_config()["time_slots_count"]):
                # Calculate how many consecutive slots we can place
                consecutive_slots = self._find_consecutive_available_slots(
                    assignment.class_id, 
                    assignment.teacher_id, 
                    day, 
                    time_slot, 
                    remaining_hours
                )
                
                if consecutive_slots > 0:
                    # Place the lesson in consecutive slots
                    for i in range(consecutive_slots):
                        new_entry = {
                            "class_id": assignment.class_id,
                            "lesson_id": assignment.lesson_id,
                            "teacher_id": assignment.teacher_id,
                            "day": day,
                            "time_slot": time_slot + i,
                            "classroom_id": 1  # Default classroom
                        }
                        
                        # Add to schedule and internal state
                        schedule.append(new_entry)
                        self.schedule_entries.append(new_entry)
                        self.class_slots[assignment.class_id].add((day, time_slot + i))
                        self.teacher_slots[assignment.teacher_id].add((day, time_slot + i))
                    
                    remaining_hours -= consecutive_slots
                    
                    if remaining_hours <= 0:
                        return True  # Successfully placed all remaining hours
        
        return False  # Could not place this assignment
    
    def _find_consecutive_available_slots(self, class_id: int, teacher_id: int, 
                                        day: int, start_slot: int, max_slots: int) -> int:
        """
        Find how many consecutive slots starting at start_slot are available
        """
        consecutive_available = 0
        
        for slot in range(start_slot, min(start_slot + max_slots, 
                                         self._get_school_config()["time_slots_count"])):
            can_place, _ = self._can_place_lesson(class_id, teacher_id, day, slot, 
                                                 check_availability=True, consecutive_slots=1)
            if can_place:
                consecutive_available += 1
            else:
                break  # Stop at first unavailable slot
        
        return consecutive_available
    
    def _should_accept_solution(self, current_score: float, new_score: float, iteration: int) -> bool:
        """
        Decide whether to accept a new solution based on simulated annealing criteria
        """
        # Always accept if it's better
        if new_score > current_score:
            return True
        
        # Accept with some probability if it's worse (to escape local optima)
        temperature = self._get_temperature(iteration)
        score_diff = new_score - current_score
        probability = min(1.0, max(0.0, score_diff / temperature))
        
        return random.random() < probability
    
    def _get_temperature(self, iteration: int) -> float:
        """
        Calculate temperature for simulated annealing (decreases over time)
        """
        max_temp = 100.0
        cooling_rate = 0.99
        return max_temp * (cooling_rate ** iteration)