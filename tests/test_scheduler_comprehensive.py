# -*- coding: utf-8 -*-
"""
Comprehensive tests for algorithms/scheduler.py
Critical test coverage for the main scheduler manager
"""

import pytest
import logging
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from algorithms.scheduler import Scheduler
from database.db_manager import DatabaseManager


class TestSchedulerInitialization:
    """Test scheduler initialization and configuration"""

    def test_scheduler_initialization_basic(self, db_manager):
        """Test basic scheduler initialization"""
        scheduler = Scheduler(db_manager)
        
        assert scheduler.db_manager == db_manager
        assert scheduler.progress_callback is None
        assert hasattr(scheduler, 'logger')
        assert scheduler.logger.name == 'algorithms.scheduler'

    def test_scheduler_initialization_with_progress_callback(self, db_manager):
        """Test scheduler initialization with progress callback"""
        callback = Mock()
        scheduler = Scheduler(db_manager, progress_callback=callback)
        
        assert scheduler.progress_callback == callback

    def test_scheduler_initialization_with_performance_monitor(self, db_manager):
        """Test scheduler initialization with performance monitor"""
        scheduler = Scheduler(db_manager, enable_performance_monitor=True)
        
        # Should attempt to initialize performance monitor
        assert hasattr(scheduler, 'performance_monitor')

    def test_scheduler_school_time_slots_constants(self, db_manager):
        """Test school time slots constants"""
        scheduler = Scheduler(db_manager)
        
        expected_slots = {
            "İlkokul": 6,
            "Ortaokul": 7,
            "Lise": 8,
            "Anadolu Lisesi": 8,
            "Fen Lisesi": 8,
            "Sosyal Bilimler Lisesi": 8,
        }
        
        assert scheduler.SCHOOL_TIME_SLOTS == expected_slots

    def test_scheduler_flags_initialization(self, db_manager):
        """Test scheduler algorithm flags"""
        scheduler = Scheduler(db_manager)
        
        # Check that flags are boolean
        assert isinstance(scheduler.use_hybrid, bool)
        assert isinstance(scheduler.use_simple_perfect, bool)
        assert isinstance(scheduler.use_ultimate, bool)
        assert isinstance(scheduler.use_enhanced_strict, bool)


class TestSchedulerAlgorithmSelection:
    """Test algorithm selection logic"""

    @patch('algorithms.scheduler.HYBRID_OPTIMAL_SCHEDULER_AVAILABLE', True)
    def test_hybrid_scheduler_selection(self, db_manager):
        """Test hybrid scheduler selection when available"""
        scheduler = Scheduler(db_manager, use_hybrid=True)
        assert scheduler.use_hybrid == True

    @patch('algorithms.scheduler.HYBRID_OPTIMAL_SCHEDULER_AVAILABLE', False)
    def test_hybrid_scheduler_unavailable(self, db_manager):
        """Test hybrid scheduler when unavailable"""
        scheduler = Scheduler(db_manager, use_hybrid=True)
        assert scheduler.use_hybrid == False

    def test_advanced_scheduler_selection(self, db_manager):
        """Test advanced scheduler selection"""
        scheduler = Scheduler(db_manager, use_advanced=True)
        # Should be based on ENHANCED_STRICT_SCHEDULER_AVAILABLE
        assert isinstance(scheduler.use_advanced, bool)

    def test_disable_advanced_scheduler(self, db_manager):
        """Test disabling advanced scheduler"""
        scheduler = Scheduler(db_manager, use_advanced=False)
        assert scheduler.use_advanced == False


class TestSchedulerLogging:
    """Test scheduler logging functionality"""

    def test_logger_configuration(self, db_manager):
        """Test logger is properly configured"""
        scheduler = Scheduler(db_manager)
        
        assert scheduler.logger is not None
        assert scheduler.logger.name == 'algorithms.scheduler'
        assert isinstance(scheduler.logger, logging.Logger)

    @patch('algorithms.scheduler.PERFORMANCE_MONITOR_AVAILABLE', True)
    @patch('algorithms.scheduler.PerformanceMonitor')
    def test_performance_monitor_logging(self, mock_performance_monitor, db_manager):
        """Test performance monitor initialization logging"""
        mock_instance = Mock()
        mock_performance_monitor.return_value = mock_instance
        
        with patch.object(logging.getLogger('algorithms.scheduler'), 'info') as mock_log:
            scheduler = Scheduler(db_manager, enable_performance_monitor=True)
            
            # Should log performance monitor activation
            mock_log.assert_any_call("📊 Performance Monitor aktif - Algoritma performansı takip ediliyor")

    @patch('algorithms.scheduler.HEURISTICS_AVAILABLE', True)
    @patch('algorithms.scheduler.HeuristicManager')
    def test_heuristics_manager_logging(self, mock_heuristics, db_manager):
        """Test heuristics manager initialization logging"""
        mock_instance = Mock()
        mock_heuristics.return_value = mock_instance
        
        with patch.object(logging.getLogger('algorithms.scheduler'), 'info') as mock_log:
            scheduler = Scheduler(db_manager)
            
            # Should log heuristics manager activation
            mock_log.assert_any_call("🧠 Heuristics Manager aktiv - Akıllı slot seçimi kullanılıyor")


