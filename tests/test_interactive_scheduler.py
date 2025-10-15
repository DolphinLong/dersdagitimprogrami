# -*- coding: utf-8 -*-
"""
Unit tests for InteractiveScheduler
"""

from unittest.mock import MagicMock

import pytest

from algorithms.interactive_scheduler import InteractiveScheduler


@pytest.fixture
def mock_db_manager():
    """Returns a mocked db_manager"""
    db = MagicMock()
    db.get_lesson_by_id.return_value = MagicMock()
    db.is_teacher_available.return_value = True
    return db


@pytest.fixture
def scheduler(mock_db_manager):
    """Returns an InteractiveScheduler instance"""
    return InteractiveScheduler(mock_db_manager)


class TestInteractiveSchedulerUnit:
    def test_load_schedule(self, scheduler):
        schedule_data = [{"class_id": 1, "day": 0, "time_slot": 0, "teacher_id": 1, "lesson_id": 1}]
        scheduler.load_schedule(schedule_data)
        assert scheduler.get_schedule() == schedule_data

    def test_lock_unlock_entry(self, scheduler):
        scheduler.load_schedule(
            [{"class_id": 1, "day": 0, "time_slot": 0, "teacher_id": 1, "lesson_id": 1}]
        )
        assert scheduler.lock_entry(0) == True
        assert scheduler.is_locked(0) == True
        assert scheduler.unlock_entry(0) == True
        assert scheduler.is_locked(0) == False

    def test_move_entry(self, scheduler):
        scheduler.load_schedule(
            [{"class_id": 1, "day": 0, "time_slot": 0, "teacher_id": 1, "lesson_id": 1}]
        )
        success, _ = scheduler.move_entry(0, 1, 1)
        assert success == True
        assert scheduler.get_schedule()[0]["day"] == 1
        assert scheduler.get_schedule()[0]["time_slot"] == 1

    def test_move_locked_entry(self, scheduler):
        scheduler.load_schedule(
            [{"class_id": 1, "day": 0, "time_slot": 0, "teacher_id": 1, "lesson_id": 1}]
        )
        scheduler.lock_entry(0)
        success, reason = scheduler.move_entry(0, 1, 1)
        assert success == False
        assert reason == "Entry is locked"

    def test_add_entry(self, scheduler):
        scheduler.load_schedule([])
        success, _ = scheduler.add_entry(1, 1, 1, 1, 0, 0)
        assert success == True
        assert len(scheduler.get_schedule()) == 1

    def test_add_entry_conflict(self, scheduler):
        scheduler.load_schedule(
            [{"class_id": 1, "day": 0, "time_slot": 0, "teacher_id": 1, "lesson_id": 1}]
        )
        success, reason = scheduler.add_entry(1, 2, 2, 1, 0, 0)
        assert success == False
        assert reason == "Class already has a lesson at this time"

    def test_remove_entry(self, scheduler):
        scheduler.load_schedule(
            [{"class_id": 1, "day": 0, "time_slot": 0, "teacher_id": 1, "lesson_id": 1}]
        )
        success, _ = scheduler.remove_entry(0)
        assert success == True
        assert len(scheduler.get_schedule()) == 0

    def test_remove_locked_entry(self, scheduler):
        scheduler.load_schedule(
            [{"class_id": 1, "day": 0, "time_slot": 0, "teacher_id": 1, "lesson_id": 1}]
        )
        scheduler.lock_entry(0)
        success, reason = scheduler.remove_entry(0)
        assert success == False
        assert reason == "Entry is locked"

    def test_undo_redo(self, scheduler):
        scheduler.load_schedule([])
        scheduler.add_entry(1, 1, 1, 1, 0, 0)
        assert len(scheduler.get_schedule()) == 1
        scheduler.undo()
        assert len(scheduler.get_schedule()) == 0
        scheduler.redo()
        assert len(scheduler.get_schedule()) == 1
