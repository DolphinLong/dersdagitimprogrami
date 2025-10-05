#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Fix Scheduler - Simple and Effective Solution
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager

def main():
    """Quick fix for scheduling issues"""
    print("🔧 QUICK FIX SCHEDULER")
    print("="*50)
    
    db_manager = DatabaseManager()
    
    # Get all data
    classes = db_manager.get_all_classes()
    teachers = db_manager.get_all_teachers()
    lessons = db_manager.get_all_lessons()
    
    # Get assignments
    assignments = db_manager.get_schedule_by_school_type()
    
    print(f"📊 Data Summary:")
    print(f"   Classes: {len(classes)}")
    print(f"   Teachers: {len(teachers)}")
    print(f"   Lessons: {len(lessons)}")
    print(f"   Assignments: {len(assignments)}")
    
    # Build assignment map
    assignment_map = {}
    for assignment in assignments:
        key = (assignment.class_id, assignment.lesson_id)
        assignment_map[key] = assignment.teacher_id
    
    print(f"\n✅ Created {len(assignment_map)} lesson-teacher assignments")
    
    # Clear existing schedule
    print(f"\n🗑️ Clearing existing schedule...")
    db_manager.clear_schedule()
    
    # Generate simple schedule
    print(f"\n📅 Generating simple schedule...")
    
    total_scheduled = 0
    total_expected = 0
    
    for class_obj in classes:
        print(f"\n📚 Processing class: {class_obj.name}")
        
        # Get lessons for this class
        class_lessons = []
        for lesson in lessons:
            assignment_key = (class_obj.class_id, lesson.lesson_id)
            if assignment_key in assignment_map:
                weekly_hours = db_manager.get_weekly_hours_for_lesson(lesson.lesson_id, class_obj.grade)
                if weekly_hours and weekly_hours > 0:
                    teacher_id = assignment_map[assignment_key]
                    teacher = db_manager.get_teacher_by_id(teacher_id)
                    if teacher:
                        class_lessons.append({
                            'lesson_id': lesson.lesson_id,
                            'lesson_name': lesson.name,
                            'teacher_id': teacher_id,
                            'teacher_name': teacher.name,
                            'weekly_hours': weekly_hours,
                        })
        
        print(f"   Found {len(class_lessons)} lessons")
        
        # Sort by weekly hours (descending)
        class_lessons.sort(key=lambda x: x['weekly_hours'], reverse=True)
        
        # Simple scheduling: fill slots sequentially
        day = 0
        slot = 0
        max_slots_per_day = 8  # Enhanced: 8 slots per day
        
        scheduled_hours = 0
        expected_hours = sum(l['weekly_hours'] for l in class_lessons)
        
        for lesson_info in class_lessons:
            lesson_name = lesson_info['lesson_name']
            teacher_id = lesson_info['teacher_id']
            lesson_id = lesson_info['lesson_id']
            weekly_hours = lesson_info['weekly_hours']
            
            print(f"   📝 Scheduling {lesson_name}: {weekly_hours} hours")
            
            remaining_hours = weekly_hours
            
            while remaining_hours > 0 and day < 5:
                # Try to schedule at current day/slot
                if slot < max_slots_per_day:
                    # Check if slot is available
                    available = True
                    
                    # Check class conflict
                    existing_class = db_manager.get_schedule_for_specific_class(class_obj.class_id)
                    for entry in existing_class:
                        if entry.day == day and entry.time_slot == slot:
                            available = False
                            break
                    
                    # Check teacher conflict
                    if available:
                        existing_teacher = db_manager.get_schedule_for_specific_teacher(teacher_id)
                        for entry in existing_teacher:
                            if entry.day == day and entry.time_slot == slot:
                                available = False
                                break
                    
                    # Check teacher availability (STRICT - respect teacher preferences)
                    if available:
                        try:
                            if not db_manager.is_teacher_available(teacher_id, day, slot):
                                available = False
                        except:
                            # If check fails, assume teacher is available
                            pass
                    
                    if available:
                        # Schedule the lesson
                        success = db_manager.add_schedule_program(
                            class_obj.class_id, teacher_id, lesson_id, 1, day, slot
                        )
                        
                        if success:
                            scheduled_hours += 1
                            remaining_hours -= 1
                            print(f"      ✓ Day {day+1}, Slot {slot+1}")
                        else:
                            print(f"      ❌ Failed to save to database")
                    
                    slot += 1
                else:
                    # Move to next day
                    day += 1
                    slot = 0
                
                # Prevent infinite loop
                if day >= 5:
                    break
            
            if remaining_hours > 0:
                print(f"      ⚠️ Could not schedule {remaining_hours} hours")
        
        coverage = (scheduled_hours / expected_hours * 100) if expected_hours > 0 else 0
        print(f"   📊 Result: {scheduled_hours}/{expected_hours} hours ({coverage:.1f}%)")
        
        total_scheduled += scheduled_hours
        total_expected += expected_hours
    
    # Final summary
    print(f"\n{'='*60}")
    print(f"🎯 FINAL SUMMARY")
    print(f"{'='*60}")
    print(f"📊 Total Scheduled: {total_scheduled} hours")
    print(f"📊 Total Expected: {total_expected} hours")
    
    overall_coverage = (total_scheduled / total_expected * 100) if total_expected > 0 else 0
    print(f"📈 Overall Coverage: {overall_coverage:.1f}%")
    
    if overall_coverage >= 90:
        print(f"✅ SUCCESS: Schedule coverage is excellent!")
    elif overall_coverage >= 70:
        print(f"✅ GOOD: Schedule coverage is acceptable")
    else:
        print(f"⚠️ NEEDS IMPROVEMENT: Schedule coverage is low")
    
    # Check for conflicts
    print(f"\n🔍 Checking for conflicts...")
    conflicts = 0
    
    # Check teacher conflicts
    for teacher in teachers:
        teacher_schedule = db_manager.get_schedule_for_specific_teacher(teacher.teacher_id)
        teacher_slots = {}
        for entry in teacher_schedule:
            key = (entry.day, entry.time_slot)
            if key in teacher_slots:
                conflicts += 1
                print(f"   ⚠️ Teacher conflict: {teacher.name} at Day {entry.day+1}, Slot {entry.time_slot+1}")
            else:
                teacher_slots[key] = entry
    
    # Check class conflicts
    for class_obj in classes:
        class_schedule = db_manager.get_schedule_for_specific_class(class_obj.class_id)
        class_slots = {}
        for entry in class_schedule:
            key = (entry.day, entry.time_slot)
            if key in class_slots:
                conflicts += 1
                print(f"   ⚠️ Class conflict: {class_obj.name} at Day {entry.day+1}, Slot {entry.time_slot+1}")
            else:
                class_slots[key] = entry
    
    if conflicts == 0:
        print(f"✅ No conflicts detected!")
    else:
        print(f"⚠️ {conflicts} conflicts detected")
    
    print(f"\n🎉 Quick fix scheduler completed!")

if __name__ == "__main__":
    main()