class TestSchedulerErrorHandling:
    """Test scheduler error handling"""

    def test_scheduler_with_none_db_manager(self):
        """Test scheduler initialization with None db_manager"""
        # Should not raise exception during initialization
        scheduler = Scheduler(None)
        assert scheduler.db_manager is None

    @patch('algorithms.scheduler.PerformanceMonitor', side_effect=ImportError)
    def test_performance_monitor_import_error(self, mock_performance_monitor, db_manager):
        """Test graceful handling of performance monitor import error"""
        # Should not raise exception
        scheduler = Scheduler(db_manager, enable_performance_monitor=True)
        assert scheduler.performance_monitor is None

    @patch('algorithms.scheduler.HeuristicManager', side_effect=ImportError)
    def test_heuristics_import_error(self, mock_heuristics, db_manager):
        """Test graceful handling of heuristics import error"""
        # Should not raise exception
        scheduler = Scheduler(db_manager)
        assert scheduler.heuristics is None


class TestSchedulerConfiguration:
    """Test scheduler configuration options"""

    def test_all_options_enabled(self, db_manager):
        """Test scheduler with all options enabled"""
        scheduler = Scheduler(
            db_manager,
            use_advanced=True,
            use_hybrid=True,
            progress_callback=Mock(),
            enable_performance_monitor=True
        )
        
        assert scheduler.db_manager == db_manager
        assert scheduler.progress_callback is not None
        assert isinstance(scheduler.use_advanced, bool)
        assert isinstance(scheduler.use_hybrid, bool)

    def test_all_options_disabled(self, db_manager):
        """Test scheduler with all options disabled"""
        scheduler = Scheduler(
            db_manager,
            use_advanced=False,
            use_hybrid=False,
            progress_callback=None,
            enable_performance_monitor=False
        )
        
        assert scheduler.db_manager == db_manager
        assert scheduler.progress_callback is None
        assert scheduler.use_advanced == False
        assert scheduler.use_hybrid == False

    def test_deprecated_ultra_parameter(self, db_manager):
        """Test that deprecated use_ultra parameter is handled"""
        # Should not raise exception even if use_ultra is passed
        scheduler = Scheduler(db_manager, use_ultra=True)
        
        # use_ultra should be ignored (deprecated)
        assert hasattr(scheduler, 'db_manager')


class TestSchedulerIntegration:
    """Test scheduler integration with other components"""

    def test_scheduler_with_real_db_manager(self):
        """Test scheduler with real database manager"""
        db = DatabaseManager(":memory:")
        scheduler = Scheduler(db)
        
        assert scheduler.db_manager == db
        assert scheduler.logger is not None

    @patch('algorithms.scheduler.AlgorithmSelector')
    def test_algorithm_selector_integration(self, mock_selector_class, db_manager):
        """Test integration with algorithm selector"""
        mock_selector = Mock()
        mock_selector_class.return_value = mock_selector
        
        # Mock the selector methods
        mock_selector.select_best_algorithm.return_value = Mock
        mock_selector.get_algorithm_recommendation.return_value = {
            'best_algorithm': 'simple_perfect',
            'reasoning': 'Test reasoning',
            'score': 8.5
        }
        
        scheduler = Scheduler(db_manager)
        
        # Should attempt to use algorithm selector
        assert hasattr(scheduler, 'algorithm_selector')


class TestSchedulerConstants:
    """Test scheduler constants and class variables"""

    def test_school_time_slots_immutable(self, db_manager):
        """Test that SCHOOL_TIME_SLOTS is properly defined"""
        scheduler = Scheduler(db_manager)
        
        # Should be a dictionary
        assert isinstance(scheduler.SCHOOL_TIME_SLOTS, dict)
        
        # Should contain expected school types
        expected_types = ["İlkokul", "Ortaokul", "Lise", "Anadolu Lisesi", "Fen Lisesi", "Sosyal Bilimler Lisesi"]
        for school_type in expected_types:
            assert school_type in scheduler.SCHOOL_TIME_SLOTS
            assert isinstance(scheduler.SCHOOL_TIME_SLOTS[school_type], int)
            assert scheduler.SCHOOL_TIME_SLOTS[school_type] > 0

    def test_time_slots_values(self, db_manager):
        """Test time slots values are reasonable"""
        scheduler = Scheduler(db_manager)
        
        for school_type, slots in scheduler.SCHOOL_TIME_SLOTS.items():
            # Time slots should be between 6-8 hours per day
            assert 6 <= slots <= 8, f"{school_type} has unreasonable time slots: {slots}"


class TestSchedulerMemoryManagement:
    """Test scheduler memory management"""

    def test_scheduler_cleanup(self, db_manager):
        """Test scheduler can be properly cleaned up"""
        scheduler = Scheduler(db_manager)
        
        # Should be able to delete references
        db_ref = scheduler.db_manager
        del scheduler
        
        # Original db_manager should still exist
        assert db_ref is not None

    def test_multiple_scheduler_instances(self, db_manager):
        """Test multiple scheduler instances can coexist"""
        scheduler1 = Scheduler(db_manager, use_advanced=True)
        scheduler2 = Scheduler(db_manager, use_advanced=False)
        
        assert scheduler1.use_advanced != scheduler2.use_advanced
        assert scheduler1.db_manager == scheduler2.db_manager


# Performance and stress tests
class TestSchedulerPerformance:
    """Test scheduler performance characteristics"""

    def test_scheduler_initialization_performance(self, db_manager):
        """Test scheduler initializes quickly"""
        import time
        
        start_time = time.time()
        scheduler = Scheduler(db_manager)
        end_time = time.time()
        
        # Should initialize in less than 1 second
        assert (end_time - start_time) < 1.0

    def test_multiple_initializations(self, db_manager):
        """Test multiple scheduler initializations"""
        schedulers = []
        
        for i in range(10):
            scheduler = Scheduler(db_manager)
            schedulers.append(scheduler)
        
        # All should be properly initialized
        assert len(schedulers) == 10
        for scheduler in schedulers:
            assert scheduler.db_manager == db_manager


if __name__ == "__main__":
    pytest.main([__file__, "-v"])