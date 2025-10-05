#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager

class ImprovedScheduler:
    def __init__(self):
        self.db = DatabaseManager()
        self.days = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
        self.time_slots = ["1", "2", "3", "4", "5", "6", "7"]  # 7 slot
        
    def get_assignments(self):
        """Mevcut ders atamalarını al"""
        assignments = {}
        schedule_entries = self.db.get_schedule_by_school_type()
        
        for entry in schedule_entries:
            class_obj = self.db.get_class_by_id(entry.class_id)
            teacher = self.db.get_teacher_by_id(entry.teacher_id)
            lesson = self.db.get_lesson_by_id(entry.lesson_id)
            
            if class_obj and teacher and lesson:
                class_name = class_obj.name
                if class_name not in assignments:
                    assignments[class_name] = {}
                
                weekly_hours = self.db.get_weekly_hours_for_lesson(lesson.lesson_id, class_obj.grade)
                
                assignments[class_name][lesson.name] = {
                    'teacher': teacher.name,
                    'hours': weekly_hours or 0
                }
        
        return assignments
    
    def create_schedule(self):
        """Gelişmiş ders programı oluştur"""
        assignments = self.get_assignments()
        schedule = {}
        
        print("📚 Gelişmiş Ders Programı Oluşturuluyor...")
        print("=" * 50)
        
        for class_name, lessons in assignments.items():
            print(f"\n🏫 {class_name} Sınıfı:")
            schedule[class_name] = {}
            
            # Her gün için boş program
            for day in self.days:
                schedule[class_name][day] = {}
                for slot in self.time_slots:
                    schedule[class_name][day][slot] = None
            
            # Dersleri programla - önce büyük dersler
            sorted_lessons = sorted(lessons.items(), key=lambda x: x[1]['hours'], reverse=True)
            
            day_index = 0
            slot_index = 0
            
            for lesson_name, lesson_info in sorted_lessons:
                hours = lesson_info['hours']
                teacher = lesson_info['teacher']
                
                if hours <= 0:
                    continue
                
                print(f"   📖 {lesson_name} ({teacher}) - {hours} saat")
                
                remaining_hours = hours
                
                while remaining_hours > 0:
                    # Mevcut gün ve slot
                    current_day = self.days[day_index % len(self.days)]
                    current_slot = self.time_slots[slot_index % len(self.time_slots)]
                    
                    # Bu slot boş mu?
                    if schedule[class_name][current_day][current_slot] is None:
                        # Akıllı blok boyutu belirleme
                        if remaining_hours >= 2 and slot_index < len(self.time_slots) - 1:
                            # 2 saatlik blok yap
                            next_slot = self.time_slots[slot_index + 1]
                            if schedule[class_name][current_day][next_slot] is None:
                                # 2 saatlik blok
                                schedule[class_name][current_day][current_slot] = {
                                    'lesson': lesson_name, 'teacher': teacher, 'hours': 1
                                }
                                schedule[class_name][current_day][next_slot] = {
                                    'lesson': lesson_name, 'teacher': teacher, 'hours': 1
                                }
                                remaining_hours -= 2
                                print(f"      ✓ {current_day} {current_slot}-{next_slot}. saat - 2 saat blok")
                                slot_index += 2
                            else:
                                # Tek saat
                                schedule[class_name][current_day][current_slot] = {
                                    'lesson': lesson_name, 'teacher': teacher, 'hours': 1
                                }
                                remaining_hours -= 1
                                print(f"      ✓ {current_day} {current_slot}. saat - 1 saat")
                                slot_index += 1
                        else:
                            # Tek saat
                            schedule[class_name][current_day][current_slot] = {
                                'lesson': lesson_name, 'teacher': teacher, 'hours': 1
                            }
                            remaining_hours -= 1
                            print(f"      ✓ {current_day} {current_slot}. saat - 1 saat")
                            slot_index += 1
                        
                        # Farklı güne geç
                        if slot_index >= len(self.time_slots):
                            slot_index = 0
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
        print("📅 GELİŞMİŞ DERS PROGRAMI")
        print("=" * 80)
        
        for class_name, class_schedule in schedule.items():
            print(f"\n🏫 {class_name} SINIFI")
            print("-" * 70)
            
            # Başlık
            print(f"{'Saat':<6}", end="")
            for day in self.days:
                print(f"{day:<14}", end="")
            print()
            print("-" * 70)
            
            # Her saat dilimi için
            for slot in self.time_slots:
                print(f"{slot:<6}", end="")
                
                for day in self.days:
                    lesson_info = class_schedule[day][slot]
                    if lesson_info:
                        lesson_text = f"{lesson_info['lesson'][:10]}"
                        print(f"{lesson_text:<14}", end="")
                    else:
                        print(f"{'Boş':<14}", end="")
                
                print()
            
            print()

def main():
    """Ana fonksiyon"""
    scheduler = ImprovedScheduler()
    
    # Ders programı oluştur
    schedule = scheduler.create_schedule()
    
    # Programı yazdır
    scheduler.print_schedule(schedule)
    
    print("\n✅ Gelişmiş ders programı tamamlandı!")
    print("\n📋 İyileştirmeler:")
    print("   • 7 saatlik gün (35 slot/hafta)")
    print("   • Akıllı blok oluşturma (1 veya 2 saat)")
    print("   • Büyük dersleri önce programlama")

if __name__ == "__main__":
    main()
