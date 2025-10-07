from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Teacher(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Müsaitlik tercihleri
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7
    
    DAY_CHOICES = [
        (MONDAY, 'Pazartesi'),
        (TUESDAY, 'Salı'),
        (WEDNESDAY, 'Çarşamba'),
        (THURSDAY, 'Perşembe'),
        (FRIDAY, 'Cuma'),
        (SATURDAY, 'Cumartesi'),
        (SUNDAY, 'Pazar'),
    ]
    
    # Her öğretmenin müsait olduğu günleri ve saat aralıklarını tutacağız
    available_days = models.ManyToManyField('TimeSlot', related_name='available_teachers', blank=True)
    
    # Ders veremeyeceği günler ve saatler
    unavailable_slots = models.ManyToManyField('TimeSlot', related_name='unavailable_teachers', blank=True)
    
    # Öğretmenin verebileceği ders sayısı
    max_daily_hours = models.IntegerField(default=8, validators=[MinValueValidator(1), MaxValueValidator(12)])
    max_weekly_hours = models.IntegerField(default=40, validators=[MinValueValidator(1), MaxValueValidator(60)])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Classroom(models.Model):
    name = models.CharField(max_length=100)
    capacity = models.IntegerField(validators=[MinValueValidator(1)])
    location = models.CharField(max_length=200, blank=True)
    
    # Sınıf özellikleri
    has_projector = models.BooleanField(default=False)
    has_computer = models.BooleanField(default=False)
    has_smart_board = models.BooleanField(default=False)
    is_lab = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Ders süresi (kaç saat)
    duration_hours = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(8)])
    
    # Dersin gerektirdiği özellikler
    requires_projector = models.BooleanField(default=False)
    requires_computer = models.BooleanField(default=False)
    requires_smart_board = models.BooleanField(default=False)
    is_lab_course = models.BooleanField(default=False)
    
    # Dersi verebilecek öğretmenler
    eligible_teachers = models.ManyToManyField(Teacher, related_name='eligible_courses', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class TimeSlot(models.Model):
    # Günler
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7
    
    DAY_CHOICES = [
        (MONDAY, 'Pazartesi'),
        (TUESDAY, 'Salı'),
        (WEDNESDAY, 'Çarşamba'),
        (THURSDAY, 'Perşembe'),
        (FRIDAY, 'Cuma'),
        (SATURDAY, 'Cumartesi'),
        (SUNDAY, 'Pazar'),
    ]
    
    day = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    class Meta:
        ordering = ['day', 'start_time']
        unique_together = ['day', 'start_time', 'end_time']
    
    def __str__(self):
        return f"{self.get_day_display()} {self.start_time}-{self.end_time}"

class Constraint(models.Model):
    # Kısıtlama türleri
    HARD = 'hard'
    SOFT = 'soft'
    
    CONSTRAINT_TYPE_CHOICES = [
        (HARD, 'Zorunlu'),
        (SOFT, 'Tercihli'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    constraint_type = models.CharField(max_length=10, choices=CONSTRAINT_TYPE_CHOICES, default=HARD)
    
    # Kısıtlamanın uygulanacağı öğretmenler (boşsa tüm öğretmenler için geçerli)
    teachers = models.ManyToManyField(Teacher, related_name='constraints', blank=True)
    
    # Kısıtlamanın uygulanacağı sınıflar (boşsa tüm sınıflar için geçerli)
    classrooms = models.ManyToManyField(Classroom, related_name='constraints', blank=True)
    
    # Kısıtlamanın uygulanacağı dersler (boşsa tüm dersler için geçerli)
    courses = models.ManyToManyField(Course, related_name='constraints', blank=True)
    
    # Zaman bazlı kısıtlamalar
    # Belirli zaman dilimlerinde uygulanacaksa
    time_slots = models.ManyToManyField(TimeSlot, related_name='constraints', blank=True)
    
    # Haftanın belirli günlerinde uygulanacaksa
    days = models.JSONField(default=list, blank=True, help_text="Haftanın günleri [1-7] şeklinde liste")
    
    # Belirli bir süre boyunca uygulanacaksa
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Schedule(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    
    # Çizelgenin kapsadığı tarih aralığı
    start_date = models.DateField()
    end_date = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class ScheduleItem(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='items')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    
    date = models.DateField()
    
    # Dersin özel notları
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['schedule', 'teacher', 'time_slot', 'date']
        ordering = ['date', 'time_slot__start_time']
    
    def __str__(self):
        return f"{self.schedule.name} - {self.course.code} - {self.teacher} - {self.classroom}"

class BackupSchedule(models.Model):
    """Yedek plan modeli"""
    name = models.CharField(max_length=100)
    primary_schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='backup_schedules')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} (Yedek for {self.primary_schedule.name})"

class ScheduleAlternative(models.Model):
    """Alternatif çözüm modeli"""
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='alternatives')
    backup_schedule = models.ForeignKey(BackupSchedule, on_delete=models.CASCADE, related_name='alternatives')
    
    # Değişen öğeler
    original_item = models.ForeignKey(ScheduleItem, on_delete=models.CASCADE, related_name='alternatives')
    alternative_teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True)
    alternative_classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, null=True, blank=True)
    alternative_time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, null=True, blank=True)
    
    # Alternatifin neden önerildiği
    reason = models.TextField()
    priority = models.IntegerField(default=1)  # 1=en düşük, 10=en yüksek
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Alternative for {self.original_item} in {self.schedule.name}"

