#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
İyileştirilmiş algoritma test scripti
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_manager
from algorithms.simple_perfect_scheduler import SimplePerfectScheduler

def test_improved_algorithm():
    """İyileştirilmiş algoritmayı test et"""
    
    print("=" * 80)
    print("🧪 İYİLEŞTİRİLMİŞ ALGORİTMA TESTİ")
    print("=" * 80)
    
    # Mevcut program kayıtlarını temizle
    print("\n🧹 Mevcut program temizleniyor...")
    db_manager.clear_schedule()
    
    # SimplePerfectScheduler ile test et (relaxed_mode=False, normal mod)
    print("\n🚀 Normal Mod ile Program Oluşturuluyor...")
    print("   • Öğretmen uygunluğu kontrol edilir")
    print("   • Ultra aggressive gap filling aktif")
    print()
    
    scheduler = SimplePerfectScheduler(db_manager, relaxed_mode=False)
    schedule_entries = scheduler.generate_schedule()
    
    print("\n" + "=" * 80)
    print("📊 SONUÇ ANALİZİ")
    print("=" * 80)
    
    # Kapsama analizi
    classes = db_manager.get_all_classes()
    lessons = db_manager.get_all_lessons()
    assignments = db_manager.get_schedule_by_school_type()
    
    assignment_map = {(a.class_id, a.lesson_id): a.teacher_id for a in assignments}
    
    total_required = 0
    total_scheduled = len(schedule_entries)
    
    class_details = {}
    
    for class_obj in classes:
        class_required = 0
        class_scheduled = 0
        
        for lesson in lessons:
            key = (class_obj.class_id, lesson.lesson_id)
            if key in assignment_map:
                weekly_hours = db_manager.get_weekly_hours_for_lesson(lesson.lesson_id, class_obj.grade)
                if weekly_hours and weekly_hours > 0:
                    class_required += weekly_hours
                    total_required += weekly_hours
                    
                    # Mevcut yerleşme
                    current_count = sum(
                        1 for entry in schedule_entries
                        if entry["class_id"] == class_obj.class_id
                        and entry["lesson_id"] == lesson.lesson_id
                    )
                    class_scheduled += current_count
        
        class_details[class_obj.name] = {
            'required': class_required,
            'scheduled': class_scheduled,
            'coverage': (class_scheduled / class_required * 100) if class_required > 0 else 0
        }
    
    # Sonuçları göster
    print(f"\n📋 Toplam Gereksinim: {total_required} saat")
    print(f"✅ Toplam Yerleşen: {total_scheduled} saat")
    coverage = (total_scheduled / total_required * 100) if total_required > 0 else 0
    print(f"📊 Kapsama Oranı: {coverage:.1f}%")
    
    print(f"\n📚 Sınıf Bazında Detaylar:")
    for class_name, details in sorted(class_details.items()):
        status = "✅" if details['coverage'] >= 100 else "⚠️" if details['coverage'] >= 95 else "❌"
        print(f"   {status} {class_name}: {details['scheduled']}/{details['required']} ({details['coverage']:.1f}%)")
    
    # Başarı durumu
    print("\n" + "=" * 80)
    if coverage >= 100:
        print("🎉 MÜKEMMEL! %100 KAPSAMA SAĞLANDI!")
    elif coverage >= 98:
        print("✅ ÇOK İYİ! %98+ Kapsama")
    elif coverage >= 95:
        print("✅ İYİ! %95+ Kapsama")
    else:
        print("⚠️  Daha fazla iyileştirme gerekiyor")
    print("=" * 80)
    
    # Çakışma kontrolü
    print("\n🔍 Çakışma Kontrolü...")
    conflicts = detect_conflicts(schedule_entries)
    if conflicts:
        print(f"   ⚠️  {len(conflicts)} çakışma tespit edildi!")
    else:
        print(f"   ✅ Çakışma yok!")
    
    return schedule_entries

def detect_conflicts(schedule_entries):
    """Çakışmaları tespit et"""
    conflicts = []
    
    # Öğretmen çakışmaları
    teacher_slots = {}
    for entry in schedule_entries:
        key = (entry["teacher_id"], entry["day"], entry["time_slot"])
        if key in teacher_slots:
            conflicts.append({
                "type": "teacher_conflict",
                "entry1": teacher_slots[key],
                "entry2": entry
            })
        else:
            teacher_slots[key] = entry
    
    # Sınıf çakışmaları
    class_slots = {}
    for entry in schedule_entries:
        key = (entry["class_id"], entry["day"], entry["time_slot"])
        if key in class_slots:
            conflicts.append({
                "type": "class_conflict",
                "entry1": class_slots[key],
                "entry2": entry
            })
        else:
            class_slots[key] = entry
    
    return conflicts

if __name__ == "__main__":
    try:
        schedule = test_improved_algorithm()
        print(f"\n✅ Test tamamlandı! {len(schedule)} slot oluşturuldu.")
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        import traceback
        traceback.print_exc()
