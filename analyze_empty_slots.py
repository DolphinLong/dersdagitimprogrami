#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager

# Initialize database
db_manager = DatabaseManager()

print("🔍 Boş Ders Slotları Analizi")
print("=" * 60)

# Get all assignments
schedule_entries = db_manager.get_schedule_by_school_type()
classes = db_manager.get_all_classes()

print(f"📊 Temel Bilgiler:")
print(f"   • Toplam sınıf: {len(classes)}")
print(f"   • Toplam atama: {len(schedule_entries)}")
print(f"   • Haftalık toplam slot: {len(classes)} sınıf × 5 gün × 4 slot = {len(classes) * 5 * 4}")

# Analyze each class
total_assigned_hours = 0
total_possible_hours = len(classes) * 5 * 4  # 8 sınıf × 5 gün × 4 slot

print(f"\n📚 Sınıf Bazında Analiz:")
for class_obj in classes:
    class_assignments = [e for e in schedule_entries if e.class_id == class_obj.class_id]
    
    # Group by lesson
    lesson_hours = {}
    for assignment in class_assignments:
        lesson = db_manager.get_lesson_by_id(assignment.lesson_id)
        teacher = db_manager.get_teacher_by_id(assignment.teacher_id)
        
        if lesson and teacher:
            if lesson.name not in lesson_hours:
                lesson_hours[lesson.name] = {
                    'teacher': teacher.name,
                    'assigned_hours': 0,
                    'weekly_hours': db_manager.get_weekly_hours_for_lesson(lesson.lesson_id, class_obj.grade) or 0
                }
            lesson_hours[lesson.name]['assigned_hours'] += 1
    
    total_class_hours = sum([info['assigned_hours'] for info in lesson_hours.values()])
    total_assigned_hours += total_class_hours
    
    print(f"\n🏫 {class_obj.name} (Grade {class_obj.grade}):")
    print(f"   📋 Toplam atanmış saat: {total_class_hours}/20 (Kullanım: %{total_class_hours/20*100:.1f})")
    
    for lesson_name, info in lesson_hours.items():
        weekly_hours = info['weekly_hours']
        assigned_hours = info['assigned_hours']
        teacher = info['teacher']
        
        if assigned_hours < weekly_hours:
            print(f"   ⚠️  {lesson_name}: {assigned_hours}/{weekly_hours} saat ({teacher}) - EKSİK!")
        elif assigned_hours > weekly_hours:
            print(f"   ❌ {lesson_name}: {assigned_hours}/{weekly_hours} saat ({teacher}) - FAZLA!")
        else:
            print(f"   ✅ {lesson_name}: {assigned_hours}/{weekly_hours} saat ({teacher})")

# Overall statistics
usage_rate = (total_assigned_hours / total_possible_hours) * 100

print(f"\n📊 GENEL İSTATİSTİKLER:")
print(f"   • Toplam atanmış saat: {total_assigned_hours}")
print(f"   • Toplam mümkün saat: {total_possible_hours}")
print(f"   • Kullanım oranı: %{usage_rate:.1f}")
print(f"   • Boş slot sayısı: {total_possible_hours - total_assigned_hours}")

# Analyze why slots are empty
print(f"\n🔍 BOŞ SLOT NEDENLERİ:")

# 1. Check curriculum requirements
print(f"\n1️⃣ Müfredat Gereksinimleri:")
for class_obj in classes:
    grade = class_obj.grade
    lessons = db_manager.get_all_lessons()
    
    total_required_hours = 0
    for lesson in lessons:
        weekly_hours = db_manager.get_weekly_hours_for_lesson(lesson.lesson_id, grade)
        if weekly_hours and weekly_hours > 0:
            total_required_hours += weekly_hours
    
    print(f"   • {class_obj.name}: Müfredat gereksinimi {total_required_hours} saat/hafta")

# 2. Check teacher availability
print(f"\n2️⃣ Öğretmen Yoğunluğu:")
teachers = db_manager.get_all_teachers()
for teacher in teachers:
    teacher_assignments = [e for e in schedule_entries if e.teacher_id == teacher.teacher_id]
    teacher_hours = len(teacher_assignments)
    max_possible = len(classes) * 5 * 4  # Teorik maksimum
    
    if teacher_hours > 15:  # Yoğun öğretmenler
        print(f"   ⚠️  {teacher.name} ({teacher.subject}): {teacher_hours} saat - ÇOK YOĞUN!")
    elif teacher_hours > 10:
        print(f"   📊 {teacher.name} ({teacher.subject}): {teacher_hours} saat - Normal")
    else:
        print(f"   ✅ {teacher.name} ({teacher.subject}): {teacher_hours} saat - Az yoğun")

# 3. Check lesson distribution
print(f"\n3️⃣ Ders Dağılımı Sorunları:")
lesson_stats = {}
for entry in schedule_entries:
    lesson = db_manager.get_lesson_by_id(entry.lesson_id)
    if lesson:
        if lesson.name not in lesson_stats:
            lesson_stats[lesson.name] = 0
        lesson_stats[lesson.name] += 1

for lesson_name, total_hours in sorted(lesson_stats.items(), key=lambda x: x[1], reverse=True):
    expected_hours = len(classes)  # Her sınıf için en az 1 saat beklenir
    if total_hours < expected_hours:
        print(f"   ⚠️  {lesson_name}: {total_hours} saat (Beklenen: ≥{expected_hours})")

print(f"\n💡 SONUÇ VE ÖNERİLER:")
if usage_rate < 80:
    print(f"   ❌ Kullanım oranı çok düşük (%{usage_rate:.1f})")
    print(f"   🔧 Öneriler:")
    print(f"      • Öğretmen sayısını artır")
    print(f"      • Ders atamalarını yeniden düzenle")
    print(f"      • Müfredat gereksinimlerini kontrol et")
    print(f"      • Scheduler algoritmasını iyileştir")
else:
    print(f"   ✅ Kullanım oranı kabul edilebilir (%{usage_rate:.1f})")