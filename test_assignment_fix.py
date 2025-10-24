#!/usr/bin/env python3
"""
Ders atama düzeltmesini test et
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.db_manager import DatabaseManager

def test_assignment_operations():
    """Ders atama işlemlerini test et"""
    print("🧪 Ders Atama İşlemleri Test Ediliyor...")
    
    db = DatabaseManager()
    
    # Mevcut verileri al
    classes = db.get_all_classes()
    teachers = db.get_all_teachers()
    lessons = db.get_all_lessons()
    
    print(f"📊 Mevcut veriler:")
    print(f"   • Sınıflar: {len(classes)}")
    print(f"   • Öğretmenler: {len(teachers)}")
    print(f"   • Dersler: {len(lessons)}")
    
    if not classes or not teachers or not lessons:
        print("❌ Test için yeterli veri yok!")
        return False
    
    # Mevcut atamaları kontrol et
    assignments_before = db.get_schedule_by_school_type()
    print(f"   • Mevcut atamalar: {len(assignments_before)}")
    
    # Test ataması yap
    test_class = classes[0]
    test_teacher = teachers[0]
    test_lesson = lessons[0]
    
    print(f"\n🧪 Test ataması yapılıyor:")
    print(f"   • Sınıf: {test_class.name}")
    print(f"   • Öğretmen: {test_teacher.name}")
    print(f"   • Ders: {test_lesson.name}")
    
    # Atama yap
    result = db.add_schedule_entry(
        class_id=test_class.class_id,
        teacher_id=test_teacher.teacher_id,
        lesson_id=test_lesson.lesson_id,
        classroom_id=1,
        day=-1,
        time_slot=-1
    )
    
    if result:
        print(f"   ✅ Atama başarılı! Entry ID: {result}")
    else:
        print(f"   ❌ Atama başarısız!")
        return False
    
    # Atamaları tekrar kontrol et
    assignments_after = db.get_schedule_by_school_type()
    print(f"   • Yeni atama sayısı: {len(assignments_after)}")
    
    if len(assignments_after) > len(assignments_before):
        print("   ✅ Atama başarıyla kaydedildi ve okunabildi!")
        
        # Test atamasını sil
        if db.delete_schedule_entry(result):
            print("   ✅ Test ataması temizlendi")
        else:
            print("   ⚠️  Test ataması silinemedi")
        
        return True
    else:
        print("   ❌ Atama kaydedildi ama okunamadı!")
        return False

if __name__ == "__main__":
    success = test_assignment_operations()
    if success:
        print("\n✅ Ders atama işlemleri düzgün çalışıyor!")
    else:
        print("\n❌ Ders atama işlemlerinde sorun var!")
        sys.exit(1)