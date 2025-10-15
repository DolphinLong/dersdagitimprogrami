# -*- coding: utf-8 -*-
"""
Unit tests for SimplePerfectScheduler
"""

from unittest.mock import MagicMock

import pytest

from algorithms.simple_perfect_scheduler import SimplePerfectScheduler


@pytest.fixture
def scheduler(db_manager):
    """Returns a SimplePerfectScheduler instance"""
    return SimplePerfectScheduler(db_manager)


@pytest.fixture
def mock_db_manager():
    """Returns a mocked db_manager"""
    db = MagicMock()
    db.get_all_classes.return_value = []
    db.get_all_teachers.return_value = []
    db.get_all_lessons.return_value = []
    db.get_all_classrooms.return_value = []
    db.get_schedule_by_school_type.return_value = []
    db.get_school_type.return_value = "Lise"
    db.get_weekly_hours_for_lesson.return_value = 2
    db.get_teacher_by_id.return_value = MagicMock()
    db.is_teacher_available.return_value = True
    return db


class TestSimplePerfectSchedulerUnit:
    def test_can_place_all_no_conflict(self, mock_db_manager):
        scheduler = SimplePerfectScheduler(mock_db_manager)
        assert scheduler._can_place_all(1, 1, 0, [0, 1]) == True

    def test_can_place_all_class_conflict(self, mock_db_manager):
        scheduler = SimplePerfectScheduler(mock_db_manager)
        scheduler.class_slots[1].add((0, 0))
        assert scheduler._can_place_all(1, 1, 0, [0, 1]) == False

    def test_can_place_all_teacher_conflict(self, mock_db_manager):
        scheduler = SimplePerfectScheduler(mock_db_manager)
        scheduler.teacher_slots[1].add((0, 0))
        assert scheduler._can_place_all(1, 1, 0, [0, 1]) == False

    def test_can_place_all_teacher_not_available(self, mock_db_manager):
        mock_db_manager.is_teacher_available.return_value = False
        scheduler = SimplePerfectScheduler(mock_db_manager)
        assert scheduler._can_place_all(1, 1, 0, [0, 1]) == False

    def test_would_create_three_consecutive_lessons_false(self, mock_db_manager):
        scheduler = SimplePerfectScheduler(mock_db_manager)
        scheduler.schedule_entries = [
            {"class_id": 1, "lesson_id": 1, "day": 0, "time_slot": 0},
        ]
        assert scheduler._would_create_three_consecutive_lessons(1, 1, 0, 2) == False

    def test_would_create_three_consecutive_lessons_true(self, mock_db_manager):
        scheduler = SimplePerfectScheduler(mock_db_manager)
        scheduler.schedule_entries = [
            {"class_id": 1, "lesson_id": 1, "day": 0, "time_slot": 0},
            {"class_id": 1, "lesson_id": 1, "day": 0, "time_slot": 1},
        ]
        assert scheduler._would_create_three_consecutive_lessons(1, 1, 0, 2) == True

    def test_try_singles(self, mock_db_manager):
        scheduler = SimplePerfectScheduler(mock_db_manager)
        scheduled_hours = scheduler._try_singles(1, 1, 1, 2, 8, [])
        assert scheduled_hours == 2
        assert len(scheduler.schedule_entries) == 2

    def test_try_blocks_strict(self, mock_db_manager):
        scheduler = SimplePerfectScheduler(mock_db_manager)
        scheduled_hours, used_days = scheduler._try_blocks_strict(1, 1, 1, 2, 8, [], 2)
        assert scheduled_hours == 4
        assert len(used_days) == 2
        assert len(scheduler.schedule_entries) == 4
