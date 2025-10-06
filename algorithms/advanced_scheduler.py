# -*- coding: utf-8 -*-
"""
Advanced Scheduling Algorithm with Scoring and Smart Distribution
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


class AdvancedScheduler:
    """Advanced scheduler with scoring system and smart distribution"""
    
    # School time slots
    SCHOOL_TIME_SLOTS = {
        "İlkokul": 7,      # İlkokul: 5 gün × 7 saat = 35 hücre
        "Ortaokul": 7,     # Ortaokul: 5 gün × 7 saat = 35 hücre
        "Lise": 8,         # Lise: 5 gün × 8 saat = 40 hücre
        "Anadolu Lisesi": 8,
        "Fen Lisesi": 8,
        "Sosyal Bilimler Lisesi": 8
    }
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
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

        # Get school configuration
        school_type = self.db_manager.get_school_type() or "Lise"
        time_slots_count = self.SCHOOL_TIME_SLOTS.get(school_type, 8)

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

        # Initialize schedule with existing entries
        schedule_entries = []
        for entry in existing_schedule:
            schedule_entries.append({
                'class_id': entry.class_id,
                'teacher_id': entry.teacher_id,
                'lesson_id': entry.lesson_id,
                'classroom_id': entry.classroom_id,
                'day': entry.day,
                'time_slot': entry.time_slot
            })

        print(f"📋 Loaded {len(schedule_entries)} existing schedule entries")
        
        # Process each class
        for class_idx, class_obj in enumerate(classes, 1):
            print(f"\n{'='*70}")
            print(f"📚 [{class_idx}/{len(classes)}] Scheduling: {class_obj.name} (Grade {class_obj.grade})")
            print(f"{'='*70}")
            
            # Get lessons for this class
            class_lessons = self._get_class_lessons(
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
                    schedule_entries,
                    class_obj,
                    lesson_info,
                    time_slots_count,
                    classrooms
                )
                
                if not success:
                    print(f"⚠️  Warning: Could not fully schedule {lesson_info['lesson_name']}")
            
            # Summary for this class
            class_total = len([e for e in schedule_entries if e['class_id'] == class_obj.class_id])
            expected_total = sum(l['weekly_hours'] for l in class_lessons)
            coverage = (class_total / expected_total * 100) if expected_total > 0 else 0
            
            print(f"\n📊 Class Summary: {class_total}/{expected_total} hours scheduled ({coverage:.1f}%)")
        
        # Final summary and conflict check
        print(f"\n{'='*70}")
        print(f"🎯 SCHEDULE GENERATION COMPLETED")
        print(f"{'='*70}")
        print(f"📊 Total entries: {len(schedule_entries)}")
        
        # Check conflicts
        conflicts = self._detect_conflicts(schedule_entries)
        if conflicts:
            print(f"⚠️  {len(conflicts)} conflicts detected!")
            resolved = self._attempt_conflict_resolution(schedule_entries, conflicts, time_slots_count)
            print(f"✅ Resolved {resolved} conflicts")
        else:
            print(f"✅ No conflicts detected!")
        
        # Save updated schedule to database
        print(f"\n💾 Saving schedule to database...")
        saved_count = 0

        # Clear existing schedule first
        self.db_manager.clear_schedule()

        # Save new schedule
        for entry in schedule_entries:
            if self.db_manager.add_schedule_program(
                entry['class_id'], entry['teacher_id'], entry['lesson_id'],
                entry['classroom_id'], entry['day'], entry['time_slot']
            ):
                saved_count += 1

        print(f"✅ Saved {saved_count} schedule entries to database")

        return schedule_entries
    
    def _get_class_lessons(self, class_obj, lessons, assignment_map, teachers) -> List[Dict]:
        """Get all lessons assigned to a class with their details"""
        class_lessons = []
        
        for lesson in lessons:
            assignment_key = (class_obj.class_id, lesson.lesson_id)
            if assignment_key in assignment_map:
                # Get weekly hours from curriculum
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
    
    def _schedule_lesson_smart(self, schedule_entries, class_obj, lesson_info, time_slots_count, classrooms) -> bool:
        """
        Smart lesson scheduling with scoring and distribution
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
                    
                    # Check if placement is valid (both in memory and database)
                    if self._is_placement_valid(
                        schedule_entries, class_obj.class_id, teacher_id, day, slots
                    ):
                        # Calculate score for this placement
                        score = self._calculate_placement_score(
                            schedule_entries, class_obj.class_id, lesson_id,
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
                
                # Find available classroom for this time slot
                available_classroom = self._find_available_classroom(
                    schedule_entries, classrooms, day, slots[0]
                )

                if available_classroom:
                    classroom_id = available_classroom.classroom_id
                else:
                    classroom_id = 1  # Fallback to default

                # Add entries to schedule
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
                
                scheduled_blocks.append({
                    'day': day,
                    'slots': slots
                })
            else:
                print(f"   ❌ Could not find valid placement for block {block_idx + 1}")
                # Try single-slot fallback
                for day in range(5):
                    for slot in range(time_slots_count):
                        if self._is_placement_valid(
                            schedule_entries, class_obj.class_id, teacher_id, day, [slot]
                        ):
                            # Find available classroom for fallback placement
                            available_classroom = self._find_available_classroom(
                                schedule_entries, classrooms, day, slot
                            )

                            fallback_classroom_id = available_classroom.classroom_id if available_classroom else 1

                            schedule_entries.append({
                                'class_id': class_obj.class_id,
                                'teacher_id': teacher_id,
                                'lesson_id': lesson_id,
                                'classroom_id': fallback_classroom_id,
                                'day': day,
                                'time_slot': slot
                            })
                            scheduled_hours += 1
                            print(f"   ⚠️  Fallback: Placed 1 hour on day {day+1}, slot {slot+1}")
                            
                            if scheduled_hours >= block_size:
                                break
                    if scheduled_hours >= len([s for b in scheduled_blocks for s in b['slots']]) + block_size:
                        break
        
        success_rate = (scheduled_hours / weekly_hours * 100) if weekly_hours > 0 else 0
        print(f"\n   📊 Result: {scheduled_hours}/{weekly_hours} hours ({success_rate:.1f}%)")
        
        return scheduled_hours >= weekly_hours  # Enforce 100% success
    
    def _create_smart_blocks(self, total_hours: int) -> List[int]:
        """
        Create smart lesson blocks with optimal distribution
        Examples:
        - 1 hour: [1]
        - 2 hours: [2]
        - 3 hours: [2, 1]
        - 4 hours: [2, 2]
        - 5 hours: [2, 2, 1]
        - 6 hours: [2, 2, 2]
        - 7 hours: [2, 2, 2, 1]
        - 8 hours: [2, 2, 2, 2]
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
    
    def _is_placement_valid(self, schedule_entries, class_id, teacher_id, day, slots) -> bool:
        """Check if placing lesson in given slots is valid (no conflicts)"""
        for slot in slots:
            # Check teacher's explicit availability
            if not self.db_manager.is_teacher_available(teacher_id, day, slot):
                return False

            # Check conflicts in memory schedule
            for entry in schedule_entries:
                entry_day = entry['day']
                entry_slot = entry['time_slot']

                # Check same time
                if entry_day == day and entry_slot == slot:
                    # Class conflict
                    if entry['class_id'] == class_id:
                        return False
                    # Teacher conflict
                    if entry['teacher_id'] == teacher_id:
                        return False

            # Also check conflicts in database schedule
            existing_schedule = self.db_manager.get_schedule_program_by_school_type()
            for entry in existing_schedule:
                if entry.day == day and entry.time_slot == slot:
                    # Class conflict
                    if entry.class_id == class_id:
                        return False
                    # Teacher conflict
                    if entry.teacher_id == teacher_id:
                        return False

        return True
    
    def _calculate_placement_score(self, schedule_entries, class_id, lesson_id,
                                   day, slots, scheduled_blocks, total_hours, time_slots_count) -> float:
        """
        Calculate score for a potential placement
        Higher score = better placement
        """
        score = 100.0  # Base score
        
        # Get existing schedule for this class on this day
        day_schedule = [e for e in schedule_entries 
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
    
    def _detect_conflicts(self, schedule_entries) -> List[Dict]:
        """Detect scheduling conflicts"""
        conflicts = []
        
        # Check teacher conflicts
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
        
        # Check class conflicts
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
    
    def _attempt_conflict_resolution(self, schedule_entries, conflicts, time_slots_count):
        """Attempt to resolve conflicts automatically"""
        print(f"\n🔧 Attempting to resolve {len(conflicts)} conflicts...")

        resolved = 0
        for conflict in conflicts:
            if 'entry2' in conflict and conflict['entry2'] in schedule_entries:
                # Try to find alternative placement for the conflicting entry
                alt_entry = conflict['entry2']
                alt_class_id = alt_entry['class_id']
                alt_teacher_id = alt_entry['teacher_id']
                alt_lesson_id = alt_entry['lesson_id']
                alt_day = alt_entry['day']
                alt_slot = alt_entry['time_slot']

                # Try to find alternative slot for this entry
                alternative_found = False
                for new_day in range(5):
                    if alternative_found:
                        break
                    for new_slot in range(time_slots_count):
                        # Skip the original conflicting slot
                        if new_day == alt_day and new_slot == alt_slot:
                            continue

                        # Check if new slot is available
                        if self._is_placement_valid(schedule_entries, alt_class_id, alt_teacher_id, new_day, [new_slot]):
                            # Update the entry with new slot
                            alt_entry['day'] = new_day
                            alt_entry['time_slot'] = new_slot
                            alternative_found = True
                            resolved += 1
                            print(f"   🔄 Moved conflicting lesson to Day {new_day+1}, Slot {new_slot+1}")
                            break

                # If no alternative found, keep the entry and report it
                if not alternative_found:
                    print(f"   ⚠️  Could not resolve conflict for lesson. It remains in the schedule and needs manual review.")

        print(f"✅ Resolved {resolved} conflicts")
        return resolved

    def _find_available_classroom(self, schedule_entries, classrooms, day, time_slot):
        """Find an available classroom for a specific day and time slot"""
        for classroom in classrooms:
            # Check if classroom is already scheduled at this time
            classroom_scheduled = False
            for entry in schedule_entries:
                entry_day = entry['day']
                entry_time_slot = entry['time_slot']
                entry_classroom_id = entry['classroom_id']

                if (entry_classroom_id == classroom.classroom_id and
                    entry_day == day and entry_time_slot == time_slot):
                    classroom_scheduled = True
                    break

            if not classroom_scheduled:
                return classroom

        return None  # No available classroom found