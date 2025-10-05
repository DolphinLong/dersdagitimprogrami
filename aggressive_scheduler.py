#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aggressive Scheduler - Keeps Trying Until Full Coverage
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import random
from database.db_manager import DatabaseManager

class AggressiveScheduler:
    """Aggressive scheduler that keeps trying until full coverage"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.max_attempts = 1000  # Maximum attempts per lesson
        self.max_daily_hours = 7  # Maximum hours per teacher per day
    
    def generate_full_schedule(self):
        """Generate schedule with aggressive retry until full coverage"""
        print("🚀 AGGRESSIVE SCHEDULER - FULL COVERAGE MODE")
        print("="*60)
        
        # Get all data
        classes = self.db_manager.get_all_classes()
        teachers = self.db_manager.get_all_teachers()
        lessons = self.db_manager.get_all_lessons()
        assignments = self.db_manager.get_schedule_by_school_type()
        
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
        
        print(f"✅ Created {len(assignment_map)} lesson-teacher assignments")
        
        # Clear existing schedule
        print(f"\n🗑️ Clearing existing schedule...")
        self.db_manager.clear_schedule()
        
        # Initialize tracking
        schedule_entries = []
        teacher_daily_hours = {}  # Track teacher hours per day
        class_daily_hours = {}    # Track class hours per day
        
        # Initialize tracking dictionaries
        for teacher in teachers:
            teacher_daily_hours[teacher.teacher_id] = {i: 0 for i in range(5)}
        
        for class_obj in classes:
            class_daily_hours[class_obj.class_id] = {i: 0 for i in range(5)}
        
        print(f"\n📅 Generating aggressive schedule...")
        
        total_scheduled = 0
        total_expected = 0
        
        # Process each class
        for class_idx, class_obj in enumerate(classes, 1):
            print(f"\n{'='*50}")
            print(f"📚 [{class_idx}/{len(classes)}] Aggressive Scheduling: {class_obj.name}")
            print(f"{'='*50}")
            
            # Get lessons for this class
            class_lessons = self._get_class_lessons(class_obj, lessons, assignment_map, teachers)
            
            if not class_lessons:
                print(f"⚠️  No assignments found for {class_obj.name}")
                continue
            
            # Sort by weekly hours (descending) - prioritize important lessons
            class_lessons.sort(key=lambda x: x['weekly_hours'], reverse=True)
            
            print(f"   Found {len(class_lessons)} lessons to schedule")
            
            # Schedule each lesson aggressively
            for lesson_info in class_lessons:
                success = self._schedule_lesson_aggressively(
                    schedule_entries, class_obj, lesson_info, 
                    teacher_daily_hours, class_daily_hours
                )
                
                if success:
                    print(f"   ✅ {lesson_info['lesson_name']}: FULLY SCHEDULED")
                else:
                    print(f"   ❌ {lesson_info['lesson_name']}: FAILED TO SCHEDULE")
            
            # Calculate coverage for this class
            class_scheduled = len([e for e in schedule_entries if e['class_id'] == class_obj.class_id])
            class_expected = sum(l['weekly_hours'] for l in class_lessons)
            coverage = (class_scheduled / class_expected * 100) if class_expected > 0 else 0
            
            print(f"\n   📊 Class Summary: {class_scheduled}/{class_expected} hours ({coverage:.1f}%)")
            
            total_scheduled += class_scheduled
            total_expected += class_expected
        
        # Final summary
        print(f"\n{'='*60}")
        print(f"🎯 AGGRESSIVE SCHEDULING COMPLETED")
        print(f"{'='*60}")
        print(f"📊 Total Scheduled: {total_scheduled} hours")
        print(f"📊 Total Expected: {total_expected} hours")
        
        overall_coverage = (total_scheduled / total_expected * 100) if total_expected > 0 else 0
        print(f"📈 Overall Coverage: {overall_coverage:.1f}%")
        
        if overall_coverage >= 95:
            print(f"🎉 EXCELLENT: Schedule coverage is outstanding!")
        elif overall_coverage >= 85:
            print(f"✅ GREAT: Schedule coverage is very good!")
        elif overall_coverage >= 75:
            print(f"✅ GOOD: Schedule coverage is acceptable")
        else:
            print(f"⚠️ NEEDS IMPROVEMENT: Schedule coverage is low")
        
        # Check for conflicts
        print(f"\n🔍 Checking for conflicts...")
        conflicts = self._detect_conflicts(schedule_entries)
        
        if conflicts == 0:
            print(f"✅ No conflicts detected!")
        else:
            print(f"⚠️ {conflicts} conflicts detected")
        
        # Save to database
        print(f"\n💾 Saving schedule to database...")
        saved_count = 0
        for entry in schedule_entries:
            if self.db_manager.add_schedule_program(
                entry['class_id'], entry['teacher_id'], entry['lesson_id'],
                entry['classroom_id'], entry['day'], entry['time_slot']
            ):
                saved_count += 1
        
        print(f"✅ Saved {saved_count} schedule entries to database")
        
        return schedule_entries
    
    def _get_class_lessons(self, class_obj, lessons, assignment_map, teachers):
        """Get all lessons assigned to a class"""
        class_lessons = []
        
        for lesson in lessons:
            assignment_key = (class_obj.class_id, lesson.lesson_id)
            if assignment_key in assignment_map:
                weekly_hours = self.db_manager.get_weekly_hours_for_lesson(
                    lesson.lesson_id, class_obj.grade
                )
                
                if weekly_hours and weekly_hours > 0:
                    teacher_id = assignment_map[assignment_key]
                    teacher = self.db_manager.get_teacher_by_id(teacher_id)
                    
                    if teacher:
                        class_lessons.append({
                            'lesson_id': lesson.lesson_id,
                            'lesson_name': lesson.name,
                            'teacher_id': teacher_id,
                            'teacher_name': teacher.name,
                            'weekly_hours': weekly_hours,
                        })
        
        return class_lessons
    
    def _schedule_lesson_aggressively(self, schedule_entries, class_obj, lesson_info, 
                                    teacher_daily_hours, class_daily_hours):
        """Aggressively schedule a lesson with multiple retry strategies"""
        lesson_name = lesson_info['lesson_name']
        teacher_id = lesson_info['teacher_id']
        teacher_name = lesson_info['teacher_name']
        weekly_hours = lesson_info['weekly_hours']
        lesson_id = lesson_info['lesson_id']
        
        print(f"   📝 Aggressively scheduling: {lesson_name} ({weekly_hours} hours)")
        print(f"      Teacher: {teacher_name}")
        
        scheduled_hours = 0
        attempts = 0
        
        # Strategy 1: Try to schedule in optimal blocks
        if weekly_hours >= 2:
            # Try 2-hour blocks first
            blocks = [2] * (weekly_hours // 2) + [1] * (weekly_hours % 2)
        else:
            blocks = [1] * weekly_hours
        
        print(f"      Strategy: {' + '.join(map(str, blocks))} blocks")
        
        # Try each block
        for block_idx, block_size in enumerate(blocks):
            if scheduled_hours >= weekly_hours:
                break
            
            print(f"      Block {block_idx + 1}: {block_size} hour(s)")
            
            # Try multiple strategies for this block
            strategies = [
                self._strategy_consecutive_same_day,
                self._strategy_consecutive_different_days,
                self._strategy_distributed_single_hours,
                self._strategy_any_available_slot
            ]
            
            block_scheduled = False
            
            for strategy_idx, strategy in enumerate(strategies):
                if block_scheduled:
                    break
                
                attempts += 1
                if attempts > self.max_attempts:
                    print(f"         ⚠️ Max attempts reached for {lesson_name}")
                    break
                
                result = strategy(
                    schedule_entries, class_obj.class_id, teacher_id, lesson_id,
                    block_size, teacher_daily_hours, class_daily_hours
                )
                
                if result:
                    day, slots = result
                    
                    # Add entries to schedule
                    for slot in slots:
                        schedule_entries.append({
                            'class_id': class_obj.class_id,
                            'teacher_id': teacher_id,
                            'lesson_id': lesson_id,
                            'classroom_id': 1,  # Default classroom
                            'day': day,
                            'time_slot': slot
                        })
                        scheduled_hours += 1
                        
                        # Update tracking
                        teacher_daily_hours[teacher_id][day] += 1
                        class_daily_hours[class_obj.class_id][day] += 1
                    
                    day_names = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
                    print(f"         ✅ Strategy {strategy_idx + 1}: {day_names[day]} slots {slots[0]+1}-{slots[-1]+1}")
                    block_scheduled = True
            
            if not block_scheduled:
                print(f"         ❌ Could not schedule block {block_idx + 1}")
        
        success_rate = (scheduled_hours / weekly_hours * 100) if weekly_hours > 0 else 0
        print(f"      📊 Result: {scheduled_hours}/{weekly_hours} hours ({success_rate:.1f}%)")
        
        return scheduled_hours >= weekly_hours
    
    def _strategy_consecutive_same_day(self, schedule_entries, class_id, teacher_id, lesson_id, 
                                     block_size, teacher_daily_hours, class_daily_hours):
        """Strategy 1: Try consecutive slots on the same day"""
        for day in range(5):
            # Check teacher daily limit
            if teacher_daily_hours[teacher_id][day] + block_size > self.max_daily_hours:
                continue
            
            # Try consecutive slots
            for start_slot in range(8 - block_size + 1):
                slots = list(range(start_slot, start_slot + block_size))
                
                if self._is_placement_valid(schedule_entries, class_id, teacher_id, day, slots):
                    return (day, slots)
        
        return None
    
    def _strategy_consecutive_different_days(self, schedule_entries, class_id, teacher_id, lesson_id, 
                                          block_size, teacher_daily_hours, class_daily_hours):
        """Strategy 2: Try consecutive slots across different days"""
        # For blocks > 1, try to split across days
        if block_size > 1:
            # Try to split into smaller consecutive blocks
            for day in range(5):
                if teacher_daily_hours[teacher_id][day] + 1 <= self.max_daily_hours:
                    for slot in range(8):
                        if self._is_placement_valid(schedule_entries, class_id, teacher_id, day, [slot]):
                            return (day, [slot])
        
        return None
    
    def _strategy_distributed_single_hours(self, schedule_entries, class_id, teacher_id, lesson_id, 
                                        block_size, teacher_daily_hours, class_daily_hours):
        """Strategy 3: Try single hours distributed across days"""
        for day in range(5):
            if teacher_daily_hours[teacher_id][day] + 1 <= self.max_daily_hours:
                for slot in range(8):
                    if self._is_placement_valid(schedule_entries, class_id, teacher_id, day, [slot]):
                        return (day, [slot])
        
        return None
    
    def _strategy_any_available_slot(self, schedule_entries, class_id, teacher_id, lesson_id, 
                                   block_size, teacher_daily_hours, class_daily_hours):
        """Strategy 4: Try any available slot (most aggressive)"""
        # Try random order for variety
        days = list(range(5))
        random.shuffle(days)
        
        for day in days:
            if teacher_daily_hours[teacher_id][day] + 1 <= self.max_daily_hours:
                slots = list(range(8))
                random.shuffle(slots)
                
                for slot in slots:
                    if self._is_placement_valid(schedule_entries, class_id, teacher_id, day, [slot]):
                        return (day, [slot])
        
        return None
    
    def _is_placement_valid(self, schedule_entries, class_id, teacher_id, day, slots):
        """Check if placement is valid (no conflicts)"""
        for slot in slots:
            # Check class conflict
            for entry in schedule_entries:
                if entry['class_id'] == class_id and entry['day'] == day and entry['time_slot'] == slot:
                    return False
            
            # Check teacher conflict
            for entry in schedule_entries:
                if entry['teacher_id'] == teacher_id and entry['day'] == day and entry['time_slot'] == slot:
                    return False
            
            # Check teacher availability (respect preferences)
            try:
                if not self.db_manager.is_teacher_available(teacher_id, day, slot):
                    return False
            except:
                # If check fails, assume teacher is available
                pass
        
        return True
    
    def _detect_conflicts(self, schedule_entries):
        """Detect scheduling conflicts"""
        conflicts = 0
        
        # Check teacher conflicts
        teacher_slots = {}
        for entry in schedule_entries:
            key = (entry['teacher_id'], entry['day'], entry['time_slot'])
            if key in teacher_slots:
                conflicts += 1
            else:
                teacher_slots[key] = entry
        
        # Check class conflicts
        class_slots = {}
        for entry in schedule_entries:
            key = (entry['class_id'], entry['day'], entry['time_slot'])
            if key in class_slots:
                conflicts += 1
            else:
                class_slots[key] = entry
        
        return conflicts

def main():
    """Test the aggressive scheduler"""
    print("🚀 Testing Aggressive Scheduler")
    print("="*50)
    
    db_manager = DatabaseManager()
    scheduler = AggressiveScheduler(db_manager)
    
    # Generate aggressive schedule
    schedule_entries = scheduler.generate_full_schedule()
    
    print(f"\n🎉 Aggressive scheduling completed!")
    print(f"📊 Total entries generated: {len(schedule_entries)}")

if __name__ == "__main__":
    main()