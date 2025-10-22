"""
Genetic Algorithm for Class Scheduling
Implements genetic algorithm to find optimal schedule
"""
import random
import time
from typing import List, Dict, Any
from algorithms.base_scheduler import BaseScheduler
from algorithms.monitoring import PerformanceMonitor
from utils.progress_tracker import SchedulerProgressTracker


class GeneticAlgorithmScheduler(BaseScheduler):
    """
    Genetic Algorithm-based scheduler that evolves solutions over generations
    """
    
    def __init__(self, db_manager, progress_callback=None, population_size=50, 
                 mutation_rate=0.1, crossover_rate=0.8, max_generations=100):
        super().__init__(db_manager, progress_callback)
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.max_generations = max_generations
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
        Generate schedule using genetic algorithm
        """
        print("=" * 80)
        print("GENETIC ALGORITHM SCHEDULER")
        print("=" * 80)
        print(f"Population size: {self.population_size}")
        print(f"Mutation rate: {self.mutation_rate}")
        print(f"Crossover rate: {self.crossover_rate}")
        print(f"Max generations: {self.max_generations}")
        
        start_time = time.time()
        
        # Initialize population
        population = self._initialize_population()
        
        best_solution = None
        best_fitness = float('-inf')
        
        # Evolution loop
        for generation in range(self.max_generations):
            # Evaluate fitness for all individuals
            fitness_scores = [self._calculate_fitness(individual) for individual in population]
            
            # Track best solution
            for i, fitness in enumerate(fitness_scores):
                if fitness > best_fitness:
                    best_fitness = fitness
                    best_solution = population[i].copy()
            
            # Report progress every 10 generations
            if generation % 10 == 0:
                avg_fitness = sum(fitness_scores) / len(fitness_scores)
                progress_percent = int((generation / self.max_generations) * 100)
                self._update_progress(f"GA generation {generation}/{self.max_generations}", progress_percent)
                print(f"Generation {generation}: Best fitness = {best_fitness:.2f}, Avg fitness = {avg_fitness:.2f}")
            
            # Selection (tournament selection)
            new_population = []
            for _ in range(self.population_size):
                parent1 = self._tournament_selection(population, fitness_scores)
                parent2 = self._tournament_selection(population, fitness_scores)
                
                # Crossover
                if random.random() < self.crossover_rate:
                    child = self._crossover(parent1, parent2)
                else:
                    child = parent1.copy()
                
                # Mutation
                if random.random() < self.mutation_rate:
                    child = self._mutate(child)
                
                new_population.append(child)
            
            population = new_population
        
        total_time = time.time() - start_time
        print(f"Evolution completed in {total_time:.2f} seconds")
        print(f"Best fitness: {best_fitness}")
        
        # Convert best solution to the expected format
        schedule = self._convert_solution_to_schedule(best_solution)
        self.schedule_entries = schedule
        
        return schedule
        
    def _initialize_population(self) -> List[List[Dict[str, Any]]]:
        """
        Initialize population with random schedules
        """
        population = []
        
        for _ in range(self.population_size):
            # Create a random valid schedule
            schedule = []
            
            # Try to place assignments randomly but respecting constraints
            assignments_to_place = self.assignments.copy()
            random.shuffle(assignments_to_place)
            
            for assignment in assignments_to_place:
                placed = False
                
                # Get weekly hours for this assignment
                class_obj = next((c for c in self.classes if c.class_id == assignment.class_id), None)
                if class_obj:
                    weekly_hours = self.db_manager.get_weekly_hours_for_lesson(assignment.lesson_id, class_obj.grade)
                    if weekly_hours:
                        # Try to place the required number of hours
                        hours_placed = 0
                        for hour in range(weekly_hours):
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
                                            "classroom_id": 1  # Default classroom
                                        }
                                        
                                        schedule.append(new_entry)
                                        
                                        # Update internal state temporarily
                                        self.class_slots[assignment.class_id].add((day, time_slot))
                                        self.teacher_slots[assignment.teacher_id].add((day, time_slot))
                                        
                                        hours_placed += 1
                                        placed = True
                                        break
                                
                                if hours_placed >= weekly_hours:
                                    break
                            if hours_placed >= weekly_hours:
                                break
                        
                        # Remove temporary state
                        for entry in schedule:
                            self.class_slots[entry["class_id"]].discard((entry["day"], entry["time_slot"]))
                            self.teacher_slots[entry["teacher_id"]].discard((entry["day"], entry["time_slot"]))
            
            population.append(schedule)
        
        return population
    
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
    
    def _tournament_selection(self, population: List[List[Dict[str, Any]]], 
                             fitness_scores: List[float], tournament_size: int = 3) -> List[Dict[str, Any]]:
        """
        Select an individual using tournament selection
        """
        tournament_indices = random.sample(range(len(population)), min(tournament_size, len(population)))
        tournament_fitness = [fitness_scores[i] for i in tournament_indices]
        winner_index = tournament_indices[tournament_fitness.index(max(tournament_fitness))]
        
        return population[winner_index].copy()
    
    def _crossover(self, parent1: List[Dict[str, Any]], parent2: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Perform crossover between two parents
        """
        if not parent1 or not parent2:
            return parent1.copy() if parent1 else parent2.copy() if parent2 else []
        
        # Select a random crossover point
        crossover_point = random.randint(0, min(len(parent1), len(parent2)))
        
        # Create child: first part from parent1, second part from parent2
        child = parent1[:crossover_point] + parent2[crossover_point:]
        
        # Repair the child if needed to maintain validity
        return self._repair_schedule(child)
    
    def _mutate(self, schedule: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Mutate a schedule by changing some assignments
        """
        mutated_schedule = schedule.copy()
        
        # Randomly select some entries to modify
        if len(mutated_schedule) > 0:
            num_mutations = random.randint(1, min(3, len(mutated_schedule) // 4))
            
            for _ in range(num_mutations):
                if len(mutated_schedule) == 0:
                    continue
                    
                # Randomly select an entry to modify
                idx = random.randint(0, len(mutated_schedule) - 1)
                entry_to_modify = mutated_schedule[idx]
                
                # Find a new slot for this entry
                new_day = random.randint(0, 4)
                new_slot = random.randint(0, self.time_slots - 1)
                
                can_place, _ = self._can_place_lesson(
                    entry_to_modify["class_id"],
                    entry_to_modify["teacher_id"],
                    new_day,
                    new_slot,
                    check_availability=True
                )
                
                if can_place:
                    # Update the entry to new location
                    mutated_schedule[idx]["day"] = new_day
                    mutated_schedule[idx]["time_slot"] = new_slot
        
        return mutated_schedule
    
    def _repair_schedule(self, schedule: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Repair a schedule to remove conflicts
        """
        # Rebuild state from scratch to handle conflicts
        repaired_schedule = []
        used_slots = set()
        
        for entry in schedule:
            slot_key = (entry["class_id"], entry["teacher_id"], entry["day"], entry["time_slot"])
            slot_key_check = (entry["day"], entry["time_slot"])
            
            # Check for conflicts at this slot
            has_class_conflict = slot_key_check in [(entry["day"], entry["time_slot"]) 
                                                   for e in repaired_schedule if e["class_id"] == entry["class_id"]]
            has_teacher_conflict = slot_key_check in [(entry["day"], entry["time_slot"]) 
                                                     for e in repaired_schedule if e["teacher_id"] == entry["teacher_id"]]
            
            if not has_class_conflict and not has_teacher_conflict:
                # No conflict, add to repaired schedule
                repaired_schedule.append(entry)
        
        return repaired_schedule
    
    def _convert_solution_to_schedule(self, solution: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert the genetic algorithm solution to the expected format
        """
        # Ensure we have a valid schedule with no conflicts
        return self._repair_schedule(solution)