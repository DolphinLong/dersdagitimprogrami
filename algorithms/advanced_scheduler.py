# -*- coding: utf-8 -*-
"""
Advanced Scheduling Algorithm with Scoring and Smart Distribution

This module implements an advanced scheduling algorithm that inherits from
BaseScheduler to leverage common scheduling functionality while providing
sophisticated features like:

- Weighted scoring system for placement optimization
- Smart block distribution across the week
- Advanced conflict resolution with backtracking
- Teacher load balancing
- Distribution quality metrics

The scheduler has been refactored to inherit from BaseScheduler, eliminating
code duplication and improving maintainability while preserving all advanced
scheduling capabilities.
"""

import sys
import io

# Set default encoding for Windows systems
if sys.platform.startswith('win'):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import logging
from typing import List, Dict, Tuple, Optional
import random

from algorithms.base_scheduler import BaseScheduler


class AdvancedScheduler(BaseScheduler):
    """
    Advanced scheduler with scoring system and smart distribution
    
    Inherits from BaseScheduler to leverage common scheduling functionality.
    
    Key Features:
    - Smart block distribution with scoring system
    - Weighted placement scoring for optimal slot selection
    - Advanced conflict resolution with backtracking
    - Teacher load balancing
    - Distribution quality optimization
    
    The scheduler uses a scoring system with configurable weights to evaluate
    placement quality and make intelligent scheduling decisions.
    """
    
    def __init__(self, db_manager, progress_callback=None):
        super().__init__(db_manager, progress_callback)
        self._load_weights()

    def _load_weights(self):
        """Load scheduler weights from settings or use defaults."""
        self.weights = self.db_manager.get_setting('scheduler_weights')
        if not self.weights or not isinstance(self.weights, dict):
            self.weights = {
                'same_day_penalty': -30,
                'distribution_bonus': 20,
                'block_preference_bonus': 15,
                'early_slot_penalty': -10,
                'late_slot_penalty': -15,
                'lunch_break_bonus': 10,
                'consecutive_bonus': 5,
                'gap_penalty': -25,
                'teacher_load_balance': 10,
            }
            self.db_manager.set_setting('scheduler_weights', self.weights)
    
    def generate_schedule(self) -> List[Dict]:
        """
        Generate optimized schedule using lesson assignments
        Returns list of schedule entries
        Uses BaseScheduler state management (class_slots, teacher_slots, schedule_entries)
        """
        print("\n" + "="*70)
        print("🚀 ADVANCED SCHEDULE GENERATION STARTING")
        print("="*70)

        # Get all required data
        classes = self.db_manager.get_all_classes()
        teachers = self.db_manager.get_all_teachers()
        lessons = self.db_manager.get_all_lessons()
        classrooms = self.db_manager.get_all_classrooms()

        # Get lesson assignments (from schedule_entries table)
        assignments = self.db_manager.get_schedule_by_school_type()

        # Get existing schedule to avoid conflicts
        existing_schedule = self.db_manager.get_schedule_program_by_school_type()

        # Get school configuration using BaseScheduler method
        config = self._get_school_config()
        school_type = config['school_type']
        time_slots_count = config['time_slots_count']

        print(f"\n📊 Configuration:")
        print(f"   School Type: {school_type}")
        print(f"   Time Slots: {time_slots_count}")
        print(f"   Classes: {len(classes)}")
        print(f"   Teachers: {len(teachers)}")
        print(f"   Lessons: {len(lessons)}")
        print(f"   Classrooms: {len(classrooms)}")
        print(f"   Assignments: {len(assignments)}")
        print(f"   Existing Schedule: {len(existing_schedule)} entries")

        # Build assignment map: {(class_id, lesson_id): teacher_id}
        assignment_map = {}
        for assignment in assignments:
            key = (assignment.class_id, assignment.lesson_id)
            assignment_map[key] = assignment.teacher_id

        print(f"\n✅ Created {len(assignment_map)} unique lesson-teacher assignments")

        # Initialize schedule with existing entries using BaseScheduler state management
        self.schedule_entries = []
        self.teacher_slots.clear()
        self.class_slots.clear()
        
        # Load existing schedule using BaseScheduler _place_lesson method
        for entry in existing_schedule:
            self._place_lesson(
                class_id=entry.class_id,
                lesson_id=entry.lesson_id,
                teacher_id=entry.teacher_id,
                day=entry.day,
                slot=entry.time_slot,
                classroom_id=entry.classroom_id
            )

        print(f"📋 Loaded {len(self.schedule_entries)} existing schedule entries")
        
        # Process each class
        for class_idx, class_obj in enumerate(classes, 1):
            print(f"\n{'='*70}")
            print(f"📚 [{class_idx}/{len(classes)}] Scheduling: {class_obj.name} (Grade {class_obj.grade})")
            print(f"{'='*70}")
            
            # Get lessons for this class (using inherited method)
            class_lessons = super()._get_class_lessons(
                class_obj, lessons, assignment_map, teachers
            )
            
            if not class_lessons:
                print(f"⚠️  No assignments found for {class_obj.name}")
                continue
            
            # Sort lessons by priority (weekly hours descending)
            class_lessons.sort(key=lambda x: x['weekly_hours'], reverse=True)
            
            # Schedule each lesson
            for lesson_info in class_lessons:
                success = self._schedule_lesson_smart(
                    class_obj,
                    lesson_info,
                    time_slots_count,
                    classrooms
                )
                
                if not success:
                    print(f"⚠️  Warning: Could not fully schedule {lesson_info['lesson_name']}")
            
            # Summary for this class
            class_total = len([e for e in self.schedule_entries if e['class_id'] == class_obj.class_id])
            expected_total = sum(l['weekly_hours'] for l in class_lessons)
            coverage = (class_total / expected_total * 100) if expected_total > 0 else 0
            
            print(f"\n📊 Class Summary: {class_total}/{expected_total} hours scheduled ({coverage:.1f}%)")
        
        # Final summary and conflict check
        print(f"\n{'='*70}")
        print(f"🎯 SCHEDULE GENERATION COMPLETED")
        print(f"{'='*70}")
        print(f"📊 Total entries: {len(self.schedule_entries)}")
        
        # Check conflicts using inherited BaseScheduler method
        conflicts = self._detect_conflicts()
        if conflicts:
            print(f"⚠️  {len(conflicts)} conflicts detected!")
            resolved = self._attempt_conflict_resolution(conflicts, time_slots_count)
            print(f"✅ Resolved {resolved} conflicts")
        else:
            print(f"✅ No conflicts detected!")
        
        # Save updated schedule to database using BaseScheduler method
        print(f"\n💾 Saving schedule to database...")
        if self._save_schedule():
            print(f"✅ Saved {len(self.schedule_entries)} schedule entries to database")
        else:
            print(f"❌ Failed to save schedule to database")

        return self.schedule_entries
    

    
    def _schedule_lesson_smart(self, class_obj, lesson_info, time_slots_count, classrooms) -> bool:
        """
        Smart lesson scheduling with scoring and distribution
        Uses BaseScheduler state management (self.schedule_entries)
        """
        lesson_name = lesson_info['lesson_name']
        teacher_id = lesson_info['teacher_id']
        teacher_name = lesson_info['teacher_name']
        weekly_hours = lesson_info['weekly_hours']
        lesson_id = lesson_info['lesson_id']
        
        print(f"\n📝 Scheduling: {lesson_name}")
        print(f"   Teacher: {teacher_name}")
        print(f"   Weekly Hours: {weekly_hours}")
        
        # Create optimal distribution blocks (e.g., 2+2+1 for 5 hours)
        blocks = self._create_smart_blocks(weekly_hours)
        print(f"   Distribution: {' + '.join(map(str, blocks))}")
        
        scheduled_hours = 0
        scheduled_blocks = []
        
        # Try to place each block on different days
        for block_idx, block_size in enumerate(blocks):
            print(f"\n   Block {block_idx + 1}: {block_size} hour(s)")
            
            best_placement = None
            best_score = -float('inf')
            
            # Evaluate all possible placements for this block
            for day in range(5):  # Monday to Friday
                # Skip days already used for this lesson
                if any(sb['day'] == day for sb in scheduled_blocks):
                    continue
                
                # Find consecutive slots for this block
                for start_slot in range(time_slots_count - block_size + 1):
                    slots = list(range(start_slot, start_slot + block_size))
                    
                    # Check if placement is valid using inherited method
                    if self._is_placement_valid_advanced(
                        class_obj.class_id, teacher_id, day, slots, check_availability=False
                    ):
                        # Calculate score for this placement
                        score = self._calculate_placement_score(
                            class_obj.class_id, lesson_id,
                            day, slots, scheduled_blocks, weekly_hours, time_slots_count
                        )
                        
                        if score > best_score:
                            best_score = score
                            best_placement = {
                                'day': day,
                                'slots': slots,
                                'score': score
                            }
            
            # Place the block if we found a good spot
            if best_placement:
                day = best_placement['day']
                slots = best_placement['slots']
                
                day_names = ["Mon", "Tue", "Wed", "Thu", "Fri"]
                print(f"   ✅ Placed on {day_names[day]}, slots {slots[0]+1}-{slots[-1]+1} (score: {best_placement['score']:.1f})")
                
                # Find available classroom for this time slot (using inherited method)
                available_classroom = self._find_available_classroom(
                    classrooms, day, slots[0]
                )

                if available_classroom:
                    classroom_id = available_classroom.classroom_id
                else:
                    classroom_id = 1  # Fallback to default

                # Add entries to schedule using BaseScheduler state management
                for slot in slots:
                    self._place_lesson(
                        class_obj.class_id,
                        lesson_id,
                        teacher_id,
                        day,
                        slot,
                        classroom_id
                    )
                    scheduled_hours += 1
                
                scheduled_blocks.append({
                    'day': day,
                    'slots': slots
                })
            else:
                print(f"   ❌ Could not find valid placement for block {block_idx + 1}")
                # Try single-slot fallback
                for day in range(5):
                    for slot in range(time_slots_count):
                        if self._is_placement_valid_advanced(
                            class_obj.class_id, teacher_id, day, [slot], check_availability=False
                        ):
                            # Find available classroom for fallback placement (using inherited method)
                            available_classroom = self._find_available_classroom(
                                classrooms, day, slot
                            )

                            fallback_classroom_id = available_classroom.classroom_id if available_classroom else 1

                            # Use BaseScheduler state management for fallback placement
                            self._place_lesson(
                                class_obj.class_id,
                                lesson_id,
                                teacher_id,
                                day,
                                slot,
                                fallback_classroom_id
                            )
                            scheduled_hours += 1
                            print(f"   ⚠️  Fallback: Placed 1 hour on day {day+1}, slot {slot+1}")
                            
                            if scheduled_hours >= block_size:
                                break
                    if scheduled_hours >= len([s for b in scheduled_blocks for s in b['slots']]) + block_size:
                        break
        
        success_rate = (scheduled_hours / weekly_hours * 100) if weekly_hours > 0 else 0
        print(f"\n   📊 Result: {scheduled_hours}/{weekly_hours} hours ({success_rate:.1f}%)")
        
        return scheduled_hours >= weekly_hours  # Enforce 100% success
    
    def _create_lesson_blocks(self, total_hours: int) -> List[int]:
        """
        Override BaseScheduler method to provide advanced smart block distribution
        
        Create smart lesson blocks with optimal distribution:
        - Prioritizes 2-hour blocks for better learning continuity
        - Adds single hour for odd numbers
        
        Examples:
        - 1 hour: [1]
        - 2 hours: [2]
        - 3 hours: [2, 1]
        - 4 hours: [2, 2]
        - 5 hours: [2, 2, 1]
        - 6 hours: [2, 2, 2]
        - 7 hours: [2, 2, 2, 1]
        - 8 hours: [2, 2, 2, 2]
        
        Args:
            total_hours: Total weekly hours for the lesson
        
        Returns:
            List of block sizes
        """
        if total_hours <= 0:
            return []
        
        blocks = []
        remaining = total_hours
        
        # Fill with 2-hour blocks first
        while remaining >= 2:
            blocks.append(2)
            remaining -= 2
        
        # Add remaining single hour if any
        if remaining == 1:
            blocks.append(1)
        
        return blocks
    
    def _create_smart_blocks(self, total_hours: int) -> List[int]:
        """
        Convenience method that calls the overridden _create_lesson_blocks
        Maintained for backward compatibility with existing code
        """
        return self._create_lesson_blocks(total_hours)
    

    
    def _calculate_placement_score(self, class_id, lesson_id,
                                   day, slots, scheduled_blocks, total_hours, time_slots_count) -> float:
        """
        Calculate score for a potential placement
        Higher score = better placement
        Uses BaseScheduler state management (self.schedule_entries)
        """
        score = 100.0  # Base score
        
        # Get existing schedule for this class on this day from BaseScheduler state
        day_schedule = [e for e in self.schedule_entries 
                       if e['class_id'] == class_id and e['day'] == day]
        
        # 1. Same day penalty - avoid scheduling same lesson twice on same day
        same_lesson_today = any(e['lesson_id'] == lesson_id for e in day_schedule)
        if same_lesson_today:
            score += self.weights['same_day_penalty']
        
        # 2. Distribution bonus - prefer spreading across different days
        used_days = set(sb['day'] for sb in scheduled_blocks)
        if day not in used_days and len(used_days) < 5:
            score += self.weights['distribution_bonus']
        
        # 3. Time slot preferences
        avg_slot = sum(slots) / len(slots) if len(slots) > 0 else 0
        
        # Avoid very early slots (before 2nd period)
        if avg_slot < 1:
            score += self.weights['early_slot_penalty']
        
        # Avoid very late slots (after 6th period)
        if avg_slot > 5:
            score += self.weights['late_slot_penalty']
        
        # 4. Lunch break consideration (typically around slot 3-4)
        # Prefer not to place lessons right at lunch time for single-hour lessons
        if len(slots) == 1 and slots[0] in [3, 4]:
            score -= 5
        
        # 5. Gap penalty - penalize if creating gaps in the schedule
        if day_schedule:
            occupied_slots = set(e['time_slot'] for e in day_schedule)
            new_slots = set(slots)
            combined = occupied_slots | new_slots
            
            # Check for gaps
            if combined:
                min_slot = min(combined)
                max_slot = max(combined)
                expected_slots = max_slot - min_slot + 1
                actual_slots = len(combined)
                
                if actual_slots < expected_slots:
                    # There are gaps
                    gaps = expected_slots - actual_slots
                    score += gaps * self.weights['gap_penalty']
        
        # 6. Consecutive bonus - slight preference for consecutive lessons
        if day_schedule:
            for slot in slots:
                if any(e['time_slot'] == slot - 1 or e['time_slot'] == slot + 1 
                      for e in day_schedule):
                    score += self.weights['consecutive_bonus']
        
        # 7. Prefer earlier days if possible for better distribution
        if day < 3:  # Monday, Tuesday, Wednesday
            score += 5
        
        return score
    

    
    def _attempt_conflict_resolution(self, conflicts, time_slots_count):
        """
        Attempt to resolve conflicts automatically using BaseScheduler conflict format
        Properly updates BaseScheduler state (class_slots, teacher_slots) when moving entries
        """
        print(f"\n🔧 Attempting to resolve {len(conflicts)} conflicts...")

        resolved = 0
        for conflict in conflicts:
            if 'entry2' in conflict and conflict['entry2'] in self.schedule_entries:
                # Try to find alternative placement for the conflicting entry
                alt_entry = conflict['entry2']
                alt_class_id = alt_entry['class_id']
                alt_teacher_id = alt_entry['teacher_id']
                alt_lesson_id = alt_entry['lesson_id']
                alt_classroom_id = alt_entry.get('classroom_id')
                old_day = alt_entry['day']
                old_slot = alt_entry['time_slot']

                # Try to find alternative slot for this entry
                alternative_found = False
                for new_day in range(5):
                    if alternative_found:
                        break
                    for new_slot in range(time_slots_count):
                        # Skip the original conflicting slot
                        if new_day == old_day and new_slot == old_slot:
                            continue

                        # Check if new slot is available using inherited BaseScheduler method
                        if self._is_placement_valid_advanced(alt_class_id, alt_teacher_id, new_day, [new_slot], check_availability=False):
                            # Remove the old entry using BaseScheduler method (updates state)
                            self._remove_lesson(alt_entry)
                            
                            # Place at new location using BaseScheduler method (updates state)
                            self._place_lesson(
                                class_id=alt_class_id,
                                lesson_id=alt_lesson_id,
                                teacher_id=alt_teacher_id,
                                day=new_day,
                                slot=new_slot,
                                classroom_id=alt_classroom_id
                            )
                            
                            alternative_found = True
                            resolved += 1
                            print(f"   🔄 Moved conflicting lesson to Day {new_day+1}, Slot {new_slot+1}")
                            break

                # If no alternative found, keep the entry and report it
                if not alternative_found:
                    print(f"   ⚠️  Could not resolve conflict for lesson. It remains in the schedule and needs manual review.")

        print(f"✅ Resolved {resolved} conflicts")
        return resolved

