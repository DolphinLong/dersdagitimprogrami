#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager

print("🚨 ACİL DÜZELTME")
print("=" * 50)

db_manager = DatabaseManager()

print("1️⃣ Schedule tablosunu tamamen temizliyorum...")
try:
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    # Tüm schedule entries'i sil
    cursor.execute("DELETE FROM schedule_entries")
    conn.commit()
    
    print("   ✅ Schedule tablosu temizlendi")
    
    # Kontrol et
    cursor.execute("SELECT COUNT(*) FROM schedule_entries")
    count = cursor.fetchone()[0]
    print(f"   📊 Kalan kayıt: {count}")
    
except Exception as e:
    print(f"   ❌ Hata: {e}")

print("\n2️⃣ Lesson assignment'ları yeniden oluşturuyorum...")

# Assignment'ları yeniden oluştur
classes = db_manager.get_all_classes()
teachers = db_manager.get_all_teachers()
lessons = db_manager.get_all_lessons()

# Teacher-subject mapping
teacher_map = {}
for teacher in teachers:
    if teacher.subject not in teacher_map:
        teacher_map[teacher.subject] = []
    teacher_map[teacher.subject].append(teacher)

assignment_count = 0

for class_obj in classes:
    print(f"\n   📚 {class_obj.name} için atamalar:")
    
    for lesson in lessons:
        # Haftalık saat sayısını al
        weekly_hours = db_manager.get_weekly_hours_for_lesson(lesson.lesson_id, class_obj.grade)
        
        if not weekly_hours or weekly_hours <= 0:
            continue
        
        # Öğretmen bul
        assigned_teacher = None
        
        # Exact match
        if lesson.name in teacher_map:
            assigned_teacher = teacher_map[lesson.name][0]
        # Special cases
        elif lesson.name == "T.C. İnkılab ve Atatürkçülük" and "Sosyal Bilgiler" in teacher_map:
            assigned_teacher = teacher_map["Sosyal Bilgiler"][0]
        elif "Bilişim" in lesson.name and "Bilişim Teknolojileri ve Yazılım" in teacher_map:
            assigned_teacher = teacher_map["Bilişim Teknolojileri ve Yazılım"][0]
        elif "Teknoloji" in lesson.name and "Teknoloji ve Tasarım" in teacher_map:
            assigned_teacher = teacher_map["Teknoloji ve Tasarım"][0]
        elif lesson.name == "Rehberlik":
            # Rehberlik için herhangi bir öğretmen
            for subject, teacher_list in teacher_map.items():
                if teacher_list:
                    assigned_teacher = teacher_list[0]
                    break
        
        if assigned_teacher:
            # TEK BİR ASSIGNMENT OLUŞTUR
            entry_id = db_manager.add_schedule_entry(
                class_obj.class_id,
                assigned_teacher.teacher_id,
                lesson.lesson_id,
                1,  # classroom
                0,  # day (dummy)
                0   # time_slot (dummy)
            )
            
            if entry_id:
                assignment_count += 1
                print(f"      ✓ {lesson.name} → {assigned_teacher.name} ({weekly_hours}h)")

print(f"\n✅ {assignment_count} assignment oluşturuldu")

print(f"\n3️⃣ Kontrol ediyorum...")
schedule_entries = db_manager.get_schedule_by_school_type()
print(f"   📊 Toplam kayıt: {len(schedule_entries)}")

if len(schedule_entries) == assignment_count:
    print("   ✅ Assignment sayısı doğru")
else:
    print("   ⚠️  Assignment sayısı yanlış!")

print(f"\n💡 Şimdi basit scheduler'ı çalıştırabilirsin")
print(f"   • Schedule tablosu temizlendi")
print(f"   • Assignment'lar yeniden oluşturuldu")
print(f"   • Çakışma sorunu çözülecek")