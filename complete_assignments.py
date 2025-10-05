#!/usr/bin/env python3
"""
Eksik ders atamalarını tamamlama scripti
Her sınıf 35 saat olana kadar ders ataması ekler
"""

from database.db_manager import DatabaseManager

def complete_assignments():
    """Eksik ders atamalarını tamamla"""
    db = DatabaseManager()
    
    print("📚 EKSİK DERS ATAMALARINI TAMAMLAMA")
    print("=" * 50)
    
    # Mevcut durumu kontrol et
    entries = db.get_schedule_by_school_type()
    print(f"🔍 Mevcut atama sayısı: {len(entries)}")
    
    # Sınıfları al
    classes = db.get_all_classes()
    
    # Her sınıf için eksik saatleri hesapla
    for cls in classes:
        class_entries = [e for e in entries if e.class_id == cls.class_id]
        current_hours = sum(db.get_weekly_hours_for_lesson(e.lesson_id, cls.grade) for e in class_entries)
        needed_hours = 35 - current_hours
        
        print(f"\n🏫 {cls.name}: {current_hours}/35 saat (Eksik: {needed_hours})")
        
        if needed_hours > 0:
            # En az saati olan dersleri bul ve ekle
            lesson_hours = {}
            for entry in class_entries:
                lesson_id = entry.lesson_id
                if lesson_id not in lesson_hours:
                    lesson_hours[lesson_id] = 0
                lesson_hours[lesson_id] += db.get_weekly_hours_for_lesson(lesson_id, cls.grade)
            
            # Türkçe ve Matematik'i öncelikle artır
            priority_lessons = []
            for entry in class_entries:
                lesson = db.get_lesson_by_id(entry.lesson_id)
                if lesson and lesson.name in ['Türkçe', 'Matematik']:
                    priority_lessons.append(entry)
            
            # Eksik saatleri tamamla
            added_hours = 0
            for i in range(needed_hours):
                if priority_lessons and added_hours < needed_hours:
                    # Öncelikli dersleri artır
                    entry = priority_lessons[i % len(priority_lessons)]
                    
                    # Yeni atama ekle
                    db.add_schedule_entry(
                        entry.class_id,
                        entry.teacher_id,
                        entry.lesson_id,
                        entry.classroom_id,
                        0,  # day
                        0   # time_slot
                    )
                    
                    lesson = db.get_lesson_by_id(entry.lesson_id)
                    teacher = db.get_teacher_by_id(entry.teacher_id)
                    print(f"   ✓ {lesson.name} → {teacher.name} (+1 saat)")
                    added_hours += 1
    
    # Final kontrol
    print("\n📊 FINAL KONTROL:")
    entries = db.get_schedule_by_school_type()
    print(f"   📋 Toplam atama: {len(entries)}")
    
    # Sınıf saatleri
    print("\n🏫 SINIF TOPLAM SAATLERİ:")
    total_hours = 0
    for cls in classes:
        class_entries = [e for e in entries if e.class_id == cls.class_id]
        class_hours = sum(db.get_weekly_hours_for_lesson(e.lesson_id, cls.grade) for e in class_entries)
        total_hours += class_hours
        
        if class_hours == 35:
            print(f"   ✅ {cls.name}: {class_hours} saat")
        else:
            print(f"   ⚠️  {cls.name}: {class_hours} saat (EKSİK - {35-class_hours} saat)")
    
    print(f"\n📊 Toplam haftalık ders saati: {total_hours}/280")
    print("✅ Ders atamaları tamamlandı!")

if __name__ == "__main__":
    complete_assignments()