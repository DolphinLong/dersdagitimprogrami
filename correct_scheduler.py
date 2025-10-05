#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager

class CorrectScheduler:
    def __init__(self):
        self.db = DatabaseManager()
        self.days = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
        self.time_slots = ["1", "2", "3", "4", "5", "6", "7"]
        
    def create_schedule(self):
        """DOĞRU ders programı oluştur - ÇAKIŞMA KONTROLÜ İLE"""
        print("📚 DOĞRU Ders Programı Oluşturuluyor...")
        print("=" * 60)
        
        # Mevcut assignment'ları al
        assignments = self.get_assignments()
        
        # Her sınıf için boş program oluştur
        schedule = {}
        classes = self.db.get_all_classes()
        
        for class_obj in classes:
            schedule[class_obj.name] = {}
            for day in self.days:
                schedule[class_obj.name][day] = {}
                for slot in self.time_slots:
                    schedule[class_obj.name][day][slot] = None
        
        # Öğretmen müsaitlik tablosu
        teacher_schedule = {}
        teachers = self.db.get_all_teachers()
        for teacher in teachers:
            teacher_schedule[teacher.name] = {}
            for day in self.days:
                teacher_schedule[teacher.name][day] = {}
                for slot in self.time_slots:
                    teacher_schedule[teacher.name][day][slot] = False  # False = müsait
        
        # Programlama sayacı
        total_scheduled = 0
        
        # Her sınıf için dersleri programla
        for class_name, lessons in assignments.items():
            print(f"\n🏫 {class_name} Sınıfı:")
            
            # Dersleri saate göre sırala (büyükten küçüğe)
            sorted_lessons = sorted(lessons.items(), key=lambda x: x[1]['hours'], reverse=True)
            
            for lesson_name, lesson_info in sorted_lessons:
                hours = lesson_info['hours']
                teacher_name = lesson_info['teacher']
                
                if hours <= 0:
                    continue
                
                print(f"   📖 {lesson_name} ({teacher_name}) - {hours} saat")
                
                scheduled_hours = 0
                
                # Dersi programla
                for day_idx, day in enumerate(self.days):
                    if scheduled_hours >= hours:
                        break
                    
                    for slot_idx, slot in enumerate(self.time_slots):
                        if scheduled_hours >= hours:
                            break
                        
                        # Sınıf müsait mi?
                        if schedule[class_name][day][slot] is not None:
                            continue  # Sınıf dolu
                        
                        # Öğretmen müsait mi?
                        if teacher_schedule[teacher_name][day][slot]:
                            continue  # Öğretmen meşgul
                        
                        # Slot'u rezerve et
                        schedule[class_name][day][slot] = {
                            'lesson': lesson_name,
                            'teacher': teacher_name,
                            'hours': 1
                        }
                        
                        teacher_schedule[teacher_name][day][slot] = True  # Öğretmeni meşgul yap
                        scheduled_hours += 1
                        total_scheduled += 1
                        
                        print(f"      ✓ {day} {slot}. saat")
                
                if scheduled_hours < hours:
                    print(f"      ⚠️  Sadece {scheduled_hours}/{hours} saat programlandı")
        
        print(f"\n📊 Toplam programlanan saat: {total_scheduled}")
        return schedule, teacher_schedule
    
    def get_assignments(self):
        """Assignment'ları al - sadece ders atamaları (day=0, time_slot=0)"""
        assignments = {}
        
        # Sadece ders atamalarını al (day=0, time_slot=0)
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            school_type = self.db._get_current_school_type()
            
            cursor.execute("""
                SELECT entry_id, class_id, teacher_id, lesson_id, classroom_id, day, time_slot, school_type 
                FROM schedule_entries 
                WHERE school_type = ? AND day = 0 AND time_slot = 0
            """, (school_type,))
            
            rows = cursor.fetchall()
            
            for row in rows:
                class_obj = self.db.get_class_by_id(row[1])  # class_id
                teacher = self.db.get_teacher_by_id(row[2])  # teacher_id
                lesson = self.db.get_lesson_by_id(row[3])    # lesson_id
                
                if class_obj and teacher and lesson:
                    class_name = class_obj.name
                    if class_name not in assignments:
                        assignments[class_name] = {}
                    
                    weekly_hours = self.db.get_weekly_hours_for_lesson(lesson.lesson_id, class_obj.grade)
                    
                    assignments[class_name][lesson.name] = {
                        'teacher': teacher.name,
                        'hours': weekly_hours or 0
                    }
        
        except Exception as e:
            print(f"❌ Atama alma hatası: {e}")
        
        return assignments
    
    def print_schedule(self, schedule):
        """Programı yazdır"""
        print("\n" + "=" * 80)
        print("📅 DOĞRU DERS PROGRAMI (ÇAKIŞMASIZ)")
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
                        lesson_text = f"{lesson_info['lesson'][:12]}"
                        print(f"{lesson_text:<14}", end="")
                    else:
                        print(f"{'Boş':<14}", end="")
                
                print()
            
            print()
    
    def check_conflicts(self, schedule, teacher_schedule):
        """Çakışma kontrolü yap"""
        print("\n🔍 ÇAKIŞMA KONTROLÜ:")
        
        conflicts = 0
        
        # Öğretmen çakışması kontrolü
        for teacher_name, teacher_sched in teacher_schedule.items():
            for day in self.days:
                for slot in self.time_slots:
                    if teacher_sched[day][slot]:
                        # Bu öğretmen bu slotta meşgul, kaç sınıfta?
                        class_count = 0
                        for class_name, class_sched in schedule.items():
                            lesson_info = class_sched[day][slot]
                            if lesson_info and lesson_info['teacher'] == teacher_name:
                                class_count += 1
                        
                        if class_count > 1:
                            print(f"   ❌ {teacher_name} - {day} {slot}. saat: {class_count} sınıf!")
                            conflicts += 1
        
        if conflicts == 0:
            print("   ✅ Hiç çakışma yok!")
        else:
            print(f"   ❌ {conflicts} çakışma bulundu!")
        
        return conflicts == 0

    def save_schedule_to_db(self, schedule):
        """Programı veritabanına kaydet"""
        print("\n💾 Programı veritabanına kaydediyorum...")
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Önce mevcut programı sil (sadece schedule tablosunu)
            cursor.execute("DELETE FROM schedule")
            
            saved_count = 0
            classes = self.db.get_all_classes()
            teachers = self.db.get_all_teachers()
            lessons = self.db.get_all_lessons()
            
            # ID mapping'leri oluştur
            class_map = {c.name: c.class_id for c in classes}
            teacher_map = {t.name: t.teacher_id for t in teachers}
            lesson_map = {l.name: l.lesson_id for l in lessons}
            
            for class_name, class_schedule in schedule.items():
                if class_name not in class_map:
                    continue
                    
                class_id = class_map[class_name]
                
                for day_idx, day in enumerate(self.days):
                    for slot_idx, slot in enumerate(self.time_slots):
                        lesson_info = class_schedule[day][slot]
                        
                        if lesson_info:
                            lesson_name = lesson_info['lesson']
                            teacher_name = lesson_info['teacher']
                            
                            if lesson_name in lesson_map and teacher_name in teacher_map:
                                cursor.execute("""
                                    INSERT INTO schedule 
                                    (class_id, teacher_id, lesson_id, classroom_id, day, time_slot, school_type)
                                    VALUES (?, ?, ?, 1, ?, ?, 'Ortaokul')
                                """, (
                                    class_id,
                                    teacher_map[teacher_name],
                                    lesson_map[lesson_name],
                                    day_idx + 1,  # 1-5 (Pazartesi-Cuma)
                                    slot_idx + 1  # 1-7 (1.-7. saat)
                                ))
                                saved_count += 1
            
            conn.commit()
            print(f"   ✅ {saved_count} program kaydı veritabanına kaydedildi")
            return True
            
        except Exception as e:
            print(f"   ❌ Kaydetme hatası: {e}")
            return False

def main():
    """Ana fonksiyon"""
    scheduler = CorrectScheduler()
    
    # Ders programı oluştur
    schedule, teacher_schedule = scheduler.create_schedule()
    
    # Çakışma kontrolü
    no_conflicts = scheduler.check_conflicts(schedule, teacher_schedule)
    
    # Programı yazdır
    scheduler.print_schedule(schedule)
    
    # Programı veritabanına kaydet
    if no_conflicts:
        scheduler.save_schedule_to_db(schedule)
    
    print("\n✅ DOĞRU scheduler tamamlandı!")
    print("\n📋 Özellikler:")
    print("   • Çakışma kontrolü var")
    print("   • Öğretmen müsaitlik takibi")
    print("   • Sınıf müsaitlik takibi")
    print("   • Tek seferde tek slot")
    print("   • Program schedule tablosuna kaydedilir")
    print("   • Ders atamaları schedule_entries'de korunur")
    
    if no_conflicts:
        print("   ✅ Hiç çakışma yok!")
    else:
        print("   ⚠️  Çakışmalar var, düzeltme gerekli")

if __name__ == "__main__":
    main()