# -*- coding: utf-8 -*-
"""
Integration Tests for AdvancedScheduler with BaseScheduler

This test suite validates the integration between AdvancedScheduler and
BaseScheduler methods.

Requirements: 5.1, 5.3
"""

import pytest

from algorithms.advanced_scheduler import AdvancedScheduler

# ============================================================================
# Test 3: Integration with BaseScheduler Methods
# ============================================================================


def test_uses_base_scheduler_place_lesson(db_manager):
    """Test that AdvancedScheduler uses BaseScheduler _place_lesson"""
    scheduler = AdvancedScheduler(db_manager)

    # Place a lesson
    scheduler._place_lesson(1, 1, 1, 0, 0)

    # Verify BaseScheduler state is updated
    assert len(scheduler.schedule_entries) == 1
    assert (0, 0) in scheduler.class_slots[1]
    assert (0, 0) in scheduler.teacher_slots[1]

    # Verify entry format
    entry = scheduler.schedule_entries[0]
    assert entry["class_id"] == 1
    assert entry["lesson_id"] == 1
    assert entry["teacher_id"] == 1
    assert entry["day"] == 0
    assert entry["time_slot"] == 0


def test_uses_base_scheduler_remove_lesson(db_manager):
    """Test that AdvancedScheduler uses BaseScheduler _remove_lesson"""
    scheduler = AdvancedScheduler(db_manager)

    # Place and then remove a lesson
    scheduler._place_lesson(1, 1, 1, 0, 0)
    entry = scheduler.schedule_entries[0]
    scheduler._remove_lesson(entry)

    # Verify BaseScheduler state is updated
    assert len(scheduler.schedule_entries) == 0
    assert (0, 0) not in scheduler.class_slots[1]
    assert (0, 0) not in scheduler.teacher_slots[1]


def test_uses_base_scheduler_can_place_lesson(db_manager):
    """Test that AdvancedScheduler uses BaseScheduler _can_place_lesson"""
    scheduler = AdvancedScheduler(db_manager)

    # Check if can place lesson
    can_place, reason = scheduler._can_place_lesson(
        class_id=1, teacher_id=1, day=0, slot=0, check_availability=False
    )

    assert can_place is True
    assert reason is None

    # Place lesson and check again
    scheduler._place_lesson(1, 1, 1, 0, 0)

    can_place, reason = scheduler._can_place_lesson(
        class_id=1, teacher_id=2, day=0, slot=0, check_availability=False
    )

    assert can_place is False
    assert reason is not None


def test_uses_base_scheduler_is_placement_valid_advanced(db_manager):
    """Test that AdvancedScheduler uses BaseScheduler _is_placement_valid_advanced"""
    scheduler = AdvancedScheduler(db_manager)

    # Test single slot validation
    is_valid = scheduler._is_placement_valid_advanced(
        class_id=1, teacher_id=1, day=0, slots=[0], check_availability=False
    )

    assert is_valid is True

    # Test multiple slots validation
    is_valid = scheduler._is_placement_valid_advanced(
        class_id=1, teacher_id=1, day=0, slots=[0, 1, 2], check_availability=False
    )

    assert is_valid is True

    # Place lesson and test again
    scheduler._place_lesson(1, 1, 1, 0, 1)

    is_valid = scheduler._is_placement_valid_advanced(
        class_id=1, teacher_id=1, day=0, slots=[0, 1, 2], check_availability=False
    )

    assert is_valid is False


def test_uses_base_scheduler_detect_conflicts(db_manager):
    """Test that AdvancedScheduler uses BaseScheduler _detect_conflicts"""
    scheduler = AdvancedScheduler(db_manager)

    # No conflicts initially
    conflicts = scheduler._detect_conflicts()
    assert isinstance(conflicts, list)
    assert len(conflicts) == 0

    # Create a conflict
    scheduler._place_lesson(1, 1, 1, 0, 0)
    scheduler._place_lesson(1, 2, 2, 0, 0)

    conflicts = scheduler._detect_conflicts()
    assert len(conflicts) > 0

    # Verify conflict format
    conflict = conflicts[0]
    assert "type" in conflict
    assert "entry1" in conflict
    assert "entry2" in conflict
    assert "day" in conflict
    assert "slot" in conflict


