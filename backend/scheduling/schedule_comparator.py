from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import json

from .models import Schedule, SchedulePerformance, ScheduleComparison
from .performance_logger import PerformanceLogger

@dataclass
class ComparisonResult:
    """Karşılaştırma sonucu"""
    schedule_a: Schedule
    schedule_b: Schedule
    metrics_a: Dict[str, Any]
    metrics_b: Dict[str, Any]
    comparison: ScheduleComparison
    winner: str  # 'A', 'B', veya 'tie'
    confidence: float  # 0-1 arası güven düzeyi

class ScheduleComparator:
    """Çizelge karşılaştırma aracı"""
    
    def __init__(self):
        self.comparisons: List[ComparisonResult] = []
    
    def compare_schedules(self, schedule_a: Schedule, schedule_b: Schedule) -> ComparisonResult:
        """
        İki çizelgeyi karşılaştırır ve detaylı sonuç döndürür
        """
        # Son performans metriklerini al
        perf_a = self._get_latest_performance(schedule_a)
        perf_b = self._get_latest_performance(schedule_b)
        
        # Metrikleri sözlük haline getir
        metrics_a = self._performance_to_dict(perf_a) if perf_a else {}
        metrics_b = self._performance_to_dict(perf_b) if perf_b else {}
        
        # Karşılaştırma yap
        comparison = PerformanceLogger.compare_schedules(
            schedule_a, schedule_b, metrics_a, metrics_b
        )
        
        # Kazananı belirle
        winner, confidence = self._determine_winner(comparison)
        
        # Sonuç oluştur
        result = ComparisonResult(
            schedule_a=schedule_a,
            schedule_b=schedule_b,
            metrics_a=metrics_a,
            metrics_b=metrics_b,
            comparison=comparison,
            winner=winner,
            confidence=confidence
        )
        
        self.comparisons.append(result)
        return result
    
    def _get_latest_performance(self, schedule: Schedule):
        """Çizelgenin en son performans metriklerini alır"""
        try:
            return SchedulePerformance.objects.filter(schedule=schedule).latest('created_at')
        except SchedulePerformance.DoesNotExist:
            return None
    
    def _performance_to_dict(self, performance: SchedulePerformance) -> Dict[str, Any]:
        """Performans objesini sözlüğe çevirir"""
        if not performance:
            return {}
        
        return {
            'total_conflicts': performance.total_conflicts,
            'teacher_conflicts': performance.teacher_conflicts,
            'classroom_conflicts': performance.classroom_conflicts,
            'constraint_violations': performance.constraint_violations,
            'teacher_utilization_rate': performance.teacher_utilization_rate,
            'classroom_utilization_rate': performance.classroom_utilization_rate,
            'average_teacher_satisfaction': performance.average_teacher_satisfaction,
            'average_student_satisfaction': performance.average_student_satisfaction,
            'total_cost': performance.total_cost,
            'cost_per_class': performance.cost_per_class,
            'generation_time': performance.generation_time,
            'optimization_time': performance.optimization_time,
            'fitness_score': performance.fitness_score,
            'solution_stability': performance.solution_stability
        }
    
    def _determine_winner(self, comparison: ScheduleComparison) -> tuple:
        """
        Karşılaştırmaya göre kazananı ve güven düzeyini belirler
        """
        # Basit bir yaklaşım: öğretmen ve öğrenci tercihlerinin ortalaması
        avg_a = (comparison.teacher_preference_a + comparison.student_preference_a) / 2
        avg_b = (comparison.teacher_preference_b + comparison.student_preference_b) / 2
        
        # Güven düzeyi: farkın büyüklüğü
        difference = abs(avg_a - avg_b)
        confidence = min(1.0, difference * 5)  # 0.2 fark = %100 güven
        
        if avg_a > avg_b:
            return 'A', confidence
        elif avg_b > avg_a:
            return 'B', confidence
        else:
            return 'tie', 0.0
    
    def get_detailed_comparison_report(self, result: ComparisonResult) -> Dict[str, Any]:
        """
        Detaylı karşılaştırma raporu oluşturur
        """
        report = {
            'comparison_id': result.comparison.id,
            'name': result.comparison.name,
            'date': result.comparison.compared_at.isoformat(),
            'winner': result.winner,
            'confidence': result.confidence,
            'schedules': {
                'A': {
                    'name': result.schedule_a.name,
                    'id': result.schedule_a.id
                },
                'B': {
                    'name': result.schedule_b.name,
                    'id': result.schedule_b.id
                }
            },
            'metrics_comparison': self._compare_metrics(result.metrics_a, result.metrics_b),
            'preference_analysis': {
                'teacher_preference': {
                    'A': result.comparison.teacher_preference_a,
                    'B': result.comparison.teacher_preference_b,
                    'winner': 'A' if result.comparison.teacher_preference_a > result.comparison.teacher_preference_b else 'B' if result.comparison.teacher_preference_b > result.comparison.teacher_preference_a else 'tie'
                },
                'student_preference': {
                    'A': result.comparison.student_preference_a,
                    'B': result.comparison.student_preference_b,
                    'winner': 'A' if result.comparison.student_preference_a > result.comparison.student_preference_b else 'B' if result.comparison.student_preference_b > result.comparison.student_preference_a else 'tie'
                }
            }
        }
        
        return report
    
    def _compare_metrics(self, metrics_a: Dict[str, Any], metrics_b: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Metrikleri karşılaştırır ve detaylı analiz sunar
        """
        comparison = []
        
        # Tüm metrikleri al
        all_metrics = set(metrics_a.keys()) | set(metrics_b.keys())
        
        for metric in all_metrics:
            value_a = metrics_a.get(metric, 0)
            value_b = metrics_b.get(metric, 0)
            
            # Kazananı belirle (kriter türüne göre)
            if self._is_higher_better(metric):
                winner = 'A' if value_a > value_b else 'B' if value_b > value_a else 'tie'
                difference = value_a - value_b
            else:
                winner = 'A' if value_a < value_b else 'B' if value_b < value_a else 'tie'
                difference = value_b - value_a
            
            comparison.append({
                'metric': metric,
                'A': value_a,
                'B': value_b,
                'difference': difference,
                'winner': winner,
                'is_percentage': self._is_percentage_metric(metric)
            })
        
        return comparison
    
    def _is_higher_better(self, metric_name: str) -> bool:
        """
        Metrik için yüksek değerlerin daha iyi olup olmadığını belirler
        """
        # Daha az değer daha iyi olan metrikler (maliyet, çakışma, zaman)
        lower_better_metrics = [
            'total_conflicts', 'teacher_conflicts', 'classroom_conflicts',
            'constraint_violations', 'total_cost', 'cost_per_class',
            'generation_time', 'optimization_time'
        ]
        
        return metric_name not in lower_better_metrics
    
    def _is_percentage_metric(self, metric_name: str) -> bool:
        """
        Metriğin yüzde bazlı olup olmadığını belirler
        """
        percentage_metrics = [
            'teacher_utilization_rate', 'classroom_utilization_rate',
            'average_teacher_satisfaction', 'average_student_satisfaction',
            'solution_stability'
        ]
        
        return metric_name in percentage_metrics or 'rate' in metric_name or 'satisfaction' in metric_name
    
    def get_comparison_history(self, schedule_a: Schedule = None, schedule_b: Schedule = None) -> List[Dict[str, Any]]:
        """
        Karşılaştırma geçmişini getirir
        """
        if schedule_a and schedule_b:
            comparisons = ScheduleComparison.objects.filter(
                schedule_a=schedule_a, schedule_b=schedule_b
            ).order_by('-compared_at')
        elif schedule_a:
            comparisons = ScheduleComparison.objects.filter(
                schedule_a=schedule_a
            ).order_by('-compared_at')
        elif schedule_b:
            comparisons = ScheduleComparison.objects.filter(
                schedule_b=schedule_b
            ).order_by('-compared_at')
        else:
            comparisons = ScheduleComparison.objects.all().order_by('-compared_at')
        
        history = []
        for comp in comparisons:
            history.append({
                'id': comp.id,
                'name': comp.name,
                'date': comp.compared_at.isoformat(),
                'winner_probability': comp.a_better_than_b,
                'teacher_preference': {
                    'A': comp.teacher_preference_a,
                    'B': comp.teacher_preference_b
                },
                'student_preference': {
                    'A': comp.student_preference_a,
                    'B': comp.student_preference_b
                }
            })
        
        return history
    
    def generate_comparison_visualization_data(self, result: ComparisonResult) -> Dict[str, Any]:
        """
        Karşılaştırma için görselleştirme verileri oluşturur
        """
        # Radar chart verileri
        categories = [
            'Teacher Satisfaction', 'Student Satisfaction', 
            'Conflict Count', 'Utilization Rate',
            'Cost Efficiency', 'Solution Stability'
        ]
        
        # A çizelgesi verileri
        series_a = [
            result.metrics_a.get('average_teacher_satisfaction', 0) / 100,
            result.metrics_a.get('average_student_satisfaction', 0) / 100,
            1 - min(1, result.metrics_a.get('total_conflicts', 0) / 10),  # Ters orantı
            result.metrics_a.get('teacher_utilization_rate', 0),
            1 - min(1, result.metrics_a.get('total_cost', 0) / 10000),  # Ters orantı
            result.metrics_a.get('solution_stability', 0)
        ]
        
        # B çizelgesi verileri
        series_b = [
            result.metrics_b.get('average_teacher_satisfaction', 0) / 100,
            result.metrics_b.get('average_student_satisfaction', 0) / 100,
            1 - min(1, result.metrics_b.get('total_conflicts', 0) / 10),  # Ters orantı
            result.metrics_b.get('teacher_utilization_rate', 0),
            1 - min(1, result.metrics_b.get('total_cost', 0) / 10000),  # Ters orantı
            result.metrics_b.get('solution_stability', 0)
        ]
        
        visualization_data = {
            'radar_chart': {
                'categories': categories,
                'series': [
                    {
                        'name': result.schedule_a.name,
                        'data': series_a
                    },
                    {
                        'name': result.schedule_b.name,
                        'data': series_b
                    }
                ]
            },
            'bar_charts': {
                'conflicts': {
                    'labels': ['Teacher', 'Classroom', 'Constraint'],
                    'series': [
                        {
                            'name': result.schedule_a.name,
                            'data': [
                                result.metrics_a.get('teacher_conflicts', 0),
                                result.metrics_a.get('classroom_conflicts', 0),
                                result.metrics_a.get('constraint_violations', 0)
                            ]
                        },
                        {
                            'name': result.schedule_b.name,
                            'data': [
                                result.metrics_b.get('teacher_conflicts', 0),
                                result.metrics_b.get('classroom_conflicts', 0),
                                result.metrics_b.get('constraint_violations', 0)
                            ]
                        }
                    ]
                },
                'satisfaction': {
                    'labels': ['Teacher', 'Student'],
                    'series': [
                        {
                            'name': result.schedule_a.name,
                            'data': [
                                result.metrics_a.get('average_teacher_satisfaction', 0),
                                result.metrics_a.get('average_student_satisfaction', 0)
                            ]
                        },
                        {
                            'name': result.schedule_b.name,
                            'data': [
                                result.metrics_b.get('average_teacher_satisfaction', 0),
                                result.metrics_b.get('average_student_satisfaction', 0)
                            ]
                        }
                    ]
                }
            }
        }
        
        return visualization_data