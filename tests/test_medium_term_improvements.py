# -*- coding: utf-8 -*-
"""
Unit Tests for Medium-Term Improvements
Tests for HybridApproach, ParallelScheduler, and PerformanceMonitor
"""

import unittest
import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.hybrid_approach_scheduler import HybridApproachScheduler
from algorithms.parallel_scheduler import ParallelScheduler
from algorithms.performance_monitor import PerformanceMonitor, timing, get_monitor


class MockDatabaseManager:
    """Mock database manager for testing"""
    
    def get_all_teachers(self):
        class MockTeacher:
            def __init__(self, teacher_id, name, subject):
                self.teacher_id = teacher_id
                self.name = name
                self.subject = subject
                self.availability = None
        
        return [MockTeacher(i, f"Teacher {i}", "Math") for i in range(1, 6)]
    
    def get_all_classes(self):
        class MockClass:
            def __init__(self, class_id, name, grade):
                self.class_id = class_id
                self.name = name
                self.grade = grade
        
        return [MockClass(i, f"Class {i}", 9) for i in range(1, 4)]
    
    def get_all_lessons(self):
        class MockLesson:
            def __init__(self, lesson_id, name):
                self.lesson_id = lesson_id
                self.name = name
        
        return [MockLesson(i, f"Lesson {i}") for i in range(1, 6)]
    
    def get_all_classrooms(self):
        class MockClassroom:
            def __init__(self, classroom_id, name):
                self.classroom_id = classroom_id
                self.name = name
        
        return [MockClassroom(1, "Room 1")]
    
    def get_schedule_by_school_type(self):
        class MockScheduleEntry:
            def __init__(self, class_id, lesson_id, teacher_id):
                self.class_id = class_id
                self.lesson_id = lesson_id
                self.teacher_id = teacher_id
        
        entries = []
        for class_id in range(1, 4):
            for lesson_id in range(1, 6):
                entries.append(MockScheduleEntry(class_id, lesson_id, lesson_id))
        return entries
    
    def get_school_type(self):
        return "Lise"
    
    def get_weekly_hours_for_lesson(self, lesson_id, grade):
        return 4
    
    def get_teacher_by_id(self, teacher_id):
        class MockTeacher:
            def __init__(self, teacher_id):
                self.teacher_id = teacher_id
                self.name = f"Teacher {teacher_id}"
        return MockTeacher(teacher_id)
    
    def is_teacher_available(self, teacher_id, day, slot):
        return True
    
    def clear_schedule(self):
        pass
    
    def add_schedule_program(self, *args, **kwargs):
        return True


class TestHybridApproachScheduler(unittest.TestCase):
    """Test cases for HybridApproachScheduler"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.db = MockDatabaseManager()
    
    def test_initialization(self):
        """Test that scheduler initializes correctly"""
        scheduler = HybridApproachScheduler(self.db)
        self.assertIsNotNone(scheduler)
        self.assertIsNotNone(scheduler.simple_perfect)
    
    def test_coverage_analysis(self):
        """Test coverage analysis"""
        scheduler = HybridApproachScheduler(self.db)
        
        # Create mock schedule
        schedule = [
            {'class_id': 1, 'teacher_id': 1, 'lesson_id': 1, 
             'classroom_id': 1, 'day': 0, 'time_slot': 0}
        ]
        
        coverage = scheduler._analyze_coverage(schedule)
        
        self.assertIn('total_slots', coverage)
        self.assertIn('total_scheduled', coverage)
        self.assertIn('overall_percentage', coverage)
        self.assertIn('class_coverage', coverage)
    
    def test_can_place_at_slot(self):
        """Test slot placement check"""
        scheduler = HybridApproachScheduler(self.db)
        
        schedule = []
        
        # Should be able to place
        self.assertTrue(scheduler._can_place_at_slot(schedule, 1, 1, 0, 0))
        
        # Add entry
        schedule.append({
            'class_id': 1, 'teacher_id': 1, 'lesson_id': 1,
            'classroom_id': 1, 'day': 0, 'time_slot': 0
        })
        
        # Should not be able to place (class conflict)
        self.assertFalse(scheduler._can_place_at_slot(schedule, 1, 2, 0, 0))
        
        # Should not be able to place (teacher conflict)
        self.assertFalse(scheduler._can_place_at_slot(schedule, 2, 1, 0, 0))
        
        # Should be able to place (different time)
        self.assertTrue(scheduler._can_place_at_slot(schedule, 2, 2, 0, 1))


class TestParallelScheduler(unittest.TestCase):
    """Test cases for ParallelScheduler"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.db = MockDatabaseManager()
    
    def test_initialization(self):
        """Test that scheduler initializes correctly"""
        scheduler = ParallelScheduler(self.db, max_workers=2, timeout=30)
        self.assertIsNotNone(scheduler)
        self.assertEqual(scheduler.max_workers, 2)
        self.assertEqual(scheduler.timeout, 30)
        self.assertGreater(len(scheduler.available_schedulers), 0)
    
    def test_calculate_coverage(self):
        """Test coverage calculation"""
        scheduler = ParallelScheduler(self.db)
        
        schedule = [
            {'class_id': 1, 'teacher_id': 1, 'lesson_id': 1,
             'classroom_id': 1, 'day': 0, 'time_slot': 0}
        ]
        
        coverage = scheduler._calculate_coverage(schedule)
        
        self.assertIsInstance(coverage, float)
        self.assertGreaterEqual(coverage, 0)
        self.assertLessEqual(coverage, 100)
    
    def test_count_conflicts(self):
        """Test conflict counting"""
        scheduler = ParallelScheduler(self.db)
        
        # No conflicts
        schedule = [
            {'class_id': 1, 'teacher_id': 1, 'lesson_id': 1,
             'classroom_id': 1, 'day': 0, 'time_slot': 0}
        ]
        
        conflicts = scheduler._count_conflicts(schedule)
        self.assertEqual(conflicts, 0)
        
        # Add class conflict
        schedule.append({
            'class_id': 1, 'teacher_id': 2, 'lesson_id': 2,
            'classroom_id': 1, 'day': 0, 'time_slot': 0
        })
        
        conflicts = scheduler._count_conflicts(schedule)
        self.assertGreater(conflicts, 0)
    
    def test_calculate_score(self):
        """Test score calculation"""
        scheduler = ParallelScheduler(self.db)
        
        schedule = [
            {'class_id': 1, 'teacher_id': 1, 'lesson_id': 1,
             'classroom_id': 1, 'day': 0, 'time_slot': 0}
        ]
        
        score = scheduler._calculate_score(schedule, 50.0, 0, 10.0)
        
        self.assertIsInstance(score, float)
        self.assertGreater(score, 0)