def test_uses_base_scheduler_find_available_classroom(db_manager, sample_schedule_data):
    """Test that AdvancedScheduler uses BaseScheduler _find_available_classroom"""
    scheduler = AdvancedScheduler(db_manager)

    classrooms = db_manager.get_all_classrooms()

    if not classrooms:
        pytest.skip("No classrooms available")

    # Find available classroom
    classroom = scheduler._find_available_classroom(classrooms, day=0, time_slot=0)

    assert classroom is not None
    assert hasattr(classroom, "classroom_id")


def test_uses_base_scheduler_get_class_lessons(db_manager, sample_schedule_data):
    """Test that AdvancedScheduler uses BaseScheduler _get_class_lessons"""
    scheduler = AdvancedScheduler(db_manager)

    classes = db_manager.get_all_classes()
    lessons = db_manager.get_all_lessons()
    teachers = db_manager.get_all_teachers()

    if not classes or not lessons or not teachers:
        pytest.skip("No test data available")

    class_obj = classes[0]

    # Create assignment map
    assignment_map = {}
    for lesson in lessons:
        assignment_map[(class_obj.class_id, lesson.lesson_id)] = teachers[0].teacher_id

    # Get class lessons using inherited method
    class_lessons = scheduler._get_class_lessons(class_obj, lessons, assignment_map, teachers)

    assert isinstance(class_lessons, list)


def test_uses_base_scheduler_get_school_config(db_manager):
    """Test that AdvancedScheduler uses BaseScheduler _get_school_config"""
    scheduler = AdvancedScheduler(db_manager)

    config = scheduler._get_school_config()

    assert "school_type" in config
    assert "time_slots_count" in config
    assert config["time_slots_count"] > 0


def test_conflict_resolution_updates_base_state(db_manager):
    """Test that conflict resolution attempts to resolve conflicts"""
    scheduler = AdvancedScheduler(db_manager)

    # Create a conflict - both lessons for same class at same time
    scheduler._place_lesson(1, 1, 1, 0, 0)
    scheduler._place_lesson(1, 2, 2, 0, 0)

    # Get conflicts
    conflicts = scheduler._detect_conflicts()
    assert len(conflicts) > 0
    initial_conflict_count = len(conflicts)

    # Attempt resolution
    resolved = scheduler._attempt_conflict_resolution(conflicts, time_slots_count=8)

    # Verify resolution was attempted
    assert resolved >= 0  # Resolution count should be non-negative

    # After resolution, check that conflicts are reduced or eliminated
    remaining_conflicts = scheduler._detect_conflicts()
    assert (
        len(remaining_conflicts) < initial_conflict_count
    ), "Conflict resolution should reduce conflicts"

    # Verify that entries still exist (moved, not deleted)
    assert len(scheduler.schedule_entries) == 2


def test_schedule_generation_uses_base_state_management(db_manager):
    """Test that schedule generation uses BaseScheduler state management"""
    scheduler = AdvancedScheduler(db_manager)

    # Manually place some lessons to simulate schedule generation
    # This tests state management without triggering full generation
    scheduler._place_lesson(1, 1, 1, 0, 0)
    scheduler._place_lesson(1, 2, 2, 0, 1)
    scheduler._place_lesson(2, 3, 3, 1, 0)
    scheduler._place_lesson(2, 4, 4, 1, 1)
    scheduler._place_lesson(3, 5, 5, 2, 0)

    # Verify BaseScheduler state is properly maintained
    assert len(scheduler.schedule_entries) == 5

    # Verify state consistency for all entries
    for entry in scheduler.schedule_entries:
        class_id = entry["class_id"]
        teacher_id = entry["teacher_id"]
        day = entry["day"]
        slot = entry["time_slot"]

        # Verify the entry is tracked in both class_slots and teacher_slots
        assert (day, slot) in scheduler.class_slots[
            class_id
        ], f"Entry not in class_slots: class={class_id}, day={day}, slot={slot}"
        assert (day, slot) in scheduler.teacher_slots[
            teacher_id
        ], f"Entry not in teacher_slots: teacher={teacher_id}, day={day}, slot={slot}"


def test_advanced_scheduler_preserves_base_validation(db_manager):
    """Test that AdvancedScheduler preserves BaseScheduler validation"""
    scheduler = AdvancedScheduler(db_manager)

    # Place valid lessons
    scheduler._place_lesson(1, 1, 1, 0, 0)
    scheduler._place_lesson(1, 2, 2, 0, 1)

    # Validation should pass
    assert scheduler._validate_schedule() is True


