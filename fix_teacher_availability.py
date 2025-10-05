#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Teacher Availability Checking in Scheduler
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager

def main():
    """Fix teacher availability checking"""
    print("🔧 ÖĞRETMEN UYGUNLUK KONTROLÜ DÜZELTİLİYOR")
    print("="*60)
    
    db_manager = DatabaseManager()
    
    # Get all teachers
    teachers = db_manager.get_all_teachers()
    print(f"📊 Toplam öğretmen sayısı: {len(teachers)}")
    
    # Check current availability data
    print(f"\n🔍 Mevcut uygunluk verilerini kontrol ediliyor...")
    
    total_availability_records = 0
    teachers_with_availability = 0
    
    for teacher in teachers:
        availability = db_manager.get_teacher_availability(teacher.teacher_id)
        if availability:
            teachers_with_availability += 1
            total_availability_records += len(availability)
            print(f"   📋 {teacher.name}: {len(availability)} uygunluk kaydı")
        else:
            print(f"   ⚠️  {teacher.name}: Uygunluk kaydı yok (varsayılan: müsait)")
    
    print(f"\n📊 Özet:")
    print(f"   Uygunluk kaydı olan öğretmenler: {teachers_with_availability}/{len(teachers)}")
    print(f"   Toplam uygunluk kaydı: {total_availability_records}")
    
    if total_availability_records == 0:
        print(f"\n⚠️  HİÇ UYGUNLUK KAYDI YOK!")
        print(f"   Bu yüzden scheduler öğretmen uygunluklarını kontrol etmiyor.")
        print(f"   Çözüm seçenekleri:")
        print(f"   A) Tüm öğretmenleri varsayılan olarak müsait yap")
        print(f"   B) Öğretmen uygunluklarını manuel olarak ayarla")
        print(f"   C) Scheduler'ı uygunluk kontrolü olmadan çalıştır")
        
        choice = input(f"\nHangi çözümü uygulayalım? (A/B/C): ").upper()
        
        if choice == "A":
            print(f"\n🔧 Çözüm A: Tüm öğretmenleri varsayılan olarak müsait yapıyoruz")
            print(f"   • 5 gün × 8 saat = 40 slot/öğretmen")
            print(f"   • Tüm slotları müsait olarak işaretle")
            
            success_count = 0
            for teacher in teachers:
                print(f"   📝 {teacher.name} için uygunluk ayarlanıyor...")
                
                for day in range(5):  # Pazartesi-Cuma
                    for time_slot in range(8):  # 8 saat
                        if db_manager.set_teacher_availability(teacher.teacher_id, day, time_slot, True):
                            success_count += 1
                
                print(f"      ✅ {teacher.name}: 40 slot müsait olarak işaretlendi")
            
            print(f"\n✅ Toplam {success_count} uygunluk kaydı oluşturuldu")
            
        elif choice == "B":
            print(f"\n🔧 Çözüm B: Öğretmen uygunluklarını manuel olarak ayarlayın")
            print(f"   • GUI'den öğretmen düzenleme ekranını kullanın")
            print(f"   • Her öğretmen için uygunluk saatlerini belirleyin")
            print(f"   • Scheduler bu ayarları dikkate alacak")
            
        elif choice == "C":
            print(f"\n🔧 Çözüm C: Scheduler'ı uygunluk kontrolü olmadan çalıştır")
            print(f"   • Mevcut scheduler'ı güncelleyeceğiz")
            print(f"   • Uygunluk kontrolünü devre dışı bırakacağız")
            
            # Update scheduler to skip availability check
            scheduler_file = "algorithms/scheduler.py"
            print(f"   📝 {scheduler_file} güncelleniyor...")
            
            # This would require modifying the scheduler code
            print(f"   ⚠️  Bu seçenek için scheduler kodunu manuel olarak güncellemeniz gerekiyor")
            
        else:
            print(f"❌ Geçersiz seçim!")
    
    else:
        print(f"\n✅ Uygunluk kayıtları mevcut!")
        print(f"   Scheduler bu kayıtları kullanmalı.")
        
        # Test availability checking
        print(f"\n🧪 Uygunluk kontrolü test ediliyor...")
        
        test_teacher = teachers[0] if teachers else None
        if test_teacher:
            print(f"   Test öğretmeni: {test_teacher.name}")
            
            # Test a few slots
            for day in range(2):  # Test first 2 days
                for time_slot in range(3):  # Test first 3 slots
                    is_available = db_manager.is_teacher_available(test_teacher.teacher_id, day, time_slot)
                    print(f"      Day {day+1}, Slot {time_slot+1}: {'Müsait' if is_available else 'Müsait değil'}")
    
    print(f"\n🎉 Öğretmen uygunluk kontrolü analizi tamamlandı!")

if __name__ == "__main__":
    main()