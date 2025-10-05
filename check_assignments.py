#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager

# Initialize database
db_manager = DatabaseManager()

print("🔍 Checking Database Content")
print("=" * 50)

# Check schedule entries
schedule_entries = db_manager.get_schedule_by_school_type()
print(f"📊 Schedule entries: {len(schedule_entries)}")

if schedule_entries:
    print("\n📋 First 5 schedule entries:")
    for i, entry in enumerate(schedule_entries[:5]):
        print(f"   {i+1}. Class: {entry.class_id}, Teacher: {entry.teacher_id}, Lesson: {entry.lesson_id}")

# Check classes
classes = db_manager.get_all_classes()
print(f"\n🏫 Classes: {len(classes)}")
for class_obj in classes:
    print(f"   • {class_obj.name} (ID: {class_obj.class_id}, Grade: {class_obj.grade})")

# Check teachers
teachers = db_manager.get_all_teachers()
print(f"\n👨‍🏫 Teachers: {len(teachers)}")
for teacher in teachers:
    print(f"   • {teacher.name} (ID: {teacher.teacher_id}, Subject: {teacher.subject})")

# Check lessons
lessons = db_manager.get_all_lessons()
print(f"\n📚 Lessons: {len(lessons)}")
for lesson in lessons:
    print(f"   • {lesson.name} (ID: {lesson.lesson_id})")

print("\n🎯 Database check completed!")