def test_advanced_scheduler_state_consistency(db_manager):
    """Test that AdvancedScheduler maintains state consistency with BaseScheduler"""
    scheduler = AdvancedScheduler(db_manager)

    # Perform multiple operations
    scheduler._place_lesson(1, 1, 1, 0, 0)
    scheduler._place_lesson(2, 2, 2, 0, 1)
    scheduler._place_lesson(3, 3, 3, 1, 0)

    # Verify state consistency
    assert len(scheduler.schedule_entries) == 3
    assert len(scheduler.class_slots) == 3
    assert len(scheduler.teacher_slots) == 3

    # Remove one entry
    entry = scheduler.schedule_entries[1]
    scheduler._remove_lesson(entry)

    # Verify state is still consistent
    assert len(scheduler.schedule_entries) == 2
    assert (0, 1) not in scheduler.class_slots[2]
    assert (0, 1) not in scheduler.teacher_slots[2]


# ============================================================================
# Test 4: Complete Schedule Generation Workflow Integration Tests
# ============================================================================


def test_complete_schedule_generation_workflow(db_manager, sample_schedule_data):
    """
    Test complete schedule generation workflow from start to finish
    Requirements: 5.1, 5.4
    """
    scheduler = AdvancedScheduler(db_manager)

    # Generate schedule
    schedule = scheduler.generate_schedule()

    # Verify schedule was generated
    assert schedule is not None
    assert isinstance(schedule, list)
    assert len(schedule) > 0

    # Verify all entries have required fields
    for entry in schedule:
        assert "class_id" in entry
        assert "lesson_id" in entry
        assert "teacher_id" in entry
        assert "day" in entry
        assert "time_slot" in entry
        assert isinstance(entry["day"], int)
        assert isinstance(entry["time_slot"], int)
        assert 0 <= entry["day"] <= 4  # Monday to Friday
        assert entry["time_slot"] >= 0

    # Verify state consistency after generation
    assert len(scheduler.schedule_entries) == len(schedule)

    # Verify no conflicts in final schedule
    conflicts = scheduler._detect_conflicts()
    assert len(conflicts) == 0, f"Schedule has {len(conflicts)} unresolved conflicts"


def test_schedule_generation_with_existing_entries(db_manager, sample_schedule_data):
    """
    Test schedule generation when there are existing schedule entries
    Requirements: 5.1, 5.4
    """
    # Add some existing schedule entries to database
    classes = db_manager.get_all_classes()
    lessons = db_manager.get_all_lessons()
    teachers = db_manager.get_all_teachers()
    classrooms = db_manager.get_all_classrooms()

    if classes and lessons and teachers and classrooms:
        # Add a few existing entries
        db_manager.add_schedule_program(
            class_id=classes[0].class_id,
            lesson_id=lessons[0].lesson_id,
            teacher_id=teachers[0].teacher_id,
            classroom_id=classrooms[0].classroom_id,
            day=0,
            time_slot=0,
        )
        db_manager.add_schedule_program(
            class_id=classes[0].class_id,
            lesson_id=lessons[1].lesson_id,
            teacher_id=teachers[1].teacher_id,
            classroom_id=classrooms[0].classroom_id,
            day=0,
            time_slot=1,
        )

    scheduler = AdvancedScheduler(db_manager)

    # Generate schedule (should include existing entries)
    schedule = scheduler.generate_schedule()

    # Verify existing entries are preserved
    assert len(schedule) >= 2

    # Verify no conflicts
    conflicts = scheduler._detect_conflicts()
    assert len(conflicts) == 0


def test_schedule_generation_conflict_detection(db_manager, sample_schedule_data):
    """
    Test that conflict detection works during schedule generation
    Requirements: 5.1, 5.4
    """
    scheduler = AdvancedScheduler(db_manager)

    # Manually create a conflict scenario
    scheduler._place_lesson(1, 1, 1, 0, 0)
    scheduler._place_lesson(1, 2, 2, 0, 0)  # Same class, same time

    # Detect conflicts
    conflicts = scheduler._detect_conflicts()

    # Verify conflicts are detected
    assert len(conflicts) > 0
    assert conflicts[0]["type"] == "class_conflict"
    assert conflicts[0]["day"] == 0
    assert conflicts[0]["slot"] == 0


