#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Teacher Availability Checking in Real Time
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager

def main():
    """Test teacher availability checking in detail"""
    print("🧪 ÖĞRETMEN UYGUNLUK KONTROLÜ TEST EDİLİYOR")
    print("="*60)
    
    db_manager = DatabaseManager()
    
    # Get all teachers
    teachers = db_manager.get_all_teachers()
    print(f"📊 Toplam öğretmen sayısı: {len(teachers)}")
    
    # Test each teacher's availability
    print(f"\n🔍 Her öğretmenin uygunluğunu test ediyoruz...")
    
    for teacher in teachers:
        print(f"\n📋 {teacher.name} ({teacher.subject}):")
        
        # Get availability data
        availability = db_manager.get_teacher_availability(teacher.teacher_id)
        print(f"   Veritabanında {len(availability)} uygunluk kaydı var")
        
        # Test each day and slot
        available_count = 0
        unavailable_count = 0
        
        for day in range(5):  # Pazartesi-Cuma
            day_name = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"][day]
            print(f"   {day_name}:")
            
            for time_slot in range(8):  # 8 saat
                is_available = db_manager.is_teacher_available(teacher.teacher_id, day, time_slot)
                status = "✅" if is_available else "❌"
                print(f"      Slot {time_slot+1}: {status}")
                
                if is_available:
                    available_count += 1
                else:
                    unavailable_count += 1
        
        print(f"   📊 Özet: {available_count} müsait, {unavailable_count} müsait değil")
        
        # Show raw availability data
        if availability:
            print(f"   📋 Ham veri:")
            for av in availability:
                day_name = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"][av['day']]
                status = "Müsait" if av['is_available'] == 1 else "Müsait değil"
                print(f"      {day_name} Slot {av['time_slot']+1}: {status}")
    
    # Test scheduler's availability checking
    print(f"\n🧪 Scheduler'ın uygunluk kontrolünü test ediyoruz...")
    
    # Import scheduler
    try:
        from algorithms.scheduler import Scheduler
        scheduler = Scheduler(db_manager)
        
        # Test a specific teacher
        test_teacher = teachers[0] if teachers else None
        if test_teacher:
            print(f"   Test öğretmeni: {test_teacher.name}")
            
            # Test scheduler's availability checking
            for day in range(2):  # Test first 2 days
                for time_slot in range(3):  # Test first 3 slots
                    # Check using scheduler's method
                    is_available = db_manager.is_teacher_available(test_teacher.teacher_id, day, time_slot)
                    print(f"      Day {day+1}, Slot {time_slot+1}: {'Müsait' if is_available else 'Müsait değil'}")
        
    except Exception as e:
        print(f"   ❌ Scheduler import hatası: {e}")
    
    # Test actual scheduling with availability
    print(f"\n🧪 Gerçek program oluşturma testi...")
    
    # Get a class and its assignments
    classes = db_manager.get_all_classes()
    if classes:
        test_class = classes[0]
        print(f"   Test sınıfı: {test_class.name}")
        
        # Get assignments for this class
        assignments = db_manager.get_schedule_by_school_type()
        class_assignments = [a for a in assignments if a.class_id == test_class.class_id]
        
        print(f"   Bu sınıf için {len(class_assignments)} ders ataması var")
        
        # Test scheduling each assignment
        for assignment in class_assignments[:3]:  # Test first 3 assignments
            teacher = db_manager.get_teacher_by_id(assignment.teacher_id)
            lesson = db_manager.get_lesson_by_id(assignment.lesson_id)
            
            if teacher and lesson:
                print(f"   📝 {lesson.name} -> {teacher.name}")
                
                # Check teacher availability for different slots
                available_slots = []
                for day in range(5):
                    for time_slot in range(8):
                        if db_manager.is_teacher_available(teacher.teacher_id, day, time_slot):
                            available_slots.append((day, time_slot))
                
                print(f"      {teacher.name} için {len(available_slots)} müsait slot var")
                
                if len(available_slots) < 5:
                    print(f"      ⚠️  Bu öğretmen çok az müsait slot'a sahip!")
                    print(f"      İlk 5 müsait slot:")
                    for i, (day, slot) in enumerate(available_slots[:5]):
                        day_name = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"][day]
                        print(f"         {day_name} Slot {slot+1}")
    
    print(f"\n🎉 Öğretmen uygunluk testi tamamlandı!")

if __name__ == "__main__":
    main()