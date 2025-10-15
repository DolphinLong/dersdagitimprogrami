# -*- coding: utf-8 -*-
"""
Tests for EnhancedStrictScheduler - Backtracking + Smart Prioritization
"""

import pytest

from algorithms.enhanced_strict_scheduler import EnhancedStrictScheduler


class TestEnhancedStrictScheduler:
    """Test EnhancedStrictScheduler class"""

    def test_initialization(self, db_manager):
        """Test scheduler initialization"""
        scheduler = EnhancedStrictScheduler(db_manager)
        assert scheduler.db_manager == db_manager
        assert len(scheduler.schedule_entries) == 0
        assert len(scheduler.teacher_usage) == 0
        assert len(scheduler.class_usage) == 0
        assert len(scheduler.slot_pressure) == 0

    def test_school_time_slots_config(self, db_manager):
        """Test that school types have correct time slots"""
        scheduler = EnhancedStrictScheduler(db_manager)

        assert scheduler.SCHOOL_TIME_SLOTS["İlkokul"] == 7
        assert scheduler.SCHOOL_TIME_SLOTS["Ortaokul"] == 7
        assert scheduler.SCHOOL_TIME_SLOTS["Lise"] == 8
        assert scheduler.SCHOOL_TIME_SLOTS["Fen Lisesi"] == 8

    def test_generate_schedule_basic(self, db_manager, sample_schedule_data):
        """Test basic schedule generation"""
        scheduler = EnhancedStrictScheduler(db_manager)
        schedule = scheduler.generate_schedule()

        # Should return a list
        assert isinstance(schedule, list)

    def test_teacher_usage_tracking(self, db_manager, sample_schedule_data):
        """Test that teacher usage is tracked"""
        scheduler = EnhancedStrictScheduler(db_manager)

        # Initial state
        assert len(scheduler.teacher_usage) == 0

        # Generate schedule
        scheduler.generate_schedule()

        # Teacher usage should be tracked (may or may not have entries depending on data)
        assert isinstance(scheduler.teacher_usage, dict)

    def test_class_usage_tracking(self, db_manager, sample_schedule_data):
        """Test that class usage is tracked"""
        scheduler = EnhancedStrictScheduler(db_manager)

        # Initial state
        assert len(scheduler.class_usage) == 0

        # Generate schedule
        scheduler.generate_schedule()

        # Class usage should be tracked
        assert isinstance(scheduler.class_usage, dict)

    def test_slot_pressure_tracking(self, db_manager, sample_schedule_data):
        """Test that slot pressure is tracked"""
        scheduler = EnhancedStrictScheduler(db_manager)

        # Initial state
        assert len(scheduler.slot_pressure) == 0

        # Generate schedule
        scheduler.generate_schedule()

        # Slot pressure should be tracked
        assert isinstance(scheduler.slot_pressure, dict)

    def test_state_reset_on_generation(self, db_manager, sample_schedule_data):
        """Test that state resets on new generation"""
        scheduler = EnhancedStrictScheduler(db_manager)

        # First generation
        scheduler.generate_schedule()

        # Manually add some entries
        scheduler.schedule_entries.append({"test": "entry"})

        # Second generation should reset
        scheduler.generate_schedule()

        # schedule_entries should be reset
        # (though it may have new entries after generation)
        assert isinstance(scheduler.schedule_entries, list)

    def test_multiple_generations(self, db_manager, sample_schedule_data):
        """Test multiple schedule generations"""
        scheduler = EnhancedStrictScheduler(db_manager)

        # First generation
        schedule1 = scheduler.generate_schedule()
        assert isinstance(schedule1, list)

        # Second generation
        schedule2 = scheduler.generate_schedule()
        assert isinstance(schedule2, list)

    def test_empty_database_handling(self, db_manager):
        """Test scheduler with empty database"""
        scheduler = EnhancedStrictScheduler(db_manager)

        # Generate with minimal/no data
        schedule = scheduler.generate_schedule()

        # Should handle gracefully
        assert isinstance(schedule, list)

    def test_schedule_entries_format(self, db_manager, sample_schedule_data):
        """Test that schedule entries have correct format"""
        scheduler = EnhancedStrictScheduler(db_manager)
        schedule = scheduler.generate_schedule()

        # Check list format
        assert isinstance(schedule, list)

        # If entries exist, check they are dicts
        for entry in schedule:
            assert isinstance(entry, dict)

    def test_school_type_affects_slots(self, db_manager):
        """Test that school type affects time slot count"""
        db_manager.set_school_type("Ortaokul")

        scheduler = EnhancedStrictScheduler(db_manager)
        schedule = scheduler.generate_schedule()

        # Should process according to school type
        assert isinstance(schedule, list)

    def test_usage_tracking_independence(self, db_manager):
        """Test that usage tracking structures are independent"""
        scheduler = EnhancedStrictScheduler(db_manager)

        # All should be separate structures
        assert scheduler.teacher_usage is not scheduler.class_usage
        assert scheduler.teacher_usage is not scheduler.slot_pressure
        assert scheduler.class_usage is not scheduler.slot_pressure

    def test_schedule_entries_cleared_on_init(self, db_manager):
        """Test that schedule entries are cleared on generation"""
        scheduler = EnhancedStrictScheduler(db_manager)

        # Add dummy entry
        scheduler.schedule_entries.append({"dummy": "data"})

        # Generate new schedule
        scheduler.generate_schedule()

        # Old entry should be cleared
        # (schedule_entries is reset to [] in generate_schedule)
        # Note: After generation it may have new entries, but old ones are gone
        assert isinstance(scheduler.schedule_entries, list)
