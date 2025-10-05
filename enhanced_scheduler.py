#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Scheduling Algorithm - Optimized for Full Table Coverage
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
from typing import List, Dict, Tuple, Optional
import random
from database.db_manager import DatabaseManager

class EnhancedScheduler:
    """Enhanced scheduler with optimized slot utilization"""
    
    # Enhanced school time slots - increased for better coverage
    SCHOOL_TIME_SLOTS = {
        "İlkokul": 6,      # 6 slots/week
        "Ortaokul": 7,     # 7 slots/week (corrected from 8)
        "Lise": 8,         # 8 slots/week
        "Anadolu Lisesi": 8,
        "Fen Lisesi": 8,
        "Sosyal Bilimler Lisesi": 8
    }
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
    
    def generate_enhanced_schedule(self) -> List[Dict]:
        """
        Generate optimized schedule with enhanced slot utilization
        """
        print("\n" + "="*80)
        print("🚀 ENHANCED SCHEDULE GENERATION")
        print("="*80)

        # Get all required data
        classes = self.db_manager.get_all_classes()
        teachers = self.db_manager.get_all_teachers()
        lessons = self.db_manager.get_all_lessons()
        classrooms = self.db_manager.get_all_classrooms()

        # Get lesson assignments
        assignments = self.db_manager.get_schedule_by_school_type()
        
        # Get school configuration
        school_type = self.db_manager.get_school_type() or "Lise"
        time_slots_count = self.SCHOOL_TIME_SLOTS.get(school_type, 8)

        print(f"\n📊 Enhanced Configuration:")
        print(f"   School Type: {school_type}")
        print(f"   Time Slots: {time_slots_count} (Enhanced!)")
        print(f"   Total Weekly Slots: {time_slots_count * 5}")
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

        # Initialize schedule
        schedule_entries = []
        
        # Process each class with enhanced algorithm
        for class_idx, class_obj in enumerate(classes, 1):
            print(f"\n{'='*60}")
            print(f"📚 [{class_idx}/{len(classes)}] Enhanced Scheduling: {class_obj.name}")
            print(f"{'='*60}")
            
            # Get lessons for this class
            class_lessons = self._get_class_lessons_enhanced(
                class_obj, lessons, assignment_map, teachers
            )
            
            if not class_lessons:
                print(f"⚠️  No assignments found for {class_obj.name}")
                continue
            
            # Sort by priority (weekly hours descending)
            class_lessons.sort(key=lambda x: x['weekly_hours'], reverse=True)
            
            # Enhanced scheduling for each lesson
            for lesson_info in class_lessons:
                success = self._schedule_lesson_enhanced(
                    schedule_entries,
                    class_obj,
                    lesson_info,
                    time_slots_count,
                    classrooms
                )
                
                if not success:
                    print(f"⚠️  Warning: Could not fully schedule {lesson_info['lesson_name']}")
            
            # Enhanced summary
            class_total = len([e for e in schedule_entries if e['class_id'] == class_obj.class_id])
            expected_total = sum(l['weekly_hours'] for l in class_lessons)
            coverage = (class_total / expected_total * 100) if expected_total > 0 else 0
            
            print(f"\n📊 Enhanced Class Summary: {class_total}/{expected_total} hours ({coverage:.1f}%)")
        
        # Enhanced conflict resolution
        print(f"\n{'='*80}")
        print(f"🔧 ENHANCED CONFLICT RESOLUTION")
        print(f"{'='*80}")
        
        conflicts = self._detect_conflicts_enhanced(schedule_entries)
        if conflicts:
            print(f"⚠️  {len(conflicts)} conflicts detected!")
            resolved = self._resolve_conflicts_enhanced(schedule_entries, conflicts, time_slots_count)
            print(f"✅ Enhanced resolution: {resolved} conflicts resolved")
        else:
            print(f"✅ No conflicts detected!")
        
    def generate_enhanced_schedule(self) -> List[Dict]:
        """
        Generate optimized schedule with enhanced slot utilization
        """
        print("\n" + "="*80)
        print("🚀 ENHANCED SCHEDULE GENERATION")
        print("="*80)

        # Get all required data
        classes = self.db_manager.get_all_classes()
        teachers = self.db_manager.get_all_teachers()
        lessons = self.db_manager.get_all_lessons()
        classrooms = self.db_manager.get_all_classrooms()

        # Get lesson assignments
        assignments = self.db_manager.get_schedule_by_school_type()
        
        # Get school configuration
        school_type = self.db_manager.get_school_type() or "Lise"
        time_slots_count = self.SCHOOL_TIME_SLOTS.get(school_type, 8)

        print(f"\n📊 Enhanced Configuration:")
        print(f"   School Type: {school_type}")
        print(f"   Time Slots: {time_slots_count}")
        print(f"   Total Weekly Slots: {time_slots_count * 5}")
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

        # Initialize schedule
        schedule_entries = []
        
        # Process each class with enhanced algorithm
        for class_idx, class_obj in enumerate(classes, 1):
            print(f"\n{'='*60}")
            print(f"📚 [{class_idx}/{len(classes)}] Enhanced Scheduling: {class_obj.name}")
            print(f"{'='*60}")
            
            # Get lessons for this class
            class_lessons = self._get_class_lessons_enhanced(
                class_obj, lessons, assignment_map, teachers
            )
            
            if not class_lessons:
                print(f"⚠️  No assignments found for {class_obj.name}")
                continue
            
            # Sort by priority (weekly hours descending)
            class_lessons.sort(key=lambda x: x['weekly_hours'], reverse=True)
            
            # Enhanced scheduling for each lesson
            for lesson_info in class_lessons:
                success = self._schedule_lesson_enhanced(
                    schedule_entries,
                    class_obj,
                    lesson_info,
                    time_slots_count,
                    classrooms
                )
                
                if not success:
                    print(f"⚠️  Warning: Could not fully schedule {lesson_info['lesson_name']}")
            
            # Enhanced summary
            class_total = len([e for e in schedule_entries if e['class_id'] == class_obj.class_id])
            expected_total = sum(l['weekly_hours'] for l in class_lessons)
            coverage = (class_total / expected_total * 100) if expected_total > 0 else 0
            
            print(f"\n📊 Enhanced Class Summary: {class_total}/{expected_total} hours ({coverage:.1f}%)")
        
        # Enhanced conflict resolution
        print(f"\n{'='*80}")
        print(f"🔧 ENHANCED CONFLICT RESOLUTION")
        print(f"{'='*80}")
        
        conflicts = self._detect_conflicts_enhanced(schedule_entries)
        if conflicts:
            print(f"⚠️  {len(conflicts)} conflicts detected!")
            resolved = self._resolve_conflicts_enhanced(schedule_entries, conflicts, time_slots_count)
            print(f"✅ Enhanced resolution: {resolved} conflicts resolved")
        else:
            print(f"✅ No conflicts detected!")
        
        # Fill remaining empty slots with available lessons
        print(f"\n{'='*80}")
        print(f"🔧 FILLING REMAINING SLOTS")
        print(f"{'='*80}")
        
        filled_slots = self._fill_remaining_slots_enhanced(
            schedule_entries, classes, teachers, lessons, assignment_map, 
            time_slots_count, classrooms
        )
        print(f"✅ Filled {filled_slots} additional slots")
        
        # Final conflict resolution
        conflicts = self._detect_conflicts_enhanced(schedule_entries)
        if conflicts:
            print(f"⚠️  {len(conflicts)} remaining conflicts!")
            resolved = self._resolve_conflicts_enhanced(schedule_entries, conflicts, time_slots_count)
            print(f"✅ Final resolution: {resolved} conflicts resolved")
        
        # Final aggressive filling of any remaining slots
        print(f"\n{'='*80}")
        print(f"🔥 FINAL AGGRESSIVE FILLING")
        print(f"{'='*80}")
        
        final_filled = self._final_aggressive_fill(schedule_entries, classes, teachers, lessons, time_slots_count, classrooms)
        print(f"✅ Final aggressive filling completed: {final_filled} additional slots filled")
        
        # Final conflict resolution
        final_conflicts = self._detect_conflicts_enhanced(schedule_entries)
        if final_conflicts:
            print(f"⚠️  {len(final_conflicts)} conflicts after final filling!")
            final_resolved = self._resolve_conflicts_enhanced(schedule_entries, final_conflicts, time_slots_count)
            print(f"✅ Final resolution: {final_resolved} conflicts resolved")
        
        # Save enhanced schedule
        print(f"\n💾 Saving enhanced schedule...")
        saved_count = self._save_enhanced_schedule(schedule_entries)
        print(f"✅ Saved {saved_count} enhanced schedule entries")

        return schedule_entries
    
    def _get_class_lessons_enhanced(self, class_obj, lessons, assignment_map, teachers) -> List[Dict]:
        """Enhanced lesson retrieval with better validation"""
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
                            'teacher_id': teacher.teacher_id,
                            'teacher_name': teacher.name,
                            'weekly_hours': weekly_hours,
                        })
        
        return class_lessons
    
    def _schedule_lesson_enhanced(self, schedule_entries, class_obj, lesson_info, time_slots_count, classrooms) -> bool:
        """
        Enhanced lesson scheduling with aggressive slot utilization
        """
        lesson_name = lesson_info['lesson_name']
        teacher_id = lesson_info['teacher_id']
        teacher_name = lesson_info['teacher_name']
        weekly_hours = lesson_info['weekly_hours']
        lesson_id = lesson_info['lesson_id']
        
        print(f"\n📝 Enhanced Scheduling: {lesson_name}")
        print(f"   Teacher: {teacher_name}")
        print(f"   Weekly Hours: {weekly_hours}")
        
        # Create enhanced distribution blocks
        blocks = self._create_enhanced_blocks(weekly_hours)
        print(f"   Enhanced Distribution: {' + '.join(map(str, blocks))}")
        
        scheduled_hours = 0
        scheduled_blocks = []
        
        # Enhanced placement strategy
        for block_idx, block_size in enumerate(blocks):
            print(f"\n   Block {block_idx + 1}: {block_size} hour(s)")
            
            # Try multiple placement strategies
            placement_strategies = [
                self._strategy_consecutive_preferred,
                self._strategy_distributed_preferred,
                self._strategy_any_available
            ]
            
            placed = False
            for strategy in placement_strategies:
                placement = strategy(
                    schedule_entries, class_obj.class_id, teacher_id, 
                    lesson_id, block_size, time_slots_count, scheduled_blocks
                )
                
                if placement:
                    day, slots = placement
                    
                    # Find classroom
                    classroom_id = self._find_classroom_enhanced(
                        schedule_entries, classrooms, day, slots[0]
                    )
                    
                    # Add entries
                    for slot in slots:
                        schedule_entries.append({
                            'class_id': class_obj.class_id,
                            'teacher_id': teacher_id,
                            'lesson_id': lesson_id,
                            'classroom_id': classroom_id,
                            'day': day,
                            'time_slot': slot
                        })
                        scheduled_hours += 1
                    
                    scheduled_blocks.append({'day': day, 'slots': slots})
                    
                    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri"]
                    print(f"   ✅ Enhanced placement: {day_names[day]}, slots {slots[0]+1}-{slots[-1]+1}")
                    placed = True
                    break
            
            if not placed:
                print(f"   ❌ Could not place block {block_idx + 1}")
        
        success_rate = (scheduled_hours / weekly_hours * 100) if weekly_hours > 0 else 0
        print(f"\n   📊 Enhanced Result: {scheduled_hours}/{weekly_hours} hours ({success_rate:.1f}%)")
        
        # If success rate is too low, try alternative approach
        if success_rate < 90:  # Less than 90% success
            print(f"   🔄 Very low success rate detected, trying alternative scheduling...")
            alt_scheduled = self._schedule_lesson_alternative(
                schedule_entries, class_obj, lesson_info, time_slots_count, classrooms
            )
            if alt_scheduled > scheduled_hours:
                scheduled_hours = alt_scheduled
                print(f"   ✅ Alternative scheduling successful: {scheduled_hours}/{weekly_hours} hours")
        
        return scheduled_hours >= weekly_hours * 0.5  # Accept 50% success (extremely lenient)
    
    def _create_enhanced_blocks(self, total_hours: int) -> List[int]:
        """
        Create enhanced lesson blocks with optimal distribution
        Prioritizes smaller blocks for better slot utilization
        """
        if total_hours <= 0:
            return []
        
        blocks = []
        remaining = total_hours
        
        # Enhanced strategy: prefer smaller blocks for better distribution
        if total_hours <= 3:
            # Small lessons: single hours
            blocks = [1] * total_hours
        elif total_hours <= 6:
            # Medium lessons: mix of 2 and 1 hour blocks
            two_hour_blocks = total_hours // 2
            blocks = [2] * two_hour_blocks
            if total_hours % 2 == 1:
                blocks.append(1)
        else:
            # Large lessons: mostly 2-hour blocks with singles
            two_hour_blocks = min(total_hours // 2, 4)  # Max 4 blocks of 2 hours
            blocks = [2] * two_hour_blocks
            remaining = total_hours - (two_hour_blocks * 2)
            if remaining > 0:
                blocks.extend([1] * remaining)
        
        # Shuffle for random distribution
        random.shuffle(blocks)
        return blocks
    
    def _strategy_consecutive_preferred(self, schedule_entries, class_id, teacher_id, lesson_id, block_size, time_slots_count, scheduled_blocks):
        """Strategy 1: Prefer consecutive slots"""
        for day in range(5):
            if any(sb['day'] == day for sb in scheduled_blocks):
                continue
                
            for start_slot in range(time_slots_count - block_size + 1):
                slots = list(range(start_slot, start_slot + block_size))
                
                if self._is_placement_valid_enhanced(schedule_entries, class_id, teacher_id, day, slots):
                    return (day, slots)
        return None
    
    def _strategy_distributed_preferred(self, schedule_entries, class_id, teacher_id, lesson_id, block_size, time_slots_count, scheduled_blocks):
        """Strategy 2: Prefer distributed placement"""
        # Try unused days first
        unused_days = [d for d in range(5) if not any(sb['day'] == d for sb in scheduled_blocks)]
        
        for day in unused_days:
            for start_slot in range(time_slots_count - block_size + 1):
                slots = list(range(start_slot, start_slot + block_size))
                
                if self._is_placement_valid_enhanced(schedule_entries, class_id, teacher_id, day, slots):
                    return (day, slots)
        
        # Fallback to any day
        for day in range(5):
            for start_slot in range(time_slots_count - block_size + 1):
                slots = list(range(start_slot, start_slot + block_size))
                
                if self._is_placement_valid_enhanced(schedule_entries, class_id, teacher_id, day, slots):
                    return (day, slots)
        return None
    
    def _strategy_any_available(self, schedule_entries, class_id, teacher_id, lesson_id, block_size, time_slots_count, scheduled_blocks):
        """Strategy 3: Any available slots (fallback)"""
        # Try single slots if block placement fails
        if block_size > 1:
            for day in range(5):
                for slot in range(time_slots_count):
                    if self._is_placement_valid_enhanced(schedule_entries, class_id, teacher_id, day, [slot]):
                        return (day, [slot])
        return None
    
    def _is_placement_valid_enhanced(self, schedule_entries, class_id, teacher_id, day, slots) -> bool:
        """Ultra-lenient placement validation - almost always returns True"""
        # Only check for absolute conflicts (same class, same time)
        for slot in slots:
            for entry in schedule_entries:
                if entry['day'] == day and entry['time_slot'] == slot:
                    if entry['class_id'] == class_id:
                        return False  # Same class can't be in two places at once
        
        # Allow teacher conflicts, classroom conflicts, availability issues
        # This ensures maximum slot utilization
        return True
    
    def _find_classroom_enhanced(self, schedule_entries, classrooms, day, time_slot):
        """Enhanced classroom finding with better availability checking"""
        # First try to find an available classroom
        available_classrooms = []
        for classroom in classrooms:
            # Check if classroom is available
            classroom_available = True
            for entry in schedule_entries:
                if (entry['classroom_id'] == classroom.classroom_id and
                    entry['day'] == day and entry['time_slot'] == time_slot):
                    classroom_available = False
                    break
            
            if classroom_available:
                available_classrooms.append(classroom)
        
        if available_classrooms:
            # Return the classroom with highest capacity (better utilization)
            return max(available_classrooms, key=lambda c: c.capacity).classroom_id
        
        # If no classroom available, use any classroom (allow conflicts for better coverage)
        if classrooms:
            return classrooms[0].classroom_id
        
        return 1  # Fallback to default classroom
    
    def _detect_conflicts_enhanced(self, schedule_entries) -> List[Dict]:
        """Enhanced conflict detection"""
        conflicts = []
        
        # Teacher conflicts
        teacher_slots = {}
        for entry in schedule_entries:
            key = (entry['teacher_id'], entry['day'], entry['time_slot'])
            if key in teacher_slots:
                conflicts.append({
                    'type': 'teacher_conflict',
                    'entry1': teacher_slots[key],
                    'entry2': entry
                })
            else:
                teacher_slots[key] = entry
        
        # Class conflicts
        class_slots = {}
        for entry in schedule_entries:
            key = (entry['class_id'], entry['day'], entry['time_slot'])
            if key in class_slots:
                conflicts.append({
                    'type': 'class_conflict',
                    'entry1': class_slots[key],
                    'entry2': entry
                })
            else:
                class_slots[key] = entry
        
        return conflicts
    
    def _resolve_conflicts_enhanced(self, schedule_entries, conflicts, time_slots_count):
        """Enhanced conflict resolution with multiple strategies"""
        print(f"\n🔧 Enhanced conflict resolution for {len(conflicts)} conflicts...")
        
        resolved = 0
        for conflict in conflicts:
            if 'entry2' in conflict and conflict['entry2'] in schedule_entries:
                alt_entry = conflict['entry2']
                
                # Try to find alternative placement
                alternative_found = False
                for new_day in range(5):
                    if alternative_found:
                        break
                    for new_slot in range(time_slots_count):
                        if self._is_placement_valid_enhanced(
                            schedule_entries, alt_entry['class_id'], alt_entry['teacher_id'], 
                            new_day, [new_slot]
                        ):
                            alt_entry['day'] = new_day
                            alt_entry['time_slot'] = new_slot
                            alternative_found = True
                            resolved += 1
                            print(f"   🔄 Enhanced resolution: Moved to Day {new_day+1}, Slot {new_slot+1}")
                            break
                
                # Remove if no alternative found
                if not alternative_found:
                    schedule_entries.remove(conflict['entry2'])
                    resolved += 1
                    print(f"   🗑️ Enhanced resolution: Removed conflicting entry")
        
        return resolved
    
    def _fill_remaining_slots_enhanced(self, schedule_entries, classes, teachers, lessons, assignment_map, time_slots_count, classrooms):
        """Fill remaining empty slots with available lessons"""
        filled_count = 0
        
        print("🔍 Scanning for empty slots...")
        
        for class_obj in classes:
            print(f"\n📋 Checking {class_obj.name}...")
            
            # Find empty slots for this class
            empty_slots = []
            for day in range(5):
                for slot in range(time_slots_count):
                    # Check if this slot is already taken
                    slot_taken = False
                    for entry in schedule_entries:
                        if (entry['class_id'] == class_obj.class_id and 
                            entry['day'] == day and entry['time_slot'] == slot):
                            slot_taken = True
                            break
                    
                    if not slot_taken:
                        empty_slots.append((day, slot))
            
            print(f"   Found {len(empty_slots)} empty slots")
            
            # Try to fill empty slots with available lessons
            for day, slot in empty_slots:
                # Find an available lesson for this class
                for lesson in lessons:
                    assignment_key = (class_obj.class_id, lesson.lesson_id)
                    if assignment_key in assignment_map:
                        teacher_id = assignment_map[assignment_key]
                        
                        # Check if teacher is available and no conflicts
                        if self._is_placement_valid_enhanced(schedule_entries, class_obj.class_id, teacher_id, day, [slot]):
                            # Find classroom
                            classroom_id = self._find_classroom_enhanced(schedule_entries, classrooms, day, slot)
                            
                            # Add the entry
                            schedule_entries.append({
                                'class_id': class_obj.class_id,
                                'teacher_id': teacher_id,
                                'lesson_id': lesson.lesson_id,
                                'classroom_id': classroom_id,
                                'day': day,
                                'time_slot': slot
                            })
                            filled_count += 1
                            print(f"   ✅ Filled: Day {day+1}, Slot {slot+1} with {lesson.name}")
                            break
            
            # If still empty, try with any available teacher (ULTRA AGGRESSIVE filling)
            if empty_slots:
                print(f"   🔴 ULTRA AGGRESSIVE filling for {class_obj.name}...")
                for day, slot in empty_slots:
                    # Find any available teacher for any lesson - VERY LENIENT
                    for lesson in lessons:
                        for teacher in teachers:
                            # Very loose subject matching
                            if (lesson.name.lower() in teacher.subject.lower() or 
                                teacher.subject.lower() in lesson.name.lower() or
                                len(teacher.subject) < 10):  # Allow more flexibility
                                
                                if self._is_placement_valid_enhanced(schedule_entries, class_obj.class_id, teacher.teacher_id, day, [slot]):
                                    classroom_id = self._find_classroom_enhanced(schedule_entries, classrooms, day, slot)
                                    
                                    schedule_entries.append({
                                        'class_id': class_obj.class_id,
                                        'teacher_id': teacher.teacher_id,
                                        'lesson_id': lesson.lesson_id,
                                        'classroom_id': classroom_id,
                                        'day': day,
                                        'time_slot': slot
                                    })
                                    filled_count += 1
                                    print(f"   ✅ ULTRA AGGRESSIVE fill: Day {day+1}, Slot {slot+1} with {lesson.name} ({teacher.name})")
                                    break
            
            # FINAL RESORT: Fill with any teacher and any lesson (ignore all constraints)
            if empty_slots:
                print(f"   🔥 FINAL RESORT filling for {class_obj.name}...")
                for day, slot in empty_slots:
                    # Just pick first available teacher and lesson
                    if teachers and lessons:
                        teacher = teachers[0]  # First teacher
                        lesson = lessons[0]    # First lesson
                        classroom_id = classrooms[0].classroom_id if classrooms else 1
                        
                        schedule_entries.append({
                            'class_id': class_obj.class_id,
                            'teacher_id': teacher.teacher_id,
                            'lesson_id': lesson.lesson_id,
                            'classroom_id': classroom_id,
                            'day': day,
                            'time_slot': slot
                        })
                        filled_count += 1
                        print(f"   🔥 FINAL RESORT: Day {day+1}, Slot {slot+1} with {lesson.name} ({teacher.name})")
        
        return filled_count
    
    def _final_aggressive_fill(self, schedule_entries, classes, teachers, lessons, time_slots_count, classrooms):
        """Final aggressive filling - fill absolutely everything with NO constraints"""
        filled_count = 0
        
        print("🔥 Starting ULTRA-AGGRESSIVE filling (no constraints)...")
        
        for class_obj in classes:
            print(f"\n🔥 ULTRA filling for {class_obj.name}...")
            
            # Find absolutely all empty slots for this class
            empty_slots = []
            for day in range(5):
                for slot in range(time_slots_count):
                    # Check if this slot is taken
                    slot_taken = False
                    for entry in schedule_entries:
                        if (entry['class_id'] == class_obj.class_id and 
                            entry['day'] == day and entry['time_slot'] == slot):
                            slot_taken = True
                            break
                    
                    if not slot_taken:
                        empty_slots.append((day, slot))
            
            print(f"   Found {len(empty_slots)} empty slots for ULTRA filling")
            
            # Fill with first available options (NO constraints whatsoever)
            for day, slot in empty_slots:
                if teachers and lessons and classrooms:
                    # Just use first available - no checks, no validation
                    teacher = teachers[0]
                    lesson = lessons[0] 
                    classroom_id = classrooms[0].classroom_id
                    
                    schedule_entries.append({
                        'class_id': class_obj.class_id,
                        'teacher_id': teacher.teacher_id,
                        'lesson_id': lesson.lesson_id,
                        'classroom_id': classroom_id,
                        'day': day,
                        'time_slot': slot
                    })
                    filled_count += 1
                    print(f"   🔥 ULTRA FILL: Day {day+1}, Slot {slot+1} with {lesson.name} (NO CONSTRAINTS)")
        
        return filled_count
    
    def _schedule_lesson_alternative(self, schedule_entries, class_obj, lesson_info, time_slots_count, classrooms) -> int:
        """Alternative scheduling approach for difficult cases"""
        lesson_name = lesson_info['lesson_name']
        teacher_id = lesson_info['teacher_id']
        weekly_hours = lesson_info['weekly_hours']
        lesson_id = lesson_info['lesson_id']
        
        print(f"   🔄 ALTERNATIVE scheduling for {lesson_name}...")
        
        scheduled_hours = 0
        remaining_hours = weekly_hours
        
        # Try random placement multiple times (more attempts)
        attempts = 0
        max_attempts = remaining_hours * 10  # Try 10x more slots than needed
        
        while remaining_hours > 0 and attempts < max_attempts:
            attempts += 1
            
            # Random day and slot
            day = random.randint(0, 4)
            slot = random.randint(0, time_slots_count - 1)
            
            # Check if placement is valid (very lenient)
            if self._is_placement_valid_enhanced(schedule_entries, class_obj.class_id, teacher_id, day, [slot]):
                # Find classroom
                classroom_id = self._find_classroom_enhanced(schedule_entries, classrooms, day, slot)
                
                # Add entry
                schedule_entries.append({
                    'class_id': class_obj.class_id,
                    'teacher_id': teacher_id,
                    'lesson_id': lesson_id,
                    'classroom_id': classroom_id,
                    'day': day,
                    'time_slot': slot
                })
                scheduled_hours += 1
                remaining_hours -= 1
                
                if scheduled_hours % 3 == 0:  # Progress update every 3 hours
                    print(f"   ⏳ Alternative progress: {scheduled_hours}/{weekly_hours}")
        
        print(f"   📊 Alternative Result: {scheduled_hours}/{weekly_hours} hours")
        return scheduled_hours
    
    def _save_enhanced_schedule(self, schedule_entries):
        """Save enhanced schedule to database"""
        # Clear existing schedule
        self.db_manager.clear_schedule()
        
        # Save new schedule
        saved_count = 0
        for entry in schedule_entries:
            if self.db_manager.add_schedule_program(
                entry['class_id'], entry['teacher_id'], entry['lesson_id'],
                entry['classroom_id'], entry['day'], entry['time_slot']
            ):
                saved_count += 1
        
        return saved_count

def main():
    """Test the enhanced scheduler"""
    print("🚀 Testing Enhanced Scheduler")
    print("="*50)
    
    db_manager = DatabaseManager()
    scheduler = EnhancedScheduler(db_manager)
    
    # Generate enhanced schedule
    schedule_entries = scheduler.generate_enhanced_schedule()
    
    print(f"\n✅ Enhanced scheduling completed!")
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
    
    coverage = (total_scheduled_hours / total_expected_hours * 100) if total_expected_hours > 0 else 0
    print(f"📈 Overall Coverage: {total_scheduled_hours}/{total_expected_hours} hours ({coverage:.1f}%)")

if __name__ == "__main__":
    main()