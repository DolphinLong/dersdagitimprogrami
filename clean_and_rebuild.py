#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager

print("🧹 VERİTABANI TEMİZLİĞİ VE YENİDEN OLUŞTURMA")
print("=" * 60)

db_manager = DatabaseManager()

try:
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    # 1. Tüm schedule_entries'leri sil
    print("1️⃣ Tüm ders atamalarını siliyorum...")
    cursor.execute("DELETE FROM schedule_entries")
    deleted_count = cursor.rowcount
    print(f"   ✓ {deleted_count} atama silindi")
    
    conn.commit()
    print("   ✅ Veritabanı temizlendi!")
    
    # 3. Temel atamaları yeniden oluştur
    print("\n3️⃣ Temel ders atamalarını oluşturuyorum...")
    
    # Sınıfları al
    classes = db_manager.get_all_classes()
    lessons = db_manager.get_all_lessons()
    teachers = db_manager.get_all_teachers()
    
    # Öğretmen ID'lerini bul
    teacher_ids = {}
    for teacher in teachers:
        teacher_ids[teacher.name] = teacher.teacher_id
    
    # Ders ID'lerini bul
    lesson_ids = {}
    for lesson in lessons:
        lesson_ids[lesson.name] = lesson.lesson_id
    
    # Her sınıf için her dersi bir kez ata
    assignment_count = 0
    
    for class_obj in classes:
        print(f"\n   🏫 {class_obj.name} sınıfı için atamalar:")
        
        # Sınıf seviyesine göre dersler
        if class_obj.grade >= 8:  # 8. sınıf
            class_lessons = [
                ("Türkçe", "Veli"),
                ("Matematik", "Ayşe"),
                ("Fen Bilimleri", "Yeliz"),
                ("Yabancı Dil", "Osman"),
                ("T.C. İnkılab ve Atatürkçülük", "Leyla"),
                ("Din Kültürü ve Ahlak Bilgisi", "Mehmet"),
                ("Beden Eğitimi", "Esen"),
                ("Görsel Sanatlar", "Zeynep"),
                ("Müzik", "Aslı"),
                ("Teknoloji ve Tasarım", "Jale"),
                ("Rehberlik", "Veli")
            ]
        elif class_obj.grade == 7:  # 7. sınıf
            class_lessons = [
                ("Türkçe", "Veli"),
                ("Matematik", "Ayşe"),
                ("Fen Bilimleri", "Yeliz"),
                ("Yabancı Dil", "Osman"),
                ("Sosyal Bilgiler", "Leyla"),
                ("Din Kültürü ve Ahlak Bilgisi", "Mehmet"),
                ("Beden Eğitimi", "Esen"),
                ("Görsel Sanatlar", "Zeynep"),
                ("Müzik", "Aslı"),
                ("Teknoloji ve Tasarım", "Jale"),
                ("Rehberlik", "Veli")
            ]
        elif class_obj.grade >= 5:  # 5-6. sınıf
            if class_obj.grade == 6:
                class_lessons = [
                    ("Türkçe", "Cengiz"),
                    ("Matematik", "Yunus"),
                    ("Fen Bilimleri", "Tarık"),
                    ("Yabancı Dil", "Lale"),
                    ("Sosyal Bilgiler", "Leyla"),
                    ("Din Kültürü ve Ahlak Bilgisi", "Mehmet"),
                    ("Beden Eğitimi", "Esen"),
                    ("Görsel Sanatlar", "Zeynep"),
                    ("Müzik", "Aslı"),
                    ("Bilişim Teknolojileri", "Büşra"),
                    ("Rehberlik", "Veli")
                ]
            else:  # 5. sınıf
                class_lessons = [
                    ("Türkçe", "Cengiz"),
                    ("Matematik", "Yunus"),
                    ("Fen Bilimleri", "Tarık"),
                    ("Yabancı Dil", "Lale"),
                    ("Sosyal Bilgiler", "Leyla"),
                    ("Din Kültürü ve Ahlak Bilgisi", "Mehmet"),
                    ("Beden Eğitimi", "Esen"),
                    ("Görsel Sanatlar", "Zeynep"),
                    ("Müzik", "Aslı"),
                    ("Bilişim Teknolojileri", "Büşra"),
                    ("Rehberlik", "Veli")
                ]
        
        # Atamaları yap
        for lesson_name, teacher_name in class_lessons:
            if lesson_name in lesson_ids and teacher_name in teacher_ids:
                # Önce var mı kontrol et
                cursor.execute("""
                    SELECT COUNT(*) as count FROM schedule_entries 
                    WHERE class_id = ? AND lesson_id = ? AND teacher_id = ?
                """, (class_obj.class_id, lesson_ids[lesson_name], teacher_ids[teacher_name]))
                
                existing = cursor.fetchone()['count']
                
                if existing == 0:  # Sadece yoksa ekle
                    cursor.execute("""
                        INSERT INTO schedule_entries 
                        (class_id, teacher_id, lesson_id, classroom_id, day, time_slot, school_type)
                        VALUES (?, ?, ?, 1, 0, 0, 'Ortaokul')
                    """, (class_obj.class_id, teacher_ids[teacher_name], lesson_ids[lesson_name]))
                    
                    assignment_count += 1
                    print(f"      ✓ {lesson_name} → {teacher_name}")
                else:
                    print(f"      ⚠️  {lesson_name} → {teacher_name} (zaten var)")
    
    conn.commit()
    print(f"\n   ✅ {assignment_count} yeni atama oluşturuldu!")
    
except Exception as e:
    print(f"❌ Hata: {e}")
    conn.rollback()

# Final kontrol
print(f"\n📊 FINAL KONTROL:")
schedule_entries = db_manager.get_schedule_by_school_type()
print(f"   📋 Toplam atama: {len(schedule_entries)}")

# Sınıf toplam saatlerini kontrol et
print(f"\n🏫 SINIF TOPLAM SAATLERİ:")
class_totals = {}
for entry in schedule_entries:
    class_obj = db_manager.get_class_by_id(entry.class_id)
    lesson = db_manager.get_lesson_by_id(entry.lesson_id)
    
    if class_obj and lesson:
        if class_obj.name not in class_totals:
            class_totals[class_obj.name] = 0
        
        weekly_hours = db_manager.get_weekly_hours_for_lesson(lesson.lesson_id, class_obj.grade)
        class_totals[class_obj.name] += weekly_hours or 0

for class_name, total in sorted(class_totals.items()):
    if total == 35:
        print(f"   ✅ {class_name}: {total} saat (Doğru)")
    elif total > 35:
        print(f"   ❌ {class_name}: {total} saat (FAZLA - {total-35} saat)")
    else:
        print(f"   ⚠️  {class_name}: {total} saat (EKSİK - {35-total} saat)")

print(f"\n✅ Temizlik ve yeniden oluşturma tamamlandı!")
print(f"💡 Şimdi correct_scheduler.py çalıştırabilirsin!")