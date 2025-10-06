# -*- coding: utf-8 -*-
"""
Tests for BaseScheduler
"""

import pytest
from algorithms.base_scheduler import BaseScheduler
from exceptions import ConflictError


class TestScheduler(BaseScheduler):
    """Test implementation of BaseScheduler"""
    
    def generate_schedule(self):
        """Dummy implementation"""
        return []


def test_base_scheduler_initialization(db_manager):
    """Test base scheduler initialization"""
    scheduler = TestScheduler(db_manager)
    
    assert scheduler.db_manager is not None
    assert len(scheduler.schedule_entries) == 0
    assert len(scheduler.teacher_slots) == 0
    assert len(scheduler.class_slots) == 0


def test_get_school_config(db_manager):
    """Test school configuration retrieval"""
    scheduler = TestScheduler(db_manager)
    config = scheduler._get_school_config()
    
    assert 'school_type' in config
    assert 'time_slots_count' in config
    assert config['time_slots_count'] > 0


def test_can_place_lesson_empty_schedule(db_manager):
    """Test placing lesson in empty schedule"""
    scheduler = TestScheduler(db_manager)
    
    can_place, reason = scheduler._can_place_lesson(
        class_id=1,
        teacher_id=1,
        day=0,
        slot=0,
        check_availability=False
    )
    
    assert can_place is True
    assert reason is None


def test_can_place_lesson_class_conflict(db_manager):
    """Test class conflict detection"""
    scheduler = TestScheduler(db_manager)
    
    # Place first lesson
    scheduler._place_lesson(
        class_id=1,
        lesson_id=1,
        teacher_id=1,
        day=0,
        slot=0
    )
    
    # Try to place another lesson at same slot
    can_place, reason = scheduler._can_place_lesson(
        class_id=1,
        teacher_id=2,
        day=0,
        slot=0,
        check_availability=False
    )
    
    assert can_place is False
    assert "Class already has a lesson" in reason


def test_can_place_lesson_teacher_conflict(db_manager):
    """Test teacher conflict detection"""
    scheduler = TestScheduler(db_manager)
    
    # Place first lesson
    scheduler._place_lesson(
        class_id=1,
        lesson_id=1,
        teacher_id=1,
        day=0,
        slot=0
    )
    
    # Try to place lesson with same teacher at same slot
    can_place, reason = scheduler._can_place_lesson(
        class_id=2,
        teacher_id=1,
        day=0,
        slot=0,
        check_availability=False
    )
    
    assert can_place is False
    assert "Teacher already teaching" in reason


def test_place_and_remove_lesson(db_manager):
    """Test placing and removing lessons"""
    scheduler = TestScheduler(db_manager)
    
    # Place lesson
    scheduler._place_lesson(
        class_id=1,
        lesson_id=1,
        teacher_id=1,
        day=0,
        slot=0
    )
    
    assert len(scheduler.schedule_entries) == 1
    assert (0, 0) in scheduler.class_slots[1]
    assert (0, 0) in scheduler.teacher_slots[1]
    
    # Remove lesson
    entry = scheduler.schedule_entries[0]
    scheduler._remove_lesson(entry)
    
    assert len(scheduler.schedule_entries) == 0
    assert (0, 0) not in scheduler.class_slots[1]
    assert (0, 0) not in scheduler.teacher_slots[1]


def test_find_available_slots(db_manager):
    """Test finding available slots"""
    scheduler = TestScheduler(db_manager)
    
    # Find available slots (should be all slots initially)
    slots = scheduler._find_available_slots(
        class_id=1,
        teacher_id=1,
        check_availability=False
    )
    
    assert len(slots) > 0  # Should have available slots
    
    # Place a lesson
    scheduler._place_lesson(
        class_id=1,
        lesson_id=1,
        teacher_id=1,
        day=0,
        slot=0
    )
    
    # Find available slots again
    new_slots = scheduler._find_available_slots(
        class_id=1,
        teacher_id=1,
        check_availability=False
    )
    
    assert len(new_slots) == len(slots) - 1  # One less slot available


def test_get_lesson_blocks(db_manager):
    """Test lesson block calculation"""
    scheduler = TestScheduler(db_manager)
    
    assert scheduler._get_lesson_blocks(6) == [2, 2, 2]
    assert scheduler._get_lesson_blocks(5) == [2, 2, 1]
    assert scheduler._get_lesson_blocks(4) == [2, 2]
    assert scheduler._get_lesson_blocks(3) == [2, 1]
    assert scheduler._get_lesson_blocks(2) == [2]
    assert scheduler._get_lesson_blocks(1) == [1]


def test_detect_conflicts_no_conflicts(db_manager):
    """Test conflict detection with no conflicts"""
    scheduler = TestScheduler(db_manager)
    
    # Place lessons without conflicts
    scheduler._place_lesson(1, 1, 1, 0, 0)
    scheduler._place_lesson(1, 2, 2, 0, 1)
    scheduler._place_lesson(2, 1, 1, 0, 1)
    
    conflicts = scheduler._detect_conflicts()
    
    assert conflicts['total_conflicts'] == 0
    assert len(conflicts['class_conflicts']) == 0
    assert len(conflicts['teacher_conflicts']) == 0


def test_detect_conflicts_class_conflict(db_manager):
    """Test conflict detection with class conflict"""
    scheduler = TestScheduler(db_manager)
    
    # Create class conflict
    scheduler._place_lesson(1, 1, 1, 0, 0)
    scheduler._place_lesson(1, 2, 2, 0, 0)  # Same class, same slot
    
    conflicts = scheduler._detect_conflicts()
    
    assert conflicts['total_conflicts'] > 0
    assert len(conflicts['class_conflicts']) > 0


def test_detect_conflicts_teacher_conflict(db_manager):
    """Test conflict detection with teacher conflict"""
    scheduler = TestScheduler(db_manager)
    
    # Create teacher conflict
    scheduler._place_lesson(1, 1, 1, 0, 0)
    scheduler._place_lesson(2, 2, 1, 0, 0)  # Same teacher, same slot
    
    conflicts = scheduler._detect_conflicts()
    
    assert conflicts['total_conflicts'] > 0
    assert len(conflicts['teacher_conflicts']) > 0


def test_validate_schedule_valid(db_manager):
    """Test schedule validation with valid schedule"""
    scheduler = TestScheduler(db_manager)
    
    # Create valid schedule
    scheduler._place_lesson(1, 1, 1, 0, 0)
    scheduler._place_lesson(1, 2, 2, 0, 1)
    
    assert scheduler._validate_schedule() is True


def test_validate_schedule_invalid(db_manager):
    """Test schedule validation with invalid schedule"""
    scheduler = TestScheduler(db_manager)
    
    # Create invalid schedule (conflict)
    scheduler._place_lesson(1, 1, 1, 0, 0)
    scheduler._place_lesson(1, 2, 2, 0, 0)  # Conflict!
    
    with pytest.raises(ConflictError):
        scheduler._validate_schedule()


def test_calculate_coverage(db_manager, sample_schedule_data):
    """Test coverage calculation"""
    scheduler = TestScheduler(db_manager)
    
    # Place some lessons
    for i in range(10):
        scheduler._place_lesson(
            class_id=1,
            lesson_id=1,
            teacher_id=1,
            day=i % 5,
            slot=i % 7
        )
    
    coverage = scheduler._calculate_coverage()
    
    assert 'total_slots' in coverage
    assert 'total_scheduled' in coverage
    assert 'empty_slots' in coverage
    assert 'coverage_percentage' in coverage
    assert coverage['total_scheduled'] == 10
