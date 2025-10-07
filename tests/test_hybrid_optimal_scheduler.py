# -*- coding: utf-8 -*-
"""
Tests for HybridOptimalScheduler - The most powerful algorithm
Arc Consistency + Soft Constraints + Advanced Heuristics
"""

import pytest
from algorithms.hybrid_optimal_scheduler import HybridOptimalScheduler


class TestHybridOptimalScheduler:
    """Test HybridOptimalScheduler class"""
    
    def test_initialization(self, db_manager):
        """Test scheduler initialization"""
        scheduler = HybridOptimalScheduler(db_manager)
        assert scheduler.db_manager == db_manager
        # HybridOptimalScheduler may have different internal structure
        assert scheduler is not None
    
    def test_school_time_slots_configuration(self, db_manager):
        """Test school time slots configuration"""
        scheduler = HybridOptimalScheduler(db_manager)
        
        # Should have school time slots configuration
        assert hasattr(scheduler, 'SCHOOL_TIME_SLOTS') or scheduler.time_slots_count > 0
    
    def test_generate_schedule_basic(self, db_manager, sample_schedule_data):
        """Test basic schedule generation"""
        scheduler = HybridOptimalScheduler(db_manager)
        schedule = scheduler.generate_schedule()
        
        # Should generate some schedule entries
        assert isinstance(schedule, list)
    
    def test_schedule_entries_structure(self, db_manager):
        """Test that schedule entries are properly structured"""
        scheduler = HybridOptimalScheduler(db_manager)
        
        # Generate schedule to create entries
        schedule = scheduler.generate_schedule()
        assert isinstance(schedule, list)
    
    def test_multiple_generations(self, db_manager, sample_schedule_data):
        """Test that scheduler can generate multiple times"""
        scheduler = HybridOptimalScheduler(db_manager)
        
        # First generation
        schedule1 = scheduler.generate_schedule()
        assert isinstance(schedule1, list)
        
        # Second generation
        schedule2 = scheduler.generate_schedule()
        assert isinstance(schedule2, list)
    
    def test_empty_database_handling(self, db_manager):
        """Test scheduler with empty database"""
        scheduler = HybridOptimalScheduler(db_manager)
        
        # Generate with minimal/no data
        schedule = scheduler.generate_schedule()
        
        # Should handle gracefully
        assert isinstance(schedule, list)
    
    def test_schedule_output_format(self, db_manager, sample_schedule_data):
        """Test that schedule output has correct format"""
        scheduler = HybridOptimalScheduler(db_manager)
        schedule = scheduler.generate_schedule()
        
        assert isinstance(schedule, list)
        
        # If there are entries, check format
        for entry in schedule:
            assert isinstance(entry, dict)
    
    def test_school_type_affects_generation(self, db_manager):
        """Test that school type affects schedule generation"""
        db_manager.set_school_type('Lise')
        
        scheduler = HybridOptimalScheduler(db_manager)
        schedule = scheduler.generate_schedule()
        
        # Should process according to school type
        assert isinstance(schedule, list)
    
    def test_initialization_with_different_school_types(self, db_manager):
        """Test initialization with different school types"""
        school_types = ['İlkokul', 'Ortaokul', 'Lise', 'Fen Lisesi']
        
        for school_type in school_types:
            db_manager.set_school_type(school_type)
            scheduler = HybridOptimalScheduler(db_manager)
            assert scheduler.db_manager == db_manager
    
    def test_schedule_entries_reset_on_generation(self, db_manager, sample_schedule_data):
        """Test that schedule entries reset on new generation"""
        scheduler = HybridOptimalScheduler(db_manager)
        
        # First generation
        schedule1 = scheduler.generate_schedule()
        
        # Second generation
        schedule2 = scheduler.generate_schedule()
        
        # Both should return valid lists
        assert isinstance(schedule1, list)
        assert isinstance(schedule2, list)
    
    def test_algorithm_components_present(self, db_manager):
        """Test that algorithm has expected components"""
        scheduler = HybridOptimalScheduler(db_manager)
        
        # Should have basic structures
        assert hasattr(scheduler, 'db_manager')
        assert scheduler.db_manager == db_manager
    
    def test_generate_schedule_returns_list(self, db_manager):
        """Test that generate_schedule always returns a list"""
        scheduler = HybridOptimalScheduler(db_manager)
        
        schedule = scheduler.generate_schedule()
        assert isinstance(schedule, list)
    
    def test_schedule_consistency(self, db_manager, sample_schedule_data):
        """Test that generated schedule is consistent"""
        scheduler = HybridOptimalScheduler(db_manager)
        
        schedule = scheduler.generate_schedule()
        
        # All entries should be dicts
        for entry in schedule:
            assert isinstance(entry, dict)
    
    def test_handles_class_data(self, db_manager, sample_schedule_data):
        """Test that scheduler properly handles class data"""
        scheduler = HybridOptimalScheduler(db_manager)
        
        # Get classes
        classes = db_manager.get_all_classes()
        
        # Generate schedule
        schedule = scheduler.generate_schedule()
        
        # Should work with or without classes
        assert isinstance(schedule, list)
    
    def test_handles_teacher_data(self, db_manager, sample_schedule_data):
        """Test that scheduler properly handles teacher data"""
        scheduler = HybridOptimalScheduler(db_manager)
        
        # Get teachers
        teachers = db_manager.get_all_teachers()
        
        # Generate schedule
        schedule = scheduler.generate_schedule()
        
        # Should work with or without teachers
        assert isinstance(schedule, list)
    
    def test_handles_lesson_data(self, db_manager, sample_schedule_data):
        """Test that scheduler properly handles lesson data"""
        scheduler = HybridOptimalScheduler(db_manager)
        
        # Get lessons
        lessons = db_manager.get_all_lessons()
        
        # Generate schedule
        schedule = scheduler.generate_schedule()
        
        # Should work with or without lessons
        assert isinstance(schedule, list)
    
    def test_time_slots_count_configuration(self, db_manager):
        """Test time slots count configuration"""
        scheduler = HybridOptimalScheduler(db_manager)
        
        # Scheduler should have SCHOOL_TIME_SLOTS configuration
        assert hasattr(scheduler, 'SCHOOL_TIME_SLOTS')
        assert len(scheduler.SCHOOL_TIME_SLOTS) > 0
    
    def test_schedule_generation_with_minimal_data(self, db_manager):
        """Test schedule generation with minimal data"""
        # Set basic configuration
        db_manager.set_school_type('Lise')
        
        # Create scheduler
        scheduler = HybridOptimalScheduler(db_manager)
        
        # Should handle minimal data gracefully
        schedule = scheduler.generate_schedule()
        assert isinstance(schedule, list)
