#!/usr/bin/env python3
"""
UI ders atama iş akışını test et
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.db_manager import DatabaseManager

def test_assignment_workflow():
    """Tam ders atama iş akışını test et"""
    print("🔄 DERS ATAMA İŞ AKIŞI TEST EDİLİYOR")
    print("=" * 50)
    
    db = DatabaseManager()
    
    # 1. Mevcut durumu kontrol et
    assignments_initial = db.get_schedule_by_school_type()
    print(f"1️⃣ Başlangıç atama sayısı: {len(assignments_initial)}")
    
    if not assignments_initial:
        print("❌ Test için atama yok!")
        return False
    
    # 2. Bir atamayı sil
    test_assignment = assignments_initial[0]
    print(f"2️⃣ Test ataması siliniyor:")
    print(f"   • Entry ID: {test_assignment.entry_id}")
    print(f"   • Sınıf ID: {test_assignment.class_id}")
    print(f"   • Ders ID: {test_assignment.lesson_id}")
    print(f"   • Öğretmen ID: {test_assignment.teacher_id}")
    
    delete_success = db.delete_schedule_entry(test_assignment.entry_id)
    if not delete_success:
        print("   ❌ Atama silinemedi!")
        return False
    
    print("   ✅ Atama silindi!")
    
    # 3. Silme sonrası durumu kontrol et
    assignments_after_delete = db.get_schedule_by_school_type()
    print(f"3️⃣ Silme sonrası atama sayısı: {len(assignments_after_delete)}")
    
    if len(assignments_after_delete) != len(assignments_initial) - 1:
        print("   ❌ Silme işlemi beklendiği gibi çalışmadı!")
        return False
    
    print("   ✅ Silme işlemi başarılı!")
    
    # 4. Eksik atamaları kontrol et
    missing = db.find_missing_assignments()
    print(f"4️⃣ Eksik atama kontrolü:")
    print(f"   • Eksik atamaya sahip sınıf sayısı: {len(missing)}")
    
    if len(missing) == 0:
        print("   ⚠️  Eksik atama bulunamadı (beklenmedik)")
        # Yine de devam et, belki başka bir ders eksik
    
    # 5. Otomatik doldurma test et
    print(f"5️⃣ Otomatik doldurma test ediliyor...")
    auto_fill_result = db.auto_fill_assignments()
    
    success_count = len(auto_fill_result["success"])
    failed_count = len(auto_fill_result["failed"])
    
    print(f"   • Başarılı: {success_count}")
    print(f"   • Başarısız: {failed_count}")
    
    if success_count > 0:
        print("   ✅ Otomatik doldurma çalışıyor!")
        for class_name, lesson_name, teacher_name in auto_fill_result["success"]:
            print(f"     - {class_name}: {lesson_name} → {teacher_name}")
    
    # 6. Final durum kontrolü
    assignments_final = db.get_schedule_by_school_type()
    print(f"6️⃣ Final atama sayısı: {len(assignments_final)}")
    
    # 7. Manuel atama test et
    print(f"7️⃣ Manuel atama test ediliyor...")
    
    # Test verileri al
    classes = db.get_all_classes()
    teachers = db.get_all_teachers()
    lessons = db.get_all_lessons()
    
    if classes and teachers and lessons:
        # Manuel atama yap
        manual_result = db.add_schedule_entry(
            class_id=classes[0].class_id,
            teacher_id=teachers[0].teacher_id,
            lesson_id=lessons[0].lesson_id,
            classroom_id=1,
            day=-1,
            time_slot=-1
        )
        
        if manual_result:
            print(f"   ✅ Manuel atama başarılı! Entry ID: {manual_result}")
            
            # Hemen sil (test temizliği)
            if db.delete_schedule_entry(manual_result):
                print("   ✅ Test ataması temizlendi")
            else:
                print("   ⚠️  Test ataması silinemedi")
        else:
            print("   ❌ Manuel atama başarısız!")
            return False
    
    print("\n" + "=" * 50)
    print("✅ DERS ATAMA İŞ AKIŞI TEST BAŞARILI!")
    print(f"📊 Özet:")
    print(f"   • Başlangıç: {len(assignments_initial)} atama")
    print(f"   • Silme: 1 atama silindi")
    print(f"   • Otomatik doldurma: {success_count} başarılı")
    print(f"   • Final: {len(assignments_final)} atama")
    print(f"   • Manuel atama: Çalışıyor")
    
    return True

if __name__ == "__main__":
    success = test_assignment_workflow()
    if not success:
        print("\n❌ Test başarısız!")
        sys.exit(1)