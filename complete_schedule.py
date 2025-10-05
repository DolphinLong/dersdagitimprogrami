#!/usr/bin/env python3
"""
Eksik program saatlerini tamamlama scripti
"""

from database.db_manager import DatabaseManager

def complete_schedule():
    """Eksik program saatlerini tamamla"""
    db = DatabaseManager()
    
    print("🔧 EKSİK PROGRAM SAATLERİNİ TAMAMLAMA")
    print("=" * 50)
    
    # Mevcut program kayıtları
    program_entries = db.get_schedule_program_by_school_type()
    print(f"Mevcut program kayıtları: {len(program_entries)}")
    
    # Sınıfları al
    classes = db.get_all_classes()
    
    # Her sınıf için eksik saatleri bul ve tamamla
    for cls in classes:
        class_entries = [e for e in program_entries if e.class_id == cls.class_id]
        current_hours = len(class_entries)
        needed_hours = 35 - current_hours
        
        print(f"\n🏫 {cls.name}: {current_hours}/35 saat (Eksik: {needed_hours})")
        
        if needed_hours > 0:
            # Boş slotları bul
            occupied_slots = set()
            for entry in class_entries:
                occupied_slots.add((entry.day, entry.time_slot))
            
            # Tüm slotları kontrol et
            available_slots = []
            for day in range(1, 6):  # Pazartesi-Cuma
                for time_slot in range(1, 8):  # 1-7 saatler
                    if (day, time_slot) not in occupied_slots:
                        available_slots.append((day, time_slot))
            
            # Ders atamalarından en çok saati olan dersleri bul
            assignments = db.get_schedule_by_school_type()
            class_assignments = [a for a in assignments if a.class_id == cls.class_id]
            
            # Türkçe ve Matematik'i öncelikle artır
            priority_assignments = []
            for assignment in class_assignments:
                lesson = db.get_lesson_by_id(assignment.lesson_id)
                if lesson and lesson.name in ['Türkçe', 'Matematik']:
                    priority_assignments.append(assignment)
            
            # Eksik saatleri tamamla
            added_count = 0
            for i in range(min(needed_hours, len(available_slots))):
                if priority_assignments and added_count < needed_hours:
                    assignment = priority_assignments[i % len(priority_assignments)]
                    day, time_slot = available_slots[i]
                    
                    # Schedule tablosuna ekle
                    db.add_schedule_program(
                        assignment.class_id,
                        assignment.teacher_id,
                        assignment.lesson_id,
                        assignment.classroom_id,
                        day,
                        time_slot
                    )
                    
                    lesson = db.get_lesson_by_id(assignment.lesson_id)
                    teacher = db.get_teacher_by_id(assignment.teacher_id)
                    day_names = ["", "Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
                    print(f"   ✓ {lesson.name} → {teacher.name} ({day_names[day]} {time_slot}. saat)")
                    added_count += 1
    
    # Final kontrol
    print("\n📊 FINAL KONTROL:")
    program_entries = db.get_schedule_program_by_school_type()
    print(f"   📋 Toplam program: {len(program_entries)}")
    
    # Sınıf saatleri
    print("\n🏫 SINIF SAATLERİ:")
    total_hours = 0
    for cls in classes:
        class_entries = [e for e in program_entries if e.class_id == cls.class_id]
        class_hours = len(class_entries)
        total_hours += class_hours
        
        if class_hours == 35:
            print(f"   ✅ {cls.name}: {class_hours} saat")
        else:
            print(f"   ⚠️  {cls.name}: {class_hours} saat (Eksik: {35-class_hours})")
    
    print(f"\n📊 Toplam: {total_hours}/280 saat")
    
    if total_hours == 280:
        print("✅ Mükemmel! 280 saate ulaştık!")
    else:
        print(f"⚠️  Hala {280-total_hours} saat eksik")

if __name__ == "__main__":
    complete_schedule()