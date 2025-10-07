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
    
    # _detect_conflicts now returns a list of conflict dicts
    assert len(conflicts) == 0
    assert isinstance(conflicts, list)


def test_detect_conflicts_class_conflict(db_manager):
    """Test conflict detection with class conflict"""
    scheduler = TestScheduler(db_manager)
    
    # Create class conflict
    scheduler._place_lesson(1, 1, 1, 0, 0)
    scheduler._place_lesson(1, 2, 2, 0, 0)  # Same class, same slot
    
    conflicts = scheduler._detect_conflicts()
    
    # _detect_conflicts now returns a list of conflict dicts
    assert len(conflicts) > 0
    assert isinstance(conflicts, list)
    # Check that we have a class conflict
    class_conflicts = [c for c in conflicts if c['type'] == 'class_conflict']
    assert len(class_conflicts) > 0


def test_detect_conflicts_teacher_conflict(db_manager):
    """Test conflict detection with teacher conflict"""
    scheduler = TestScheduler(db_manager)
    
    # Create teacher conflict
    scheduler._place_lesson(1, 1, 1, 0, 0)
    scheduler._place_lesson(2, 2, 1, 0, 0)  # Same teacher, same slot
    
    conflicts = scheduler._detect_conflicts()
    
    # _detect_conflicts now returns a list of conflict dicts
    assert len(conflicts) > 0
    assert isinstance(conflicts, list)
    # Check that we have a teacher conflict
    teacher_conflicts = [c for c in conflicts if c['type'] == 'teacher_conflict']
    assert len(teacher_conflicts) > 0


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


# ============================================================================
# Tests for Enhanced BaseScheduler Methods (Task 1.4)
# ============================================================================


def test_can_place_lesson_consecutive_slots(db_manager):
    """Test consecutive slot checking in _can_place_lesson"""
    scheduler = TestScheduler(db_manager)
    
    # Test placing 2 consecutive slots - should succeed
    can_place, reason = scheduler._can_place_lesson(
        class_id=1,
        teacher_id=1,
        day=0,
        slot=0,
        check_availability=False,
        consecutive_slots=2
    )
    
    assert can_place is True
    assert reason is None
    
    # Place a lesson at slot 1
    scheduler._place_lesson(1, 1, 1, 0, 1)
    
    # Try to place 2 consecutive slots starting at 0 - should fail
    can_place, reason = scheduler._can_place_lesson(
        class_id=1,
        teacher_id=1,
        day=0,
        slot=0,
        check_availability=False,
        consecutive_slots=2
    )
    
    assert can_place is False
    assert "slot 1" in reason


def test_can_place_lesson_consecutive_slots_teacher_conflict(db_manager):
    """Test consecutive slot checking with teacher conflict"""
    scheduler = TestScheduler(db_manager)
    
    # Place a lesson for teacher 1 at slot 2
    scheduler._place_lesson(2, 1, 1, 0, 2)
    
    # Try to place 3 consecutive slots for same teacher starting at 1
    can_place, reason = scheduler._can_place_lesson(
        class_id=1,
        teacher_id=1,
        day=0,
        slot=1,
        check_availability=False,
        consecutive_slots=3
    )
    
    assert can_place is False
    assert "Teacher already teaching" in reason


def test_is_placement_valid_advanced_single_slot(db_manager):
    """Test advanced placement validation with single slot"""
    scheduler = TestScheduler(db_manager)
    
    # Test single slot - should be valid
    is_valid = scheduler._is_placement_valid_advanced(
        class_id=1,
        teacher_id=1,
        day=0,
        slots=[0],
        check_availability=False
    )
    
    assert is_valid is True


def test_is_placement_valid_advanced_multiple_slots(db_manager):
    """Test advanced placement validation with multiple slots"""
    scheduler = TestScheduler(db_manager)
    
    # Test multiple slots - should be valid
    is_valid = scheduler._is_placement_valid_advanced(
        class_id=1,
        teacher_id=1,
        day=0,
        slots=[0, 2, 4],
        check_availability=False
    )
    
    assert is_valid is True
    
    # Place a lesson at slot 2
    scheduler._place_lesson(1, 1, 1, 0, 2)
    
    # Test again - should be invalid
    is_valid = scheduler._is_placement_valid_advanced(
        class_id=1,
        teacher_id=1,
        day=0,
        slots=[0, 2, 4],
        check_availability=False
    )
    
    assert is_valid is False


def test_is_placement_valid_advanced_empty_slots(db_manager):
    """Test advanced placement validation with empty slot list"""
    scheduler = TestScheduler(db_manager)
    
    # Empty slots list should return True
    is_valid = scheduler._is_placement_valid_advanced(
        class_id=1,
        teacher_id=1,
        day=0,
        slots=[],
        check_availability=False
    )
    
    assert is_valid is True


