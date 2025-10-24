#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to diagnose schedule distribution problems
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_manager
from algorithms.scheduler import Scheduler

def analyze_current_schedule():
    """Mevcut programı analiz et"""
    print("=" * 80)
    print("📊 MEVCUT PROGRAM ANALİZİ")
    print("=" * 80)
    
    db = db_manager
    
    # Okul tipi
    school_type = db.get_school_type()
    print(f"\n🏫 Okul Türü: {school_type}")
    
    # Sınıflar
    classes = db.get_all_classes()
    print(f"\n📚 Sınıflar: {len(classes)}")
    for c in classes:
        print(f"   • {c.name} (Seviye {c.grade})")
    
    # Öğretmenler
    teachers = db.get_all_teachers()
    print(f"\n👨‍🏫 Öğretmenler: {len(teachers)}")
    teacher_subjects = {}
    for t in teachers:
        if t.subject not in teacher_subjects:
            teacher_subjects[t.subject] = []
        teacher_subjects[t.subject].append(t.name)
    
    for subject, names in sorted(teacher_subjects.items()):
        print(f"   • {subject}: {', '.join(names)}")
    
    # Dersler
    lessons = db.get_all_lessons()
    print(f"\n📖 Dersler: {len(lessons)}")
    for l in lessons:
        print(f"   • {l.name}")
    
    # Ders atamaları (schedule tablosu)
    assignments = db.get_schedule_by_school_type()
    print(f"\n📝 Ders Atamaları: {len(assignments)}")
    
    # Atamaları sınıf bazında grupla
    class_assignments = {}
    for a in assignments:
        if a.class_id not in class_assignments:
            class_assignments[a.class_id] = []
        class_assignments[a.class_id].append(a)
    
    for class_id, class_assigns in sorted(class_assignments.items()):
        class_obj = next((c for c in classes if c.class_id == class_id), None)
        if class_obj:
            print(f"\n   {class_obj.name}:")
            for a in class_assigns:
                lesson_obj = next((l for l in lessons if l.lesson_id == a.lesson_id), None)
                teacher_obj = next((t for t in teachers if t.teacher_id == a.teacher_id), None)
                if lesson_obj and teacher_obj:
                    # Haftalık saat gereksinimini al
                    weekly_hours = db.get_weekly_hours_for_lesson(a.lesson_id, class_obj.grade)
                    print(f"      • {lesson_obj.name} -> {teacher_obj.name} ({weekly_hours if weekly_hours else 0} saat/hafta)")
    
    # Müfredat gereksinimleri
    print(f"\n📋 MÜF REDAT GEREKSİNİMLERİ:")
    total_required = 0
    curriculum_details = {}
    
    for class_obj in classes:
        class_required = 0
        curriculum_details[class_obj.name] = []
        
        for lesson in lessons:
            weekly_hours = db.get_weekly_hours_for_lesson(lesson.lesson_id, class_obj.grade)
            if weekly_hours and weekly_hours > 0:
                # Bu ders bu sınıfa atanmış mı kontrol et
                assignment_key = (class_obj.class_id, lesson.lesson_id)
                has_assignment = any(
                    a.class_id == class_obj.class_id and a.lesson_id == lesson.lesson_id
                    for a in assignments
                )
                
                if has_assignment:
                    class_required += weekly_hours
                    total_required += weekly_hours
                    curriculum_details[class_obj.name].append({
                        'lesson': lesson.name,
                        'hours': weekly_hours
                    })
    
    for class_name, details in sorted(curriculum_details.items()):
        if details:
            class_total = sum(d['hours'] for d in details)
            print(f"\n   {class_name} (Toplam: {class_total} saat/hafta):")
            for d in sorted(details, key=lambda x: -x['hours']):
                print(f"      • {d['lesson']}: {d['hours']} saat")
    
    print(f"\n💰 TOPLAM HAFTALIK SAAT GEREKSİNİMİ: {total_required} saat")
    
    # Oluşturulan program (schedule_program tablosu)
    schedule_program = db.get_schedule_program_by_school_type()
    print(f"\n📅 OLUŞTURULAN PROGRAM: {len(schedule_program)} slot")
    
    if schedule_program:
        # Sınıf bazında dağılım
        class_slots = {}
        for entry in schedule_program:
            if entry.class_id not in class_slots:
                class_slots[entry.class_id] = []
            class_slots[entry.class_id].append(entry)
        
        print(f"\n   Sınıf Bazında Dağılım:")
        for class_id, slots in sorted(class_slots.items()):
            class_obj = next((c for c in classes if c.class_id == class_id), None)
            if class_obj:
                print(f"      • {class_obj.name}: {len(slots)} slot")
        
        # Gün bazında dağılım
        day_names = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
        day_slots = {i: 0 for i in range(5)}
        for entry in schedule_program:
            day_slots[entry.day] += 1
        
        print(f"\n   Gün Bazında Dağılım:")
        for day, count in sorted(day_slots.items()):
            print(f"      • {day_names[day]}: {count} slot")
    
    # Kapsama analizi
    coverage = (len(schedule_program) / total_required * 100) if total_required > 0 else 0
    print(f"\n📊 KAPSAMA ORANI: {coverage:.1f}% ({len(schedule_program)}/{total_required})")
    
    if coverage < 90:
        print(f"\n⚠️  DÜŞÜK KAPSAMA! Hedef: %90+")
        print(f"   • Eksik: {total_required - len(schedule_program)} saat")
    elif coverage < 100:
        print(f"\n⚠️  İYİ AMA EKSİK! Hedef: %100")
        print(f"   • Eksik: {total_required - len(schedule_program)} saat")
    else:
        print(f"\n✅ MÜKEMMEL KAPSAMA!")
    
    return db

def test_algorithm():
    """Algoritma testi"""
    print("\n\n" + "=" * 80)
    print("🧪 ALGORİTMA TESTİ")
    print("=" * 80)
    
    db = db_manager
    
    # Scheduler oluştur
    print("\n📌 Scheduler oluşturuluyor...")
    scheduler = Scheduler(db, use_hybrid=True)
    
    # Programı temizle
    print("🧹 Mevcut program temizleniyor...")
    db.clear_schedule_program()
    
    # Yeni program oluştur
    print("\n🚀 Yeni program oluşturuluyor...\n")
    schedule_entries = scheduler.generate_schedule()
    
    print(f"\n✅ Algoritma tamamlandı: {len(schedule_entries)} slot oluşturuldu")
    
    # Sonuçları analiz et
    analyze_current_schedule()

if __name__ == "__main__":
    print("\n🔍 DERS DAĞITIM SORUNU TANI ARACI")
    print("=" * 80)
    
    # Önce mevcut durumu analiz et
    db = analyze_current_schedule()
    
    # Kullanıcıya sor
    print("\n\n❓ Algoritmayı test etmek ister misiniz? (e/h): ", end="")
    try:
        answer = input().lower().strip()
        if answer == 'e':
            test_algorithm()
        else:
            print("\n👋 Test iptal edildi.")
    except (KeyboardInterrupt, EOFError):
        print("\n\n👋 Çıkış yapıldı.")
