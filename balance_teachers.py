#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager

print("⚖️ ÖĞRETMEN YÜKÜ DENGELEME")
print("=" * 50)

db_manager = DatabaseManager()

# Önce mevcut atama sayısını kontrol et
schedule_entries = db_manager.get_schedule_by_school_type()
print(f"🔍 Mevcut atama sayısı: {len(schedule_entries)}")

if len(schedule_entries) > 88:  # Normal 88 olmalı (8 sınıf × 11 ders)
    print("⚠️  Fazla atama tespit edildi! Önce clean_and_rebuild.py çalıştır.")
    exit(1)

try:
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    # Matematik öğretmenlerini paylaştır
    print("1️⃣ Matematik öğretmenlerini dengeliyorum...")
    
    # Ayşe ve Yunus ID'lerini bul
    ayse_id = None
    yunus_id = None
    teachers = db_manager.get_all_teachers()
    for teacher in teachers:
        if teacher.name == "Ayşe":
            ayse_id = teacher.teacher_id
        elif teacher.name == "Yunus":
            yunus_id = teacher.teacher_id
    
    # Matematik lesson ID bul
    matematik_id = None
    lessons = db_manager.get_all_lessons()
    for lesson in lessons:
        if lesson.name == "Matematik":
            matematik_id = lesson.lesson_id
            break
    
    if ayse_id and yunus_id and matematik_id:
        # Matematik atamalarını sil
        cursor.execute("DELETE FROM schedule_entries WHERE lesson_id = ?", (matematik_id,))
        
        # Yeniden ata - HER SINIF İÇİN SADECE BİR KAYIT
        classes = db_manager.get_all_classes()
        ayse_classes = ["8A", "8B", "7A", "7B"]  # Ayşe
        yunus_classes = ["6A", "6B", "5A", "5B"]  # Yunus
        
        for class_obj in classes:
            if class_obj.name in ayse_classes:
                # Önce var mı kontrol et
                cursor.execute("SELECT COUNT(*) as count FROM schedule_entries WHERE class_id = ? AND lesson_id = ?", 
                             (class_obj.class_id, matematik_id))
                existing = cursor.fetchone()['count']
                
                if existing == 0:  # Sadece yoksa ekle
                    cursor.execute("""
                        INSERT INTO schedule_entries 
                        (class_id, teacher_id, lesson_id, classroom_id, day, time_slot, school_type)
                        VALUES (?, ?, ?, 1, 0, 0, 'Ortaokul')
                    """, (class_obj.class_id, ayse_id, matematik_id))
                    print(f"   ✓ {class_obj.name}: Matematik → Ayşe")
                else:
                    print(f"   ⚠️  {class_obj.name}: Matematik zaten atanmış")
            elif class_obj.name in yunus_classes:
                # Önce var mı kontrol et
                cursor.execute("SELECT COUNT(*) as count FROM schedule_entries WHERE class_id = ? AND lesson_id = ?", 
                             (class_obj.class_id, matematik_id))
                existing = cursor.fetchone()['count']
                
                if existing == 0:  # Sadece yoksa ekle
                    cursor.execute("""
                        INSERT INTO schedule_entries 
                        (class_id, teacher_id, lesson_id, classroom_id, day, time_slot, school_type)
                        VALUES (?, ?, ?, 1, 0, 0, 'Ortaokul')
                    """, (class_obj.class_id, yunus_id, matematik_id))
                    print(f"   ✓ {class_obj.name}: Matematik → Yunus")
                else:
                    print(f"   ⚠️  {class_obj.name}: Matematik zaten atanmış")
    
    # Fen Bilimleri öğretmenlerini paylaştır
    print(f"\n2️⃣ Fen Bilimleri öğretmenlerini dengeliyorum...")
    
    # Yeliz ve Tarık ID'lerini bul
    yeliz_id = None
    tarik_id = None
    for teacher in teachers:
        if teacher.name == "Yeliz":
            yeliz_id = teacher.teacher_id
        elif teacher.name == "Tarık":
            tarik_id = teacher.teacher_id
    
    # Fen Bilimleri lesson ID bul
    fen_id = None
    for lesson in lessons:
        if lesson.name == "Fen Bilimleri":
            fen_id = lesson.lesson_id
            break
    
    if yeliz_id and tarik_id and fen_id:
        # Fen Bilimleri atamalarını sil
        cursor.execute("DELETE FROM schedule_entries WHERE lesson_id = ?", (fen_id,))
        
        # Yeniden ata - HER SINIF İÇİN SADECE BİR KAYIT
        yeliz_classes = ["8A", "8B", "7A", "7B"]  # Yeliz
        tarik_classes = ["6A", "6B", "5A", "5B"]  # Tarık
        
        for class_obj in classes:
            if class_obj.name in yeliz_classes:
                # Önce var mı kontrol et
                cursor.execute("SELECT COUNT(*) as count FROM schedule_entries WHERE class_id = ? AND lesson_id = ?", 
                             (class_obj.class_id, fen_id))
                existing = cursor.fetchone()['count']
                
                if existing == 0:  # Sadece yoksa ekle
                    cursor.execute("""
                        INSERT INTO schedule_entries 
                        (class_id, teacher_id, lesson_id, classroom_id, day, time_slot, school_type)
                        VALUES (?, ?, ?, 1, 0, 0, 'Ortaokul')
                    """, (class_obj.class_id, yeliz_id, fen_id))
                    print(f"   ✓ {class_obj.name}: Fen Bilimleri → Yeliz")
                else:
                    print(f"   ⚠️  {class_obj.name}: Fen Bilimleri zaten atanmış")
            elif class_obj.name in tarik_classes:
                # Önce var mı kontrol et
                cursor.execute("SELECT COUNT(*) as count FROM schedule_entries WHERE class_id = ? AND lesson_id = ?", 
                             (class_obj.class_id, fen_id))
                existing = cursor.fetchone()['count']
                
                if existing == 0:  # Sadece yoksa ekle
                    cursor.execute("""
                        INSERT INTO schedule_entries 
                        (class_id, teacher_id, lesson_id, classroom_id, day, time_slot, school_type)
                        VALUES (?, ?, ?, 1, 0, 0, 'Ortaokul')
                    """, (class_obj.class_id, tarik_id, fen_id))
                    print(f"   ✓ {class_obj.name}: Fen Bilimleri → Tarık")
                else:
                    print(f"   ⚠️  {class_obj.name}: Fen Bilimleri zaten atanmış")
    
    # Yabancı Dil öğretmenlerini paylaştır
    print(f"\n3️⃣ Yabancı Dil öğretmenlerini dengeliyorum...")
    
    # Osman ve Lale ID'lerini bul
    osman_id = None
    lale_id = None
    for teacher in teachers:
        if teacher.name == "Osman":
            osman_id = teacher.teacher_id
        elif teacher.name == "Lale":
            lale_id = teacher.teacher_id
    
    # Yabancı Dil lesson ID bul
    yabanci_id = None
    for lesson in lessons:
        if lesson.name == "Yabancı Dil":
            yabanci_id = lesson.lesson_id
            break
    
    if osman_id and lale_id and yabanci_id:
        # Yabancı Dil atamalarını sil
        cursor.execute("DELETE FROM schedule_entries WHERE lesson_id = ?", (yabanci_id,))
        
        # Yeniden ata - HER SINIF İÇİN SADECE BİR KAYIT
        osman_classes = ["8A", "8B", "7A", "7B"]  # Osman
        lale_classes = ["6A", "6B", "5A", "5B"]   # Lale
        
        for class_obj in classes:
            if class_obj.name in osman_classes:
                # Önce var mı kontrol et
                cursor.execute("SELECT COUNT(*) as count FROM schedule_entries WHERE class_id = ? AND lesson_id = ?", 
                             (class_obj.class_id, yabanci_id))
                existing = cursor.fetchone()['count']
                
                if existing == 0:  # Sadece yoksa ekle
                    cursor.execute("""
                        INSERT INTO schedule_entries 
                        (class_id, teacher_id, lesson_id, classroom_id, day, time_slot, school_type)
                        VALUES (?, ?, ?, 1, 0, 0, 'Ortaokul')
                    """, (class_obj.class_id, osman_id, yabanci_id))
                    print(f"   ✓ {class_obj.name}: Yabancı Dil → Osman")
                else:
                    print(f"   ⚠️  {class_obj.name}: Yabancı Dil zaten atanmış")
            elif class_obj.name in lale_classes:
                # Önce var mı kontrol et
                cursor.execute("SELECT COUNT(*) as count FROM schedule_entries WHERE class_id = ? AND lesson_id = ?", 
                             (class_obj.class_id, yabanci_id))
                existing = cursor.fetchone()['count']
                
                if existing == 0:  # Sadece yoksa ekle
                    cursor.execute("""
                        INSERT INTO schedule_entries 
                        (class_id, teacher_id, lesson_id, classroom_id, day, time_slot, school_type)
                        VALUES (?, ?, ?, 1, 0, 0, 'Ortaokul')
                    """, (class_obj.class_id, lale_id, yabanci_id))
                    print(f"   ✓ {class_obj.name}: Yabancı Dil → Lale")
                else:
                    print(f"   ⚠️  {class_obj.name}: Yabancı Dil zaten atanmış")
    
    conn.commit()
    
