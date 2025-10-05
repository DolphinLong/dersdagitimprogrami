#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simple schedule coverage analysis"""

import sys
import io

# Fix encoding
if sys.platform.startswith('win'):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from database import db_manager

classes = db_manager.get_all_classes()
teachers = db_manager.get_all_teachers()
lessons = db_manager.get_all_lessons()
assignments = db_manager.get_schedule_by_school_type()
schedule = db_manager.get_schedule_program_by_school_type()

print("\n" + "="*70)
print("DERS PROGRAMI KAPSAMA ANALIZI")
print("="*70)

print(f"\nSinif Sayisi: {len(classes)}")
print(f"Ogretmen Sayisi: {len(teachers)}")
print(f"Ders Sayisi: {len(lessons)}")
print(f"Ders Atamalari: {len(assignments)}")
print(f"Programdaki Kayitlar: {len(schedule)}")

# Build assignment map
assignment_map = {}
for assignment in assignments:
    key = (assignment.class_id, assignment.lesson_id)
    assignment_map[key] = assignment.teacher_id

# Calculate expected vs actual
print(f"\n" + "="*70)
print("SINIF BAZLI ANALIZ")
print("="*70)

total_expected = 0
total_actual = 0

for class_obj in classes:
    print(f"\nSinif: {class_obj.name} (Seviye {class_obj.grade})")
    
    # Get expected hours
    class_expected = 0
    class_lessons = []
    
    for lesson in lessons:
        key = (class_obj.class_id, lesson.lesson_id)
        if key in assignment_map:
            weekly_hours = db_manager.get_weekly_hours_for_lesson(
                lesson.lesson_id, class_obj.grade
            )
            if weekly_hours and weekly_hours > 0:
                teacher_id = assignment_map[key]
                teacher = db_manager.get_teacher_by_id(teacher_id)
                if teacher:
                    class_expected += weekly_hours
                    class_lessons.append({
                        'lesson': lesson.name,
                        'lesson_id': lesson.lesson_id,
                        'teacher': teacher.name,
                        'hours': weekly_hours
                    })
    
    # Get actual scheduled
    class_actual = len([s for s in schedule if s.class_id == class_obj.class_id])
    
    print(f"  Beklenen: {class_expected} saat/hafta")
    print(f"  Yerlestirilen: {class_actual} saat")
    
    if class_expected > 0:
        coverage = (class_actual / class_expected * 100)
        print(f"  Kapsama: {coverage:.1f}%")
    
    if class_expected > class_actual:
        print(f"  EKSIK: {class_expected - class_actual} saat!")
    
    # Show details
    if class_lessons:
        print(f"  Dersler:")
        for lesson_info in class_lessons:
            scheduled = len([s for s in schedule 
                           if s.class_id == class_obj.class_id 
                           and s.lesson_id == lesson_info['lesson_id']])
            status = "OK" if scheduled >= lesson_info['hours'] else "EKSIK"
            print(f"    [{status}] {lesson_info['lesson']}: {scheduled}/{lesson_info['hours']} saat (Ogr: {lesson_info['teacher']})")
    
    total_expected += class_expected
    total_actual += class_actual

# Overall summary
print(f"\n" + "="*70)
print("GENEL OZET")
print("="*70)
print(f"Toplam Beklenen: {total_expected} saat")
print(f"Toplam Yerlestirilen: {total_actual} saat")
print(f"Bos Kalan: {total_expected - total_actual} saat")

if total_expected > 0:
    overall = (total_actual / total_expected * 100)
    print(f"Genel Kapsama: {overall:.1f}%")

# Teacher availability analysis
print(f"\n" + "="*70)
print("OGRETMEN UYGUNLUK ANALIZI")
print("="*70)

for teacher in teachers:
    available_count = 0
    for day in range(5):
        for slot in range(8):
            if db_manager.is_teacher_available(teacher.teacher_id, day, slot):
                available_count += 1
    
    teaching_count = len([s for s in schedule if s.teacher_id == teacher.teacher_id])
    
    print(f"\n{teacher.name} ({teacher.subject}):")
    print(f"  Uygun saat sayisi: {available_count}")
    print(f"  Ders veriyor: {teaching_count} saat")
    
    if available_count > 0:
        usage = (teaching_count / available_count * 100)
        print(f"  Kullanim orani: {usage:.0f}%")
        
        if available_count == 0:
            print(f"  SORUN: Hic uygun saat yok!")
        elif usage > 90:
            print(f"  UYARI: Neredeyse tum saatler dolu!")
    else:
        print(f"  SORUN: Hic uygun saat tanimlanmamis!")

print(f"\n" + "="*70)
print("ONERILER:")
print("="*70)
if total_expected > total_actual:
    print("1. Ogretmenlerin uygunluk saatlerini artirin")
    print("2. Tum derslere ogretmen atandigini kontrol edin")
    print("3. Ders yuku dagilimini inceleyin")
else:
    print("Tum dersler basariyla yerlesti!")
