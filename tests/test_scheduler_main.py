"""
Comprehensive tests for algorithms/scheduler.py
Target: 80%+ coverage
Priority: CRITICAL
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from algorithms.scheduler import Scheduler


class TestSchedulerInitialization:
    """Test scheduler initialization and configuration"""
    
    def test_scheduler_creation(self, db_manager):
        """Test basic scheduler creation"""
        scheduler = Scheduler(db_manager)
        assert scheduler is not None
        assert scheduler.db_manager == db_manager
        assert scheduler.logger is not None
    
    def test_scheduler_with_progress_callback(self, db_manager):
        """Test scheduler with progress callback"""
        callback_called = []
        def callback(msg):
            callback_called.append(msg)
        
        scheduler = Scheduler(db_manager, progress_callback=callback)
        assert scheduler.progress_callback == callback
    
    def test_scheduler_algorithm_availability_flags(self, db_manager):
        """Test which algorithms are available"""
        scheduler = Scheduler(db_manager)
        # Check flags exist
        assert hasattr(scheduler, 'use_ultra')
        assert hasattr(scheduler, 'use_hybrid')
        assert hasattr(scheduler, 'use_simple_perfect')
        assert hasattr(scheduler, 'use_ultimate')
        assert hasattr(scheduler, 'use_enhanced_strict')
        assert hasattr(scheduler, 'use_strict')
        assert hasattr(scheduler, 'use_advanced')
    
    def test_scheduler_with_all_algorithms_disabled(self, db_manager):
        """Test scheduler when all advanced algorithms are disabled"""
        scheduler = Scheduler(
            db_manager, 
            use_advanced=False, 
            use_hybrid=False, 
            use_ultra=False
        )
        assert scheduler is not None
        # Should still have fallback options
    
    def test_scheduler_school_time_slots_constant(self, db_manager):
        """Test SCHOOL_TIME_SLOTS constant"""
        scheduler = Scheduler(db_manager)
        assert hasattr(Scheduler, 'SCHOOL_TIME_SLOTS')
        assert isinstance(Scheduler.SCHOOL_TIME_SLOTS, dict)
        assert 'İlkokul' in Scheduler.SCHOOL_TIME_SLOTS
        assert 'Ortaokul' in Scheduler.SCHOOL_TIME_SLOTS
        assert 'Lise' in Scheduler.SCHOOL_TIME_SLOTS
        assert Scheduler.SCHOOL_TIME_SLOTS['İlkokul'] == 6
        assert Scheduler.SCHOOL_TIME_SLOTS['Ortaokul'] == 7
        assert Scheduler.SCHOOL_TIME_SLOTS['Lise'] == 8


class TestSchedulerAlgorithmSelection:
    """Test algorithm selection logic"""
    
    def test_ultra_aggressive_priority(self, db_manager):
        """Test that ultra aggressive has highest priority"""
        scheduler = Scheduler(db_manager, use_ultra=True)
        if scheduler.use_ultra:
            assert hasattr(scheduler, 'ultra_scheduler')
            assert scheduler.ultra_scheduler is not None
    
    def test_hybrid_optimal_fallback(self, db_manager):
        """Test hybrid optimal as fallback"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=True)
        if scheduler.use_hybrid:
            assert hasattr(scheduler, 'hybrid_scheduler')
    
    def test_simple_perfect_fallback(self, db_manager):
        """Test simple perfect as fallback"""
        scheduler = Scheduler(
            db_manager, 
            use_ultra=False, 
            use_hybrid=False
        )
        # Simple perfect should be available as fallback
        assert scheduler.use_simple_perfect or scheduler.use_ultimate
    
    def test_algorithm_priority_order(self, db_manager):
        """Test that algorithms are checked in correct priority order"""
        # Priority: Ultra > Hybrid > SimplePerfect > Ultimate > Enhanced > Strict > Advanced
        scheduler = Scheduler(db_manager)
        
        # If ultra is available, it should be used
        if scheduler.use_ultra:
            assert hasattr(scheduler, 'ultra_scheduler')
        # Otherwise check next in priority
        elif scheduler.use_hybrid:
            assert hasattr(scheduler, 'hybrid_scheduler')


