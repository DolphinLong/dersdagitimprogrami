from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import statistics

from .models import MLTrainingData, SchedulePerformance
from .genetic_algorithm import GeneticScheduler
from .multi_criteria_decision import MultiCriteriaDecision
from .performance_logger import PerformanceLogger

@dataclass
class LearningPattern:
    """Öğrenme deseni"""
    pattern_id: str
    description: str
    trigger_conditions: Dict[str, Any]
    actions: List[str]
    effectiveness: float = 0.0  # 0-1 arası etkinlik
    last_applied: Optional[datetime] = None
    application_count: int = 0

@dataclass
class SystemImprovement:
    """Sistem iyileştirme önerisi"""
    id: str
    title: str
    description: str
    priority: int  # 1-10 arası öncelik
    estimated_impact: float  # 0-1 arası tahmini etki
    implementation_cost: float  # Tahmini uygulama maliyeti
    confidence: float  # 0-1 arası öneri güveni

class AdaptiveLearningEngine:
    """Adaptive learning motoru - sistem kendini geliştirme"""
    
    def __init__(self):
        self.learning_patterns: List[LearningPattern] = []
        self.improvements: List[SystemImprovement] = []
        self.performance_history: List[Dict[str, Any]] = []
        self.initialized = False
        
    def initialize(self):
        """Motoru başlatır ve temel öğrenme desenlerini yükler"""
        if self.initialized:
            return
            
        # Temel öğrenme desenlerini yükle
        self._load_base_patterns()
        self.initialized = True
    
    def _load_base_patterns(self):
        """Temel öğrenme desenlerini yükler"""
        patterns = [
            LearningPattern(
                pattern_id="high_conflict_reduction",
                description="Yüksek çakışma sayısını azaltma stratejisi",
                trigger_conditions={
                    "conflict_threshold": 5,
                    "conflict_trend": "increasing"
                },
                actions=[
                    "increase_mutation_rate",
                    "adjust_crossover_rate",
                    "add_constraint_weight"
                ]
            ),
            LearningPattern(
                pattern_id="low_satisfaction_improvement",
                description="Düşük memnuniyet skorlarını iyileştirme",
                trigger_conditions={
                    "satisfaction_threshold": 70,
                    "satisfaction_trend": "decreasing"
                },
                actions=[
                    "adjust_teacher_preferences",
                    "modify_time_slot_weights",
                    "increase_elitism_rate"
                ]
            ),
            LearningPattern(
                pattern_id="performance_optimization",
                description="Performans optimizasyonu",
                trigger_conditions={
                    "generation_time_threshold": 300,  # 5 dakika
                    "optimization_time_trend": "increasing"
                },
                actions=[
                    "reduce_population_size",
                    "optimize_crossover_points",
                    "cache_frequent_calculations"
                ]
            )
        ]
        
        self.learning_patterns.extend(patterns)
    
    def analyze_performance_trends(self, schedule_id: int = None) -> Dict[str, Any]:
        """
        Performans trendlerini analiz eder
        """
        if schedule_id:
            performances = SchedulePerformance.objects.filter(
                schedule_id=schedule_id
            ).order_by('created_at')
        else:
            performances = SchedulePerformance.objects.all().order_by('created_at')
        
        if not performances.exists():
            return {}
        
        # Trend analizi
        performance_list = list(performances)
        latest = performance_list[-1]
        
        # Önceki performans (varsa)
        previous = performance_list[-2] if len(performance_list) > 1 else None
        
        trends = {
            'latest': {
                'conflicts': latest.total_conflicts,
                'teacher_satisfaction': latest.average_teacher_satisfaction,
                'student_satisfaction': latest.average_student_satisfaction,
                'generation_time': latest.generation_time,
                'optimization_time': latest.optimization_time,
                'fitness_score': latest.fitness_score
            },
            'trends': {}
        }
        
        if previous:
            trends['trends'] = {
                'conflict_change': latest.total_conflicts - previous.total_conflicts,
                'satisfaction_change': latest.average_teacher_satisfaction - previous.average_teacher_satisfaction,
                'generation_time_change': latest.generation_time - previous.generation_time,
                'optimization_time_change': latest.optimization_time - previous.optimization_time,
                'fitness_change': latest.fitness_score - previous.fitness_score
            }
            
            # Trend yönlerini belirle
            for key, value in trends['trends'].items():
                if 'change' in key:
                    metric_name = key.replace('_change', '')
                    if value > 0:
                        trends['trends'][f'{metric_name}_trend'] = 'increasing'
                    elif value < 0:
                        trends['trends'][f'{metric_name}_trend'] = 'decreasing'
                    else:
                        trends['trends'][f'{metric_name}_trend'] = 'stable'
        
        return trends
    
    def detect_patterns(self, trends: Dict[str, Any]) -> List[LearningPattern]:
        """
        Performans trendlerine göre öğrenme desenlerini tespit eder
        """
        detected_patterns = []
        
        latest_metrics = trends.get('latest', {})
        trend_metrics = trends.get('trends', {})
        
        for pattern in self.learning_patterns:
            # Desen koşullarını kontrol et
            match = True
            for condition, value in pattern.trigger_conditions.items():
                if condition == "conflict_threshold":
                    if latest_metrics.get('conflicts', 0) < value:
                        match = False
                        break
                elif condition == "satisfaction_threshold":
                    if latest_metrics.get('teacher_satisfaction', 100) > value:
                        match = False
                        break
                elif condition.endswith("_trend"):
                    metric_name = condition.replace("_trend", "")
                    if trend_metrics.get(condition) != value:
                        match = False
                        break
            
            if match:
                detected_patterns.append(pattern)
        
        return detected_patterns
    
    def apply_learning_patterns(self, patterns: List[LearningPattern]) -> List[str]:
        """
        Öğrenme desenlerini uygular
        """
        applied_actions = []
        
        for pattern in patterns:
            # Desenin uygulandığını işaretle
            pattern.last_applied = datetime.now()
            pattern.application_count += 1
            
            # Eylemleri uygula
            for action in pattern.actions:
                applied_actions.append(f"{pattern.pattern_id}: {action}")
                
                # Eyleme göre sistem parametrelerini ayarla
                self._adjust_system_parameters(action)
        
        return applied_actions
    
    def _adjust_system_parameters(self, action: str):
        """
        Sistem parametrelerini ayarlar
        """
        # Bu metodda genetik algoritma ve diğer sistem parametreleri
        # otomatik olarak ayarlanabilir
        # Şimdilik sadece loglama yapıyoruz
        print(f"Sistem parametresi ayarlandı: {action}")
    
    def generate_improvement_suggestions(self, trends: Dict[str, Any]) -> List[SystemImprovement]:
        """
        İyileştirme önerileri üretir
        """
        suggestions = []
        
        latest = trends.get('latest', {})
        trend_changes = trends.get('trends', {})
        
        # Çakışma sayısına göre öneri
        if latest.get('conflicts', 0) > 3:
            suggestions.append(SystemImprovement(
                id="reduce_conflicts",
                title="Çakışma Sayısını Azalt",
                description="Yüksek çakışma sayısı tespit edildi. Kısıtlama ağırlıklarını artırarak çakışmaları azaltın.",
                priority=8,
                estimated_impact=0.3,
                implementation_cost=2.0,
                confidence=0.8
            ))
        
        # Memnuniyet skoruna göre öneri
        teacher_satisfaction = latest.get('teacher_satisfaction', 100)
        if teacher_satisfaction < 75:
            suggestions.append(SystemImprovement(
                id="improve_satisfaction",
                title="Memnuniyet Skorunu Artır",
                description="Öğretmen memnuniyet skoru düşük. Zaman tercihlerini daha çok dikkate alın.",
                priority=9,
                estimated_impact=0.25,
                implementation_cost=3.0,
                confidence=0.75
            ))
        
        # Performans süresine göre öneri
        generation_time = latest.get('generation_time', 0)
        if generation_time > 300:  # 5 dakika
            suggestions.append(SystemImprovement(
                id="optimize_performance",
                title="Performansı Optimize Et",
                description="Çizelge oluşturma süresi uzun. Algoritma parametrelerini optimize edin.",
                priority=7,
                estimated_impact=0.2,
                implementation_cost=4.0,
                confidence=0.7
            ))
        
        # Fitness skoruna göre öneri
        fitness_score = latest.get('fitness_score', 0)
        if fitness_score < 80:
            suggestions.append(SystemImprovement(
                id="improve_solution_quality",
                title="Çözüm Kalitesini Artır",
                description="Çözüm kalitesi düşük. Seçim ve çaprazlama stratejilerini gözden geçirin.",
                priority=6,
                estimated_impact=0.35,
                implementation_cost=5.0,
                confidence=0.85
            ))
        
        self.improvements.extend(suggestions)
        return suggestions
    
    def learn_from_ml_data(self):
        """
        ML eğitim verilerinden öğren
        """
        # En son ML eğitim verilerini al
        recent_training_data = MLTrainingData.objects.order_by('-trained_at')[:10]
        
        if not recent_training_data:
            return
        
        # Performans metriklerini analiz et
        solution_times = [data.optimal_solution_time for data in recent_training_data]
        solution_qualities = [data.solution_quality for data in recent_training_data]
        
        # Ortalama değerleri hesapla
        avg_solution_time = statistics.mean(solution_times) if solution_times else 0
        avg_solution_quality = statistics.mean(solution_qualities) if solution_qualities else 0
        
        # Öğrenme deseni oluştur
        if avg_solution_time > 300:  # 5 dakika
            pattern = LearningPattern(
                pattern_id="ml_performance_optimization",
                description="ML verilerine göre performans optimizasyonu",
                trigger_conditions={
                    "avg_solution_time": avg_solution_time
                },
                actions=[
                    "adjust_ml_model_parameters",
                    "optimize_feature_selection"
                ],
                effectiveness=0.7
            )
            
            self.learning_patterns.append(pattern)
    
    def get_system_health_report(self) -> Dict[str, Any]:
        """
        Sistem sağlık raporu oluşturur
        """
        trends = self.analyze_performance_trends()
        latest = trends.get('latest', {})
        
        # Sistem sağlık puanı hesapla
        health_score = 0
        max_score = 100
        
        # Çakışma skoru (0-25 puan)
        conflicts = latest.get('conflicts', 0)
        conflict_score = max(0, 25 - (conflicts * 5))
        
        # Memnuniyet skoru (0-35 puan)
        satisfaction = latest.get('teacher_satisfaction', 100)
        satisfaction_score = (satisfaction / 100) * 35
        
        # Performans skoru (0-20 puan)
        generation_time = latest.get('generation_time', 0)
        performance_score = max(0, 20 - (generation_time / 30))  # 30 saniyeye kadar tam puan
        
        # Fitness skoru (0-20 puan)
        fitness = latest.get('fitness_score', 0)
        fitness_score = (fitness / 100) * 20
        
        health_score = conflict_score + satisfaction_score + performance_score + fitness_score
        
        report = {
            'health_score': health_score,
            'max_score': max_score,
            'status': self._get_health_status(health_score),
            'metrics': {
                'conflicts': {
                    'value': conflicts,
                    'score': conflict_score,
                    'max_score': 25
                },
                'satisfaction': {
                    'value': satisfaction,
                    'score': satisfaction_score,
                    'max_score': 35
                },
                'performance': {
                    'value': generation_time,
                    'score': performance_score,
                    'max_score': 20
                },
                'fitness': {
                    'value': fitness,
                    'score': fitness_score,
                    'max_score': 20
                }
            },
            'recommendations': self.improvements[:5]  # İlk 5 öneri
        }
        
        return report
    
    def _get_health_status(self, score: float) -> str:
        """
        Sağlık skoruna göre durum mesajı döndürür
        """
        if score >= 90:
            return "Excellent"
        elif score >= 75:
            return "Good"
        elif score >= 60:
            return "Fair"
        elif score >= 40:
            return "Poor"
        else:
            return "Critical"
    
    def auto_improve(self) -> Dict[str, Any]:
        """
        Otomatik iyileştirme işlemi
        """
        # Performans trendlerini analiz et
        trends = self.analyze_performance_trends()
        
        # Öğrenme desenlerini tespit et
        patterns = self.detect_patterns(trends)
        
        # Desenleri uygula
        actions = self.apply_learning_patterns(patterns)
        
        # İyileştirme önerileri üret
        suggestions = self.generate_improvement_suggestions(trends)
        
        # ML verilerinden öğren
        self.learn_from_ml_data()
        
        return {
            'patterns_detected': len(patterns),
            'actions_applied': actions,
            'suggestions_generated': len(suggestions),
            'ml_learning_applied': True
        }