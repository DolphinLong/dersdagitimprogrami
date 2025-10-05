#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ders programı kapsama analizini yapan script
"""

import sys
import io

# Fix encoding for Windows
if sys.platform.startswith('win'):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from database import db_manager

def analyze_schedule_coverage():
    """Analyze schedule coverage and identify gaps"""
    
    print("\n" + "="*80)
    print("DERS PROGRAMI KAPSAMA ANALIZI")
    print("="*80)
    
    # Get basic data
    classes = db_manager.get_all_classes()
    teachers = db_manager.get_all_teachers()
    lessons = db_manager.get_all_lessons()
    assignments = db_manager.get_schedule_by_school_type()
    schedule = db_manager.get_schedule_program_by_school_type()
    
    school_type = db_manager.get_school_type() or "Lise"
    
    # Time slots per day
    time_slots = 8  # Most schools have 8 periods
    days = 5  # Monday to Friday
    
    print(f"\nOkul Turu: {school_type}")
    print(f"Sinif Sayisi: {len(classes)}")
    print(f"Ogretmen Sayisi: {len(teachers)}")
    print(f"Ders Sayisi: {len(lessons)}")
    print(f"Ders Atamalari: {len(assignments)}")
    print(f"Mevcut Program Kayitlari: {len(schedule)}")
    
    # Build assignment map
    assignment_map = {}
    for assignment in assignments:
        key = (assignment.class_id, assignment.lesson_id)
        assignment_map[key] = assignment.teacher_id
    
    # Calculate expected vs actual
    print(f"\n{'='*80}")
    print(f"SINIF BAZLI ANALİZ")
    print(f"{'='*80}")
    
    total_expected = 0
    total_actual = 0
    
    for class_obj in classes:
        print(f"\n📚 Sınıf: {class_obj.name} (Seviye {class_obj.grade})")
        
        # Get expected hours for this class
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
                            'teacher': teacher.name,
                            'hours': weekly_hours
                        })
        
        # Get actual hours scheduled
        class_actual = len([s for s in schedule if s.class_id == class_obj.class_id])
        
        print(f"   Beklenen Toplam: {class_expected} saat/hafta")
        print(f"   Yerleştirilen: {class_actual} saat")
        
        coverage = (class_actual / class_expected * 100) if class_expected > 0 else 0
        print(f"   Kapsama Oranı: {coverage:.1f}%")
        
        if class_expected > class_actual:
            print(f"   ⚠️  EKSİK: {class_expected - class_actual} saat yerleştirilmedi!")
        
        if class_lessons:
            print(f"   Dersler:")
            for lesson_info in class_lessons:
                # Count how many hours scheduled for this lesson
                scheduled = len([s for s in schedule 
                               if s.class_id == class_obj.class_id 
                               and s.lesson_id == next((l.lesson_id for l in lessons if l.name == lesson_info['lesson']), None)])
                status = "✅" if scheduled >= lesson_info['hours'] else "❌"
                print(f"      {status} {lesson_info['lesson']}: {scheduled}/{lesson_info['hours']} saat (Öğretmen: {lesson_info['teacher']})")
        
        total_expected += class_expected
        total_actual += class_actual
        
        # Show empty cells
        empty_cells = class_expected - class_actual
        if empty_cells > 0:
            print(f"   🔴 {empty_cells} boş hücre var!")
    
    # Overall summary
    print(f"\n{'='*80}")
    print(f"GENEL ÖZET")
    print(f"{'='*80}")
    print(f"📊 Toplam Beklenen: {total_expected} saat")
    print(f"✅ Toplam Yerleştirilen: {total_actual} saat")
    print(f"❌ Boş Kalan: {total_expected - total_actual} saat")
    
    overall_coverage = (total_actual / total_expected * 100) if total_expected > 0 else 0
    print(f"📈 Genel Kapsama Oranı: {overall_coverage:.1f}%")
    
    # Maximum possible cells
    max_cells = len(classes) * days * time_slots
    print(f"\n📦 Maksimum Hücre Sayısı: {max_cells} ({len(classes)} sınıf × {days} gün × {time_slots} saat)")
    print(f"🎯 Doldurulması Gereken: {total_expected} hücre")
    print(f"✅ Dolduruldu: {total_actual} hücre")
    print(f"⬜ Boş Kalacak (normal): {max_cells - total_expected} hücre")
    print(f"🔴 Boş Kalmaması Gereken: {total_expected - total_actual} hücre")
    
    # Analyze why lessons couldn't be placed
    if total_expected > total_actual:
        print(f"\n{'='*80}")
        print(f"SORUN ANALİZİ - Neden Bazı Dersler Yerleştirilemedi?")
        print(f"{'='*80}")
        
        # Check teacher availability
        print(f"\n👨‍🏫 Öğretmen Uygunluk Durumu:")
        for teacher in teachers:
            available_slots = 0
            for day in range(5):
                for slot in range(8):
                    if db_manager.is_teacher_available(teacher.teacher_id, day, slot):
                        available_slots += 1
            
            teaching_slots = len([s for s in schedule if s.teacher_id == teacher.teacher_id])
            utilization = (teaching_slots / available_slots * 100) if available_slots > 0 else 0
            
            status = "✅" if available_slots > teaching_slots else "⚠️"
            print(f"   {status} {teacher.name} ({teacher.subject}): {teaching_slots}/{available_slots} kullanım ({utilization:.0f}%)")
            
            if available_slots == 0:
                print(f"      🔴 SORUN: Hiç uygun saat yok!")
            elif teaching_slots > available_slots * 0.9:
                print(f"      ⚠️  UYARI: Neredeyse tüm uygun saatler dolu!")
        
        # Check assignments without teachers
        print(f"\n🔗 Ders Atama Durumu:")
        for class_obj in classes:
            for lesson in lessons:
                key = (class_obj.class_id, lesson.lesson_id)
                if key in assignment_map:
                    weekly_hours = db_manager.get_weekly_hours_for_lesson(
                        lesson.lesson_id, class_obj.grade
                    )
                    if weekly_hours and weekly_hours > 0:
                        teacher_id = assignment_map[key]
                        teacher = db_manager.get_teacher_by_id(teacher_id)
                        if not teacher:
                            print(f"   ❌ {class_obj.name} - {lesson.name}: Atanmış öğretmen bulunamadı!")
        
        print(f"\n💡 ÖNERİLER:")
        print(f"   1. Öğretmenlerin uygunluk saatlerini artırın")
        print(f"   2. Tüm derslere öğretmen atandığından emin olun")
        print(f"   3. Öğretmen sayısını/ders yükü dağılımını kontrol edin")
        print(f"   4. Bazı derslerin haftalık saat sayısını azaltmayı düşünün")

if __name__ == "__main__":
    analyze_schedule_coverage()
