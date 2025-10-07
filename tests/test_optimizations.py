# -*- coding: utf-8 -*-
"""
Unit Tests for Performance Optimizations
Tests for TeacherAvailabilityCache and OptimizedConflictChecker
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.teacher_availability_cache import TeacherAvailabilityCache
from algorithms.optimized_conflict_checker import OptimizedConflictChecker


class MockDatabaseManager:
    """Mock database manager for testing"""
    
    def get_all_teachers(self):
        """Return mock teachers"""
        class MockTeacher:
            def __init__(self, teacher_id, name, availability=None):
                self.teacher_id = teacher_id
                self.name = name
                self.availability = availability
        
        return [
            MockTeacher(1, "Teacher 1", {
                "Pazartesi": [0, 1, 2, 3],
                "Salı": [0, 1, 2, 3, 4],
                "Çarşamba": [0, 1, 2],
            }),
            MockTeacher(2, "Teacher 2", {
                "Pazartesi": [4, 5, 6],
                "Perşembe": [0, 1, 2, 3],
            }),
            MockTeacher(3, "Teacher 3", None),  # No explicit availability
        ]


class TestTeacherAvailabilityCache(unittest.TestCase):
    """Test cases for TeacherAvailabilityCache"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.db = MockDatabaseManager()
        self.cache = TeacherAvailabilityCache(self.db)
    
    def test_cache_initialization(self):
        """Test that cache initializes correctly"""
        stats = self.cache.get_cache_stats()
        self.assertEqual(stats['total_teachers'], 3)
        self.assertGreater(stats['total_cached_slots'], 0)
    
    def test_is_available_explicit(self):
        """Test availability check for teacher with explicit availability"""
        # Teacher 1 is available on Monday slot 0
        self.assertTrue(self.cache.is_available(1, 0, 0))
        
        # Teacher 1 is NOT available on Monday slot 7
        self.assertFalse(self.cache.is_available(1, 0, 7))
        
        # Teacher 1 is available on Tuesday slot 4
        self.assertTrue(self.cache.is_available(1, 1, 4))
    
    def test_is_available_no_explicit(self):
        """Test availability check for teacher without explicit availability"""
        # Teacher 3 has no explicit availability, should be available everywhere
        self.assertTrue(self.cache.is_available(3, 0, 0))
        self.assertTrue(self.cache.is_available(3, 4, 7))
    
    def test_get_available_slots(self):
        """Test getting all available slots for a teacher"""
        slots = self.cache.get_available_slots(1)
        self.assertIsInstance(slots, set)
        self.assertGreater(len(slots), 0)
        
        # Check specific slot is in set
        self.assertIn((0, 0), slots)  # Monday, slot 0
    
    def test_add_availability(self):
        """Test adding availability"""
        # Add new availability
        self.cache.add_teacher_availability(1, 4, 7)  # Friday, slot 7
        
        # Verify it was added
        self.assertTrue(self.cache.is_available(1, 4, 7))
    
    def test_remove_availability(self):
        """Test removing availability"""
        # Remove existing availability
        self.cache.remove_teacher_availability(1, 0, 0)  # Monday, slot 0
        
        # Verify it was removed
        self.assertFalse(self.cache.is_available(1, 0, 0))
    
    def test_refresh(self):
        """Test cache refresh"""
        # Modify cache
        self.cache.add_teacher_availability(1, 4, 7)
        
        # Refresh should reload from database
        self.cache.refresh()
        
        # Modification should be gone
        # (assuming database doesn't have this slot)
        stats = self.cache.get_cache_stats()
        self.assertEqual(stats['total_teachers'], 3)