def test_create_lesson_blocks_default(db_manager):
    """Test default lesson block creation"""
    scheduler = TestScheduler(db_manager)
    
    # Test various hour counts
    assert scheduler._create_lesson_blocks(0) == []
    assert scheduler._create_lesson_blocks(1) == [1]
    assert scheduler._create_lesson_blocks(2) == [2]
    assert scheduler._create_lesson_blocks(3) == [2, 1]
    assert scheduler._create_lesson_blocks(4) == [2, 2]
    assert scheduler._create_lesson_blocks(5) == [2, 2, 1]
    assert scheduler._create_lesson_blocks(6) == [2, 2, 2]
    assert scheduler._create_lesson_blocks(7) == [2, 2, 2, 1]
    assert scheduler._create_lesson_blocks(8) == [2, 2, 2, 2]


def test_get_lesson_blocks_advanced_strategy(db_manager):
    """Test lesson blocks with advanced strategy"""
    scheduler = TestScheduler(db_manager)
    
    # Test advanced strategy uses _create_lesson_blocks
    blocks = scheduler._get_lesson_blocks(5, strategy='advanced')
    
    assert blocks == [2, 2, 1]
    assert isinstance(blocks, list)


def test_get_lesson_blocks_default_strategy(db_manager):
    """Test lesson blocks with default strategy"""
    scheduler = TestScheduler(db_manager)
    
    # Test default strategy
    assert scheduler._get_lesson_blocks(6, strategy='default') == [2, 2, 2]
    assert scheduler._get_lesson_blocks(5, strategy='default') == [2, 2, 1]
    assert scheduler._get_lesson_blocks(4, strategy='default') == [2, 2]


def test_detect_conflicts_format(db_manager):
    """Test that _detect_conflicts returns correct format"""
    scheduler = TestScheduler(db_manager)
    
    # Create a class conflict
    scheduler._place_lesson(1, 1, 1, 0, 0)
    scheduler._place_lesson(1, 2, 2, 0, 0)
    
    conflicts = scheduler._detect_conflicts()
    
    # Verify format
    assert isinstance(conflicts, list)
    assert len(conflicts) > 0
    
    # Check conflict structure
    conflict = conflicts[0]
    assert 'type' in conflict
    assert 'entry1' in conflict
    assert 'entry2' in conflict
    assert 'day' in conflict
    assert 'slot' in conflict
    assert conflict['type'] == 'class_conflict'


def test_detect_conflicts_multiple_types(db_manager):
    """Test detecting both class and teacher conflicts"""
    scheduler = TestScheduler(db_manager)
    
    # Create class conflict
    scheduler._place_lesson(1, 1, 1, 0, 0)
    scheduler._place_lesson(1, 2, 2, 0, 0)
    
    # Create teacher conflict
    scheduler._place_lesson(2, 3, 3, 1, 1)
    scheduler._place_lesson(3, 4, 3, 1, 1)
    
    conflicts = scheduler._detect_conflicts()
    
    # Should have both types
    class_conflicts = [c for c in conflicts if c['type'] == 'class_conflict']
    teacher_conflicts = [c for c in conflicts if c['type'] == 'teacher_conflict']
    
    assert len(class_conflicts) > 0
    assert len(teacher_conflicts) > 0


def test_get_class_lessons(db_manager, sample_schedule_data):
    """Test getting class lessons with details"""
    scheduler = TestScheduler(db_manager)
    
    # Get test data
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
    
    # Get class lessons
    class_lessons = scheduler._get_class_lessons(
        class_obj, lessons, assignment_map, teachers
    )
    
    # Verify structure
    assert isinstance(class_lessons, list)
    
    # If we have lessons, check structure
    if len(class_lessons) > 0:
        lesson_info = class_lessons[0]
        assert 'lesson_id' in lesson_info
        assert 'lesson_name' in lesson_info
        assert 'teacher_id' in lesson_info
        assert 'teacher_name' in lesson_info
        assert 'weekly_hours' in lesson_info


def test_get_class_lessons_no_assignments(db_manager, sample_schedule_data):
    """Test getting class lessons with no assignments"""
    scheduler = TestScheduler(db_manager)
    
    classes = db_manager.get_all_classes()
    lessons = db_manager.get_all_lessons()
    teachers = db_manager.get_all_teachers()
    
    if not classes or not lessons:
        pytest.skip("No test data available")
    
    class_obj = classes[0]
    
    # Empty assignment map
    assignment_map = {}
    
    # Get class lessons
    class_lessons = scheduler._get_class_lessons(
        class_obj, lessons, assignment_map, teachers
    )
    
    # Should return empty list
    assert isinstance(class_lessons, list)
    assert len(class_lessons) == 0


