#!/usr/bin/env python3
"""
Debug script for scheduler
"""

import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_manager
from algorithms.scheduler import Scheduler

def debug_scheduler():
    """Debug the scheduler to understand how lessons are being distributed"""
    print("Debugging scheduler...")
    
    # Create scheduler instance
    scheduler = Scheduler(db_manager)
    
    # Get data
    classes = db_manager.get_all_classes()
    lessons = db_manager.get_all_lessons()
    
    if not classes or not lessons:
        print("No classes or lessons found")
        return
    
    # Look at a specific class and lesson
    test_class = classes[0]
    print(f"Testing with class: {test_class.name}")
    
    # Find a lesson with 6 hours
    test_lesson = None
    for lesson in lessons:
        if lesson.weekly_hours == 6:
            test_lesson = lesson
            break
    
    if not test_lesson:
        print("No lesson with 6 hours found")
        return
    
    print(f"Testing with lesson: {test_lesson.name} ({test_lesson.weekly_hours} hours/week)")
    
    # Calculate distribution
    days = list(range(5))
    distribution = scheduler._distribute_hours_evenly(test_lesson.weekly_hours, len(days))
    print(f"Calculated distribution: {distribution}")
    
    # Show day requirements
    day_requirements = [(i, distribution[i]) for i in range(len(days)) if distribution[i] > 0]
    print(f"Day requirements: {day_requirements}")
    
    # Test the actual scheduling for this specific class and lesson
    print("\nTesting actual scheduling...")
    
    # Get teachers and classrooms
    teachers = db_manager.get_all_teachers()
    classrooms = db_manager.get_all_classrooms()
    
    # Get school type and time slots
    school_type = db_manager.get_school_type()
    if not school_type:
        school_type = "Lise"
    
    time_slots_count = scheduler.SCHOOL_TIME_SLOTS.get(school_type, 8)
    time_slots = list(range(time_slots_count))
    
    # Initialize schedule entries (empty for this test)
    schedule_entries = []
    
    # Try to schedule according to distribution
    for day_index, hours_needed in day_requirements:
        print(f"\nTrying to schedule {hours_needed} hours on day {day_index}")
        hours_scheduled = 0
        
        while hours_scheduled < hours_needed:
            slot_found = False
            print(f"  Trying to schedule hour {hours_scheduled + 1} of {hours_needed}")
            
            # Try all time slots for this day
            for time_slot in time_slots:
                print(f"    Checking time slot {time_slot}")
                if scheduler._is_slot_available_for_class(schedule_entries, test_class.class_id, days[day_index], time_slot):
                    print(f"      Class slot available")
                    teacher = scheduler._find_available_teacher(schedule_entries, teachers, test_lesson, days[day_index], time_slot)
                    if teacher:
                        print(f"      Teacher {teacher.name} available")
                        if db_manager.is_teacher_available(teacher.teacher_id, days[day_index], time_slot):
                            print(f"      Teacher availability confirmed")
                            classroom = scheduler._find_available_classroom(schedule_entries, classrooms, days[day_index], time_slot)
                            if classroom:
                                print(f"      Classroom {classroom.name} available")
                                schedule_entries.append({
                                    'class_id': test_class.class_id,
                                    'teacher_id': teacher.teacher_id,
                                    'lesson_id': test_lesson.lesson_id,
                                    'classroom_id': classroom.classroom_id,
                                    'day': days[day_index],
                                    'time_slot': time_slot
                                })
                                hours_scheduled += 1
                                slot_found = True
                                print(f"      Scheduled successfully! Hours scheduled: {hours_scheduled}")
                                break
                            else:
                                print(f"      No classroom available")
                        else:
                            print(f"      Teacher not available according to settings")
                    else:
                        print(f"      No teacher available")
                else:
                    print(f"      Class slot not available")
            
            if not slot_found:
                print(f"    Could not schedule hour {hours_scheduled + 1} on day {day_index}")
                break
        
        print(f"  Finished day {day_index}: {hours_scheduled}/{hours_needed} hours scheduled")
    
    # Analyze results
    print(f"\nFinal results:")
    day_counts = [0] * 5
    for entry in schedule_entries:
        day_counts[entry['day']] += 1
    
    print(f"Day distribution: {day_counts}")
    print(f"Total entries: {len(schedule_entries)}")

if __name__ == "__main__":
    debug_scheduler()