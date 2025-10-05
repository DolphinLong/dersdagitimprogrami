#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Aggressive Scheduler
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from algorithms.scheduler import Scheduler
from database.db_manager import DatabaseManager

def main():
    """Test the aggressive scheduler"""
    print("🚀 Testing Aggressive Scheduler")
    print("="*50)
    
    db_manager = DatabaseManager()
    scheduler = Scheduler(db_manager, use_advanced=False)  # Use standard scheduler with aggressive mode
    
    # Generate schedule
    schedule_entries = scheduler.generate_schedule()
    
    print(f"\n🎉 Aggressive scheduling completed!")
    print(f"📊 Total entries generated: {len(schedule_entries)}")
    
    # Calculate coverage
    classes = db_manager.get_all_classes()
    total_expected_hours = 0
    total_scheduled_hours = 0
    
    for class_obj in classes:
        assignments = db_manager.get_schedule_by_school_type()
        class_assignments = [a for a in assignments if a.class_id == class_obj.class_id]
        
        for assignment in class_assignments:
            weekly_hours = db_manager.get_weekly_hours_for_lesson(assignment.lesson_id, class_obj.grade)
            if weekly_hours:
                total_expected_hours += weekly_hours
        
        class_scheduled = len([e for e in schedule_entries if e['class_id'] == class_obj.class_id])
        total_scheduled_hours += class_scheduled
        
        coverage = (class_scheduled / sum(db_manager.get_weekly_hours_for_lesson(a.lesson_id, class_obj.grade) or 0 for a in class_assignments) * 100) if class_assignments else 0
        print(f"📚 {class_obj.name}: {class_scheduled} hours scheduled ({coverage:.1f}%)")
    
    overall_coverage = (total_scheduled_hours / total_expected_hours * 100) if total_expected_hours > 0 else 0
    print(f"\n📈 Overall Coverage: {total_scheduled_hours}/{total_expected_hours} hours ({overall_coverage:.1f}%)")
    
    if overall_coverage >= 95:
        print(f"🎉 EXCELLENT: Schedule coverage is outstanding!")
    elif overall_coverage >= 85:
        print(f"✅ GREAT: Schedule coverage is very good!")
    elif overall_coverage >= 75:
        print(f"✅ GOOD: Schedule coverage is acceptable")
    else:
        print(f"⚠️ NEEDS IMPROVEMENT: Schedule coverage is low")

if __name__ == "__main__":
    main()