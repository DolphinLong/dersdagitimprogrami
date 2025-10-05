#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
from algorithms.scheduler import Scheduler

# Initialize database and scheduler
db_manager = DatabaseManager()
scheduler = Scheduler(db_manager)

print("🚀 Quick Schedule Test")
print("=" * 50)

# Generate new schedule (without clearing assignments)
schedule_entries = scheduler.generate_schedule()

print(f"\n📊 Generated {len(schedule_entries)} schedule entries")

# Check for incomplete lessons
print("\n🔍 Checking for incomplete lessons...")
classes = db_manager.get_all_classes()
incomplete_count = 0

for class_obj in classes:
    assignments = db_manager.get_schedule_for_specific_class(class_obj.class_id)
    
    # Group by lesson-teacher
    lesson_teacher_hours = {}
    for assignment in assignments:
        key = (assignment.lesson_id, assignment.teacher_id)
        lesson_teacher_hours[key] = lesson_teacher_hours.get(key, 0) + 1
    
    for (lesson_id, teacher_id), scheduled_hours in lesson_teacher_hours.items():
        lesson = db_manager.get_lesson_by_id(lesson_id)
        teacher = db_manager.get_teacher_by_id(teacher_id)
        
        if lesson and teacher and scheduled_hours < lesson.weekly_hours:
            print(f"⚠️  {class_obj.name}: {lesson.name} ({teacher.name}) - {scheduled_hours}/{lesson.weekly_hours} hours")
            incomplete_count += 1

if incomplete_count == 0:
    print("✅ All lessons are fully scheduled!")
else:
    print(f"\n⚠️  Found {incomplete_count} incomplete lesson assignments")
    print("💡 Consider adjusting teacher assignments or increasing time slots")

print("\n🎯 Quick test completed!")