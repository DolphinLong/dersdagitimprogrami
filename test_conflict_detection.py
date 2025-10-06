# -*- coding: utf-8 -*-
"""
Çakışma Tespit Test Suite
Ders programındaki çakışmaları otomatik tespit eder
"""

import sys
import io

if sys.platform.startswith('win'):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from database import db_manager
from typing import List, Dict, Tuple


class ConflictDetector:
    """Çakışma tespit sistemi"""
    
    def __init__(self):
        self.conflicts = []
        
    def detect_all_conflicts(self, schedule: List) -> Dict:
        """
        Tüm çakışmaları tespit et
        
        Returns:
            Dict: {
                'class_conflicts': [...],
                'teacher_conflicts': [...],
                'total_conflicts': int
            }
        """
        class_conflicts = self._detect_class_conflicts(schedule)
        teacher_conflicts = self._detect_teacher_conflicts(schedule)
        
        return {
            'class_conflicts': class_conflicts,
            'teacher_conflicts': teacher_conflicts,
            'total_conflicts': len(class_conflicts) + len(teacher_conflicts)
        }
    
    def _detect_class_conflicts(self, schedule: List) -> List[Dict]:
        """Sınıf çakışmalarını tespit et"""
        conflicts = []
        
        # Sınıf bazlı gruplama
        class_slots = {}
        for entry in schedule:
            key = (entry.class_id, entry.day, entry.time_slot)
            if key not in class_slots:
                class_slots[key] = []
            class_slots[key].append(entry)
        
        # Çakışmaları bul
        days_tr = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
        
        for key, entries in class_slots.items():
            if len(entries) > 1:
                class_id, day, slot = key
                class_obj = db_manager.get_class_by_id(class_id)
                class_name = class_obj.name if class_obj else f"Sınıf {class_id}"
                day_name = days_tr[day] if day < 5 else f"Gün {day}"
                
                lessons = []
                for entry in entries:
                    lesson = db_manager.get_lesson_by_id(entry.lesson_id)
                    teacher = db_manager.get_teacher_by_id(entry.teacher_id)
                    
                    lesson_name = lesson.name if lesson else "?"
                    teacher_name = teacher.name if teacher else "?"
                    
                    lessons.append({
                        'lesson': lesson_name,
                        'teacher': teacher_name
                    })
                
                conflicts.append({
                    'type': 'class',
                    'class_name': class_name,
                    'day': day_name,
                    'slot': slot + 1,
                    'count': len(entries),
                    'lessons': lessons
                })
        
        return conflicts
    
    def _detect_teacher_conflicts(self, schedule: List) -> List[Dict]:
        """Öğretmen çakışmalarını tespit et"""
        conflicts = []
        
        # Öğretmen bazlı gruplama
        teacher_slots = {}
        for entry in schedule:
            key = (entry.teacher_id, entry.day, entry.time_slot)
            if key not in teacher_slots:
                teacher_slots[key] = []
            teacher_slots[key].append(entry)
        
        # Çakışmaları bul
        days_tr = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
        
        for key, entries in teacher_slots.items():
            if len(entries) > 1:
                teacher_id, day, slot = key
                teacher = db_manager.get_teacher_by_id(teacher_id)
                teacher_name = teacher.name if teacher else f"Öğretmen {teacher_id}"
                day_name = days_tr[day] if day < 5 else f"Gün {day}"
                
                classes = []
                for entry in entries:
                    class_obj = db_manager.get_class_by_id(entry.class_id)
                    lesson = db_manager.get_lesson_by_id(entry.lesson_id)
                    
                    class_name = class_obj.name if class_obj else "?"
                    lesson_name = lesson.name if lesson else "?"
                    
                    classes.append({
                        'class': class_name,
                        'lesson': lesson_name
                    })
                
                conflicts.append({
                    'type': 'teacher',
                    'teacher_name': teacher_name,
                    'day': day_name,
                    'slot': slot + 1,
                    'count': len(entries),
                    'classes': classes
                })
        
        return conflicts
    
    def print_report(self, conflicts: Dict):
        """Çakışma raporunu yazdır"""
        print("\n" + "="*80)
        print("🔍 ÇAKIŞMA TESPİT RAPORU")
        print("="*80)
        
        total = conflicts['total_conflicts']
        class_count = len(conflicts['class_conflicts'])
        teacher_count = len(conflicts['teacher_conflicts'])
        
        if total == 0:
            print("\n✅ HİÇ ÇAKIŞMA YOK! Mükemmel!")
            return
        
        print(f"\n⚠️  TOPLAM {total} ÇAKIŞMA TESPİT EDİLDİ!")
        print(f"   • Sınıf çakışması: {class_count}")
        print(f"   • Öğretmen çakışması: {teacher_count}")
        
        # Sınıf çakışmaları
        if class_count > 0:
            print("\n" + "-"*80)
            print("❌ SINIF ÇAKIŞMALARI:")
            print("-"*80)
            
            for i, conflict in enumerate(conflicts['class_conflicts'], 1):
                print(f"\n{i}. {conflict['class_name']} - {conflict['day']} {conflict['slot']}. saat")
                print(f"   {conflict['count']} ders aynı slotta:")
                for lesson_info in conflict['lessons']:
                    print(f"   → {lesson_info['lesson']} ({lesson_info['teacher']})")
        
        # Öğretmen çakışmaları
        if teacher_count > 0:
            print("\n" + "-"*80)
            print("❌ ÖĞRETMEN ÇAKIŞMALARI:")
            print("-"*80)
            
            for i, conflict in enumerate(conflicts['teacher_conflicts'], 1):
                print(f"\n{i}. {conflict['teacher_name']} - {conflict['day']} {conflict['slot']}. saat")
                print(f"   {conflict['count']} farklı sınıfta aynı anda:")
                for class_info in conflict['classes']:
                    print(f"   → {class_info['class']} - {class_info['lesson']}")
        
        print("\n" + "="*80)


def main():
    """Ana test fonksiyonu"""
    print("="*80)
    print("🧪 ÇAKIŞMA TESPİT TEST SİSTEMİ")
    print("="*80)
    
    # Programı al
    schedule = db_manager.get_schedule_program_by_school_type()
    
    if not schedule:
        print("\n❌ Hiç program bulunamadı!")
        print("   Önce 'PROGRAMI OLUŞTUR' butonuna tıklayın.")
        return
    
    print(f"\n✅ {len(schedule)} ders kaydı bulundu")
    
    # Çakışmaları tespit et
    detector = ConflictDetector()
    conflicts = detector.detect_all_conflicts(schedule)
    
    # Raporu yazdır
    detector.print_report(conflicts)
    
    # Özet
    if conflicts['total_conflicts'] == 0:
        print("\n🎉 TEST BAŞARILI! Program çakışmasız.")
        return 0
    else:
        print(f"\n❌ TEST BAŞARISIZ! {conflicts['total_conflicts']} çakışma var.")
        print("\nÖneriler:")
        print("  1. Programı yeniden oluşturun")
        print("  2. Öğretmen uygunluğunu kontrol edin")
        print("  3. Ultra Aggressive Scheduler kullanıyorsanız, Hybrid Optimal deneyin")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