except Exception as e:
    print(f"❌ Hata: {e}")

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

# Öğretmen yüklerini yeniden hesapla
teacher_loads = {}
for entry in schedule_entries:
    teacher = db_manager.get_teacher_by_id(entry.teacher_id)
    class_obj = db_manager.get_class_by_id(entry.class_id)
    lesson = db_manager.get_lesson_by_id(entry.lesson_id)
    
    if teacher and class_obj and lesson:
        if teacher.name not in teacher_loads:
            teacher_loads[teacher.name] = 0
        
        weekly_hours = db_manager.get_weekly_hours_for_lesson(lesson.lesson_id, class_obj.grade)
        teacher_loads[teacher.name] += weekly_hours or 0

print(f"\n👨‍🏫 Dengeli Öğretmen Yükleri:")
for teacher_name, load in sorted(teacher_loads.items(), key=lambda x: x[1], reverse=True):
    if load > 30:
        print(f"   ❌ {teacher_name}: {load} saat (Hala fazla)")
    elif load > 20:
        print(f"   ⚠️  {teacher_name}: {load} saat (Kabul edilebilir)")
    else:
        print(f"   ✅ {teacher_name}: {load} saat (İyi)")

print(f"\n✅ Öğretmen yükleri dengelendi!")
print(f"💡 Şimdi correct_scheduler.py çalıştır - çok daha iyi olacak!")