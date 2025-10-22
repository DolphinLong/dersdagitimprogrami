"""
Simulated Annealing for Class Scheduling
Implements simulated annealing algorithm to find optimal schedule
"""
import random
import math
import time
from typing import List, Dict, Any
from algorithms.base_scheduler import BaseScheduler
from algorithms.monitoring import PerformanceMonitor
from utils.progress_tracker import SchedulerProgressTracker


class SimulatedAnnealingScheduler(BaseScheduler):
    """
    Simulated Annealing-based scheduler that uses thermal cooling analogy to find optimal solutions
    """
    
    def __init__(self, db_manager, progress_callback=None, initial_temperature=1000.0,
                 cooling_rate=0.95, min_temperature=1.0, max_iterations_without_improvement=100):
        super().__init__(db_manager, progress_callback)
        self.initial_temperature = initial_temperature
        self.cooling_rate = cooling_rate
        self.min_temperature = min_temperature
        self.max_iterations_without_improvement = max_iterations_without_improvement
        self.performance_monitor = PerformanceMonitor()
        self.progress_tracker = SchedulerProgressTracker()
        
        # Get all assignments to know what needs to be scheduled
        self.assignments = self.db_manager.get_schedule_by_school_type()
        self.classes = self.db_manager.get_all_classes()
        self.teachers = self.db_manager.get_all_teachers()
        self.lessons = self.db_manager.get_all_lessons()
        
        school_config = self._get_school_config()
        self.time_slots = school_config["time_slots_count"]
        self.days = 5  # Assuming 5 days per week
        
    def generate_schedule(self) -> List[Dict[str, Any]]:
        """
        Generate schedule using simulated annealing
        """
        print("=" * 80)
        print("SIMULATED ANNEALING SCHEDULER")
        print("=" * 80)
        print(f"Initial temperature: {self.initial_temperature}")
        print(f"Cooling rate: {self.cooling_rate}")
        print(f"Min temperature: {self.min_temperature}")
        print(f"Max iterations without improvement: {self.max_iterations_without_improvement}")
        
        start_time = time.time()
        
        # Create initial solution (using greedy approach)
        current_schedule = self._create_initial_solution()
        current_fitness = self._calculate_fitness(current_schedule)
        
        best_schedule = current_schedule.copy()
        best_fitness = current_fitness
        
        print(f"Initial solution fitness: {current_fitness}")
        
        temperature = self.initial_temperature
        iteration = 0
        iterations_without_improvement = 0
        
        while temperature > self.min_temperature and iterations_without_improvement < self.max_iterations_without_improvement:
            # Generate neighbor solution
            neighbor_schedule = self._generate_neighbor(current_schedule)
            neighbor_fitness = self._calculate_fitness(neighbor_schedule)
            
            # Calculate fitness difference
            fitness_diff = neighbor_fitness - current_fitness
            
            # Accept or reject the neighbor based on Metropolis criterion
            if fitness_diff > 0 or random.random() < math.exp(fitness_diff / temperature):
                current_schedule = neighbor_schedule
                current_fitness = neighbor_fitness
                
                # Update best solution if improved
                if current_fitness > best_fitness:
                    best_schedule = current_schedule.copy()
                    best_fitness = current_fitness
                    iterations_without_improvement = 0
                    print(f"  IMPROVEMENT: New best fitness = {best_fitness:.2f}")
                else:
                    iterations_without_improvement += 1
            else:
                iterations_without_improvement += 1
            
            # Cool down
            temperature *= self.cooling_rate
            
            # Progress reporting
            if iteration % 100 == 0:
                progress_percent = max(0, min(100, int((self.initial_temperature - temperature) / 
                                                     (self.initial_temperature - self.min_temperature) * 100)))
                self._update_progress(f"SA iteration {iteration}, T={temperature:.2f}", progress_percent)
                
                print(f"Iteration {iteration}: Current fitness = {current_fitness:.2f}, "
                      f"Best fitness = {best_fitness:.2f}, Temperature = {temperature:.2f}")
            
            iteration += 1
        
        total_time = time.time() - start_time
        print(f"Optimization completed in {total_time:.2f} seconds")
        print(f"Final temperature: {temperature:.2f}")
        print(f"Final best fitness: {best_fitness}")
        print(f"Total iterations: {iteration}")
        
        # Convert best solution to the expected format
        self.schedule_entries = best_schedule
        return best_schedule
    
    def _create_initial_solution(self) -> List[Dict[str, Any]]:
        """
        Create an initial solution using a greedy approach
        """
        schedule = []
        
        # Try to place assignments in a greedy way
        assignments_to_place = self.assignments.copy()
        random.shuffle(assignments_to_place)
        
        for assignment in assignments_to_place:
            # Get weekly hours for this assignment
            class_obj = next((c for c in self.classes if c.class_id == assignment.class_id), None)
            if class_obj:
                weekly_hours = self.db_manager.get_weekly_hours_for_lesson(assignment.lesson_id, class_obj.grade)
                
                if weekly_hours:
                    # Try to place the required number of hours
                    hours_placed = 0
                    
                    # Try different days and time slots
                    for day in range(self.days):
                        if hours_placed >= weekly_hours:
                            break
                        for time_slot in range(self.time_slots):
                            if hours_placed >= weekly_hours:
                                break
                                
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
                                    "classroom_id": 1  # Default classroom
                                }
                                
                                schedule.append(new_entry)
                                hours_placed += 1
        
        return schedule
    
    def _generate_neighbor(self, schedule: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate a neighbor solution by making a small change to the current solution
        """
        neighbor = schedule.copy()
        
        if not neighbor:
            return neighbor
        
        # Choose a random operation to modify the schedule
        operation = random.choice(["move", "swap", "add", "remove"])
        
        if operation == "move" and len(neighbor) > 0:
            # Move an existing assignment to a different slot
            idx = random.randint(0, len(neighbor) - 1)
            entry_to_move = neighbor[idx]
            
            # Try to find a new valid slot
            for day in range(self.days):
                for time_slot in range(self.time_slots):
                    if (day == entry_to_move["day"] and time_slot == entry_to_move["time_slot"]):
                        continue  # Skip the current position
                        
                    can_place, _ = self._can_place_lesson(
                        entry_to_move["class_id"],
                        entry_to_move["teacher_id"], 
                        day, 
                        time_slot,
                        check_availability=True
                    )
                    
                    if can_place:
                        # Update the entry's position
                        entry_to_move["day"] = day
                        entry_to_move["time_slot"] = time_slot
                        break
                else:
                    continue
                break
        
        elif operation == "swap" and len(neighbor) > 1:
            # Swap two assignments
            idx1, idx2 = random.sample(range(len(neighbor)), 2)
            entry1 = neighbor[idx1]
            entry2 = neighbor[idx2]
            
            # Check if swapping is valid for both entries
            can_place_1, _ = self._can_place_lesson(
                entry1["class_id"],
                entry1["teacher_id"],
                entry2["day"],
                entry2["time_slot"],
                check_availability=True
            )
            
            can_place_2, _ = self._can_place_lesson(
                entry2["class_id"],
                entry2["teacher_id"],
                entry1["day"],
                entry1["time_slot"],
                check_availability=True
            )
            
            if can_place_1 and can_place_2:
                # Swap the positions
                neighbor[idx1]["day"] = entry2["day"]
                neighbor[idx1]["time_slot"] = entry2["time_slot"]
                neighbor[idx2]["day"] = entry1["day"]
                neighbor[idx2]["time_slot"] = entry1["time_slot"]
        
        elif operation == "add":
            # Try to add a new valid assignment not currently scheduled
            # Find assignments that might not be fully placed
            scheduled_class_lesson_pairs = {(entry["class_id"], entry["lesson_id"]) for entry in neighbor}
            unscheduled_assignments = [a for a in self.assignments 
                                       if (a.class_id, a.lesson_id) not in scheduled_class_lesson_pairs]
            
            if unscheduled_assignments:
                assignment = random.choice(unscheduled_assignments)
                
                # Find a free slot for this assignment
                for day in range(self.days):
                    for time_slot in range(self.time_slots):
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
                            
                            neighbor.append(new_entry)
                            break
                    else:
                        continue
                    break
        
        elif operation == "remove" and len(neighbor) > 0:
            # Remove a random assignment
            idx = random.randint(0, len(neighbor) - 1)
            neighbor.pop(idx)
        
        return neighbor
    
    def _calculate_fitness(self, schedule: List[Dict[str, Any]]) -> float:
        """
        Calculate fitness score for a schedule
        Higher is better
        """
        if not schedule:
            return 0.0
        
        # Calculate coverage (how many slots are filled)
        classes = self.db_manager.get_all_classes()
        school_config = self._get_school_config()
        daily_hours = school_config["time_slots_count"]
        theoretical_capacity = len(classes) * 5 * daily_hours
        coverage = len(schedule) / theoretical_capacity if theoretical_capacity > 0 else 0
        
        # Check conflicts (penalize heavily)
        conflicts = self._detect_conflicts_in_schedule(schedule)
        conflict_penalty = len(conflicts) * 1000  # Heavy penalty for conflicts
        
        # Calculate soft constraints satisfaction
        soft_score = self._calculate_soft_constraints_score(schedule)
        
        # Final fitness: prioritize valid solutions
        if conflict_penalty > 0:
            # If there are conflicts, heavily penalize
            fitness = coverage * 100 - conflict_penalty
        else:
            # If no conflicts, reward coverage and soft constraints
            fitness = coverage * 1000 + soft_score
        
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
                score += 2.0  # Bonus for preferred time
        
        # Add points for avoiding overly crowded days
        class_daily_hours = {}
        for entry in schedule:
            class_day_key = (entry["class_id"], entry["day"])
            if class_day_key not in class_daily_hours:
                class_daily_hours[class_day_key] = 0
            class_daily_hours[class_day_key] += 1
        
        # Reward balanced distribution
        for _, daily_hours in class_daily_hours.items():
            if 4 <= daily_hours <= 6:  # Optimal daily load
                score += daily_hours * 0.5
            elif daily_hours > 6:  # Heavy penalty for overloaded days
                score -= (daily_hours - 6) * 3
        
        return score