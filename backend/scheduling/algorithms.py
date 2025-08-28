from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import logging

from .models import Teacher, Classroom, Course, TimeSlot, Schedule, ScheduleItem, Constraint

# Logger ayarları
logger = logging.getLogger(__name__)

class SchedulingAlgorithm:
    def __init__(self, schedule: Schedule):
        self.schedule = schedule
        self.conflicts = []
        
    def check_teacher_availability(self, teacher: Teacher, time_slot: TimeSlot, date: datetime.date) -> bool:
        """Öğretmenin belirli bir zamanda müsait olup olmadığını kontrol eder"""
        # Öğretmenin o zaman diliminde zaten bir dersi var mı kontrolü
        existing_items = ScheduleItem.objects.filter(
            schedule=self.schedule,
            teacher=teacher,
            time_slot=time_slot,
            date=date
        )
        if existing_items.exists():
            return False # Öğretmen zaten meşgul

        # Doğrudan müsaitlik kontrolü
        if time_slot in teacher.available_days.all():
            return True
            
        # Doğrudan müsait değilse, müsait olmayan zamanları kontrol edelim
        if time_slot in teacher.unavailable_slots.all():
            return False
            
        # Eğer ne müsait ne de müsait değil olarak işaretlenmişse, varsayılan olarak müsait kabul edelim
        return True
    
    def check_classroom_availability(self, classroom: Classroom, time_slot: TimeSlot, date: datetime.date) -> bool:
        """Sınıfın belirli bir zamanda müsait olup olmadığını kontrol eder"""
        # Zaten o zaman diliminde ders olan sınıf var mı kontrolü
        existing_items = ScheduleItem.objects.filter(
            schedule=self.schedule,
            classroom=classroom,
            time_slot=time_slot,
            date=date
        )
        
        return not existing_items.exists()
    
    def check_course_requirements(self, course: Course, classroom: Classroom) -> bool:
        """Dersin sınıf gereksinimlerini karşılayıp karşılamadığını kontrol eder"""
        if course.requires_projector and not classroom.has_projector:
            return False
        if course.requires_computer and not classroom.has_computer:
            return False
        if course.requires_smart_board and not classroom.has_smart_board:
            return False
        if course.is_lab_course and not classroom.is_lab:
            return False
        return True
    
    def check_constraints(self, course: Course, teacher: Teacher, classroom: Classroom, 
                         time_slot: TimeSlot, date: datetime.date) -> bool:
        """Tüm kısıtlamaları kontrol eder"""
        # Zorunlu kısıtlamaları kontrol edelim
        hard_constraints = Constraint.objects.filter(constraint_type=Constraint.HARD, is_active=True)
        
        for constraint in hard_constraints:
            # Kısıtlama belirli öğretmenler için geçerliyse ve öğretmen listede değilse devam et
            if constraint.teachers.exists() and teacher not in constraint.teachers.all():
                continue
                
            # Kısıtlama belirli sınıflar için geçerliyse ve sınıf listede değilse devam et
            if constraint.classrooms.exists() and classroom not in constraint.classrooms.all():
                continue
                
            # Kısıtlama belirli dersler için geçerliyse ve ders listede değilse devam et
            if constraint.courses.exists() and course not in constraint.courses.all():
                continue
                
            # Zaman dilimi kısıtlaması varsa kontrol et
            if constraint.time_slots.exists() and time_slot in constraint.time_slots.all():
                return False
                
            # Gün kısıtlaması varsa kontrol et
            if constraint.days and time_slot.day in constraint.days:
                return False
                
        return True
    
    def find_conflicts(self) -> List[Dict]:
        """Çakışmaları bulur ve döndürür"""
        conflicts = []
        
        # Aynı öğretmene ait çakışan dersleri bul
        teacher_conflicts = self.find_teacher_conflicts()
        conflicts.extend(teacher_conflicts)
        
        # Aynı sınıfta çakışan dersleri bul
        classroom_conflicts = self.find_classroom_conflicts()
        conflicts.extend(classroom_conflicts)
        
        # Kısıtlama ihlallerini bul
        constraint_violations = self.find_constraint_violations()
        conflicts.extend(constraint_violations)
        
        return conflicts
    
    def find_teacher_conflicts(self) -> List[Dict]:
        """Aynı öğretmene ait çakışan dersleri bulur"""
        conflicts = []
        
        # Öğretmen bazında gruplayalım
        teacher_items = defaultdict(list)
        schedule_items = ScheduleItem.objects.filter(schedule=self.schedule)
        
        for item in schedule_items:
            teacher_items[item.teacher].append(item)
            
        # Her öğretmen için çakışan dersleri kontrol edelim
        for teacher, items in teacher_items.items():
            # Tarih ve zaman dilimine göre gruplayalım
            time_slot_groups = defaultdict(list)
            
            for item in items:
                key = (item.date, item.time_slot)
                time_slot_groups[key].append(item)
                
            # Aynı zamanda birden fazla ders varsa çakışma var
            for (date, time_slot), conflicting_items in time_slot_groups.items():
                if len(conflicting_items) > 1:
                    conflicts.append({
                        'type': 'teacher_conflict',
                        'teacher': teacher,
                        'date': date,
                        'time_slot': time_slot,
                        'conflicting_items': conflicting_items,
                        'message': f"{teacher} öğretmeni {date} tarihinde {time_slot} zaman diliminde birden fazla derse atanmış"
                    })
                    
        return conflicts
    
    def find_classroom_conflicts(self) -> List[Dict]:
        """Aynı sınıfta çakışan dersleri bulur"""
        conflicts = []
        
        # Sınıf bazında gruplayalım
        classroom_items = defaultdict(list)
        schedule_items = ScheduleItem.objects.filter(schedule=self.schedule)
        
        for item in schedule_items:
            classroom_items[item.classroom].append(item)
            
        # Her sınıf için çakışan dersleri kontrol edelim
        for classroom, items in classroom_items.items():
            # Tarih ve zaman dilimine göre gruplayalım
            time_slot_groups = defaultdict(list)
            
            for item in items:
                key = (item.date, item.time_slot)
                time_slot_groups[key].append(item)
                
            # Aynı zamanda birden fazla ders varsa çakışma var
            for (date, time_slot), conflicting_items in time_slot_groups.items():
                if len(conflicting_items) > 1:
                    conflicts.append({
                        'type': 'classroom_conflict',
                        'classroom': classroom,
                        'date': date,
                        'time_slot': time_slot,
                        'conflicting_items': conflicting_items,
                        'message': f"{classroom} sınıfında {date} tarihinde {time_slot} zaman diliminde birden fazla ders planlanmış"
                    })
                    
        return conflicts
    
    def find_constraint_violations(self) -> List[Dict]:
        """Kısıtlama ihlallerini bulur"""
        violations = []
        
        schedule_items = ScheduleItem.objects.filter(schedule=self.schedule)
        
        for item in schedule_items:
            # Kısıtlamaları kontrol edelim
            if not self.check_constraints(item.course, item.teacher, item.classroom, item.time_slot, item.date):
                violations.append({
                    'type': 'constraint_violation',
                    'item': item,
                    'message': f"{item.course.code} dersi için kısıtlama ihlali"
                })
                
        return violations
    
    def create_schedule_item(self, course: Course, teacher: Teacher, classroom: Classroom, 
                           time_slot: TimeSlot, date: datetime.date) -> Tuple[bool, Optional[ScheduleItem], List[Dict]]:
        """Yeni bir ders planı öğesi oluşturur ve çakışmaları kontrol eder"""
        errors = []
        
        # Öğretmen müsait mi?
        if not self.check_teacher_availability(teacher, time_slot, date):
            errors.append({'type': 'teacher_conflict', 'message': f"{teacher} öğretmeni {date} tarihinde {time_slot} zaman diliminde müsait değil"})
            
        # Sınıf müsait mi?
        if not self.check_classroom_availability(classroom, time_slot, date):
            errors.append({'type': 'classroom_conflict', 'message': f"{classroom} sınıfı {date} tarihinde {time_slot} zaman diliminde müsait değil"})
            
        # Ders sınıf gereksinimlerini karşılıyor mu?
        if not self.check_course_requirements(course, classroom):
            errors.append({'type': 'course_requirement_violation', 'message': f"{course.code} dersi için {classroom} sınıfı gereksinimleri karşılamıyor"})
            
        # Kısıtlamalar sağlanıyor mu?
        if not self.check_constraints(course, teacher, classroom, time_slot, date):
            errors.append({'type': 'constraint_violation', 'message': f"{course.code} dersi için kısıtlama ihlali"})
            
        # Hata varsa dersi oluşturmayalım
        if errors:
            return False, None, errors
            
        # Dersi oluşturalım
        try:
            schedule_item = ScheduleItem.objects.create(
                schedule=self.schedule,
                course=course,
                teacher=teacher,
                classroom=classroom,
                time_slot=time_slot,
                date=date
            )
            return True, schedule_item, []
        except Exception as e:
            errors.append({'type': 'creation_error', 'message': f"Ders oluşturulurken hata: {str(e)}"})
            return False, None, errors