def test_schedule_generation_conflict_resolution(db_manager, sample_schedule_data):
    """
    Test that conflict resolution works during schedule generation
    Requirements: 5.1, 5.4
    """
    scheduler = AdvancedScheduler(db_manager)

    # Create conflicts (without checking availability)
    scheduler._place_lesson(1, 1, 1, 0, 0)
    scheduler._place_lesson(1, 2, 2, 0, 0)  # Class conflict
    scheduler._place_lesson(2, 3, 1, 0, 0)  # Teacher conflict

    conflicts = scheduler._detect_conflicts()
    initial_conflict_count = len(conflicts)
    assert initial_conflict_count > 0

    # Attempt resolution (conflict resolution doesn't check availability)
    config = scheduler._get_school_config()
    resolved = scheduler._attempt_conflict_resolution(conflicts, config["time_slots_count"])

    # Verify resolution was attempted
    assert resolved >= 0

    # Verify conflicts are reduced
    remaining_conflicts = scheduler._detect_conflicts()
    assert len(remaining_conflicts) < initial_conflict_count


def test_schedule_generation_teacher_availability(db_manager, sample_schedule_data):
    """
    Test that schedule generation respects teacher availability mechanism
    Requirements: 5.1, 5.4

    Note: This test verifies the availability check mechanism exists,
    but doesn't test actual availability since Teacher model doesn't
    have availability attribute by default. The test verifies that
    the check_availability parameter is properly handled.
    """
    teachers = db_manager.get_all_teachers()

    if not teachers:
        pytest.skip("No teachers available")

    teacher = teachers[0]

    scheduler = AdvancedScheduler(db_manager)

    # Test without availability check (default behavior in advanced scheduler)
    can_place_no_check, reason_no_check = scheduler._can_place_lesson(
        class_id=1, teacher_id=teacher.teacher_id, day=0, slot=0, check_availability=False
    )

    # Should be able to place when not checking availability
    assert can_place_no_check is True
    assert reason_no_check is None

    # Verify the scheduler uses check_availability=False by default
    # This is important for the migration to work correctly
    is_valid = scheduler._is_placement_valid_advanced(
        class_id=1, teacher_id=teacher.teacher_id, day=0, slots=[0], check_availability=False
    )

    assert is_valid is True


def test_schedule_generation_classroom_assignment(db_manager, sample_schedule_data):
    """
    Test that schedule generation assigns classrooms correctly
    Requirements: 5.1, 5.4
    """
    scheduler = AdvancedScheduler(db_manager)
    classrooms = db_manager.get_all_classrooms()

    if not classrooms:
        pytest.skip("No classrooms available")

    # Find available classroom
    classroom = scheduler._find_available_classroom(classrooms, day=0, time_slot=0)

    assert classroom is not None

    # Place lesson with classroom
    scheduler._place_lesson(1, 1, 1, 0, 0, classroom_id=classroom.classroom_id)

    # Verify classroom is assigned
    entry = scheduler.schedule_entries[0]
    assert entry["classroom_id"] == classroom.classroom_id

    # Verify classroom is now occupied
    classroom2 = scheduler._find_available_classroom(classrooms, day=0, time_slot=0)
    # Should return different classroom or None if all occupied
    if classroom2:
        assert classroom2.classroom_id != classroom.classroom_id


def test_schedule_generation_smart_block_distribution(db_manager, sample_schedule_data):
    """
    Test that schedule generation uses smart block distribution
    Requirements: 5.1, 5.4
    """
    scheduler = AdvancedScheduler(db_manager)

    # Test smart block creation for various weekly hours
    blocks_3 = scheduler._create_smart_blocks(3)
    assert sum(blocks_3) == 3
    assert len(blocks_3) <= 3  # Should distribute across days

    blocks_5 = scheduler._create_smart_blocks(5)
    assert sum(blocks_5) == 5
    assert len(blocks_5) <= 5

    blocks_6 = scheduler._create_smart_blocks(6)
    assert sum(blocks_6) == 6
    assert len(blocks_6) <= 5  # Max 5 days


def test_schedule_generation_state_management(db_manager, sample_schedule_data):
    """
    Test that schedule generation properly manages BaseScheduler state
    Requirements: 5.1, 5.4
    """
    scheduler = AdvancedScheduler(db_manager)

    # Generate schedule
    schedule = scheduler.generate_schedule()

    # Verify state is properly maintained
    assert len(scheduler.schedule_entries) == len(schedule)

    # Verify all entries are tracked in state
    for entry in schedule:
        class_id = entry["class_id"]
        teacher_id = entry["teacher_id"]
        day = entry["day"]
        slot = entry["time_slot"]

        assert (day, slot) in scheduler.class_slots[class_id]
        assert (day, slot) in scheduler.teacher_slots[teacher_id]


