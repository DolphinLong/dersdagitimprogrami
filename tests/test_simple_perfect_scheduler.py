# -*- coding: utf-8 -*-
"""
Tests for SimplePerfectScheduler
"""

import pytest
from algorithms.simple_perfect_scheduler import SimplePerfectScheduler


def test_simple_perfect_scheduler_initialization(db_manager):
    """Test SimplePerfectScheduler initialization"""
    scheduler = SimplePerfectScheduler(db_manager)
    
    assert scheduler.db_manager is not None
    assert len(scheduler.schedule_entries) == 0
    assert len(scheduler.teacher_slots) == 0
    assert len(scheduler.class_slots) == 0


def test_simple_perfect_scheduler_school_time_slots():
    """Test SCHOOL_TIME_SLOTS configuration"""
    assert SimplePerfectScheduler.SCHOOL_TIME_SLOTS["İlkokul"] == 7
    assert SimplePerfectScheduler.SCHOOL_TIME_SLOTS["Ortaokul"] == 7
    assert SimplePerfectScheduler.SCHOOL_TIME_SLOTS["Lise"] == 8
    assert SimplePerfectScheduler.SCHOOL_TIME_SLOTS["Anadolu Lisesi"] == 8


def test_generate_schedule_empty_database(db_manager):
    """Test schedule generation with empty database"""
    scheduler = SimplePerfectScheduler(db_manager)
    schedule = scheduler.generate_schedule()
    
    # With empty database, should return empty schedule
    assert isinstance(schedule, list)
    assert len(schedule) == 0


def test_generate_schedule_with_data(db_manager, sample_schedule_data):
    """Test schedule generation with sample data"""
    scheduler = SimplePerfectScheduler(db_manager)
    schedule = scheduler.generate_schedule()
    
    # Should generate some schedule entries
    assert isinstance(schedule, list)
    assert len(schedule) > 0
    
    # Check entry structure
    if schedule:
        entry = schedule[0]
        assert 'class_id' in entry
        assert 'lesson_id' in entry
        assert 'teacher_id' in entry
        assert 'day' in entry
        assert 'time_slot' in entry


def test_schedule_no_conflicts(db_manager, sample_schedule_data):
    """Test that generated schedule has no conflicts"""
    scheduler = SimplePerfectScheduler(db_manager)
    schedule = scheduler.generate_schedule()
    
    # Check for class conflicts
    class_slots = {}
    for entry in schedule:
        key = (entry['class_id'], entry['day'], entry['time_slot'])
        if key in class_slots:
            pytest.fail(f"Class conflict detected at {key}")
        class_slots[key] = entry
    
    # Check for teacher conflicts
    teacher_slots = {}
    for entry in schedule:
        key = (entry['teacher_id'], entry['day'], entry['time_slot'])
        if key in teacher_slots:
            pytest.fail(f"Teacher conflict detected at {key}")
        teacher_slots[key] = entry


def test_schedule_respects_weekly_hours(db_manager, sample_schedule_data):
    """Test that schedule respects weekly hour limits"""
    scheduler = SimplePerfectScheduler(db_manager)
    schedule = scheduler.generate_schedule()
    
    # Count hours per class-lesson combination
    lesson_hours = {}
    for entry in schedule:
        key = (entry['class_id'], entry['lesson_id'])
        lesson_hours[key] = lesson_hours.get(key, 0) + 1
    
    # Verify hours don't exceed weekly requirements
    # (This is a basic check - actual limits depend on curriculum)
    for key, hours in lesson_hours.items():
        assert hours <= 10, f"Too many hours ({hours}) for {key}"


def test_schedule_uses_available_days(db_manager, sample_schedule_data):
    """Test that schedule uses valid days (0-4)"""
    scheduler = SimplePerfectScheduler(db_manager)
    schedule = scheduler.generate_schedule()
    
    for entry in schedule:
        assert 0 <= entry['day'] <= 4, f"Invalid day: {entry['day']}"


