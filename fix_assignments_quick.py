#!/usr/bin/env python3
"""
Hızlı ders atama scripti - Acil durum için
"""

import sqlite3
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.db_manager import DatabaseManager

def create_quick_assignments():
    """Hızlı ders ataması oluştur"""
    print("🚀 Hızlı Ders Atama Başlatılıyor...")
    
    # Database manager
    db = DatabaseManager()
    
    # Mevcut verileri al
    classes = db.get_all_classes()
    teachers = db.get_all_teachers()
    lessons = db.get_all_lessons()
    
    print(f"📊 Mevcut veriler:")
    print(f"   • Sınıflar: {len(classes)}")
    print(f"   • Öğretmenler: {len(teachers)}")
    print(f"   • Dersler: {len(lessons)}")
    
    if not classes or not teachers or not lessons:
        print("❌ Temel veriler eksik! Önce sınıf, öğretmen ve ders ekleyin.")
        return False
    
    # Okul türünü kontrol et
    school_type = db.get_school_type()
    print(f"   • Okul türü: {school_type}")
    
    # Mevcut atamaları kontrol et
    print("\n🔍 Mevcut atamalar kontrol ediliyor...")
    
    # Doğru tablo adını bul
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%assignment%' OR name LIKE '%schedule%'")
    tables = cursor.fetchall()
    print(f"   📋 İlgili tablolar: {[t[0] for t in tables]}")
    
    # schedule_entries tablosunu kullan (mevcut veriler burada)
    cursor.execute("SELECT COUNT(*) FROM schedule_entries")
    existing_count = cursor.fetchone()[0]
    print(f"   📊 Mevcut schedule_entries: {existing_count}")
    conn.close()
    
    # Her sınıf için ders ataması yap
    assignment_count = 0
    
    for class_obj in classes:
        print(f"\n📚 {class_obj.name} sınıfı için atamalar:")
        
        for lesson in lessons:
            # Haftalık saat sayısını al
            weekly_hours = db.get_weekly_hours_for_lesson(lesson.lesson_id, class_obj.grade)
            
            if weekly_hours and weekly_hours > 0:
                # Uygun öğretmen bul (ders adına göre)
                suitable_teacher = None
                
                # Önce aynı branştaki öğretmeni ara
                for teacher in teachers:
                    if teacher.subject and lesson.name in teacher.subject:
                        suitable_teacher = teacher
                        break
                
                # Bulamazsa ilk öğretmeni ata
                if not suitable_teacher:
                    suitable_teacher = teachers[0]
                
                # Atamayı yap - schedule_entries tablosuna direkt ekle
                try:
                    conn = sqlite3.connect('schedule.db')
                    cursor = conn.cursor()
                    
                    # schedule_entries tablosuna ekle
                    cursor.execute("""
                        INSERT INTO schedule_entries 
                        (class_id, lesson_id, teacher_id, classroom_id, day, time_slot, school_type)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (class_obj.class_id, lesson.lesson_id, suitable_teacher.teacher_id, 1, -1, -1, school_type))
                    
                    conn.commit()
                    conn.close()
                    success = True
                    
                    if success:
                        assignment_count += 1
                        print(f"   ✅ {lesson.name} → {suitable_teacher.name} ({weekly_hours} saat)")
                    else:
                        print(f"   ❌ {lesson.name} ataması başarısız")
                        
                except Exception as e:
                    print(f"   ⚠️  {lesson.name} atama hatası: {e}")
    
    print(f"\n🎉 Toplam {assignment_count} ders ataması yapıldı!")
    
    # Kontrol et
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM schedule_entries WHERE day = -1 AND time_slot = -1")
    assignment_count_check = cursor.fetchone()[0]
    conn.close()
    
    print(f"✅ Doğrulama: {assignment_count_check} atama kaydedildi")
    
    return assignment_count_check > 0

if __name__ == "__main__":
    success = create_quick_assignments()
    if success:
        print("\n✅ Ders atamaları tamamlandı!")
        print("🚀 Artık 'PROGRAMI OLUŞTUR' butonunu kullanabilirsiniz!")
    else:
        print("\n❌ Ders atamaları başarısız!")
        sys.exit(1)