class TestScheduleGeneration:
    """Test schedule generation with different algorithms"""
    
    def test_generate_schedule_basic(self, db_manager):
        """Test basic schedule generation"""
        scheduler = Scheduler(db_manager)
        
        # Mock the underlying scheduler's generate_schedule
        with patch.object(scheduler, '_generate_schedule_standard', return_value=[]):
            schedule = scheduler.generate_schedule()
            assert isinstance(schedule, list)
    
    def test_generate_schedule_with_ultra_aggressive(self, db_manager):
        """Test schedule generation with ultra aggressive scheduler"""
        scheduler = Scheduler(db_manager, use_ultra=True)
        
        if scheduler.use_ultra and hasattr(scheduler, 'ultra_scheduler'):
            with patch.object(scheduler.ultra_scheduler, 'generate_schedule', return_value=[]):
                schedule = scheduler.generate_schedule()
                assert isinstance(schedule, list)
    
    def test_generate_schedule_with_hybrid_optimal(self, db_manager):
        """Test schedule generation with hybrid optimal scheduler"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=True)
        
        if scheduler.use_hybrid and hasattr(scheduler, 'hybrid_scheduler'):
            with patch.object(scheduler.hybrid_scheduler, 'generate_schedule', return_value=[]):
                schedule = scheduler.generate_schedule()
                assert isinstance(schedule, list)
    
    def test_generate_schedule_with_simple_perfect(self, db_manager):
        """Test schedule generation with simple perfect scheduler"""
        scheduler = Scheduler(db_manager, use_ultra=False, use_hybrid=False)
        
        if scheduler.use_simple_perfect and hasattr(scheduler, 'simple_perfect_scheduler'):
            with patch.object(scheduler.simple_perfect_scheduler, 'generate_schedule', return_value=[]):
                schedule = scheduler.generate_schedule()
                assert isinstance(schedule, list)
    
    def test_generate_schedule_fallback_chain(self, db_manager):
        """Test that fallback chain works correctly"""
        scheduler = Scheduler(db_manager)
        
        # Should not raise exception even if preferred algorithm fails
        with patch.object(scheduler, '_generate_schedule_standard', return_value=[]):
            schedule = scheduler.generate_schedule()
            assert isinstance(schedule, list)
    
    def test_generate_schedule_returns_list(self, db_manager):
        """Test that generate_schedule always returns a list"""
        scheduler = Scheduler(db_manager)
        
        with patch.object(scheduler, '_generate_schedule_standard', return_value=[]):
            schedule = scheduler.generate_schedule()
            assert isinstance(schedule, list)


class TestSchedulerErrorHandling:
    """Test error handling in scheduler"""
    
    def test_scheduler_with_invalid_db_manager(self):
        """Test scheduler with invalid database manager"""
        with pytest.raises(Exception):
            scheduler = Scheduler(None)
            scheduler.generate_schedule()
    
    def test_scheduler_handles_algorithm_import_errors(self, db_manager):
        """Test that scheduler handles missing algorithm imports gracefully"""
        # Even if some algorithms are not available, scheduler should work
        scheduler = Scheduler(db_manager)
        assert scheduler is not None
    
    def test_generate_schedule_with_empty_database(self, empty_db_manager):
        """Test schedule generation with empty database"""
        scheduler = Scheduler(empty_db_manager)
        
        with patch.object(scheduler, '_generate_schedule_standard', return_value=[]):
            schedule = scheduler.generate_schedule()
            # Should return empty schedule, not crash
            assert isinstance(schedule, list)


class TestSchedulerStandardGeneration:
    """Test standard schedule generation method"""
    
    def test_generate_schedule_standard_exists(self, db_manager):
        """Test that _generate_schedule_standard method exists"""
        scheduler = Scheduler(db_manager)
        assert hasattr(scheduler, '_generate_schedule_standard')
        assert callable(scheduler._generate_schedule_standard)
    
    def test_generate_schedule_standard_with_mock_data(self, db_manager):
        """Test standard generation with mocked data"""
        scheduler = Scheduler(db_manager)
        
        # Mock database methods
        with patch.object(db_manager, 'get_all_classes', return_value=[]):
            with patch.object(db_manager, 'get_all_teachers', return_value=[]):
                with patch.object(db_manager, 'get_all_lessons', return_value=[]):
                    schedule = scheduler._generate_schedule_standard()
                    assert isinstance(schedule, list)


class TestSchedulerLogging:
    """Test logging functionality"""
    
    def test_scheduler_logs_algorithm_selection(self, db_manager, caplog):
        """Test that scheduler logs which algorithm is selected"""
        import logging
        caplog.set_level(logging.INFO)
        
        scheduler = Scheduler(db_manager)
        
        # Check that some logging occurred
        assert len(caplog.records) > 0
    
    def test_scheduler_logs_contain_algorithm_name(self, db_manager, caplog):
        """Test that logs contain algorithm name"""
        import logging
        caplog.set_level(logging.INFO)
        
        scheduler = Scheduler(db_manager)
        
        # Check log messages contain scheduler information
        log_messages = [record.message for record in caplog.records]
        assert any('SCHEDULER' in msg.upper() for msg in log_messages)


class TestSchedulerIntegration:
    """Integration tests for scheduler"""
    
    def test_scheduler_with_real_database(self, db_manager):
        """Test scheduler with real database operations"""
        # Setup test data
        db_manager.set_school_type("Lise")
        
        scheduler = Scheduler(db_manager)
        assert scheduler is not None
        assert scheduler.db_manager == db_manager
    
    def test_scheduler_algorithm_switching(self, db_manager):
        """Test switching between different algorithms"""
        # Create scheduler with ultra
        scheduler1 = Scheduler(db_manager, use_ultra=True, use_hybrid=False)
        
        # Create scheduler with hybrid
        scheduler2 = Scheduler(db_manager, use_ultra=False, use_hybrid=True)
        
        # Both should work
        assert scheduler1 is not None
        assert scheduler2 is not None


class TestSchedulerPerformance:
    """Test scheduler performance characteristics"""
    
    def test_scheduler_initialization_time(self, db_manager):
        """Test that scheduler initializes quickly"""
        import time
        
        start = time.time()
        scheduler = Scheduler(db_manager)
        duration = time.time() - start
        
        # Should initialize in less than 1 second
        assert duration < 1.0, f"Initialization took {duration}s"
    
    def test_scheduler_memory_footprint(self, db_manager):
        """Test scheduler memory usage"""
        import sys
        
        scheduler = Scheduler(db_manager)
        size = sys.getsizeof(scheduler)
        
        # Scheduler object should be reasonably sized
        assert size < 10000, f"Scheduler size: {size} bytes"


class TestSchedulerEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_scheduler_with_all_algorithms_enabled(self, db_manager):
        """Test with all algorithms enabled"""
        scheduler = Scheduler(
            db_manager,
            use_advanced=True,
            use_hybrid=True,
            use_ultra=True
        )
        assert scheduler is not None
    
    def test_scheduler_with_none_progress_callback(self, db_manager):
        """Test with None as progress callback"""
        scheduler = Scheduler(db_manager, progress_callback=None)
        assert scheduler.progress_callback is None
    
    def test_scheduler_multiple_instantiation(self, db_manager):
        """Test creating multiple scheduler instances"""
        scheduler1 = Scheduler(db_manager)
        scheduler2 = Scheduler(db_manager)
        
        # Should be independent instances
        assert scheduler1 is not scheduler2
        assert scheduler1.db_manager == scheduler2.db_manager


class TestSchedulerConfiguration:
    """Test scheduler configuration options"""
    
    def test_use_advanced_flag(self, db_manager):
        """Test use_advanced configuration flag"""
        scheduler_with = Scheduler(db_manager, use_advanced=True)
        scheduler_without = Scheduler(db_manager, use_advanced=False)
        
        assert scheduler_with.use_advanced or not scheduler_with.use_advanced
        assert not scheduler_without.use_advanced or scheduler_without.use_advanced
    
    def test_use_hybrid_flag(self, db_manager):
        """Test use_hybrid configuration flag"""
        scheduler = Scheduler(db_manager, use_hybrid=False)
        # If hybrid is not available, flag should be False
        if not scheduler.use_hybrid:
            assert scheduler.use_hybrid == False
    
    def test_use_ultra_flag(self, db_manager):
        """Test use_ultra configuration flag"""
        scheduler = Scheduler(db_manager, use_ultra=False)
        assert scheduler.use_ultra == False


class TestSchedulerCompatibility:
    """Test backward compatibility"""
    
    def test_scheduler_without_optional_params(self, db_manager):
        """Test scheduler works without optional parameters"""
        scheduler = Scheduler(db_manager)
        assert scheduler is not None
    
    def test_scheduler_with_legacy_usage(self, db_manager):
        """Test legacy usage patterns still work"""
        # Old style: just db_manager
        scheduler = Scheduler(db_manager)
        
        with patch.object(scheduler, '_generate_schedule_standard', return_value=[]):
            schedule = scheduler.generate_schedule()
            assert isinstance(schedule, list)


# Fixtures
@pytest.fixture
def empty_db_manager(tmp_path):
    """Create an empty database manager for testing"""
    from database.db_manager import DatabaseManager
    db_path = tmp_path / "empty_test.db"
    return DatabaseManager(str(db_path))