class SchedulePerformance(models.Model):
    """Çizelge performans metrikleri"""
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='performances')
    
    # Temel metrikler
    total_conflicts = models.IntegerField(default=0)
    teacher_conflicts = models.IntegerField(default=0)
    classroom_conflicts = models.IntegerField(default=0)
    constraint_violations = models.IntegerField(default=0)
    
    # Verimlilik metrikleri
    teacher_utilization_rate = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Öğretmen kullanım oranı (0-1)"
    )
    classroom_utilization_rate = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Sınıf kullanım oranı (0-1)"
    )
    
    # Memnuniyet metrikleri
    average_teacher_satisfaction = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Ortalama öğretmen memnuniyeti (0-100)"
    )
    average_student_satisfaction = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Ortalama öğrenci memnuniyeti (0-100)"
    )
    
    # Maliyet metrikleri
    total_cost = models.FloatField(default=0.0, help_text="Toplam maliyet")
    cost_per_class = models.FloatField(default=0.0, help_text="Ders başına ortalama maliyet")
    
    # Zaman metrikleri
    generation_time = models.FloatField(default=0.0, help_text="Çizelge oluşturma süresi (saniye)")
    optimization_time = models.FloatField(default=0.0, help_text="Optimizasyon süresi (saniye)")
    
    # Çözüm kalitesi
    fitness_score = models.FloatField(default=0.0, help_text="Genetik algoritma fitness skoru")
    solution_stability = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Çözüm kararlılığı (0-1)"
    )
    
    # Tarihler
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.schedule.name} - Performans ({self.created_at.strftime('%Y-%m-%d')})"

class TeacherFeedback(models.Model):
    """Öğretmen geri bildirimleri"""
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='feedbacks')
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='teacher_feedbacks')
    
    # Memnuniyet seviyesi
    satisfaction_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Memnuniyet puanı (1-10)"
    )
    
    # Spesifik geri bildirim alanları
    schedule_clarity = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Çizelge açıklığı (1-10)"
    )
    time_preference_match = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Zaman tercihleri uyumu (1-10)"
    )
    workload_balance = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="İş yükü dengesi (1-10)"
    )
    
    # Açık geri bildirim
    comments = models.TextField(blank=True, help_text="Açık geri bildirim")
    suggestions = models.TextField(blank=True, help_text="Öneriler")
    
    # Tarihler
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['teacher', 'schedule']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.teacher} - {self.schedule.name} Geri Bildirimi"

class ScheduleComparison(models.Model):
    """Çizelge karşılaştırma verileri"""
    name = models.CharField(max_length=100, help_text="Karşılaştırma adı")
    
    # Karşılaştırılan çizelgeler
    schedule_a = models.ForeignKey(
        Schedule, 
        on_delete=models.CASCADE, 
        related_name='comparison_as_a'
    )
    schedule_b = models.ForeignKey(
        Schedule, 
        on_delete=models.CASCADE, 
        related_name='comparison_as_b'
    )
    
    # Karşılaştırma metrikleri
    a_better_than_b = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="A'nın B'den daha iyi olma olasılığı (0-1)"
    )
    
    # Detaylı karşılaştırma alanları
    teacher_preference_a = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Öğretmenlerin A'yı tercih etme oranı"
    )
    teacher_preference_b = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Öğretmenlerin B'yi tercih etme oranı"
    )
    
    student_preference_a = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Öğrencilerin A'yı tercih etme oranı"
    )
    student_preference_b = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Öğrencilerin B'yi tercih etme oranı"
    )
    
    # Karşılaştırma tarihi
    compared_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-compared_at']
    
    def __str__(self):
        return f"{self.name} - {self.schedule_a.name} vs {self.schedule_b.name}"

class MLTrainingData(models.Model):
    """ML modeli için eğitim verileri"""
    
    # Girdi özellikleri (features)
    total_teachers = models.IntegerField(help_text="Toplam öğretmen sayısı")
    total_classrooms = models.IntegerField(help_text="Toplam sınıf sayısı")
    total_courses = models.IntegerField(help_text="Toplam ders sayısı")
    total_time_slots = models.IntegerField(help_text="Toplam zaman dilimi sayısı")
    
    # Kısıtlama özellikleri
    hard_constraints_count = models.IntegerField(help_text="Zorunlu kısıtlama sayısı")
    soft_constraints_count = models.IntegerField(help_text="Tercihli kısıtlama sayısı")
    
    # Geçmiş performans verileri
    previous_conflict_rate = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Önceki çakışma oranı"
    )
    previous_satisfaction_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Önceki memnuniyet skoru"
    )
    
    # Hedef değişken (target)
    optimal_solution_time = models.FloatField(
        help_text="Optimal çözümü bulma süresi (saniye)"
    )
    solution_quality = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Çözüm kalitesi (0-100)"
    )
    
    # Kullanılan algoritma
    algorithm_used = models.CharField(max_length=50, help_text="Kullanılan algoritma")
    
    # Eğitim tarihi
    trained_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-trained_at']
    
    def __str__(self):
        return f"ML Eğitim Verisi - {self.trained_at.strftime('%Y-%m-%d')}"