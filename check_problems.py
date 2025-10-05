#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager

print("🔍 SORUN ANALİZİ")
print("=" * 60)

db_manager = DatabaseManager()

# 1. Çakışma kontrolü
print("1️⃣ ÇAKIŞMA KONTROLÜ:")
schedule_entries = db_manager.get_schedule_by_school_type()
print(f"   📊 Toplam program girişi: {len(schedule_entries)}")

# Çakışmaları bul
conflicts = {}
teacher_conflicts = {}
class_conflicts = {}

for entry in schedule_entries:
    # Öğretmen çakışması
    teacher_key = (entry.teacher_id, entry.day, entry.time_slot)
    if teacher_key in teacher_conflicts:
        teacher_conflicts[teacher_key].append(entry)
    else:
        teacher_conflicts[teacher_key] = [entry]
    
    # Sınıf çakışması  
    class_key = (entry.class_id, entry.day, entry.time_slot)
    if class_key in class_conflicts:
        class_conflicts[class_key].append(entry)
    else:
        class_conflicts[class_key] = [entry]

# Çakışmaları raporla
teacher_conflict_count = 0
class_conflict_count = 0

print("\n   🔴 ÖĞRETMEN ÇAKIŞMALARI:")
for key, entries in teacher_conflicts.items():
    if len(entries) > 1:
        teacher_id, day, slot = key
        teacher = db_manager.get_teacher_by_id(teacher_id)
        teacher_name = teacher.name if teacher else f"ID:{teacher_id}"
        
        print(f"      ⚠️  {teacher_name} - Gün {day+1}, Saat {slot+1}:")
        for entry in entries:
            class_obj = db_manager.get_class_by_id(entry.class_id)
            lesson = db_manager.get_lesson_by_id(entry.lesson_id)
            class_name = class_obj.name if class_obj else f"ID:{entry.class_id}"
            lesson_name = lesson.name if lesson else f"ID:{entry.lesson_id}"
            print(f"         • {class_name}: {lesson_name}")
        teacher_conflict_count += 1

print(f"\n   🔴 SINIF ÇAKIŞMALARI:")
for key, entries in class_conflicts.items():
    if len(entries) > 1:
        class_id, day, slot = key
        class_obj = db_manager.get_class_by_id(class_id)
        class_name = class_obj.name if class_obj else f"ID:{class_id}"
        
        print(f"      ⚠️  {class_name} - Gün {day+1}, Saat {slot+1}:")
        for entry in entries:
            teacher = db_manager.get_teacher_by_id(entry.teacher_id)
            lesson = db_manager.get_lesson_by_id(entry.lesson_id)
            teacher_name = teacher.name if teacher else f"ID:{entry.teacher_id}"
            lesson_name = lesson.name if lesson else f"ID:{entry.lesson_id}"
            print(f"         • {teacher_name}: {lesson_name}")
        class_conflict_count += 1

print(f"\n   📊 Çakışma Özeti:")
print(f"      • Öğretmen çakışması: {teacher_conflict_count}")
print(f"      • Sınıf çakışması: {class_conflict_count}")

# 2. Öğretmen yük analizi
print(f"\n2️⃣ ÖĞRETMEN YÜK ANALİZİ:")
teachers = db_manager.get_all_teachers()

for teacher in teachers:
    teacher_entries = [e for e in schedule_entries if e.teacher_id == teacher.teacher_id]
    actual_hours = len(teacher_entries)
    
    # Beklenen saat hesapla (assignment'lardan)
    expected_hours = 0
    classes = db_manager.get_all_classes()
    for class_obj in classes:
        class_assignments = [e for e in schedule_entries if e.class_id == class_obj.class_id and e.teacher_id == teacher.teacher_id]
        for assignment in class_assignments:
            lesson = db_manager.get_lesson_by_id(assignment.lesson_id)
            if lesson:
                weekly_hours = db_manager.get_weekly_hours_for_lesson(lesson.lesson_id, class_obj.grade)
                if weekly_hours:
                    expected_hours += weekly_hours
                    break  # Aynı dersi bir kez say
    
    if actual_hours != expected_hours:
        print(f"   ⚠️  {teacher.name} ({teacher.subject}):")
        print(f"      • Beklenen: {expected_hours} saat")
        print(f"      • Gerçek: {actual_hours} saat")
        print(f"      • Fark: {actual_hours - expected_hours}")

# 3. Ders atama tablosu kontrolü
print(f"\n3️⃣ DERS ATAMA TABLOSU KONTROLÜ:")
print("   📋 Mevcut atamalar (schedule_entries tablosundan):")

assignment_summary = {}
for entry in schedule_entries:
    class_obj = db_manager.get_class_by_id(entry.class_id)
    teacher = db_manager.get_teacher_by_id(entry.teacher_id)
    lesson = db_manager.get_lesson_by_id(entry.lesson_id)
    
    if class_obj and teacher and lesson:
        key = (class_obj.name, lesson.name, teacher.name)
        if key not in assignment_summary:
            assignment_summary[key] = 0
        assignment_summary[key] += 1

print(f"   📊 Toplam farklı atama: {len(assignment_summary)}")
for (class_name, lesson_name, teacher_name), count in sorted(assignment_summary.items()):
    print(f"      • {class_name}: {lesson_name} ({teacher_name}) - {count} saat")

print(f"\n💡 SORUN TESPİTİ:")
if teacher_conflict_count > 0:
    print(f"   ❌ Öğretmen çakışmaları var!")
if class_conflict_count > 0:
    print(f"   ❌ Sınıf çakışmaları var!")
if len(schedule_entries) > 280:  # 8 sınıf × 35 saat = 280
    print(f"   ❌ Fazla program girişi var! ({len(schedule_entries)} > 280)")
    print(f"   💡 Bu yüzden öğretmen saatleri artıyor!")

print(f"\n🔧 ÖNERİLER:")
print(f"   1. Schedule tablosunu temizle")
print(f"   2. Çakışma kontrolü ekle")
print(f"   3. Scheduler'ı düzelt")