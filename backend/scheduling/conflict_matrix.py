from typing import List, Dict, Set
from datetime import datetime, date
from collections import defaultdict
import logging

from .models import Teacher, Classroom, Course, TimeSlot, Schedule, ScheduleItem, Constraint

# Logger ayarları
logger = logging.getLogger(__name__)

class ConflictMatrix:
    """Çakışma matrisi algoritması - tüm çakışmaları sistemli şekilde tespit eder"""
    
    def __init__(self, schedule: Schedule):
        self.schedule = schedule
        self.conflicts = []
        self.conflict_matrix = defaultdict(lambda: defaultdict(list))
        
    def build_conflict_matrix(self) -> Dict:
        """Çakışma matrisini oluşturur"""
        # Tüm ders planı öğelerini al
        schedule_items = ScheduleItem.objects.filter(schedule=self.schedule).select_related(
            'teacher', 'classroom', 'course', 'time_slot'
        )
        
        # Çiftler halinde çakışma kontrolü yap
        items_list = list(schedule_items)
        
        for i in range(len(items_list)):
            for j in range(i + 1, len(items_list)):
                item1 = items_list[i]
                item2 = items_list[j]
                
                # Çakışmaları kontrol et
                conflicts = self._check_item_conflicts(item1, item2)
                
                if conflicts:
                    # Çakışmaları matrise ekle
                    for conflict in conflicts:
                        conflict_key = f"{conflict['type']}_{conflict['date']}_{conflict['time_slot_id']}"
                        self.conflict_matrix[conflict_key][item1.id].append(conflict)
                        self.conflict_matrix[conflict_key][item2.id].append(conflict)
                        
                        # Genel çakışma listesine ekle
                        self.conflicts.append(conflict)
        
        return dict(self.conflict_matrix)
    
    def _check_item_conflicts(self, item1: ScheduleItem, item2: ScheduleItem) -> List[Dict]:
        """İki ders planı öğesi arasında çakışma olup olmadığını kontrol eder"""
        conflicts = []
        
        # Aynı tarih ve zaman dilimi mi?
        if item1.date == item2.date and item1.time_slot == item2.time_slot:
            # Öğretmen çakışması
            if item1.teacher == item2.teacher:
                conflicts.append({
                    'type': 'teacher_conflict',
                    'date': item1.date,
                    'time_slot_id': item1.time_slot.id,
                    'teacher': item1.teacher,
                    'items': [item1, item2],
                    'message': f"{item1.teacher} öğretmeni {item1.date} tarihinde {item1.time_slot} zaman diliminde iki derse atanmış"
                })
            
            # Sınıf çakışması
            if item1.classroom == item2.classroom:
                conflicts.append({
                    'type': 'classroom_conflict',
                    'date': item1.date,
                    'time_slot_id': item1.time_slot.id,
                    'classroom': item1.classroom,
                    'items': [item1, item2],
                    'message': f"{item1.classroom} sınıfında {item1.date} tarihinde {item1.time_slot} zaman diliminde iki ders planlanmış"
                })
        
        return conflicts
    
    def get_conflicts_by_type(self, conflict_type: str) -> List[Dict]:
        """Belirli bir türdeki çakışmaları döndürür"""
        return [conflict for conflict in self.conflicts if conflict['type'] == conflict_type]
    
    def get_conflicts_by_date(self, conflict_date: date) -> List[Dict]:
        """Belirli bir tarihteki çakışmaları döndürür"""
        return [conflict for conflict in self.conflicts if conflict['date'] == conflict_date]
    
    def get_conflicts_summary(self) -> Dict:
        """Çakışma özeti"""
        summary = {
            'total_conflicts': len(self.conflicts),
            'teacher_conflicts': len(self.get_conflicts_by_type('teacher_conflict')),
            'classroom_conflicts': len(self.get_conflicts_by_type('classroom_conflict')),
            'constraint_violations': len(self.get_conflicts_by_type('constraint_violation')),
        }
        return summary