def test_find_available_classroom_empty_schedule(db_manager, sample_schedule_data):
    """Test finding available classroom in empty schedule"""
    scheduler = TestScheduler(db_manager)
    
    classrooms = db_manager.get_all_classrooms()
    
    if not classrooms:
        pytest.skip("No classrooms available")
    
    # Find available classroom
    classroom = scheduler._find_available_classroom(classrooms, day=0, time_slot=0)
    
    # Should find a classroom
    assert classroom is not None
    assert hasattr(classroom, 'classroom_id')


def test_find_available_classroom_occupied(db_manager, sample_schedule_data):
    """Test finding available classroom when some are occupied"""
    scheduler = TestScheduler(db_manager)
    
    classrooms = db_manager.get_all_classrooms()
    
    if not classrooms or len(classrooms) < 2:
        pytest.skip("Need at least 2 classrooms")
    
    # Occupy first classroom
    scheduler._place_lesson(
        class_id=1,
        lesson_id=1,
        teacher_id=1,
        day=0,
        slot=0,
        classroom_id=classrooms[0].classroom_id
    )
    
    # Find available classroom
    classroom = scheduler._find_available_classroom(classrooms, day=0, time_slot=0)
    
    # Should find a different classroom
    assert classroom is not None
    assert classroom.classroom_id != classrooms[0].classroom_id


def test_find_available_classroom_all_occupied(db_manager, sample_schedule_data):
    """Test finding available classroom when all are occupied"""
    scheduler = TestScheduler(db_manager)
    
    classrooms = db_manager.get_all_classrooms()
    
    if not classrooms:
        pytest.skip("No classrooms available")
    
    # Occupy all classrooms
    for i, classroom in enumerate(classrooms):
        scheduler._place_lesson(
            class_id=i + 1,
            lesson_id=1,
            teacher_id=i + 1,
            day=0,
            slot=0,
            classroom_id=classroom.classroom_id
        )
    
    # Try to find available classroom
    classroom = scheduler._find_available_classroom(classrooms, day=0, time_slot=0)
    
    # Should return None
    assert classroom is None


def test_load_scheduler_weights_default(db_manager):
    """Test default scheduler weights loading"""
    scheduler = TestScheduler(db_manager)
    
    # Default implementation should return empty dict
    weights = scheduler._load_scheduler_weights()
    
    assert isinstance(weights, dict)
    assert len(weights) == 0


def test_load_scheduler_weights_override(db_manager):
    """Test that subclasses can override weight loading"""
    
    class CustomScheduler(BaseScheduler):
        """Custom scheduler with weights"""
        
        def generate_schedule(self):
            return []
        
        def _load_scheduler_weights(self):
            return {
                'morning_preference': 1.5,
                'afternoon_preference': 0.8,
                'consecutive_penalty': -0.5
            }
    
    scheduler = CustomScheduler(db_manager)
    weights = scheduler._load_scheduler_weights()
    
    assert isinstance(weights, dict)
    assert len(weights) == 3
    assert 'morning_preference' in weights
    assert weights['morning_preference'] == 1.5


def test_create_lesson_blocks_override(db_manager):
    """Test that subclasses can override block creation"""
    
    class CustomScheduler(BaseScheduler):
        """Custom scheduler with custom block logic"""
        
        def generate_schedule(self):
            return []
        
        def _create_lesson_blocks(self, total_hours):
            # Custom logic: always create single-hour blocks
            return [1] * total_hours
    
    scheduler = CustomScheduler(db_manager)
    
    # Test custom block creation
    blocks = scheduler._create_lesson_blocks(5)
    assert blocks == [1, 1, 1, 1, 1]
    
    # Test with advanced strategy
    blocks = scheduler._get_lesson_blocks(5, strategy='advanced')
    assert blocks == [1, 1, 1, 1, 1]


def test_is_slot_occupied_by_class(db_manager):
    """Test checking if slot is occupied by class"""
    scheduler = TestScheduler(db_manager)
    
    # Initially not occupied
    assert scheduler._is_slot_occupied_by_class(1, 0, 0) is False
    
    # Place lesson
    scheduler._place_lesson(1, 1, 1, 0, 0)
    
    # Now occupied
    assert scheduler._is_slot_occupied_by_class(1, 0, 0) is True
    
    # Different slot not occupied
    assert scheduler._is_slot_occupied_by_class(1, 0, 1) is False


def test_is_slot_occupied_by_teacher(db_manager):
    """Test checking if slot is occupied by teacher"""
    scheduler = TestScheduler(db_manager)
    
    # Initially not occupied
    assert scheduler._is_slot_occupied_by_teacher(1, 0, 0) is False
    
    # Place lesson
    scheduler._place_lesson(1, 1, 1, 0, 0)
    
    # Now occupied
    assert scheduler._is_slot_occupied_by_teacher(1, 0, 0) is True
    
    # Different slot not occupied
    assert scheduler._is_slot_occupied_by_teacher(1, 0, 1) is False
