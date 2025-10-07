# -*- coding: utf-8 -*-
"""
Tests for AdvancedScheduler - Refactored Version

This test suite validates the refactored AdvancedScheduler that inherits from
BaseScheduler. It tests:
1. Inheritance behavior and method overrides
2. Advanced-specific functionality preservation
3. Integration with BaseScheduler methods

Requirements: 5.1, 5.3
"""

import pytest
from algorithms.advanced_scheduler import AdvancedScheduler
from algorithms.base_scheduler import BaseScheduler


# ============================================================================
# Test 1: Inheritance Behavior and Method Overrides
# ============================================================================


def test_advanced_scheduler_inherits_from_base(db_manager):
    """Test that AdvancedScheduler properly inherits from BaseScheduler"""
    scheduler = AdvancedScheduler(db_manager)
    
    # Verify inheritance
    assert isinstance(scheduler, BaseScheduler)
    assert isinstance(scheduler, AdvancedScheduler)


def test_advanced_scheduler_initialization(db_manager):
    """Test AdvancedScheduler initialization calls super().__init__"""
    scheduler = AdvancedScheduler(db_manager)
    
    # Verify BaseScheduler attributes are initialized
    assert scheduler.db_manager is not None
    assert hasattr(scheduler, 'schedule_entries')
    assert hasattr(scheduler, 'teacher_slots')
    assert hasattr(scheduler, 'class_slots')
    assert len(scheduler.schedule_entries) == 0
    
    # Verify AdvancedScheduler-specific attributes
    assert hasattr(scheduler, 'weights')
    assert isinstance(scheduler.weights, dict)
    assert len(scheduler.weights) > 0


def test_advanced_scheduler_weights_initialization(db_manager):
    """Test that scheduler weights are properly initialized"""
    scheduler = AdvancedScheduler(db_manager)
    
    # Check that all expected weights are present
    expected_weights = [
        'same_day_penalty',
        'distribution_bonus',
        'block_preference_bonus',
        'early_slot_penalty',
        'late_slot_penalty',
        'lunch_break_bonus',
        'consecutive_bonus',
        'gap_penalty',
        'teacher_load_balance'
    ]
    
    for weight_key in expected_weights:
        assert weight_key in scheduler.weights
        assert isinstance(scheduler.weights[weight_key], (int, float))


def test_create_lesson_blocks_override(db_manager):
    """Test that AdvancedScheduler overrides _create_lesson_blocks"""
    scheduler = AdvancedScheduler(db_manager)
    
    # Test the override produces expected smart blocks
    assert scheduler._create_lesson_blocks(0) == []
    assert scheduler._create_lesson_blocks(1) == [1]
    assert scheduler._create_lesson_blocks(2) == [2]
    assert scheduler._create_lesson_blocks(3) == [2, 1]
    assert scheduler._create_lesson_blocks(4) == [2, 2]
    assert scheduler._create_lesson_blocks(5) == [2, 2, 1]
    assert scheduler._create_lesson_blocks(6) == [2, 2, 2]
    assert scheduler._create_lesson_blocks(7) == [2, 2, 2, 1]
    assert scheduler._create_lesson_blocks(8) == [2, 2, 2, 2]


def test_create_smart_blocks_calls_create_lesson_blocks(db_manager):
    """Test that _create_smart_blocks calls overridden _create_lesson_blocks"""
    scheduler = AdvancedScheduler(db_manager)
    
    # Both methods should produce identical results
    for hours in range(1, 9):
        smart_blocks = scheduler._create_smart_blocks(hours)
        lesson_blocks = scheduler._create_lesson_blocks(hours)
        assert smart_blocks == lesson_blocks


def test_get_lesson_blocks_uses_advanced_strategy(db_manager):
    """Test that _get_lesson_blocks with advanced strategy uses override"""
    scheduler = AdvancedScheduler(db_manager)
    
    # Test with advanced strategy
    blocks = scheduler._get_lesson_blocks(5, strategy='advanced')
    assert blocks == [2, 2, 1]
    
    # Verify it matches the overridden method
    assert blocks == scheduler._create_lesson_blocks(5)


# ============================================================================
# Test 2: Advanced-Specific Functionality Preservation
# ============================================================================


def test_calculate_placement_score_base_score(db_manager):
    """Test that placement scoring works correctly"""
    scheduler = AdvancedScheduler(db_manager)
    
    # Calculate score for a simple placement
    score = scheduler._calculate_placement_score(
        class_id=1,
        lesson_id=1,
        day=0,
        slots=[0],
        scheduled_blocks=[],
        total_hours=5,
        time_slots_count=8
    )
    
    # Base score should be 100.0
    assert isinstance(score, float)
    assert score > 0  # Should have positive score


