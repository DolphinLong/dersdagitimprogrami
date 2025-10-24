#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ortaokul için ders atamalarını düzelt/oluştur
"""

import sys
import os
import io

if sys.platform.startswith("win"):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_manager
import sqlite3

print("=" * 80)
print("🔧 ORTAOKUL İÇİN DERS ATAMALARI DÜZELTİLİYOR")
print("=" * 80)

conn = sqlite3.connect('schedule.db')
cursor = conn.cursor()

# Mevcut okul türünü kontrol et
school_type = db_manager.get_school_type()
print(f"\n📌 Mevcut okul türü: {school_type}")

# Schedule tablosundaki Ortaokul kayıtlarını kontrol et
cursor.execute("SELECT COUNT(*) FROM schedule WHERE school_type = ?", (school_type,))
ortaokul_count = cursor.fetchone()[0]
print(f"📋 {school_type} için mevcut atamalar: {ortaokul_count}")

if ortaokul_count == 0:
    print("\n❌ Ortaokul için atama yok!")
    print("\n🔄 Atamaları otomatik oluşturuyorum...")
    
    # Sınıfları al
    classes = db_manager.get_all_classes()
    teachers = db_manager.get_all_teachers()
    lessons = db_manager.get_all_lessons()
    
    print(f"\n   Sınıflar: {len(classes)}")
    print(f"   Öğretmenler: {len(teachers)}")
    print(f"   Dersler: {len(lessons)}")
    
    # Öğretmen branş eşleşmesi
    teacher_by_subject = {}
    for teacher in teachers:
        if teacher.subject not in teacher_by_subject:
            teacher_by_subject[teacher.subject] = []
        teacher_by_subject[teacher.subject].append(teacher)
    
    print(f"\n   Branşlar: {list(teacher_by_subject.keys())}")
    
    # Her sınıf için her dersi uygun öğretmene ata
    created_count = 0
    for class_obj in classes:
        print(f"\n   📚 {class_obj.name} (Seviye {class_obj.grade}) için atamalar...")
        
        for lesson in lessons:
            # Bu dersin haftalık saati var mı?
            weekly_hours = db_manager.get_weekly_hours_for_lesson(lesson.lesson_id, class_obj.grade)
            
            if weekly_hours and weekly_hours > 0:
                # Bu derse uygun öğretmen var mı?
                suitable_teachers = teacher_by_subject.get(lesson.name, [])
                
                if suitable_teachers:
                    # İlk uygun öğretmeni seç (basit yaklaşım)
                    teacher = suitable_teachers[0]
                    
                    # Atamayı yap
                    try:
                        # schedule tablosuna ekle
                        cursor.execute("""
                            INSERT INTO schedule (class_id, lesson_id, teacher_id, day, time_slot, school_type)
                            VALUES (?, ?, ?, 0, 0, ?)
                        """, (class_obj.class_id, lesson.lesson_id, teacher.teacher_id, school_type))
                        
                        created_count += 1
                        print(f"      ✅ {lesson.name} -> {teacher.name} ({weekly_hours} saat)")
                    except Exception as e:
                        print(f"      ⚠️  {lesson.name}: {e}")
                else:
                    print(f"      ⚠️  {lesson.name}: Uygun öğretmen yok!")
    
    conn.commit()
    print(f"\n✅ {created_count} atama oluşturuldu!")
    
else:
    print(f"\n✅ {school_type} için zaten {ortaokul_count} atama mevcut")

conn.close()

# Kontrol
print("\n" + "=" * 80)
print("✅ KONTROL")
print("=" * 80)

assignments = db_manager.get_schedule_by_school_type()
print(f"\n📝 DB Manager - Atamalar: {len(assignments)}")

if len(assignments) > 0:
    print(f"\n   İlk 5 atama:")
    for i, assignment in enumerate(assignments[:5], 1):
        teacher = db_manager.get_teacher_by_id(assignment.teacher_id)
        lesson = db_manager.get_lesson_by_id(assignment.lesson_id)
        class_obj = next((c for c in db_manager.get_all_classes() if c.class_id == assignment.class_id), None)
        
        if teacher and lesson and class_obj:
            print(f"   {i}. {class_obj.name} - {lesson.name} -> {teacher.name}")
    
    print("\n🎉 Ders atamaları hazır! Şimdi program oluşturabilirsiniz.")
else:
    print("\n❌ Hala atama yok! Manuel atama yapmanız gerekebilir.")