def test_schedule_uses_available_time_slots(db_manager, sample_schedule_data):
    """Test that schedule uses valid time slots"""
    scheduler = SimplePerfectScheduler(db_manager)
    schedule = scheduler.generate_schedule()
    
    # Get school type time slots
    school_type = db_manager.get_school_type() or "Lise"
    max_slots = SimplePerfectScheduler.SCHOOL_TIME_SLOTS.get(school_type, 8)
    
    for entry in schedule:
        assert 0 <= entry['time_slot'] < max_slots, \
            f"Invalid time slot: {entry['time_slot']} (max: {max_slots})"


def test_schedule_assigns_valid_teachers(db_manager, sample_schedule_data):
    """Test that schedule assigns valid teacher IDs"""
    scheduler = SimplePerfectScheduler(db_manager)
    schedule = scheduler.generate_schedule()
    
    teachers = db_manager.get_all_teachers()
    valid_teacher_ids = {t.teacher_id for t in teachers}
    
    for entry in schedule:
        assert entry['teacher_id'] in valid_teacher_ids, \
            f"Invalid teacher ID: {entry['teacher_id']}"


def test_schedule_assigns_valid_classes(db_manager, sample_schedule_data):
    """Test that schedule assigns valid class IDs"""
    scheduler = SimplePerfectScheduler(db_manager)
    schedule = scheduler.generate_schedule()
    
    classes = db_manager.get_all_classes()
    valid_class_ids = {c.class_id for c in classes}
    
    for entry in schedule:
        assert entry['class_id'] in valid_class_ids, \
            f"Invalid class ID: {entry['class_id']}"


def test_schedule_assigns_valid_lessons(db_manager, sample_schedule_data):
    """Test that schedule assigns valid lesson IDs"""
    scheduler = SimplePerfectScheduler(db_manager)
    schedule = scheduler.generate_schedule()
    
    lessons = db_manager.get_all_lessons()
    valid_lesson_ids = {l.lesson_id for l in lessons}
    
    for entry in schedule:
        assert entry['lesson_id'] in valid_lesson_ids, \
            f"Invalid lesson ID: {entry['lesson_id']}"


def test_schedule_saves_to_database(db_manager, sample_schedule_data):
    """Test that schedule is saved to database"""
    scheduler = SimplePerfectScheduler(db_manager)
    schedule = scheduler.generate_schedule()
    
    # Get schedule from database
    db_schedule = db_manager.get_schedule_program_by_school_type()
    
    # Should have entries
    assert len(db_schedule) > 0
    
    # Should match generated schedule count
    assert len(db_schedule) == len(schedule)


def test_multiple_schedule_generations(db_manager, sample_schedule_data):
    """Test that multiple generations work correctly"""
    scheduler = SimplePerfectScheduler(db_manager)
    
    # First generation
    schedule1 = scheduler.generate_schedule()
    assert len(schedule1) > 0
    
    # Second generation
    schedule2 = scheduler.generate_schedule()
    assert len(schedule2) > 0
    
    # Both should have similar sizes (may vary slightly due to algorithm)
    assert abs(len(schedule1) - len(schedule2)) < 10


def test_schedule_handles_insufficient_slots(db_manager):
    """Test scheduler behavior when there aren't enough slots"""
    # Add class
    class_id = db_manager.add_class(name="Test Class", grade=5)
    class_obj = db_manager.get_class_by_id(class_id)
    
    # Add many lessons requiring lots of hours
    for i in range(10):
        lesson_id = db_manager.add_lesson(name=f"Lesson {i}")
        teacher_id = db_manager.add_teacher(name=f"Teacher {i}", subject=f"Subject {i}")
        
        # Use the correct method name
        assignment = db_manager.add_schedule_by_school_type(
            class_id=class_id,
            lesson_id=lesson_id,
            teacher_id=teacher_id
        )
        
        # Add weekly hours (total would exceed available slots)
        db_manager.add_lesson_weekly_hours(
            lesson_id=lesson_id,
            grade=5,
            school_type="Ortaokul",
            weekly_hours=5
        )
    
    scheduler = SimplePerfectScheduler(db_manager)
    schedule = scheduler.generate_schedule()
    
    # Should still generate valid schedule (may not place everything)
    assert isinstance(schedule, list)
    
    # Should not exceed total available slots (5 days * 7 hours = 35)
    assert len(schedule) <= 35
