#!/usr/bin/env python3
"""
UI ders atama işlevlerini test et
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.db_manager import DatabaseManager

def test_missing_assignments():
    """Eksik atamaları test et"""
    print("🔍 Eksik Atamalar Test Ediliyor...")
    
    db = DatabaseManager()
    
    # Eksik atamaları bul
    missing = db.find_missing_assignments()
    
    print(f"📊 Sonuçlar:")
    print(f"   • Eksik atamaya sahip sınıf sayısı: {len(missing)}")
    
    total_missing = 0
    for class_id, data in missing.items():
        class_obj = data["class"]
        missing_lessons = data["missing_lessons"]
        total_missing += len(missing_lessons)
        print(f"   • {class_obj.name}: {len(missing_lessons)} eksik ders")
        
        # İlk 3 eksik dersi göster
        for i, (lesson_id, lesson_name, weekly_hours) in enumerate(missing_lessons[:3]):
            print(f"     - {lesson_name} ({weekly_hours} saat/hafta)")
        
        if len(missing_lessons) > 3:
            print(f"     ... ve {len(missing_lessons) - 3} ders daha")
    
    print(f"   • Toplam eksik atama: {total_missing}")
    
    return len(missing) > 0

def test_auto_fill():
    """Otomatik doldurma test et"""
    print("\n🤖 Otomatik Doldurma Test Ediliyor...")
    
    db = DatabaseManager()
    
    # Mevcut atama sayısını al
    assignments_before = db.get_schedule_by_school_type()
    print(f"   • Önceki atama sayısı: {len(assignments_before)}")
    
    # Otomatik doldur
    result = db.auto_fill_assignments()
    
    # Sonuçları göster
    success_count = len(result["success"])
    failed_count = len(result["failed"])
    
    print(f"   • Başarılı atamalar: {success_count}")
    print(f"   • Başarısız atamalar: {failed_count}")
    
    if success_count > 0:
        print("   ✅ Başarılı atamalar (ilk 5):")
        for i, (class_name, lesson_name, teacher_name) in enumerate(result["success"][:5]):
            print(f"     {i+1}. {class_name}: {lesson_name} → {teacher_name}")
    
    if failed_count > 0:
        print("   ❌ Başarısız atamalar (ilk 5):")
        for i, (class_name, lesson_name, reason) in enumerate(result["failed"][:5]):
            print(f"     {i+1}. {class_name}: {lesson_name} - {reason}")
    
    # Yeni atama sayısını kontrol et
    assignments_after = db.get_schedule_by_school_type()
    print(f"   • Sonraki atama sayısı: {len(assignments_after)}")
    print(f"   • Eklenen atama sayısı: {len(assignments_after) - len(assignments_before)}")
    
    return success_count > 0

if __name__ == "__main__":
    print("🧪 UI DERS ATAMA İŞLEVLERİ TEST EDİLİYOR")
    print("=" * 50)
    
    # Test 1: Eksik atamaları bul
    has_missing = test_missing_assignments()
    
    # Test 2: Otomatik doldur (sadece eksik varsa)
    if has_missing:
        auto_fill_success = test_auto_fill()
        
        if auto_fill_success:
            print("\n✅ Otomatik doldurma başarılı!")
        else:
            print("\n⚠️  Otomatik doldurma başarısız veya eksik atama yok!")
    else:
        print("\n✅ Tüm atamalar zaten mevcut!")
    
    print("\n" + "=" * 50)
    print("✅ UI ders atama işlevleri test tamamlandı!")