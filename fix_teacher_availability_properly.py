#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Teacher Availability Properly - Make All Teachers Available for All Slots
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager

def main():
    """Fix teacher availability properly"""
    print("🔧 ÖĞRETMEN UYGUNLUKLARINI DÜZELTİYOR")
    print("="*50)
    
    db_manager = DatabaseManager()
    
    # Get all teachers
    teachers = db_manager.get_all_teachers()
    print(f"📊 Toplam öğretmen sayısı: {len(teachers)}")
    
    # Clear all existing availability records
    print(f"\n🗑️ Mevcut uygunluk kayıtlarını temizliyor...")
    
    try:
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM teacher_availability")
        conn.commit()
        print(f"   ✅ Tüm uygunluk kayıtları silindi")
    except Exception as e:
        print(f"   ❌ Hata: {e}")
    
    # Set all teachers available for ALL time slots
    print(f"\n📝 Tüm öğretmenleri TÜM saatlerde müsait yapıyor...")
    
    success_count = 0
    total_attempts = 0
    
    for teacher in teachers:
        print(f"   📋 {teacher.name} için uygunluk ayarlanıyor...")
        
        teacher_success = 0
        for day in range(5):  # Pazartesi-Cuma
            for time_slot in range(8):  # 8 saat
                total_attempts += 1
                if db_manager.set_teacher_availability(teacher.teacher_id, day, time_slot, True):
                    success_count += 1
                    teacher_success += 1
        
        print(f"      ✅ {teacher.name}: {teacher_success}/40 slot müsait olarak işaretlendi")
    
    print(f"\n📊 Özet:")
    print(f"   Toplam deneme: {total_attempts}")
    print(f"   Başarılı: {success_count}")
    print(f"   Başarı oranı: {(success_count/total_attempts*100):.1f}%")
    
    # Verify the changes
    print(f"\n🧪 Değişiklikleri doğruluyor...")
    
    for teacher in teachers[:3]:  # Test first 3 teachers
        print(f"   📋 {teacher.name}:")
        
        available_count = 0
        unavailable_count = 0
        
        for day in range(2):  # Test first 2 days
            day_name = ["Pazartesi", "Salı"][day]
            print(f"      {day_name}:")
            
            for time_slot in range(8):  # 8 saat
                is_available = db_manager.is_teacher_available(teacher.teacher_id, day, time_slot)
                status = "✅ Müsait" if is_available else "❌ Müsait değil"
                print(f"         Slot {time_slot+1}: {status}")
                
                if is_available:
                    available_count += 1
                else:
                    unavailable_count += 1
        
        print(f"      📊 {teacher.name}: {available_count} müsait, {unavailable_count} müsait değil")
    
    print(f"\n🎉 Öğretmen uygunlukları düzeltildi!")
    print(f"   Artık tüm öğretmenler tüm saatlerde müsait.")

if __name__ == "__main__":
    main()