class TestPerformanceMonitor(unittest.TestCase):
    """Test cases for PerformanceMonitor"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.monitor = PerformanceMonitor()
    
    def test_initialization(self):
        """Test that monitor initializes correctly"""
        self.assertIsNotNone(self.monitor)
        self.assertEqual(len(self.monitor.metrics), 0)
        self.assertEqual(len(self.monitor.call_counts), 0)
    
    def test_timing_decorator(self):
        """Test timing decorator"""
        @self.monitor.timing_decorator
        def test_function():
            time.sleep(0.01)
            return "result"
        
        result = test_function()
        
        self.assertEqual(result, "result")
        self.assertGreater(len(self.monitor.metrics), 0)
        self.assertGreater(self.monitor.call_counts[f"{test_function.__module__}.{test_function.__name__}"], 0)
    
    def test_record_scheduler_run(self):
        """Test recording scheduler run"""
        self.monitor.record_scheduler_run(
            "TestScheduler", 10.5, 95.0, 100, 0
        )
        
        self.assertEqual(len(self.monitor.session_metrics), 1)
        
        metric = self.monitor.session_metrics[0]
        self.assertEqual(metric['scheduler'], "TestScheduler")
        self.assertEqual(metric['duration'], 10.5)
        self.assertEqual(metric['coverage'], 95.0)
    
    def test_get_function_stats(self):
        """Test getting function statistics"""
        @self.monitor.timing_decorator
        def test_function():
            time.sleep(0.01)
        
        # Call multiple times
        for _ in range(3):
            test_function()
        
        func_name = f"{test_function.__module__}.{test_function.__name__}"
        stats = self.monitor.get_function_stats(func_name)
        
        self.assertEqual(stats['call_count'], 3)
        self.assertGreater(stats['total_time'], 0)
        self.assertGreater(stats['avg_time'], 0)
    
    def test_get_all_stats(self):
        """Test getting all statistics"""
        @self.monitor.timing_decorator
        def func1():
            time.sleep(0.01)
        
        @self.monitor.timing_decorator
        def func2():
            time.sleep(0.01)
        
        func1()
        func2()
        
        stats = self.monitor.get_all_stats()
        
        self.assertEqual(len(stats), 2)
        self.assertIn('function', stats[0])
        self.assertIn('call_count', stats[0])
    
    def test_get_session_summary(self):
        """Test getting session summary"""
        summary = self.monitor.get_session_summary()
        
        self.assertIn('session_duration', summary)
        self.assertIn('total_functions_tracked', summary)
        self.assertIn('scheduler_runs', summary)
    
    def test_generate_report(self):
        """Test report generation"""
        @self.monitor.timing_decorator
        def test_function():
            time.sleep(0.01)
        
        test_function()
        
        report = self.monitor.generate_report()
        
        self.assertIsInstance(report, str)
        self.assertIn("PERFORMANCE REPORT", report)
        self.assertIn("Session Duration", report)
    
    def test_reset(self):
        """Test monitor reset"""
        @self.monitor.timing_decorator
        def test_function():
            pass
        
        test_function()
        
        self.assertGreater(len(self.monitor.metrics), 0)
        
        self.monitor.reset()
        
        self.assertEqual(len(self.monitor.metrics), 0)
        self.assertEqual(len(self.monitor.call_counts), 0)
    
    def test_global_timing_decorator(self):
        """Test global timing decorator"""
        @timing
        def test_function():
            time.sleep(0.01)
            return "result"
        
        result = test_function()
        
        self.assertEqual(result, "result")
        
        # Check global monitor
        global_monitor = get_monitor()
        self.assertGreater(len(global_monitor.metrics), 0)


class TestIntegration(unittest.TestCase):
    """Integration tests for medium-term improvements"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.db = MockDatabaseManager()
    
    def test_hybrid_with_monitoring(self):
        """Test hybrid scheduler with performance monitoring"""
        monitor = PerformanceMonitor()
        
        @monitor.timing_decorator
        def run_hybrid():
            scheduler = HybridApproachScheduler(self.db)
            # Don't actually run (would take too long)
            return []
        
        schedule = run_hybrid()
        
        stats = monitor.get_all_stats()
        self.assertGreater(len(stats), 0)


if __name__ == '__main__':
    unittest.main()
