#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager

print("🔧 ÖĞRETMEN YÜK DAĞILIMI DÜZELTMESİ")
print("=" * 60)

db_manager = DatabaseManager()

print("📊 Mevcut Türkçe Atamaları:")
schedule_entries = db_manager.get_schedule_by_school_type()

turkce_assignments = []
for entry in schedule_entries:
    lesson = db_manager.get_lesson_by_id(entry.lesson_id)
    teacher = db_manager.get_teacher_by_id(entry.teacher_id)
    class_obj = db_manager.get_class_by_id(entry.class_id)
    
    if lesson and lesson.name == "Türkçe":
        weekly_hours = db_manager.get_weekly_hours_for_lesson(lesson.lesson_id, class_obj.grade)
        turkce_assignments.append({
            'class': class_obj.name,
            'teacher': teacher.name,
            'hours': weekly_hours,
            'entry_id': entry.entry_id
        })

print(f"   📚 Toplam Türkçe ataması: {len(turkce_assignments)}")
total_hours = sum([a['hours'] for a in turkce_assignments])
print(f"   ⏰ Toplam Türkçe saati: {total_hours}")

for assignment in turkce_assignments:
    print(f"      • {assignment['class']}: {assignment['teacher']} ({assignment['hours']}h)")

print(f"\n🔧 Yeniden Dağıtım:")
print(f"   • Veli: 8A, 8B, 7A, 7B (4 sınıf)")
print(f"   • Cengiz: 6A, 6B, 5A, 5B (4 sınıf)")

# Türkçe atamalarını yeniden düzenle
try:
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    # Önce tüm Türkçe atamalarını sil
    cursor.execute("DELETE FROM schedule_entries WHERE lesson_id = (SELECT lesson_id FROM lessons WHERE name = 'Türkçe')")
    
    # Veli için atamalar (8A, 8B, 7A, 7B)
    veli_classes = ["8A", "8B", "7A", "7B"]
    cengiz_classes = ["6A", "6B", "5A", "5B"]
    
    # Veli ID ve Cengiz ID bul
    veli_id = None
    cengiz_id = None
    teachers = db_manager.get_all_teachers()
    for teacher in teachers:
        if teacher.name == "Veli":
            veli_id = teacher.teacher_id
        elif teacher.name == "Cengiz":
            cengiz_id = teacher.teacher_id
    
    # Türkçe lesson ID bul
    turkce_id = None
    lessons = db_manager.get_all_lessons()
    for lesson in lessons:
        if lesson.name == "Türkçe":
            turkce_id = lesson.lesson_id
            break
    
    if veli_id and cengiz_id and turkce_id:
        classes = db_manager.get_all_classes()
        
        for class_obj in classes:
            if class_obj.name in veli_classes:
                # Veli'ye ata
                cursor.execute("""
                    INSERT INTO schedule_entries 
                    (class_id, teacher_id, lesson_id, classroom_id, day, time_slot, school_type)
                    VALUES (?, ?, ?, 1, 0, 0, 'Ortaokul')
                """, (class_obj.class_id, veli_id, turkce_id))
                print(f"   ✓ {class_obj.name}: Türkçe → Veli")
                
            elif class_obj.name in cengiz_classes:
                # Cengiz'e ata
                cursor.execute("""
                    INSERT INTO schedule_entries 
                    (class_id, teacher_id, lesson_id, classroom_id, day, time_slot, school_type)
                    VALUES (?, ?, ?, 1, 0, 0, 'Ortaokul')
                """, (class_obj.class_id, cengiz_id, turkce_id))
                print(f"   ✓ {class_obj.name}: Türkçe → Cengiz")
    
    conn.commit()
    print(f"\n✅ Türkçe atamaları yeniden düzenlendi")
    
except Exception as e:
    print(f"❌ Hata: {e}")

# Kontrol et
print(f"\n📊 Yeni Durum:")
schedule_entries = db_manager.get_schedule_by_school_type()
print(f"   📋 Toplam atama: {len(schedule_entries)}")

# Öğretmen yüklerini hesapla
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

print(f"\n👨‍🏫 Öğretmen Yükleri:")
for teacher_name, load in sorted(teacher_loads.items(), key=lambda x: x[1], reverse=True):
    if load > 30:
        print(f"   ❌ {teacher_name}: {load} saat (ÇOK FAZLA!)")
    elif load > 20:
        print(f"   ⚠️  {teacher_name}: {load} saat (Yoğun)")
    else:
        print(f"   ✅ {teacher_name}: {load} saat (Normal)")

print(f"\n💡 Şimdi correct_scheduler.py'yi tekrar çalıştır!")