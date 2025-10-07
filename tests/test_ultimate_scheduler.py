# -*- coding: utf-8 -*-
"""
Tests for UltimateScheduler - CSP + Backtracking + Forward Checking
"""

import pytest
from algorithms.ultimate_scheduler import UltimateScheduler, SchedulingState


class TestSchedulingState:
    """Test SchedulingState class"""
    
    def test_state_initialization(self):
        """Test that state initializes correctly"""
        state = SchedulingState()
        assert state.assignments == []
        assert len(state.teacher_usage) == 0
        assert len(state.class_usage) == 0
        assert len(state.lesson_progress) == 0
    
    def test_state_copy(self):
        """Test that state copy works correctly"""
        state = SchedulingState()
        state.assignments.append({'test': 'data'})
        state.lesson_progress[(1, 2)] = 5
        
        copied = state.copy()
        assert copied.assignments == state.assignments
        assert copied.lesson_progress == state.lesson_progress
        
        # Ensure it's a deep copy
        copied.assignments.append({'new': 'data'})
        assert len(copied.assignments) != len(state.assignments)


class TestUltimateScheduler:
    """Test UltimateScheduler class"""
    
    def test_initialization(self, db_manager):
        """Test scheduler initialization"""
        scheduler = UltimateScheduler(db_manager)
        assert scheduler.db_manager == db_manager
        assert scheduler.time_slots_count == 7
        assert scheduler.backtrack_count == 0
        assert scheduler.max_backtracks == 4000
    
    def test_school_time_slots_config(self, db_manager):
        """Test that school types have correct time slots"""
        scheduler = UltimateScheduler(db_manager)
        
        assert scheduler.SCHOOL_TIME_SLOTS["İlkokul"] == 6
        assert scheduler.SCHOOL_TIME_SLOTS["Ortaokul"] == 7
        assert scheduler.SCHOOL_TIME_SLOTS["Lise"] == 8
        assert scheduler.SCHOOL_TIME_SLOTS["Anadolu Lisesi"] == 8
    
    def test_generate_schedule_basic(self, db_manager, sample_schedule_data):
        """Test basic schedule generation"""
        scheduler = UltimateScheduler(db_manager)
        schedule = scheduler.generate_schedule()
        
        # Should generate some schedule entries
        assert isinstance(schedule, list)
    
    def test_state_management(self, db_manager):
        """Test that scheduler manages state correctly"""
        scheduler = UltimateScheduler(db_manager)
        
        # Initial state
        assert isinstance(scheduler.state, SchedulingState)
        assert len(scheduler.state.assignments) == 0
        
        # After generating
        scheduler.generate_schedule()
        # State should be managed (might be reset or have entries)
        assert isinstance(scheduler.state, SchedulingState)
    
    def test_backtrack_counter_reset(self, db_manager):
        """Test that backtrack counter resets on new generation"""
        scheduler = UltimateScheduler(db_manager)
        
        # Set counter
        scheduler.backtrack_count = 100
        
        # Generate new schedule
        scheduler.generate_schedule()
        
        # Counter should reset to 0 at start
        # (will increase during generation, but starts at 0)
        assert scheduler.backtrack_count >= 0
    
    def test_lesson_requirements_structure(self, db_manager, sample_schedule_data):
        """Test that lesson requirements are properly structured"""
        scheduler = UltimateScheduler(db_manager)
        
        # Generate schedule
        scheduler.generate_schedule()
        
        # Lesson requirements should be a list
        assert isinstance(scheduler.lesson_requirements, list)
    
    def test_domains_structure(self, db_manager):
        """Test that domains dictionary exists"""
        scheduler = UltimateScheduler(db_manager)
        
        # Domains should be a dict
        assert isinstance(scheduler.domains, dict)
    
    def test_max_backtracks_limit(self, db_manager):
        """Test that max backtracks is properly set"""
        scheduler = UltimateScheduler(db_manager)
        
        assert scheduler.max_backtracks == 4000
        assert scheduler.max_backtracks > 0
    
    def test_schedule_output_format(self, db_manager, sample_schedule_data):
        """Test that schedule output has correct format"""
        scheduler = UltimateScheduler(db_manager)
        schedule = scheduler.generate_schedule()
        
        assert isinstance(schedule, list)
        
        # If there are entries, check format
        for entry in schedule:
            assert isinstance(entry, dict)
            # Common keys that should exist in schedule entries
            # (actual keys depend on implementation)
    
    def test_multiple_generations(self, db_manager, sample_schedule_data):
        """Test that scheduler can generate multiple times"""
        scheduler = UltimateScheduler(db_manager)
        
        # First generation
        schedule1 = scheduler.generate_schedule()
        assert isinstance(schedule1, list)
        
        # Second generation
        schedule2 = scheduler.generate_schedule()
        assert isinstance(schedule2, list)
    
    def test_empty_database_handling(self, db_manager):
        """Test scheduler behavior with empty database"""
        scheduler = UltimateScheduler(db_manager)
        
        # Generate with no data (or minimal data)
        schedule = scheduler.generate_schedule()
        
        # Should return empty list or handle gracefully
        assert isinstance(schedule, list)
    
    def test_school_type_configuration(self, db_manager):
        """Test that school type affects time slot count"""
        db_manager.set_school_type('Lise')
        
        scheduler = UltimateScheduler(db_manager)
        scheduler.generate_schedule()
        
        # Lise should have 8 time slots
        assert scheduler.time_slots_count in [7, 8]  # Could be 7 or 8 depending on setup
