"""
Ant Colony Optimization for Class Scheduling
Implements ACO algorithm to find optimal schedule
"""
import random
import math
import time
from typing import List, Dict, Any
from algorithms.base_scheduler import BaseScheduler
from algorithms.monitoring import PerformanceMonitor
from utils.progress_tracker import SchedulerProgressTracker


class AntColonyOptimizationScheduler(BaseScheduler):
    """
    Ant Colony Optimization-based scheduler that mimics ant behavior to find optimal solutions
    """
    
    def __init__(self, db_manager, progress_callback=None, num_ants=20, 
                 evaporation_rate=0.5, pheromone_constant=100, alpha=1.0, beta=2.0, max_iterations=100):
        super().__init__(db_manager, progress_callback)
        self.num_ants = num_ants
        self.evaporation_rate = evaporation_rate
        self.pheromone_constant = pheromone_constant
        self.alpha = alpha  # Pheromone importance
        self.beta = beta    # Heuristic importance
        self.max_iterations = max_iterations
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
        
        # Initialize pheromone matrix (day, time_slot, class_id, teacher_id)
        # For practical reasons, we'll use a simplified version
        self.pheromones = {}
        self._initialize_pheromones()
    
    def _initialize_pheromones(self):
        """
        Initialize pheromone levels for all possible assignments
        """
        for day in range(self.days):
            for time_slot in range(self.time_slots):
                for assignment in self.assignments:
                    key = (assignment.class_id, assignment.teacher_id, day, time_slot)
                    self.pheromones[key] = 0.1  # Start with low pheromone level
    
    def generate_schedule(self) -> List[Dict[str, Any]]:
        """
        Generate schedule using ant colony optimization
        """
        print("=" * 80)
        print("ANT COLONY OPTIMIZATION SCHEDULER")
        print("=" * 80)
        print(f"Number of ants: {self.num_ants}")
        print(f"Evaporation rate: {self.evaporation_rate}")
        print(f"Pheromone constant: {self.pheromone_constant}")
        print(f"Alpha (pheromone importance): {self.alpha}")
        print(f"Beta (heuristic importance): {self.beta}")
        print(f"Max iterations: {self.max_iterations}")
        
        start_time = time.time()
        
        best_schedule = []
        best_fitness = float('-inf')
        
        for iteration in range(self.max_iterations):
            # Generate solutions for all ants
            ant_solutions = []
            ant_fitnesses = []
            
            for ant_id in range(self.num_ants):
                schedule = self._construct_solution()
                fitness = self._calculate_fitness(schedule)
                
                ant_solutions.append(schedule)
                ant_fitnesses.append(fitness)
                
                # Update best solution if improved
                if fitness > best_fitness:
                    best_fitness = fitness
                    best_schedule = schedule.copy()
                    print(f"  IMPROVEMENT: New best fitness = {best_fitness:.2f}")
            
            # Update pheromones based on solutions
            self._update_pheromones(ant_solutions, ant_fitnesses)
            
            # Progress reporting
            if iteration % 10 == 0:
                avg_fitness = sum(ant_fitnesses) / len(ant_fitnesses) if ant_fitnesses else 0
                progress_percent = int((iteration / self.max_iterations) * 100)
                self._update_progress(f"ACO iteration {iteration}/{self.max_iterations}", progress_percent)
                
                print(f"Iteration {iteration}: Best fitness = {best_fitness:.2f}, "
                      f"Average fitness = {avg_fitness:.2f}")
        
        total_time = time.time() - start_time
        print(f"Optimization completed in {total_time:.2f} seconds")
        print(f"Final best fitness: {best_fitness}")
        
        # Convert best solution to the expected format
        self.schedule_entries = best_schedule
        return best_schedule
    
    def _construct_solution(self) -> List[Dict[str, Any]]:
        """
        Construct a solution by simulating an ant building a schedule
        """
        schedule = []
        # Reset the internal state for this ant's solution
        self.teacher_slots.clear()
        self.class_slots.clear()
        
        # Sort assignments by some priority (e.g., number of available slots, difficulty, etc.)
        priority_assignments = self._get_priority_assignments()
        
        for assignment in priority_assignments:
            # Get weekly hours for this assignment
            class_obj = next((c for c in self.classes if c.class_id == assignment.class_id), None)
            if class_obj:
                weekly_hours = self.db_manager.get_weekly_hours_for_lesson(assignment.lesson_id, class_obj.grade)
                
                if weekly_hours:
                    # Place the required number of hours
                    hours_placed = 0
                    
                    # For each hour needed, probabilistically select a slot based on pheromones and heuristic
                    for hour in range(weekly_hours):
                        available_slots = self._get_available_slots(assignment)
                        
                        if not available_slots:
                            break  # No more slots available for this assignment
                        
                        # Calculate probabilities based on pheromones and heuristic
                        probabilities = []
                        total_prob = 0
                        
                        for day, time_slot in available_slots:
                            pheromone = self.pheromones.get((assignment.class_id, assignment.teacher_id, day, time_slot), 0.1)
                            heuristic = self._calculate_heuristic(assignment, day, time_slot)
                            
                            prob = (pheromone ** self.alpha) * (heuristic ** self.beta)
                            probabilities.append(prob)
                            total_prob += prob
                        
                        if total_prob == 0:
                            # If no pheromones or heuristics, pick randomly
                            day, time_slot = random.choice(available_slots)
                        else:
                            # Select based on probability
                            r = random.random() * total_prob
                            cumulative = 0
                            selected_slot = available_slots[0]  # default to first
                            
                            for i, (day, time_slot) in enumerate(available_slots):
                                cumulative += probabilities[i]
                                if r <= cumulative:
                                    selected_slot = (day, time_slot)
                                    break
                            
                            day, time_slot = selected_slot
                        
                        # Add to schedule
                        new_entry = {
                            "class_id": assignment.class_id,
                            "lesson_id": assignment.lesson_id,
                            "teacher_id": assignment.teacher_id,
                            "day": day,
                            "time_slot": time_slot,
                            "classroom_id": 1  # Default classroom
                        }
                        
                        schedule.append(new_entry)
                        
                        # Update internal state
                        self.class_slots[assignment.class_id].add((day, time_slot))
                        self.teacher_slots[assignment.teacher_id].add((day, time_slot))
                        
                        hours_placed += 1
        
        return schedule
    
    def _get_available_slots(self, assignment) -> List[tuple]:
        """
        Get all available slots for an assignment
        """
        available_slots = []
        
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
                    available_slots.append((day, time_slot))
        
        return available_slots
    
    def _calculate_heuristic(self, assignment, day: int, time_slot: int) -> float:
        """
        Calculate heuristic value for assigning this assignment to the given slot
        Higher values are better
        """
        # Factors that increase heuristic value:
        # 1. Teacher available at this time
        teacher_available = self.db_manager.is_teacher_available(assignment.teacher_id, day, time_slot)
        availability_bonus = 10.0 if teacher_available else 1.0
        
        # 2. Avoiding over-crowded days for the class
        class_daily_count = sum(1 for entry in self.schedule_entries 
                                if entry["class_id"] == assignment.class_id and entry["day"] == day)
        day_crowding_penalty = max(0, 1.0 / (class_daily_count + 1))
        
        # 3. Balance across the week
        class_weekly_count = sum(1 for entry in self.schedule_entries 
                                 if entry["class_id"] == assignment.class_id)
        balance_factor = max(0.1, 1.0 - (class_weekly_count / (self.days * self.time_slots * 0.8)))
        
        return availability_bonus * day_crowding_penalty * balance_factor
    
    def _get_priority_assignments(self) -> List:
        """
        Get assignments in priority order (e.g., harder to place first)
        """
        # Sort assignments by difficulty: fewer available slots = higher priority
        assignment_priorities = []
        
        for assignment in self.assignments:
            class_obj = next((c for c in self.classes if c.class_id == assignment.class_id), None)
            if class_obj:
                weekly_hours = self.db_manager.get_weekly_hours_for_lesson(assignment.lesson_id, class_obj.grade)
                
                if weekly_hours:
                    # Count how many slots are theoretically available for this assignment
                    available_slots = 0
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
                                available_slots += 1
                    
                    # Assign priority: fewer available slots = higher priority
                    priority = available_slots  # Lower number means higher priority in this context
                    assignment_priorities.append((assignment, priority, weekly_hours))
        
        # Sort by priority (ascending = fewer available slots first)
        assignment_priorities.sort(key=lambda x: x[1])
        
        return [assignment for assignment, _, _ in assignment_priorities]
    
    def _update_pheromones(self, ant_solutions: List[List[Dict[str, Any]]], ant_fitnesses: List[float]):
        """
        Update pheromone levels based on ant solutions
        """
        # Evaporate pheromones first
        for key in self.pheromones:
            self.pheromones[key] *= (1 - self.evaporation_rate)
        
        # Deposit pheromones based on solution quality
        for solution, fitness in zip(ant_solutions, ant_fitnesses):
            if fitness > 0:  # Only deposit pheromones for valid solutions
                # Calculate pheromone amount based on fitness
                pheromone_amount = self.pheromone_constant / (1 + fitness) if fitness != float('-inf') else 0.1
                
                for entry in solution:
                    key = (entry["class_id"], entry["teacher_id"], entry["day"], entry["time_slot"])
                    self.pheromones[key] += pheromone_amount
    
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