def test_schedule_generation_validation(db_manager, sample_schedule_data):
    """
    Test that schedule generation produces valid schedules
    Requirements: 5.1, 5.4
    """
    scheduler = AdvancedScheduler(db_manager)

    # Generate schedule
    schedule = scheduler.generate_schedule()

    # Validate schedule using BaseScheduler validation
    is_valid = scheduler._validate_schedule()

    assert is_valid is True


def test_schedule_generation_output_format(db_manager, sample_schedule_data):
    """
    Test that schedule generation output matches expected format
    Requirements: 5.1, 5.4
    """
    scheduler = AdvancedScheduler(db_manager)

    # Generate schedule
    schedule = scheduler.generate_schedule()

    # Verify output format
    assert isinstance(schedule, list)

    for entry in schedule:
        # Verify all required fields exist
        assert "class_id" in entry
        assert "lesson_id" in entry
        assert "teacher_id" in entry
        assert "day" in entry
        assert "time_slot" in entry

        # Verify field types
        assert isinstance(entry["class_id"], int)
        assert isinstance(entry["lesson_id"], int)
        assert isinstance(entry["teacher_id"], int)
        assert isinstance(entry["day"], int)
        assert isinstance(entry["time_slot"], int)

        # Verify field ranges
        assert entry["class_id"] > 0
        assert entry["lesson_id"] > 0
        assert entry["teacher_id"] > 0
        assert 0 <= entry["day"] <= 4
        assert entry["time_slot"] >= 0


def test_schedule_generation_database_persistence(db_manager, sample_schedule_data):
    """
    Test that generated schedule is properly saved to database
    Requirements: 5.1, 5.4
    """
    scheduler = AdvancedScheduler(db_manager)

    # Generate schedule
    schedule = scheduler.generate_schedule()

    # Retrieve schedule from database
    db_schedule = db_manager.get_schedule_program_by_school_type()

    # Verify schedule was saved
    assert len(db_schedule) > 0

    # Verify all generated entries are in database
    # Note: May have more entries if there were existing ones
    assert len(db_schedule) >= len(schedule)


def test_schedule_generation_empty_data(db_manager):
    """
    Test schedule generation with no data (edge case)
    Requirements: 5.1, 5.4
    """
    scheduler = AdvancedScheduler(db_manager)

    # Generate schedule with no data
    schedule = scheduler.generate_schedule()

    # Should return empty list or handle gracefully
    assert isinstance(schedule, list)
    assert len(schedule) == 0


def test_schedule_generation_single_class(db_manager):
    """
    Test schedule generation with single class
    Requirements: 5.1, 5.4
    """
    # Create minimal data - one class, one teacher, one lesson
    class_id = db_manager.add_class(name="5A", grade=5)
    teacher_id = db_manager.add_teacher(name="Test Teacher", subject="Math")
    lesson_id = db_manager.add_lesson(name="Math")
    classroom_id = db_manager.add_classroom(name="Room 1", capacity=30)

    # Add weekly hours
    db_manager.add_lesson_weekly_hours(
        lesson_id=lesson_id, grade=5, school_type="Ortaokul", weekly_hours=3
    )

    # Create assignment
    db_manager.add_schedule_by_school_type(
        class_id=class_id, lesson_id=lesson_id, teacher_id=teacher_id, classroom_id=classroom_id
    )

    scheduler = AdvancedScheduler(db_manager)

    # Generate schedule
    schedule = scheduler.generate_schedule()

    # Verify schedule was generated
    assert len(schedule) > 0
    assert all(e["class_id"] == class_id for e in schedule)
    assert all(e["teacher_id"] == teacher_id for e in schedule)
    assert all(e["lesson_id"] == lesson_id for e in schedule)


def test_schedule_generation_consistency_across_runs(db_manager, sample_schedule_data):
    """
    Test that schedule generation produces consistent results
    Requirements: 5.1, 5.4
    """
    scheduler1 = AdvancedScheduler(db_manager)
    schedule1 = scheduler1.generate_schedule()

    # Get initial count
    initial_count = len(schedule1)

    # Generate again without clearing (should produce similar results)
    scheduler2 = AdvancedScheduler(db_manager)
    schedule2 = scheduler2.generate_schedule()

    # Verify both schedules have entries
    assert len(schedule1) > 0
    assert len(schedule2) > 0

    # Verify both schedules are valid
    assert scheduler1._validate_schedule() is True
    assert scheduler2._validate_schedule() is True
