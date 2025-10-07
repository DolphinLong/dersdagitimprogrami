from .models import Schedule, SchedulePerformance, TeacherFeedback, MLTrainingData, ScheduleComparison

class PerformanceLogger:
    """Performans metriklerini ölçme ve kaydetme sistemi"""
    
    @staticmethod
    def log_schedule_performance(schedule, metrics):
        """Çizelge performans metriklerini kaydeder"""
        performance = SchedulePerformance.objects.create(
            schedule=schedule,
            total_conflicts=metrics.get('total_conflicts', 0),
            teacher_conflicts=metrics.get('teacher_conflicts', 0),
            classroom_conflicts=metrics.get('classroom_conflicts', 0),
            constraint_violations=metrics.get('constraint_violations', 0),
            teacher_utilization_rate=metrics.get('teacher_utilization_rate', 0.0),
            classroom_utilization_rate=metrics.get('classroom_utilization_rate', 0.0),
            average_teacher_satisfaction=metrics.get('average_teacher_satisfaction', 0.0),
            average_student_satisfaction=metrics.get('average_student_satisfaction', 0.0),
            total_cost=metrics.get('total_cost', 0.0),
            cost_per_class=metrics.get('cost_per_class', 0.0),
            generation_time=metrics.get('generation_time', 0.0),
            optimization_time=metrics.get('optimization_time', 0.0),
            fitness_score=metrics.get('fitness_score', 0.0),
            solution_stability=metrics.get('solution_stability', 0.0)
        )
        return performance
    
    @staticmethod
    def log_teacher_feedback(teacher, schedule, feedback_data):
        """Öğretmen geri bildirimini kaydeder"""
        feedback, created = TeacherFeedback.objects.update_or_create(
            teacher=teacher,
            schedule=schedule,
            defaults={
                'satisfaction_score': feedback_data.get('satisfaction_score', 5),
                'schedule_clarity': feedback_data.get('schedule_clarity', 5),
                'time_preference_match': feedback_data.get('time_preference_match', 5),
                'workload_balance': feedback_data.get('workload_balance', 5),
                'comments': feedback_data.get('comments', ''),
                'suggestions': feedback_data.get('suggestions', '')
            }
        )
        return feedback
    
    @staticmethod
    def log_ml_training_data(features, target, algorithm):
        """ML eğitim verisini kaydeder"""
        training_data = MLTrainingData.objects.create(
            total_teachers=features.get('total_teachers', 0),
            total_classrooms=features.get('total_classrooms', 0),
            total_courses=features.get('total_courses', 0),
            total_time_slots=features.get('total_time_slots', 0),
            hard_constraints_count=features.get('hard_constraints_count', 0),
            soft_constraints_count=features.get('soft_constraints_count', 0),
            previous_conflict_rate=features.get('previous_conflict_rate', 0.0),
            previous_satisfaction_score=features.get('previous_satisfaction_score', 0.0),
            optimal_solution_time=target.get('optimal_solution_time', 0.0),
            solution_quality=target.get('solution_quality', 0.0),
            algorithm_used=algorithm
        )
        return training_data
    
    @staticmethod
    def get_performance_trends(schedule, days=30):
        """Çizelge performans trendlerini getirir"""
        from django.utils import timezone
        from datetime import timedelta
        
        start_date = timezone.now() - timedelta(days=days)
        performances = SchedulePerformance.objects.filter(
            schedule=schedule,
            created_at__gte=start_date
        ).order_by('created_at')
        
        return performances
    
    @staticmethod
    def compare_schedules(schedule_a, schedule_b, metrics_a, metrics_b):
        """İki çizelgeyi karşılaştırır"""
        # Temel karşılaştırma metrikleri
        teacher_pref_a = metrics_a.get('average_teacher_satisfaction', 0) / 100
        teacher_pref_b = metrics_b.get('average_teacher_satisfaction', 0) / 100
        
        student_pref_a = metrics_a.get('average_student_satisfaction', 0) / 100
        student_pref_b = metrics_b.get('average_student_satisfaction', 0) / 100
        
        # A'nın B'den daha iyi olma olasılığı (basit bir hesaplama)
        a_better = (teacher_pref_a + student_pref_a) / 2
        b_better = (teacher_pref_b + student_pref_b) / 2
        
        comparison = ScheduleComparison.objects.create(
            name=f"{schedule_a.name} vs {schedule_b.name}",
            schedule_a=schedule_a,
            schedule_b=schedule_b,
            a_better_than_b=a_better,
            teacher_preference_a=teacher_pref_a,
            teacher_preference_b=teacher_pref_b,
            student_preference_a=student_pref_a,
            student_preference_b=student_pref_b
        )
        
        return comparison