#!/usr/bin/env python3
"""
Eksik saatleri tek tek ekleyerek 280 toplam saate ulaşma scripti
"""

from database.db_manager import DatabaseManager

def add_missing_hours():
    """Eksik saatleri tek tek ekle"""
    db = DatabaseManager()
    
    print("📚 EKSİK SAATLERİ EKLEME")
    print("=" * 40)
    
    # Sınıfları al
    classes = db.get_all_classes()
    
    # Her sınıf için eksik saatleri ekle
    for cls in classes:
        print(f"\n🏫 {cls.name} sınıfı:")
        
        # Mevcut atamaları al
        entries = db.get_schedule_by_school_type()
        class_entries = [e for e in entries if e.class_id == cls.class_id]
        
        # Mevcut toplam saati hesapla
        current_hours = sum(db.get_weekly_hours_for_lesson(e.lesson_id, cls.grade) for e in class_entries)
        needed_hours = 35 - current_hours
        
        print(f"   Mevcut: {current_hours} saat, Gerekli: {needed_hours} saat")
        
        if needed_hours > 0:
            # Türkçe ve Matematik atamalarını bul
            turkce_entry = None
            matematik_entry = None
            
            for entry in class_entries:
                lesson = db.get_lesson_by_id(entry.lesson_id)
                if lesson.name == 'Türkçe':
                    turkce_entry = entry
                elif lesson.name == 'Matematik':
                    matematik_entry = entry
            
            # Eksik saatleri ekle (Türkçe ve Matematik'e dönüşümlü)
            for i in range(needed_hours):
                if i % 2 == 0 and turkce_entry:
                    # Türkçe ekle
                    db.add_schedule_entry(
                        turkce_entry.class_id,
                        turkce_entry.teacher_id,
                        turkce_entry.lesson_id,
                        turkce_entry.classroom_id,
                        0, 0
                    )
                    teacher = db.get_teacher_by_id(turkce_entry.teacher_id)
                    print(f"   ✓ Türkçe → {teacher.name} (+1 saat)")
                elif matematik_entry:
                    # Matematik ekle
                    db.add_schedule_entry(
                        matematik_entry.class_id,
                        matematik_entry.teacher_id,
                        matematik_entry.lesson_id,
                        matematik_entry.classroom_id,
                        0, 0
                    )
                    teacher = db.get_teacher_by_id(matematik_entry.teacher_id)
                    print(f"   ✓ Matematik → {teacher.name} (+1 saat)")
    
    # Final kontrol
    print("\n📊 FINAL KONTROL:")
    entries = db.get_schedule_by_school_type()
    print(f"   📋 Toplam atama: {len(entries)}")
    
    total_hours = 0
    for cls in classes:
        class_entries = [e for e in entries if e.class_id == cls.class_id]
        class_hours = len(class_entries)  # Her atama 1 saat
        total_hours += class_hours
        
        if class_hours == 35:
            print(f"   ✅ {cls.name}: {class_hours} saat")
        else:
            print(f"   ⚠️  {cls.name}: {class_hours} saat")
    
    print(f"\n📊 Toplam: {total_hours}/280 saat")
    
    if total_hours == 280:
        print("✅ Mükemmel! 280 saate ulaştık!")
    else:
        print(f"⚠️  Hala {280-total_hours} saat eksik")

if __name__ == "__main__":
    add_missing_hours()