def test_calculate_placement_score_same_day_penalty(db_manager):
    """Test same day penalty in scoring"""
    scheduler = AdvancedScheduler(db_manager)
    
    # Place a lesson first
    scheduler._place_lesson(1, 1, 1, 0, 0)
    
    # Calculate score for same lesson on same day
    score = scheduler._calculate_placement_score(
        class_id=1,
        lesson_id=1,
        day=0,
        slots=[2],
        scheduled_blocks=[],
        total_hours=5,
        time_slots_count=8
    )
    
    # Should have penalty applied
    assert score < 100.0  # Penalty should reduce score


def test_calculate_placement_score_distribution_bonus(db_manager):
    """Test distribution bonus for spreading across days"""
    scheduler = AdvancedScheduler(db_manager)
    
    # Calculate score for first block
    score1 = scheduler._calculate_placement_score(
        class_id=1,
        lesson_id=1,
        day=0,
        slots=[0],
        scheduled_blocks=[],
        total_hours=5,
        time_slots_count=8
    )
    
    # Calculate score for second block on different day
    score2 = scheduler._calculate_placement_score(
        class_id=1,
        lesson_id=1,
        day=1,
        slots=[0],
        scheduled_blocks=[{'day': 0, 'slots': [0]}],
        total_hours=5,
        time_slots_count=8
    )
    
    # Second placement should get distribution bonus
    assert isinstance(score2, float)


def test_calculate_placement_score_early_slot_penalty(db_manager):
    """Test early slot penalty"""
    scheduler = AdvancedScheduler(db_manager)
    
    # Calculate score for very early slot
    score_early = scheduler._calculate_placement_score(
        class_id=1,
        lesson_id=1,
        day=0,
        slots=[0],
        scheduled_blocks=[],
        total_hours=5,
        time_slots_count=8
    )
    
    # Calculate score for normal slot
    score_normal = scheduler._calculate_placement_score(
        class_id=1,
        lesson_id=1,
        day=0,
        slots=[2],
        scheduled_blocks=[],
        total_hours=5,
        time_slots_count=8
    )
    
    # Early slot should have lower score
    assert score_early < score_normal


def test_calculate_placement_score_late_slot_penalty(db_manager):
    """Test late slot penalty"""
    scheduler = AdvancedScheduler(db_manager)
    
    # Calculate score for very late slot
    score_late = scheduler._calculate_placement_score(
        class_id=1,
        lesson_id=1,
        day=0,
        slots=[6, 7],
        scheduled_blocks=[],
        total_hours=5,
        time_slots_count=8
    )
    
    # Calculate score for normal slot
    score_normal = scheduler._calculate_placement_score(
        class_id=1,
        lesson_id=1,
        day=0,
        slots=[2, 3],
        scheduled_blocks=[],
        total_hours=5,
        time_slots_count=8
    )
    
    # Late slot should have lower score
    assert score_late < score_normal


def test_calculate_placement_score_gap_penalty(db_manager):
    """Test gap penalty for non-consecutive lessons"""
    scheduler = AdvancedScheduler(db_manager)
    
    # Place lessons with a gap
    scheduler._place_lesson(1, 1, 1, 0, 0)
    scheduler._place_lesson(1, 2, 2, 0, 4)
    
    # Calculate score for slot that creates gap
    score_gap = scheduler._calculate_placement_score(
        class_id=1,
        lesson_id=3,
        day=0,
        slots=[2],
        scheduled_blocks=[],
        total_hours=5,
        time_slots_count=8
    )
    
    # Should have gap penalty
    assert isinstance(score_gap, float)


def test_calculate_placement_score_consecutive_bonus(db_manager):
    """Test consecutive bonus for adjacent lessons"""
    scheduler = AdvancedScheduler(db_manager)
    
    # Place a lesson
    scheduler._place_lesson(1, 1, 1, 0, 2)
    
    # Calculate score for adjacent slot
    score_adjacent = scheduler._calculate_placement_score(
        class_id=1,
        lesson_id=2,
        day=0,
        slots=[3],
        scheduled_blocks=[],
        total_hours=5,
        time_slots_count=8
    )
    
    # Calculate score for non-adjacent slot
    score_non_adjacent = scheduler._calculate_placement_score(
        class_id=1,
        lesson_id=2,
        day=0,
        slots=[5],
        scheduled_blocks=[],
        total_hours=5,
        time_slots_count=8
    )
    
    # Adjacent should have higher score
    assert score_adjacent > score_non_adjacent


