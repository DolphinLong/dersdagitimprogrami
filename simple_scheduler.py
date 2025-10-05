#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basit Ders Programı Sistemi
Kural 1: Dersler günlük 2 saatlik bloklar halinde ve farklı günlerde
Kural 2: Ders atamasını mevcut atamalardan al
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager

class SimpleScheduler:
    def __init__(self):
        self.db = DatabaseManager()
        self.days = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
        self.time_slots = ["1", "2", "3", "4", "5", "6", "7"]  # 2'şerli bloklar
        
    def get_assignments(self):
        """Mevcut ders atamalarını al"""
        assignments = {}
        
        # Veritabanından mevcut atamaları çek
        schedule_entries = self.db.get_schedule_by_school_type()
        
        for entry in schedule_entries:
            class_obj = self.db.get_class_by_id(entry.class_id)
            teacher = self.db.get_teacher_by_id(entry.teacher_id)
            lesson = self.db.get_lesson_by_id(entry.lesson_id)
            
            if class_obj and teacher and lesson:
                class_name = class_obj.name
                if class_name not in assignments:
                    assignments[class_name] = {}
                
                # Haftalık saat sayısını al
                weekly_hours = self.db.get_weekly_hours_for_lesson(lesson.lesson_id, class_obj.grade)
                
                assignments[class_name][lesson.name] = {
                    'teacher': teacher.name,
                    'hours': weekly_hours or 0
                }
        
        return assignments
    
    def create_schedule(self):
        """Basit ders programı oluştur"""
        assignments = self.get_assignments()
        schedule = {}
        
        print("📚 Basit Ders Programı Oluşturuluyor...")
        print("=" * 50)
        
        for class_name, lessons in assignments.items():
            print(f"\n🏫 {class_name} Sınıfı:")
            schedule[class_name] = {}
            
            # Her gün için boş program
            for day in self.days:
                schedule[class_name][day] = {}
                for slot in self.time_slots:
                    schedule[class_name][day][slot] = None
            
            # Dersleri programla
            day_index = 0
            slot_index = 0
            
            for lesson_name, lesson_info in lessons.items():
                hours = lesson_info['hours']
                teacher = lesson_info['teacher']
                
                if hours <= 0:
                    continue
                
                print(f"   📖 {lesson_name} ({teacher}) - {hours} saat")
                
                # Kural 1: 2 saatlik bloklar halinde ve farklı günlerde
                remaining_hours = hours
                
                while remaining_hours > 0:
                    # Mevcut gün ve slot
                    current_day = self.days[day_index % len(self.days)]
                    current_slot = self.time_slots[slot_index % len(self.time_slots)]
                    
                    # Bu slot boş mu?
                    if schedule[class_name][current_day][current_slot] is None:
                        # 2 saatlik blok olarak programla
                        block_hours = min(2, remaining_hours)
                        
                        schedule[class_name][current_day][current_slot] = {
                            'lesson': lesson_name,
                            'teacher': teacher,
                            'hours': block_hours
                        }
                        
                        remaining_hours -= block_hours
                        print(f"      ✓ {current_day} {current_slot}. saat - {block_hours} saat")
                        
                        # Farklı güne geç (Kural 1)
                        day_index += 1
                    else:
                        # Slot dolu, sonraki slota geç
                        slot_index += 1
                        if slot_index >= len(self.time_slots):
                            slot_index = 0
                            day_index += 1
                    
                    # Sonsuz döngü önleme
                    if day_index > len(self.days) * 2:
                        print(f"      ⚠️ {lesson_name} için yer bulunamadı!")
                        break
        
        return schedule
    
    def print_schedule(self, schedule):
        """Programı yazdır"""
        print("\n" + "=" * 80)
        print("📅 DERS PROGRAMI")
        print("=" * 80)
        
        for class_name, class_schedule in schedule.items():
            print(f"\n🏫 {class_name} SINIFI")
            print("-" * 60)
            
            # Başlık
            print(f"{'Saat':<10}", end="")
            for day in self.days:
                print(f"{day:<12}", end="")
            print()
            print("-" * 60)
            
            # Her saat dilimi için
            for slot in self.time_slots:
                print(f"{slot:<10}", end="")
                
                for day in self.days:
                    lesson_info = class_schedule[day][slot]
                    if lesson_info:
                        lesson_text = f"{lesson_info['lesson'][:8]}({lesson_info['hours']}h)"
                        print(f"{lesson_text:<12}", end="")
                    else:
                        print(f"{'Boş':<12}", end="")
                
                print()
            
            print()

def main():
    """Ana fonksiyon"""
    scheduler = SimpleScheduler()
    
    # Ders programı oluştur
    schedule = scheduler.create_schedule()
    
    # Programı yazdır
    scheduler.print_schedule(schedule)
    
    print("\n✅ Basit ders programı tamamlandı!")
    print("\n📋 Kurallar:")
    print("   • Kural 1: Dersler 2 saatlik bloklar halinde ve farklı günlerde")
    print("   • Kural 2: Ders atamaları mevcut atamalardan alındı")

if __name__ == "__main__":
    main()