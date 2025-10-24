#!/usr/bin/env python3
"""
Blok kurallarını test et
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.db_manager import DatabaseManager
from algorithms.curriculum_based_scheduler import CurriculumBasedFullScheduleGenerator

def test_block_rules():
    """Blok kurallarını test et"""
    print("🧪 BLOK KURALLARI TEST EDİLİYOR")
    print("=" * 50)
    
    db = DatabaseManager()
    
    # Curriculum-based scheduler'ı test et
    scheduler = CurriculumBasedFullScheduleGenerator(db)
    
    print("📋 Test ders dağılımları:")
    
    # Test different hour distributions
    test_cases = [
        (1, "1 saat"),
        (2, "2 saat"), 
        (3, "3 saat"),
        (4, "4 saat"),
        (5, "5 saat"),
        (6, "6 saat")
    ]
    
    for hours, description in test_cases:
        blocks = scheduler._decompose_into_blocks(hours)
        print(f"   • {description}: {blocks}")
    
    print("\n🔍 Gerçek program oluşturma testi...")
    
    # Generate actual schedule
    schedule = scheduler.generate_full_schedule()
    
    print(f"\n📊 Sonuçlar:")
    print(f"   • Toplam slot: {len(schedule)}")
    
    # Analyze block compliance
    print(f"\n🔍 Blok uygunluk analizi:")
    
    # Group by class and lesson
    class_lesson_slots = {}
    for entry in schedule:
        key = (entry['class_id'], entry['lesson_id'])
        if key not in class_lesson_slots:
            class_lesson_slots[key] = []
        class_lesson_slots[key].append((entry['day'], entry['time_slot']))
    
    # Check block rules for each lesson
    violations = 0
    total_lessons = 0
    
    for (class_id, lesson_id), slots in class_lesson_slots.items():
        total_lessons += 1
        
        # Get class and lesson info
        class_obj = db.get_class_by_id(class_id)
        lesson_obj = db.get_lesson_by_id(lesson_id)
        
        if class_obj and lesson_obj:
            weekly_hours = len(slots)
            
            # Check if slots follow block rules
            is_compliant = check_block_compliance(slots, weekly_hours)
            
            if not is_compliant:
                violations += 1
                print(f"   ❌ {class_obj.name} - {lesson_obj.name}: {weekly_hours} saat - KURAL İHLALİ")
                print(f"      Slotlar: {sorted(slots)}")
            else:
                print(f"   ✅ {class_obj.name} - {lesson_obj.name}: {weekly_hours} saat - UYGUN")
    
    print(f"\n📈 Özet:")
    print(f"   • Toplam ders: {total_lessons}")
    print(f"   • Kural ihlali: {violations}")
    print(f"   • Uygunluk oranı: {((total_lessons - violations) / total_lessons * 100):.1f}%")
    
    return violations == 0

def check_block_compliance(slots, weekly_hours):
    """
    Check if slots comply with block rules
    """
    if weekly_hours <= 0:
        return True
    
    # Group slots by day
    day_slots = {}
    for day, slot in slots:
        if day not in day_slots:
            day_slots[day] = []
        day_slots[day].append(slot)
    
    # Sort slots within each day
    for day in day_slots:
        day_slots[day].sort()
    
    # Check block rules based on weekly hours
    if weekly_hours == 1:
        # 1 hour: should be on 1 day
        return len(day_slots) == 1 and len(day_slots[list(day_slots.keys())[0]]) == 1
    
    elif weekly_hours == 2:
        # 2 hours: should be consecutive on same day
        if len(day_slots) != 1:
            return False
        day_slot_list = day_slots[list(day_slots.keys())[0]]
        return len(day_slot_list) == 2 and day_slot_list[1] == day_slot_list[0] + 1
    
    elif weekly_hours == 3:
        # 3 hours: [2+1] on different days
        if len(day_slots) != 2:
            return False
        
        slot_counts = [len(slots) for slots in day_slots.values()]
        slot_counts.sort()
        
        if slot_counts != [1, 2]:
            return False
        
        # Check that 2-hour block is consecutive
        for day, slots in day_slots.items():
            if len(slots) == 2:
                return slots[1] == slots[0] + 1
        
        return True
    
    elif weekly_hours == 4:
        # 4 hours: [2+2] on different days
        if len(day_slots) != 2:
            return False
        
        # Each day should have exactly 2 consecutive slots
        for day, slots in day_slots.items():
            if len(slots) != 2 or slots[1] != slots[0] + 1:
                return False
        
        return True
    
    elif weekly_hours == 5:
        # 5 hours: [2+2+1] on different days
        if len(day_slots) != 3:
            return False
        
        slot_counts = [len(slots) for slots in day_slots.values()]
        slot_counts.sort()
        
        if slot_counts != [1, 2, 2]:
            return False
        
        # Check that 2-hour blocks are consecutive
        for day, slots in day_slots.items():
            if len(slots) == 2 and slots[1] != slots[0] + 1:
                return False
        
        return True
    
    elif weekly_hours == 6:
        # 6 hours: [2+2+2] on different days
        if len(day_slots) != 3:
            return False
        
        # Each day should have exactly 2 consecutive slots
        for day, slots in day_slots.items():
            if len(slots) != 2 or slots[1] != slots[0] + 1:
                return False
        
        return True
    
    else:
        # For more than 6 hours, check that we have mostly 2-hour blocks
        # and each 2-hour block is consecutive
        for day, slots in day_slots.items():
            if len(slots) == 2:
                if slots[1] != slots[0] + 1:
                    return False
            elif len(slots) > 2:
                # No more than 2 consecutive hours per day
                return False
        
        return True

if __name__ == "__main__":
    success = test_block_rules()
    if success:
        print("\n✅ Tüm blok kuralları uygulanıyor!")
    else:
        print("\n❌ Blok kuralları ihlal ediliyor!")
        sys.exit(1)