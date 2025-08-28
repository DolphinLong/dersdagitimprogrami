import random
import copy
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import date, timedelta
import numpy as np

from .models import Schedule, ScheduleItem, Teacher, Classroom, Course, TimeSlot
from .algorithms import SchedulingAlgorithm
from .conflict_matrix import ConflictMatrix

@dataclass
class Individual:
    """Genetik algoritma bireyi - bir çizelge çözümü"""
    schedule: Schedule
    items: List[ScheduleItem]
    fitness: float = 0.0
    conflicts: List[Dict] = None
    
    def __post_init__(self):
        if self.conflicts is None:
            self.conflicts = []

class GeneticScheduler:
    """Genetik algoritma tabanlı çizelgeleme sistemi"""
    
    def __init__(self, schedule: Schedule, population_size: int = 50, generations: int = 100):
        self.schedule = schedule
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = 0.1
        self.crossover_rate = 0.8
        self.elitism_rate = 0.1
        
        # Kısıtlar
        self.algorithm = SchedulingAlgorithm(schedule)
        
    def create_initial_population(self) -> List[Individual]:
        """Başlangıç popülasyonunu oluşturur"""
        population = []
        
        for _ in range(self.population_size):
            # Rastgele bir çizelge çözümü oluştur
            individual = self._create_random_individual()
            population.append(individual)
            
        return population
    
    def _create_random_individual(self) -> Individual:
        """Rastgele bir birey (çizelge çözümü) oluşturur"""
        # Mevcut çizelge öğelerini al
        existing_items = list(ScheduleItem.objects.filter(schedule=self.schedule))
        
        # Çakışma matrisini oluştur
        conflict_matrix = ConflictMatrix(self.schedule)
        conflict_matrix.build_conflict_matrix()
        
        # Birey oluştur
        individual = Individual(
            schedule=self.schedule,
            items=existing_items,
            conflicts=conflict_matrix.conflicts
        )
        
        # Fitness değerini hesapla
        individual.fitness = self._calculate_fitness(individual)
        
        return individual
    
    def _calculate_fitness(self, individual: Individual) -> float:
        """Bireyin fitness değerini hesaplar"""
        # Çakışma sayısına göre fitness hesapla (daha az çakışma = daha iyi fitness)
        conflict_count = len(individual.conflicts)
        
        # Kısıtlama ihlallerini say
        constraint_violations = len([
            c for c in individual.conflicts if c['type'] == 'constraint_violation'
        ])
        
        # Öğretmen tercihlerini ihlal sayısını hesapla
        preference_violations = len([
            c for c in individual.conflicts if c['type'] == 'preference_violation'
        ])
        
        # Toplam ceza puanı
        penalty = (
            conflict_count * 10 +  # Çakışmalar için yüksek ceza
            constraint_violations * 5 +  # Kısıtlama ihlalleri için orta ceza
            preference_violations * 2  # Tercih ihlalleri için düşük ceza
        )
        
        # Fitness değeri (0-100 arası), daha az ceza = daha yüksek fitness
        fitness = max(0, 100 - penalty)
        
        return fitness
    
    def selection(self, population: List[Individual]) -> List[Individual]:
        """Turnuva seçimi ile ebeveynleri seçer"""
        selected = []
        tournament_size = 3
        
        for _ in range(len(population)):
            # Rastgele bireyler seç
            tournament = random.sample(population, min(tournament_size, len(population)))
            # En iyi bireyi seç
            winner = max(tournament, key=lambda x: x.fitness)
            selected.append(copy.deepcopy(winner))
            
        return selected
    
    def crossover(self, parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        """Çaprazlama işlemi"""
        if random.random() > self.crossover_rate:
            return copy.deepcopy(parent1), copy.deepcopy(parent2)
        
        # Tek noktalı çaprazlama
        child1_items = []
        child2_items = []
        
        # Çaprazlama noktası
        crossover_point = random.randint(0, len(parent1.items))
        
        # İlk kısmı birinci ebeveynden, ikinci kısmı ikinci ebeveynden al
        child1_items.extend(parent1.items[:crossover_point])
        child1_items.extend(parent2.items[crossover_point:])
        
        # Tersi için
        child2_items.extend(parent2.items[:crossover_point])
        child2_items.extend(parent1.items[crossover_point:])
        
        # Çocuk bireyleri oluştur
        child1 = Individual(
            schedule=self.schedule,
            items=child1_items,
            conflicts=self._resolve_conflicts(child1_items)
        )
        child1.fitness = self._calculate_fitness(child1)
        
        child2 = Individual(
            schedule=self.schedule,
            items=child2_items,
            conflicts=self._resolve_conflicts(child2_items)
        )
        child2.fitness = self._calculate_fitness(child2)
        
        return child1, child2
    
    def _resolve_conflicts(self, items: List[ScheduleItem]) -> List[Dict]:
        """Çakışmaları çözer"""
        # Bu metod daha karmaşık çakışma çözme algoritmaları için yer tutucudur
        # Şimdilik sadece mevcut çakışmaları döndürüyoruz
        conflict_matrix = ConflictMatrix(self.schedule)
        conflict_matrix.build_conflict_matrix()
        return conflict_matrix.conflicts
    
    def mutate(self, individual: Individual) -> Individual:
        """Mutasyon işlemi"""
        if random.random() > self.mutation_rate:
            return individual
        
        # Rastgele bir ders öğesini seç
        if not individual.items:
            return individual
            
        item_index = random.randint(0, len(individual.items) - 1)
        item = individual.items[item_index]
        
        # Mutasyon türlerini belirle
        mutation_type = random.choice(['teacher', 'classroom', 'time_slot'])
        
        if mutation_type == 'teacher':
            # Alternatif öğretmen bul
            alternative_teacher = self._find_alternative_teacher(item.teacher, item.course)
            if alternative_teacher:
                item.teacher = alternative_teacher
                
        elif mutation_type == 'classroom':
            # Alternatif sınıf bul
            alternative_classroom = self._find_alternative_classroom(item.classroom)
            if alternative_classroom:
                item.classroom = alternative_classroom
                
        elif mutation_type == 'time_slot':
            # Alternatif zaman dilimi bul
            alternative_time_slot = self._find_alternative_time_slot(item.time_slot, item.teacher, item.classroom)
            if alternative_time_slot:
                item.time_slot = alternative_time_slot
        
        # Çakışmaları güncelle
        individual.conflicts = self._resolve_conflicts(individual.items)
        individual.fitness = self._calculate_fitness(individual)
        
        return individual
    
    def _find_alternative_teacher(self, current_teacher: Teacher, course: Course) -> Optional[Teacher]:
        """Alternatif öğretmen bulur"""
        # Dersi verebilecek diğer öğretmenler
        eligible_teachers = list(course.eligible_teachers.exclude(id=current_teacher.id))
        
        if not eligible_teachers:
            return None
            
        # Rastgele bir öğretmen seç
        return random.choice(eligible_teachers)
    
    def _find_alternative_classroom(self, current_classroom: Classroom) -> Optional[Classroom]:
        """Alternatif sınıf bulur"""
        # Aynı özelliklere sahip sınıflar
        suitable_classrooms = list(Classroom.objects.filter(
            has_projector=current_classroom.has_projector,
            has_computer=current_classroom.has_computer,
            has_smart_board=current_classroom.has_smart_board,
            is_lab=current_classroom.is_lab
        ).exclude(id=current_classroom.id))
        
        if not suitable_classrooms:
            return None
            
        # Rastgele bir sınıf seç
        return random.choice(suitable_classrooms)
    
    def _find_alternative_time_slot(self, current_time_slot: TimeSlot, teacher: Teacher, classroom: Classroom) -> Optional[TimeSlot]:
        """Alternatif zaman dilimi bulur"""
        # Aynı günün diğer zaman dilimleri
        same_day_slots = list(TimeSlot.objects.filter(
            day=current_time_slot.day
        ).exclude(id=current_time_slot.id))
        
        if not same_day_slots:
            return None
            
        # Rastgele bir zaman dilimi seç
        return random.choice(same_day_slots)
    
    def evolve(self) -> Individual:
        """Genetik algoritma ile en iyi çözümü bulur"""
        # Başlangıç popülasyonunu oluştur
        population = self.create_initial_population()
        
        best_individual = None
        best_fitness = -1
        
        for generation in range(self.generations):
            # Fitness değerlerine göre sırala
            population.sort(key=lambda x: x.fitness, reverse=True)
            
            # En iyi bireyi takip et
            current_best = population[0]
            if current_best.fitness > best_fitness:
                best_fitness = current_best.fitness
                best_individual = copy.deepcopy(current_best)
            
            print(f"Nesil {generation + 1}: En iyi fitness = {current_best.fitness:.2f}")
            
            # Yeni nesil oluştur
            new_population = []
            
            # Elitizm - en iyi bireyleri doğrudan yeni nesle aktar
            elitism_count = int(self.population_size * self.elitism_rate)
            new_population.extend(copy.deepcopy(population[:elitism_count]))
            
            # Seçim, çaprazlama ve mutasyon
            selected = self.selection(population)
            
            while len(new_population) < self.population_size:
                # Rastgele iki ebeveyn seç
                parent1, parent2 = random.sample(selected, 2)
                
                # Çaprazlama
                child1, child2 = self.crossover(parent1, parent2)
                
                # Mutasyon
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)
                
                # Yeni nesle ekle
                new_population.append(child1)
                if len(new_population) < self.population_size:
                    new_population.append(child2)
            
            # Popülasyonu güncelle
            population = new_population[:self.population_size]
        
        return best_individual
    
    def get_optimization_report(self, best_individual: Individual) -> Dict:
        """Optimizasyon raporu oluşturur"""
        report = {
            'fitness': best_individual.fitness,
            'conflict_count': len(best_individual.conflicts),
            'constraint_violations': len([
                c for c in best_individual.conflicts if c['type'] == 'constraint_violation'
            ]),
            'items_count': len(best_individual.items),
            'improvement': self._calculate_improvement(best_individual)
        }
        
        return report
    
    def _calculate_improvement(self, best_individual: Individual) -> float:
        """İyileşme oranını hesaplar"""
        # Başlangıç popülasyonunun ortalama fitness değeri
        initial_population = self.create_initial_population()
        initial_fitness = sum(ind.fitness for ind in initial_population) / len(initial_population)
        
        # İyileşme oranı
        if initial_fitness > 0:
            improvement = ((best_individual.fitness - initial_fitness) / initial_fitness) * 100
        else:
            improvement = 0
            
        return improvement