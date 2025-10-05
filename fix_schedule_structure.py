#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager

print("🔧 DERS PROGRAMI YAPISINI DÜZELTİYORUM")
print("=" * 60)

db_manager = DatabaseManager()

try:
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    # 1. Yeni schedule tablosu oluştur (eğer yoksa)
    print("1️⃣ Schedule tablosu oluşturuluyor...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedule (
            schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER NOT NULL,
            teacher_id INTEGER NOT NULL,
            lesson_id INTEGER NOT NULL,
            classroom_id INTEGER NOT NULL,
            day INTEGER NOT NULL,
            time_slot INTEGER NOT NULL,
            school_type TEXT NOT NULL,
            FOREIGN KEY (class_id) REFERENCES classes(class_id),
            FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id),
            FOREIGN KEY (lesson_id) REFERENCES lessons(lesson_id),
            FOREIGN KEY (classroom_id) REFERENCES classrooms(classroom_id)
        )
    """)
    print("   ✓ Schedule tablosu hazır")
    
    # 2. Mevcut schedule_entries'leri kontrol et
    print("\n2️⃣ Mevcut ders atamalarını kontrol ediyorum...")
    cursor.execute("SELECT COUNT(*) as count FROM schedule_entries WHERE day = 0 AND time_slot = 0")
    assignment_count = cursor.fetchone()['count']
    print(f"   📋 Ders ataması: {assignment_count} kayıt")
    
    cursor.execute("SELECT COUNT(*) as count FROM schedule_entries WHERE day > 0 AND time_slot > 0")
    schedule_count = cursor.fetchone()['count']
    print(f"   📅 Ders programı: {schedule_count} kayıt")
    
    # 3. Eğer schedule_entries'de program kayıtları varsa, bunları schedule tablosuna taşı
    if schedule_count > 0:
        print("\n3️⃣ Program kayıtlarını schedule tablosuna taşıyorum...")
        
        # Önce schedule tablosunu temizle
        cursor.execute("DELETE FROM schedule")
        
        # Program kayıtlarını kopyala
        cursor.execute("""
            INSERT INTO schedule (class_id, teacher_id, lesson_id, classroom_id, day, time_slot, school_type)
            SELECT class_id, teacher_id, lesson_id, classroom_id, day, time_slot, school_type
            FROM schedule_entries 
            WHERE day > 0 AND time_slot > 0
        """)
        
        moved_count = cursor.rowcount
        print(f"   ✓ {moved_count} program kaydı taşındı")
        
        # Program kayıtlarını schedule_entries'den sil
        cursor.execute("DELETE FROM schedule_entries WHERE day > 0 AND time_slot > 0")
        deleted_count = cursor.rowcount
        print(f"   ✓ {deleted_count} program kaydı schedule_entries'den silindi")
    
    # 4. schedule_entries'de sadece atamalar kalsın (day=0, time_slot=0)
    print("\n4️⃣ Final kontrol...")
    cursor.execute("SELECT COUNT(*) as count FROM schedule_entries")
    final_assignments = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM schedule")
    final_schedule = cursor.fetchone()['count']
    
    print(f"   📋 schedule_entries (atamalar): {final_assignments}")
    print(f"   📅 schedule (program): {final_schedule}")
    
    conn.commit()
    print("\n✅ Yapı düzeltildi!")
    
    print("\n📝 YENİ YAPI:")
    print("   • schedule_entries: Ders atamaları (öğretmen-sınıf-ders)")
    print("   • schedule: Ders programı (gün-saat-ders)")
    print("   • Program silinince sadece schedule tablosu temizlenir")
    print("   • Ders atamaları schedule_entries'de korunur")
    
except Exception as e:
    print(f"❌ Hata: {e}")
    conn.rollback()