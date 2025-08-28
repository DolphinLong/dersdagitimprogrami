from typing import List, Dict, Optional
from datetime import date
from django.db import transaction
from .models import Schedule, ScheduleItem, Teacher, Classroom, Course, TimeSlot, BackupSchedule, ScheduleAlternative
from .algorithms import SchedulingAlgorithm

class BackupScheduler:
    """Yedek plan oluşturma algoritması"""
    
    def __init__(self, schedule: Schedule):
        self.schedule = schedule
        self.algorithm = SchedulingAlgorithm(schedule)
        
    def find_conflicts(self) -> List[Dict]:
        """Çakışmaları bulur"""
        return self.algorithm.find_conflicts()
    
    def generate_backup_plan(self, name: str) -> BackupSchedule:
        """Yedek plan oluşturur"""
        with transaction.atomic():
            # Yedek plan oluştur
            backup_schedule = BackupSchedule.objects.create(
                name=name,
                primary_schedule=self.schedule
            )
            
            # Çakışan öğeler için alternatifler oluştur
            conflicts = self.find_conflicts()
            
            for conflict in conflicts:
                # Her çakışma için alternatif çözüm oluştur
                self._create_alternative(backup_schedule, conflict)
                
            return backup_schedule
    
    def _create_alternative(self, backup_schedule: BackupSchedule, conflict: Dict) -> Optional[ScheduleAlternative]:
        """Alternatif çözüm oluşturur"""
        try:
            # Çakışan ders öğesini al
            conflicting_items = conflict.get('conflicting_items', [])
            if not conflicting_items:
                # ConflictMatrix formatı için items anahtarını kontrol et
                conflicting_items = conflict.get('items', [])
                if not conflicting_items:
                    return None
                
            original_item = conflicting_items[0]
            
            # Alternatif öğretmen, sınıf ve zaman dilimi bul
            alternative_teacher = self._find_alternative_teacher(original_item.teacher, original_item.time_slot, original_item.date)
            alternative_classroom = self._find_alternative_classroom(original_item.classroom, original_item.time_slot, original_item.date)
            alternative_time_slot = self._find_alternative_time_slot(original_item.time_slot, original_item.teacher, original_item.classroom)
            
            # En az bir alternatif bulunmuşsa alternative oluştur
            if alternative_teacher or alternative_classroom or alternative_time_slot:
                reason = self._generate_reason(conflict)
                
                alternative = ScheduleAlternative.objects.create(
                    schedule=self.schedule,
                    backup_schedule=backup_schedule,
                    original_item=original_item,
                    alternative_teacher=alternative_teacher,
                    alternative_classroom=alternative_classroom,
                    alternative_time_slot=alternative_time_slot,
                    reason=reason,
                    priority=self._calculate_priority(conflict)
                )
                
                return alternative
                
            return None
        except Exception as e:
            print(f"Alternatif oluşturulurken hata: {e}")
            return None
    
    def _find_alternative_teacher(self, current_teacher: Teacher, time_slot: TimeSlot, date: date) -> Optional[Teacher]:
        """Alternatif öğretmen bulur"""
        # ScheduleItem üzerinden dersi bul
        try:
            schedule_item = ScheduleItem.objects.get(teacher=current_teacher, time_slot=time_slot, date=date)
            course = schedule_item.course
        except ScheduleItem.DoesNotExist:
            # Doğrudan course'u bulmaya çalış
            course = None
            schedule_items = ScheduleItem.objects.filter(teacher=current_teacher, time_slot=time_slot, date=date)
            if schedule_items.exists():
                course = schedule_items.first().course
            
        if not course:
            return None
            
        # Dersi verebilecek diğer öğretmenler
        eligible_teachers = course.eligible_teachers.exclude(id=current_teacher.id)
        
        # Müsait olan öğretmenleri filtrele
        algorithm = SchedulingAlgorithm(self.schedule)
        for teacher in eligible_teachers:
            if algorithm.check_teacher_availability(teacher, time_slot, date):
                return teacher
                
        return None
    
    def _find_alternative_classroom(self, current_classroom: Classroom, time_slot: TimeSlot, date: date) -> Optional[Classroom]:
        """Alternatif sınıf bulur"""
        # Aynı özelliklere sahip müsait sınıfları bul
        suitable_classrooms = Classroom.objects.filter(
            has_projector=current_classroom.has_projector,
            has_computer=current_classroom.has_computer,
            has_smart_board=current_classroom.has_smart_board,
            is_lab=current_classroom.is_lab
        ).exclude(id=current_classroom.id)
        
        # Müsait olan sınıfları filtrele
        algorithm = SchedulingAlgorithm(self.schedule)
        for classroom in suitable_classrooms:
            if algorithm.check_classroom_availability(classroom, time_slot, date):
                return classroom
                
        return None
    
    def _find_alternative_time_slot(self, current_time_slot: TimeSlot, teacher: Teacher, classroom: Classroom) -> Optional[TimeSlot]:
        """Alternatif zaman dilimi bulur"""
        # Aynı günün diğer zaman dilimlerini al
        same_day_slots = TimeSlot.objects.filter(day=current_time_slot.day).exclude(id=current_time_slot.id)
        
        # Müsait zaman dilimlerini bul
        algorithm = SchedulingAlgorithm(self.schedule)
        for time_slot in same_day_slots:
            teacher_available = algorithm.check_teacher_availability(teacher, time_slot, date.today())
            classroom_available = algorithm.check_classroom_availability(classroom, time_slot, date.today())
            
            if teacher_available and classroom_available:
                return time_slot
                
        return None
    
    def _generate_reason(self, conflict: Dict) -> str:
        """Alternatifin neden önerildiği açıklamasını oluşturur"""
        conflict_type = conflict.get('type', 'unknown')
        message = conflict.get('message', '')
        
        if conflict_type == 'teacher_conflict':
            return f"Öğretmen çakışması: {message}"
        elif conflict_type == 'classroom_conflict':
            return f"Sınıf çakışması: {message}"
        elif conflict_type == 'constraint_violation':
            return f"Kısıtlama ihlali: {message}"
        else:
            return f"Diğer çakışma: {message}"
    
    def _calculate_priority(self, conflict: Dict) -> int:
        """Alternatifin önceliğini hesaplar"""
        conflict_type = conflict.get('type', 'unknown')
        
        # Çakışma türüne göre öncelik belirle
        if conflict_type == 'teacher_conflict':
            return 8
        elif conflict_type == 'classroom_conflict':
            return 7
        elif conflict_type == 'constraint_violation':
            return 9
        else:
            return 5
    
    def apply_backup_plan(self, backup_schedule: BackupSchedule) -> bool:
        """Yedek planı uygular"""
        try:
            with transaction.atomic():
                # Yedek planı aktif yap
                backup_schedule.is_active = True
                backup_schedule.save()
                
                # Ana planı pasif yap
                self.schedule.is_active = False
                self.schedule.save()
                
                # Alternatif çözümleri uygula
                alternatives = ScheduleAlternative.objects.filter(backup_schedule=backup_schedule)
                
                for alternative in alternatives:
                    # Orijinal ders öğesini güncelle
                    original_item = alternative.original_item
                    
                    if alternative.alternative_teacher:
                        original_item.teacher = alternative.alternative_teacher
                        
                    if alternative.alternative_classroom:
                        original_item.classroom = alternative.alternative_classroom
                        
                    if alternative.alternative_time_slot:
                        original_item.time_slot = alternative.alternative_time_slot
                        
                    original_item.save()
                
                return True
        except Exception as e:
            print(f"Yedek plan uygulanırken hata: {e}")
            return False