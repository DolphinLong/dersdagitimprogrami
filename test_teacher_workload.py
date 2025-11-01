#!/usr/bin/env python3
"""
Öğretmen yük dağılımı kuralını test et
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.db_manager import DatabaseManager
from algorithms.optimized_curriculum_scheduler import OptimizedCurriculumScheduler

def test_teacher_workload_rule():
    """Öğretmen yük dağılımı kuralını test et"""
    print("🧪 ÖĞRETMEN YÜK DAĞILIMI KURALI TEST EDİLİYOR")
    print("=" * 60)
    print("📋 Kural: Hiçbir öğretmen haftada 1'den fazla gün boş kalmamalı")
    print("")
    
    db = DatabaseManager()
    
    # Optimized curriculum scheduler'ı test et
    scheduler = OptimizedCurriculumScheduler(db)
    
    print("🔍 Program oluşturuluyor...")
    schedule = scheduler.generate_schedule()
    
    print(f"\n📊 Program Özeti:")
    print(f"   • Toplam slot: {len(schedule)}")
    
    # Öğretmen yük analizi
    print(f"\n👨‍🏫 Öğretmen Yük Analizi:")
    
    teachers = db.get_all_teachers()
    violations = 0
    compliant_teachers = 0
    
    for teacher in teachers:
        # Bu öğretmenin çalıştığı günleri bul
        teacher_days = set()
        teacher_lessons = 0
        
        for entry in schedule:
            if entry['teacher_id'] == teacher.teacher_id:
                teacher_days.add(entry['day'])
                teacher_lessons += 1
        
        working_days = len(teacher_days)
        empty_days = 5 - working_days
        
        # Kural kontrolü: En fazla 1 gün boş olabilir
        if empty_days > 1:
            violations += 1
            print(f"   ❌ {teacher.name}: {working_days} gün çalışıyor, {empty_days} gün boş (İHLAL)")
            print(f"      Çalışma günleri: {sorted([f'Gün {d+1}' for d in teacher_days])}")
        elif empty_days == 1:
            compliant_teachers += 1
            print(f"   ✅ {teacher.name}: {working_days} gün çalışıyor, {empty_days} gün boş (UYGUN)")
        elif empty_days == 0:
            compliant_teachers += 1
            print(f"   ✅ {teacher.name}: {working_days} gün çalışıyor, {empty_days} gün boş (MÜKEMMEL)")
        
        # Detay bilgi
        if teacher_lessons > 0:
            print(f"      Toplam ders saati: {teacher_lessons}")
    
    print(f"\n📈 Özet:")
    print(f"   • Toplam öğretmen: {len(teachers)}")
    print(f"   • Kurala uygun: {compliant_teachers}")
    print(f"   • Kural ihlali: {violations}")
    
    if violations == 0:
        print(f"   🎉 Tüm öğretmenler kurala uygun!")
        compliance_rate = 100.0
    else:
        compliance_rate = (compliant_teachers / len(teachers)) * 100
        print(f"   ⚠️  Uygunluk oranı: {compliance_rate:.1f}%")
    
    # Detaylı analiz
    print(f"\n📋 Detaylı Günlük Analiz:")
    
    # Her gün kaç öğretmen çalışıyor
    daily_teacher_count = {day: set() for day in range(5)}
    
    for entry in schedule:
        daily_teacher_count[entry['day']].add(entry['teacher_id'])
    
    day_names = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma']
    
    for day in range(5):
        teacher_count = len(daily_teacher_count[day])
        print(f"   • {day_names[day]}: {teacher_count} öğretmen çalışıyor")
    
    return violations == 0

if __name__ == "__main__":
    success = test_teacher_workload_rule()
    if success:
        print("\n✅ Öğretmen yük dağılımı kuralı başarıyla uygulanıyor!")
    else:
        print("\n⚠️  Öğretmen yük dağılımı kuralında iyileştirme gerekiyor.")
        print("💡 Sistem otomatik olarak dersleri yeniden dağıtmaya çalışacak.")