#!/usr/bin/env python3
"""
Critical Bug Fixes - Acil hata düzeltmeleri
"""

import sqlite3
import os
import sys

def fix_database_schema():
    """Veritabanı şema sorunlarını düzelt"""
    print("🔧 Veritabanı şema düzeltmeleri...")
    
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()
    
    # 1. schedule tablosunun varlığını kontrol et
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schedule'")
    if not cursor.fetchone():
        print("   📋 schedule tablosu oluşturuluyor...")
        cursor.execute("""
            CREATE TABLE schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                lesson_id INTEGER NOT NULL,
                teacher_id INTEGER NOT NULL,
                classroom_id INTEGER,
                day INTEGER NOT NULL,
                time_slot INTEGER NOT NULL,
                school_type TEXT,
                FOREIGN KEY (class_id) REFERENCES classes(class_id),
                FOREIGN KEY (lesson_id) REFERENCES lessons(lesson_id),
                FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id),
                FOREIGN KEY (classroom_id) REFERENCES classrooms(classroom_id)
            )
        """)
        print("   ✅ schedule tablosu oluşturuldu")
    
    # 2. İndeksleri kontrol et ve oluştur
    indexes = [
        ("idx_schedule_class_day", "CREATE INDEX IF NOT EXISTS idx_schedule_class_day ON schedule(class_id, day)"),
        ("idx_schedule_teacher_day", "CREATE INDEX IF NOT EXISTS idx_schedule_teacher_day ON schedule(teacher_id, day)"),
        ("idx_schedule_day_slot", "CREATE INDEX IF NOT EXISTS idx_schedule_day_slot ON schedule(day, time_slot)")
    ]
    
    for idx_name, idx_sql in indexes:
        cursor.execute(idx_sql)
        print(f"   ✅ {idx_name} indeksi oluşturuldu")
    
    conn.commit()
    conn.close()
    print("   ✅ Veritabanı şema düzeltmeleri tamamlandı")

def fix_teacher_availability():
    """Öğretmen uygunluk verilerini düzelt"""
    print("👨‍🏫 Öğretmen uygunluk verileri düzeltiliyor...")
    
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()
    
    # Mevcut öğretmenleri al
    cursor.execute("SELECT teacher_id FROM teachers")
    teachers = cursor.fetchall()
    
    # Her öğretmen için tüm günlerde uygunluk ekle (eğer yoksa)
    for teacher_id, in teachers:
        for day in range(5):  # Pazartesi-Cuma
            for time_slot in range(7):  # 7 saat/gün
                cursor.execute("""
                    INSERT OR IGNORE INTO teacher_availability 
                    (teacher_id, day, time_slot) VALUES (?, ?, ?)
                """, (teacher_id, day, time_slot))
    
    conn.commit()
    
    # Kontrol
    cursor.execute("SELECT COUNT(*) FROM teacher_availability")
    count = cursor.fetchone()[0]
    print(f"   ✅ {count} öğretmen uygunluk kaydı mevcut")
    
    conn.close()

def fix_lesson_curriculum():
    """Ders müfredatı verilerini kontrol et"""
    print("📚 Ders müfredatı kontrol ediliyor...")
    
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()
    
    # Eksik müfredat kayıtlarını kontrol et
    cursor.execute("""
        SELECT l.lesson_id, l.name, COUNT(lc.lesson_id) as curriculum_count
        FROM lessons l
        LEFT JOIN curriculum lc ON l.lesson_id = lc.lesson_id
        GROUP BY l.lesson_id, l.name
        HAVING curriculum_count = 0
    """)
    
    missing_lessons = cursor.fetchall()
    
    if missing_lessons:
        print(f"   ⚠️  {len(missing_lessons)} ders için müfredat kaydı eksik")
        
        # Ortaokul için temel müfredat ekle
        for lesson_id, lesson_name, _ in missing_lessons:
            # Varsayılan haftalık saat sayıları
            default_hours = {
                'Matematik': 5, 'Türkçe': 6, 'Fen Bilimleri': 4,
                'Sosyal Bilgiler': 3, 'Yabancı Dil': 4, 'Beden Eğitimi': 2,
                'Görsel Sanatlar': 1, 'Müzik': 1, 'Din Kültürü ve Ahlak Bilgisi': 2,
                'Teknoloji ve Tasarım': 2, 'Bilişim Teknolojileri': 2
            }
            
            hours = default_hours.get(lesson_name, 2)  # Varsayılan 2 saat
            
            # 5-8. sınıflar için ekle
            for grade in [5, 6, 7, 8]:
                cursor.execute("""
                    INSERT OR IGNORE INTO curriculum 
                    (lesson_id, grade, weekly_hours, school_type) 
                    VALUES (?, ?, ?, ?)
                """, (lesson_id, grade, hours, 'Ortaokul'))
            
            print(f"   ✅ {lesson_name} için müfredat eklendi ({hours} saat/hafta)")
    
    conn.commit()
    conn.close()

def fix_classroom_data():
    """Sınıf verilerini kontrol et"""
    print("🏫 Sınıf verileri kontrol ediliyor...")
    
    conn = sqlite3.connect('schedule.db')
    cursor = conn.cursor()
    
    # En az bir sınıf olduğundan emin ol
    cursor.execute("SELECT COUNT(*) FROM classrooms")
    classroom_count = cursor.fetchone()[0]
    
    if classroom_count == 0:
        print("   📋 Varsayılan sınıf oluşturuluyor...")
        cursor.execute("""
            INSERT INTO classrooms (name, capacity) 
            VALUES ('Genel Sınıf', 30)
        """)
        conn.commit()
        print("   ✅ Varsayılan sınıf oluşturuldu")
    
    conn.close()

def run_all_fixes():
    """Tüm kritik düzeltmeleri çalıştır"""
    print("🚨 KRİTİK HATA DÜZELTMELERİ BAŞLATIYOR...")
    print("=" * 50)
    
    try:
        fix_database_schema()
        fix_teacher_availability()
        fix_lesson_curriculum()
        fix_classroom_data()
        
        print("\n" + "=" * 50)
        print("✅ TÜM KRİTİK HATALAR DÜZELTİLDİ!")
        print("🚀 Sistem artık stabil çalışmaya hazır!")
        return True
        
    except Exception as e:
        print(f"\n❌ Hata düzeltme sırasında sorun: {e}")
        return False

if __name__ == "__main__":
    success = run_all_fixes()
    sys.exit(0 if success else 1)