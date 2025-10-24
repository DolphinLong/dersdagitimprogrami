#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os, io
if sys.platform.startswith("win"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_manager
from algorithms.simple_perfect_scheduler import SimplePerfectScheduler
import logging

# Enable verbose logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

print("DEBUG: Scheduler baslatiliyor...")

# Verileri kontrol et
classes = db_manager.get_all_classes()
teachers = db_manager.get_all_teachers()
lessons = db_manager.get_all_lessons()
assignments = db_manager.get_schedule_by_school_type()

print(f"Classes: {len(classes)}")
print(f"Teachers: {len(teachers)}")
print(f"Lessons: {len(lessons)}")
print(f"Assignments: {len(assignments)}")

if len(assignments) == 0:
    print("\nHATA: Atama yok!")
    sys.exit(1)

print(f"\nIlk 3 atama:")
for i, a in enumerate(assignments[:3], 1):
    print(f"{i}. Class:{a.class_id}, Lesson:{a.lesson_id}, Teacher:{a.teacher_id}")

# Scheduler calistir
db_manager.clear_schedule()
scheduler = SimplePerfectScheduler(db_manager)
result = scheduler.generate_schedule()

print(f"\n\nSONUC: {len(result)} slot olusturuldu")
