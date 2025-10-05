#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Make All Teachers Available for Better Schedule Coverage
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager

def main():
    """Make all teachers available for better coverage"""
    print("🔧 TÜM ÖĞRETMENLERİ MÜSAİT YAPIYOR")
    print("="*50)
    
    db_manager = DatabaseManager()
    
    # Get all teachers
    teachers = db_manager.get_all_teachers()
    print(f"📊 Toplam öğretmen sayısı: {len(teachers)}")
    
    # Make all teachers available for all time slots
    print(f"\n📝 Tüm öğretmenler için uygunluk ayarlanıyor...")
    
    success_count = 0
    total_slots = 0
    
    for teacher in teachers:
        print(f"   📋 {teacher.name} için uygunluk ayarlanıyor...")
        
        teacher_success = 0
        for day in range(5):  # Pazartesi-Cuma
            for time_slot in range(8):  # 8 saat
                if db_manager.set_teacher_availability(teacher.teacher_id, day, time_slot, True):
                    teacher_success += 1
                    success_count += 1
                total_slots += 1
        
        print(f"      ✅ {teacher.name}: {teacher_success}/40 slot müsait olarak işaretlendi")
    
    print(f"\n📊 Özet:")
    print(f"   Toplam slot: {total_slots}")
    print(f"   Başarılı ayarlama: {success_count}")
    print(f"   Başarı oranı: {(success_count/total_slots*100):.1f}%")
    
    # Test a few teachers
    print(f"\n🧪 Test: Birkaç öğretmenin uygunluğunu kontrol ediliyor...")
    
    for i, teacher in enumerate(teachers[:3]):  # Test first 3 teachers
        print(f"   📋 {teacher.name}:")
        for day in range(2):  # Test first 2 days
            for time_slot in range(3):  # Test first 3 slots
                is_available = db_manager.is_teacher_available(teacher.teacher_id, day, time_slot)
                status = "✅ Müsait" if is_available else "❌ Müsait değil"
                print(f"      Day {day+1}, Slot {time_slot+1}: {status}")
    
    print(f"\n🎉 Tüm öğretmenler müsait olarak ayarlandı!")
    print(f"   Artık scheduler daha iyi sonuçlar verecek.")

if __name__ == "__main__":
    main()