class TestOptimizedConflictChecker(unittest.TestCase):
    """Test cases for OptimizedConflictChecker"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.checker = OptimizedConflictChecker()
    
    def test_initialization(self):
        """Test that checker initializes correctly"""
        stats = self.checker.get_stats()
        self.assertEqual(stats['total_entries'], 0)
    
    def test_add_entry(self):
        """Test adding an entry"""
        entry = {
            'class_id': 1,
            'teacher_id': 1,
            'lesson_id': 1,
            'classroom_id': 1,
            'day': 0,
            'time_slot': 0
        }
        
        self.checker.add_entry(entry)
        
        stats = self.checker.get_stats()
        self.assertEqual(stats['total_entries'], 1)
    
    def test_has_class_conflict(self):
        """Test class conflict detection"""
        entry = {
            'class_id': 1,
            'teacher_id': 1,
            'lesson_id': 1,
            'classroom_id': 1,
            'day': 0,
            'time_slot': 0
        }
        
        self.checker.add_entry(entry)
        
        # Should have conflict at same time
        self.assertTrue(self.checker.has_class_conflict(1, 0, 0))
        
        # Should NOT have conflict at different time
        self.assertFalse(self.checker.has_class_conflict(1, 0, 1))
        self.assertFalse(self.checker.has_class_conflict(1, 1, 0))
    
    def test_has_teacher_conflict(self):
        """Test teacher conflict detection"""
        entry = {
            'class_id': 1,
            'teacher_id': 1,
            'lesson_id': 1,
            'classroom_id': 1,
            'day': 0,
            'time_slot': 0
        }
        
        self.checker.add_entry(entry)
        
        # Should have conflict at same time
        self.assertTrue(self.checker.has_teacher_conflict(1, 0, 0))
        
        # Should NOT have conflict at different time
        self.assertFalse(self.checker.has_teacher_conflict(1, 0, 1))
    
    def test_has_any_conflict(self):
        """Test combined conflict detection"""
        entry = {
            'class_id': 1,
            'teacher_id': 1,
            'lesson_id': 1,
            'classroom_id': 1,
            'day': 0,
            'time_slot': 0
        }
        
        self.checker.add_entry(entry)
        
        # Should have conflict (same class)
        self.assertTrue(self.checker.has_any_conflict(1, 2, 0, 0))
        
        # Should have conflict (same teacher)
        self.assertTrue(self.checker.has_any_conflict(2, 1, 0, 0))
        
        # Should NOT have conflict (different time)
        self.assertFalse(self.checker.has_any_conflict(2, 2, 0, 1))
    
    def test_remove_entry(self):
        """Test removing an entry"""
        entry = {
            'class_id': 1,
            'teacher_id': 1,
            'lesson_id': 1,
            'classroom_id': 1,
            'day': 0,
            'time_slot': 0
        }
        
        self.checker.add_entry(entry)
        self.assertTrue(self.checker.has_class_conflict(1, 0, 0))
        
        self.checker.remove_entry(entry)
        self.assertFalse(self.checker.has_class_conflict(1, 0, 0))
        
        stats = self.checker.get_stats()
        self.assertEqual(stats['total_entries'], 0)
    
    def test_detect_all_conflicts(self):
        """Test detecting all conflicts"""
        # Add two entries with class conflict
        entry1 = {
            'class_id': 1,
            'teacher_id': 1,
            'lesson_id': 1,
            'classroom_id': 1,
            'day': 0,
            'time_slot': 0
        }
        
        entry2 = {
            'class_id': 1,  # Same class
            'teacher_id': 2,
            'lesson_id': 2,
            'classroom_id': 2,
            'day': 0,  # Same day
            'time_slot': 0  # Same slot
        }
        
        self.checker.add_entry(entry1)
        self.checker.add_entry(entry2)
        
        conflicts = self.checker.detect_all_conflicts()
        
        # Should detect class conflict
        self.assertGreater(len(conflicts), 0)
        self.assertEqual(conflicts[0]['type'], 'class_conflict')
    
    def test_clear(self):
        """Test clearing all state"""
        entry = {
            'class_id': 1,
            'teacher_id': 1,
            'lesson_id': 1,
            'classroom_id': 1,
            'day': 0,
            'time_slot': 0
        }
        
        self.checker.add_entry(entry)
        self.checker.clear()
        
        stats = self.checker.get_stats()
        self.assertEqual(stats['total_entries'], 0)
        self.assertFalse(self.checker.has_class_conflict(1, 0, 0))


class TestPerformance(unittest.TestCase):
    """Performance tests for optimizations"""
    
    def test_conflict_checker_performance(self):
        """Test that conflict checker is fast with many entries"""
        import time
        
        checker = OptimizedConflictChecker()
        
        # Add 1000 entries
        start = time.time()
        for i in range(1000):
            entry = {
                'class_id': i % 10,
                'teacher_id': i % 20,
                'lesson_id': i % 15,
                'classroom_id': i % 5,
                'day': i % 5,
                'time_slot': i % 8
            }
            checker.add_entry(entry)
        add_time = time.time() - start
        
        # Check conflicts (should be O(1) per check)
        start = time.time()
        for i in range(1000):
            checker.has_any_conflict(i % 10, i % 20, i % 5, i % 8)
        check_time = time.time() - start
        
        # Should be very fast
        self.assertLess(add_time, 1.0)  # Less than 1 second to add 1000
        self.assertLess(check_time, 0.1)  # Less than 0.1 second for 1000 checks
        
        print(f"\nPerformance: Add {add_time:.4f}s, Check {check_time:.4f}s")


if __name__ == '__main__':
    unittest.main()
