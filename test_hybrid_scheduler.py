# -*- coding: utf-8 -*-
"""
Hybrid Optimal Scheduler Test Script
Yeni iyileştirmeleri test eder
"""

import sys
import os

# Project path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
from algorithms.scheduler import Scheduler


def test_hybrid_scheduler():
    """Hybrid scheduler'ı test et"""
    print("\n" + "="*80)
    print("🧪 HYBRID OPTIMAL SCHEDULER TEST")
    print("="*80)
    
    # Database bağlantısı
    db = DatabaseManager()
    
    # Okul tipi kontrolü
    school_type = db.get_school_type()
    print(f"\n📚 Okul Tipi: {school_type}")
    
    # İstatistikler
    classes = db.get_all_classes()
    teachers = db.get_all_teachers()
    lessons = db.get_all_lessons()
    assignments = db.get_schedule_by_school_type()
    
    print(f"\n📊 Mevcut Veriler:")
    print(f"   • Sınıflar: {len(classes)}")
    print(f"   • Öğretmenler: {len(teachers)}")
    print(f"   • Dersler: {len(lessons)}")
    print(f"   • Atamalar: {len(assignments)}")
    
    if len(assignments) == 0:
        print("\n⚠️  UYARI: Ders ataması yok! Önce ders atama yapılmalı.")
        return
    
    # Scheduler oluştur (hybrid mode aktif)
    print("\n🚀 Hybrid Optimal Scheduler başlatılıyor...")
    scheduler = Scheduler(db, use_hybrid=True)
    
    # Program oluştur
    print("\n🎯 Program oluşturuluyor...\n")
    schedule = scheduler.generate_schedule()
    
    # Sonuç analizi
    print("\n" + "="*80)
    print("📊 TEST SONUÇLARI")
    print("="*80)
    
    if schedule:
        print(f"✅ Program başarıyla oluşturuldu!")
        print(f"   • Toplam kayıt: {len(schedule)}")
        
        # Sınıf bazlı analiz
        class_counts = {}
        for entry in schedule:
            class_id = entry['class_id']
            class_counts[class_id] = class_counts.get(class_id, 0) + 1
        
        print(f"\n📈 Sınıf Bazlı Dağılım:")
        for class_obj in classes:
            count = class_counts.get(class_obj.class_id, 0)
            print(f"   • {class_obj.name}: {count} saat")
        
        # Öğretmen bazlı analiz
        teacher_counts = {}
        for entry in schedule:
            teacher_id = entry['teacher_id']
            teacher_counts[teacher_id] = teacher_counts.get(teacher_id, 0) + 1
        
        print(f"\n👨‍🏫 Öğretmen Bazlı Dağılım:")
        for teacher in teachers[:10]:  # İlk 10 öğretmen
            count = teacher_counts.get(teacher.teacher_id, 0)
            print(f"   • {teacher.name}: {count} saat")
        
        # Çakışma kontrolü
        print(f"\n🔍 Çakışma Kontrolü:")
        conflicts = detect_conflicts(schedule)
        if conflicts:
            print(f"   ⚠️  {len(conflicts)} çakışma tespit edildi")
            for i, conflict in enumerate(conflicts[:5], 1):
                print(f"      {i}. {conflict['type']}")
        else:
            print(f"   ✅ Çakışma yok!")
        
    else:
        print(f"❌ Program oluşturulamadı!")
    
    print("\n" + "="*80)
    print("✅ TEST TAMAMLANDI")
    print("="*80)


def detect_conflicts(schedule):
    """Basit çakışma tespiti"""
    from collections import defaultdict
    
    conflicts = []
    
    # Öğretmen çakışmaları
    teacher_slots = defaultdict(list)
    for entry in schedule:
        key = (entry['teacher_id'], entry['day'], entry['time_slot'])
        teacher_slots[key].append(entry)
    
    for key, entries in teacher_slots.items():
        if len(entries) > 1:
            conflicts.append({'type': 'teacher_conflict', 'entries': entries})
    
    # Sınıf çakışmaları
    class_slots = defaultdict(list)
    for entry in schedule:
        key = (entry['class_id'], entry['day'], entry['time_slot'])
        class_slots[key].append(entry)
    
    for key, entries in class_slots.items():
        if len(entries) > 1:
            conflicts.append({'type': 'class_conflict', 'entries': entries})
    
    return conflicts


def test_individual_modules():
    """Bireysel modülleri test et"""
    print("\n" + "="*80)
    print("🧪 BİREYSEL MODÜL TESTLERİ")
    print("="*80)
    
    db = DatabaseManager()
    
    # 1. CSP Solver Test
    print("\n1️⃣ CSP Solver Testi:")
    try:
        from algorithms.csp_solver import CSPSolver, ArcConsistency
        print("   ✅ CSP Solver modülü yüklendi")
        
        ac3 = ArcConsistency()
        print(f"   ✅ Arc Consistency örneği oluşturuldu")
    except Exception as e:
        print(f"   ❌ Hata: {e}")
    
    # 2. Soft Constraints Test
    print("\n2️⃣ Soft Constraints Testi:")
    try:
        from algorithms.soft_constraints import SoftConstraintManager
        print("   ✅ Soft Constraints modülü yüklendi")
        
        scm = SoftConstraintManager(db)
        print(f"   ✅ {len(scm.constraints)} constraint tanımlandı")
        print(f"\n{scm.get_constraint_summary()}")
    except Exception as e:
        print(f"   ❌ Hata: {e}")
    
    # 3. Local Search Test
    print("\n3️⃣ Local Search Testi:")
    try:
        from algorithms.local_search import SimulatedAnnealing, adaptive_backtrack_limit
        print("   ✅ Local Search modülü yüklendi")
        
        limit = adaptive_backtrack_limit(8, 12, 10)
        print(f"   ✅ Adaptif backtrack limiti: {limit}")
    except Exception as e:
        print(f"   ❌ Hata: {e}")
    
    # 4. Heuristics Test
    print("\n4️⃣ Heuristics Testi:")
    try:
        from algorithms.heuristics import HeuristicManager, ScheduleHeuristics
        print("   ✅ Heuristics modülü yüklendi")
        
        hm = HeuristicManager()
        print(f"   ✅ Heuristic Manager oluşturuldu")
    except Exception as e:
        print(f"   ❌ Hata: {e}")
    
    # 5. Explainer Test
    print("\n5️⃣ Explainer Testi:")
    try:
        from algorithms.scheduler_explainer import SchedulerExplainer
        print("   ✅ Explainer modülü yüklendi")
        
        explainer = SchedulerExplainer(db)
        print(f"   ✅ Explainer oluşturuldu")
    except Exception as e:
        print(f"   ❌ Hata: {e}")


if __name__ == "__main__":
    print("\n🎯 Hangi test çalıştırılsın?")
    print("1. Hybrid Scheduler Test (Ana Test)")
    print("2. Bireysel Modül Testleri")
    print("3. Her İkisi")
    
    choice = input("\nSeçim (1-3): ").strip()
    
    if choice == "1":
        test_hybrid_scheduler()
    elif choice == "2":
        test_individual_modules()
    elif choice == "3":
        test_individual_modules()
        print("\n" + "="*80 + "\n")
        test_hybrid_scheduler()
    else:
        print("Geçersiz seçim!")
