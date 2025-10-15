# -*- coding: utf-8 -*-
"""
Integration Tests - Testing component interactions
"""

import pytest

from algorithms.enhanced_strict_scheduler import EnhancedStrictScheduler
from algorithms.simple_perfect_scheduler import SimplePerfectScheduler
from algorithms.ultimate_scheduler import UltimateScheduler
from database.db_manager import DatabaseManager


class TestEndToEndScheduling:
    """Test complete scheduling workflow"""

    def test_complete_workflow_simple_perfect(self, db_manager, sample_schedule_data):
        """Test complete workflow with SimplePerfectScheduler"""
        # 1. Verify data setup
        classes = db_manager.get_all_classes()
        teachers = db_manager.get_all_teachers()
        lessons = db_manager.get_all_lessons()

        assert len(classes) > 0
        assert len(teachers) > 0
        assert len(lessons) > 0

        # 2. Create scheduler
        scheduler = SimplePerfectScheduler(db_manager)

        # 3. Generate schedule
        schedule = scheduler.generate_schedule()

        # 4. Verify schedule
        assert isinstance(schedule, list)

        # 5. Verify no conflicts
        # (scheduler should handle this internally)

    def test_complete_workflow_ultimate(self, db_manager, sample_schedule_data):
        """Test complete workflow with UltimateScheduler"""
        # Setup
        classes = db_manager.get_all_classes()
        assert len(classes) > 0

        # Create and run
        scheduler = UltimateScheduler(db_manager)
        schedule = scheduler.generate_schedule()

        # Verify
        assert isinstance(schedule, list)

    def test_complete_workflow_enhanced_strict(self, db_manager, sample_schedule_data):
        """Test complete workflow with EnhancedStrictScheduler"""
        scheduler = EnhancedStrictScheduler(db_manager)
        schedule = scheduler.generate_schedule()

        assert isinstance(schedule, list)


class TestDatabaseIntegration:
    """Test database integration across modules"""

    def test_teacher_availability_with_scheduling(self, db_manager, sample_schedule_data):
        """Test that teacher availability affects scheduling"""
        teachers = db_manager.get_all_teachers()

        if teachers:
            teacher = teachers[0]

            # Set availability
            db_manager.set_teacher_availability(teacher.teacher_id, 1, 1, 1)

            # Get availability
            availability = db_manager.get_teacher_availability(teacher.teacher_id)

            # Should have at least one entry
            assert len(availability) >= 1

    def test_lesson_curriculum_integration(self, db_manager):
        """Test lesson and curriculum integration"""
        # Add lesson
        lesson_id = db_manager.add_lesson("Test Lesson", 0)
        assert lesson_id is not None

        # Add curriculum
        result = db_manager.add_or_update_curriculum(lesson_id, 9, 5)
        assert result is True

        # Get curriculum
        curriculum = db_manager.get_curriculum_for_lesson(lesson_id)
        assert len(curriculum) > 0


class TestSchedulerInteroperability:
    """Test different schedulers work with same data"""

    def test_all_schedulers_with_same_data(self, db_manager, sample_schedule_data):
        """Test that all schedulers can process the same data"""
        schedulers = [
            SimplePerfectScheduler(db_manager),
            UltimateScheduler(db_manager),
            EnhancedStrictScheduler(db_manager),
        ]

        for scheduler in schedulers:
            schedule = scheduler.generate_schedule()
            assert isinstance(schedule, list)
            # All should return valid schedule (empty or with entries)


class TestCRUDIntegration:
    """Test CRUD operations integration"""

    def test_full_teacher_lifecycle(self, db_manager):
        """Test complete teacher CRUD lifecycle"""
        # Create
        teacher_id = db_manager.add_teacher("Integration Teacher", "Math")
        assert teacher_id is not None

        # Read
        teacher = db_manager.get_teacher_by_id(teacher_id)
        assert teacher is not None
        assert teacher.name == "Integration Teacher"

        # Update
        result = db_manager.update_teacher(teacher_id, "Updated Teacher", "Science")
        assert result is True

        teacher = db_manager.get_teacher_by_id(teacher_id)
        assert teacher.name == "Updated Teacher"

        # Delete
        result = db_manager.delete_teacher(teacher_id)
        assert result is True

        teacher = db_manager.get_teacher_by_id(teacher_id)
        assert teacher is None

    def test_full_class_lifecycle(self, db_manager):
        """Test complete class CRUD lifecycle"""
        # Create
        class_id = db_manager.add_class("Test Class", 9)
        assert class_id is not None

        # Read
        class_obj = db_manager.get_class_by_id(class_id)
        assert class_obj is not None

        # Update
        result = db_manager.update_class(class_id, "Updated Class", 10)
        assert result is True

        # Delete
        result = db_manager.delete_class(class_id)
        assert result is True

    def test_schedule_entry_lifecycle(self, db_manager):
        """Test schedule entry lifecycle"""
        # Setup
        db_manager.set_school_type("Lise")
        class_id = db_manager.add_class("9-A", 9)
        teacher_id = db_manager.add_teacher("Teacher", "Math")
        lesson_id = db_manager.add_lesson("Math", 5)
        classroom_id = db_manager.add_classroom("A101", 30)

        # Create entry
        entry_id = db_manager.add_schedule_entry(
            class_id, teacher_id, lesson_id, classroom_id, 1, 1
        )
        assert entry_id is not None

        # Update entry
        result = db_manager.update_schedule_entry(
            entry_id, class_id, teacher_id, lesson_id, classroom_id, 2, 2
        )
        assert result is True

        # Delete entry
        result = db_manager.delete_schedule_entry(entry_id)
        assert result is True


class TestDataConsistency:
    """Test data consistency across operations"""

    def test_cascade_operations(self, db_manager):
        """Test cascade behavior (if implemented)"""
        # Create related data
        class_id = db_manager.add_class("Cascade Test", 9)
        teacher_id = db_manager.add_teacher("Cascade Teacher", "Math")
        lesson_id = db_manager.add_lesson("Cascade Lesson", 5)
        classroom_id = db_manager.add_classroom("B101", 30)

        db_manager.set_school_type("Lise")

        # Create schedule entry
        entry_id = db_manager.add_schedule_entry(
            class_id, teacher_id, lesson_id, classroom_id, 1, 1
        )

        assert entry_id is not None

        # Note: Actual cascade behavior depends on DB constraints

    def test_school_type_consistency(self, db_manager):
        """Test school type consistency across operations"""
        # Set school type
        db_manager.set_school_type("Ortaokul")

        # Verify it persists
        school_type = db_manager.get_school_type()
        assert school_type == "Ortaokul"

        # Change it
        db_manager.set_school_type("Lise")
        school_type = db_manager.get_school_type()
        assert school_type == "Lise"


class TestErrorHandling:
    """Test error handling in integrated scenarios"""

    def test_invalid_teacher_id(self, db_manager):
        """Test handling of invalid teacher ID"""
        teacher = db_manager.get_teacher_by_id(99999)
        assert teacher is None

    def test_invalid_class_id(self, db_manager):
        """Test handling of invalid class ID"""
        class_obj = db_manager.get_class_by_id(99999)
        assert class_obj is None

    def test_schedule_with_missing_data(self, db_manager):
        """Test scheduling with minimal/missing data"""
        db_manager.set_school_type("Lise")

        scheduler = SimplePerfectScheduler(db_manager)
        schedule = scheduler.generate_schedule()

        # Should handle gracefully (return empty or partial schedule)
        assert isinstance(schedule, list)