class ConstraintAnalyzer:
    """Kısıtlama analizi ve tasarım dokümantasyonu"""
    
    CONSTRAINT_TYPES = {
        'hard': 'Zorunlu Kısıtlamalar',
        'soft': 'Tercihli Kısıtlamalar'
    }
    
    CONSTRAINT_CATEGORIES = {
        'time': 'Zaman Kısıtlamaları',
        'resource': 'Kaynak Kısıtlamaları',
        'preference': 'Tercih Kısıtlamaları',
        'regulatory': 'Yönetmelik Kısıtlamaları'
    }
    
    def __init__(self):
        self.constraints_analysis = {}
    
    def analyze_constraints(self) -> Dict:
        """Tüm kısıtlamaları analiz eder"""
        constraints = Constraint.objects.all()
        
        analysis = {
            'total_constraints': constraints.count(),
            'by_type': {},
            'by_category': {},
            'active_constraints': constraints.filter(is_active=True).count(),
            'inactive_constraints': constraints.filter(is_active=False).count(),
        }
        
        # Tür bazında analiz
        for constraint_type, type_name in self.CONSTRAINT_TYPES.items():
            count = constraints.filter(constraint_type=constraint_type).count()
            analysis['by_type'][constraint_type] = {
                'name': type_name,
                'count': count
            }
        
        # Aktif kısıtlamalar için detaylı analiz
        active_constraints = constraints.filter(is_active=True)
        constraint_details = []
        
        for constraint in active_constraints:
            detail = {
                'id': constraint.id,
                'name': constraint.name,
                'type': self.CONSTRAINT_TYPES.get(constraint.constraint_type, constraint.constraint_type),
                'priority': constraint.priority,
                'affected_teachers': constraint.teachers.count(),
                'affected_classrooms': constraint.classrooms.count(),
                'affected_courses': constraint.courses.count(),
                'time_slots': constraint.time_slots.count(),
                'days': constraint.days
            }
            constraint_details.append(detail)
        
        analysis['constraint_details'] = constraint_details
        self.constraints_analysis = analysis
        return analysis
    
    def generate_design_document(self) -> str:
        """Kısıtlama tasarım dokümantasyonu oluşturur"""
        if not self.constraints_analysis:
            self.analyze_constraints()
        
        doc = []
        doc.append("# Kısıtlama Tasarım Dokümantasyonu")
        doc.append("")
        doc.append("## Genel Bakış")
        doc.append(f"Toplam Kısıtlama Sayısı: {self.constraints_analysis['total_constraints']}")
        doc.append(f"Aktif Kısıtlamalar: {self.constraints_analysis['active_constraints']}")
        doc.append(f"Pasif Kısıtlamalar: {self.constraints_analysis['inactive_constraints']}")
        doc.append("")
        doc.append("## Tür Bazında Dağılım")
        for ctype, data in self.constraints_analysis['by_type'].items():
            doc.append(f"- {data['name']}: {data['count']} adet")
        doc.append("")
        doc.append("## Aktif Kısıtlamalar Detayları")
        doc.append("")
        
        for constraint in self.constraints_analysis.get('constraint_details', []):
            doc.append(f"### {constraint['name']}")
            doc.append(f"- Tür: {constraint['type']}")
            doc.append(f"- Öncelik: {constraint['priority']}")
            doc.append(f"- Etkilenen Öğretmenler: {constraint['affected_teachers']}")
            doc.append(f"- Etkilenen Sınıflar: {constraint['affected_classrooms']}")
            doc.append(f"- Etkilenen Dersler: {constraint['affected_courses']}")
            doc.append(f"- Zaman Dilimleri: {constraint['time_slots']}")
            if constraint['days']:
                doc.append(f"- Günler: {constraint['days']}")
            doc.append("")
        
        return "\n".join(doc)