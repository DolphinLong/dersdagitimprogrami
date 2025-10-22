'''
Unit tests for the main Scheduler manager class in algorithms/scheduler.py.

These tests verify:
- Correct scheduler selection based on availability and priority.
- Proper delegation of the generate_schedule call to the selected scheduler instance.
'''

import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Ensure the project root is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from algorithms.scheduler import Scheduler


class TestSchedulerManager(unittest.TestCase):
    '''Tests the functionality of the main Scheduler class.'''

    def setUp(self):
        '''Set up a mock database manager for each test.'''
        self.mock_db_manager = MagicMock()

    @patch('algorithms.scheduler.ADVANCED_SCHEDULER_AVAILABLE', True)
    @patch('algorithms.scheduler.STRICT_SCHEDULER_AVAILABLE', False)
    @patch('algorithms.scheduler.ENHANCED_STRICT_SCHEDULER_AVAILABLE', False)
    @patch('algorithms.scheduler.ULTIMATE_SCHEDULER_AVAILABLE', False)
    @patch('algorithms.scheduler.SIMPLE_PERFECT_SCHEDULER_AVAILABLE', False)
    @patch('algorithms.scheduler.HYBRID_OPTIMAL_SCHEDULER_AVAILABLE', False)
    @patch('algorithms.scheduler.ULTRA_AGGRESSIVE_SCHEDULER_AVAILABLE', False)
    def test_selects_advanced_scheduler_when_only_one_available(self):
        '''Verify it falls back to AdvancedScheduler when no others are available.'''
        scheduler = Scheduler(self.mock_db_manager)
        self.assertIsNotNone(scheduler.advanced_scheduler)
        # Check the state of other schedulers based on the __init__ logic
        self.assertIsNone(scheduler.hybrid_scheduler)
        self.assertIsNone(scheduler.ultimate_scheduler)
        self.assertIsNone(scheduler.enhanced_strict_scheduler)
        self.assertIsNone(scheduler.strict_scheduler)
        self.assertFalse(hasattr(scheduler, 'ultra_scheduler'))
        self.assertFalse(hasattr(scheduler, 'simple_perfect_scheduler'))

    @patch('algorithms.scheduler.ADVANCED_SCHEDULER_AVAILABLE', True)
    @patch('algorithms.scheduler.STRICT_SCHEDULER_AVAILABLE', True)
    @patch('algorithms.scheduler.ENHANCED_STRICT_SCHEDULER_AVAILABLE', False)
    @patch('algorithms.scheduler.ULTIMATE_SCHEDULER_AVAILABLE', False)
    @patch('algorithms.scheduler.SIMPLE_PERFECT_SCHEDULER_AVAILABLE', True)
    @patch('algorithms.scheduler.HYBRID_OPTIMAL_SCHEDULER_AVAILABLE', False)
    @patch('algorithms.scheduler.ULTRA_AGGRESSIVE_SCHEDULER_AVAILABLE', False)
    def test_selects_simple_perfect_over_advanced_and_strict(self):
        '''Verify SimplePerfectScheduler is prioritized over less preferred schedulers.'''
        scheduler = Scheduler(self.mock_db_manager)
        self.assertIsNotNone(scheduler.simple_perfect_scheduler)
        self.assertIsNone(scheduler.hybrid_scheduler) # Should be None
        # The others might be initialized depending on the logic, but the main one is what we test

    @patch('algorithms.scheduler.ADVANCED_SCHEDULER_AVAILABLE', True)
    @patch('algorithms.scheduler.STRICT_SCHEDULER_AVAILABLE', True)
    @patch('algorithms.scheduler.ENHANCED_STRICT_SCHEDULER_AVAILABLE', True)
    @patch('algorithms.scheduler.ULTIMATE_SCHEDULER_AVAILABLE', True)
    @patch('algorithms.scheduler.SIMPLE_PERFECT_SCHEDULER_AVAILABLE', True)
    @patch('algorithms.scheduler.HYBRID_OPTIMAL_SCHEDULER_AVAILABLE', True)
    @patch('algorithms.scheduler.ULTRA_AGGRESSIVE_SCHEDULER_AVAILABLE', True)
    def test_selects_ultra_aggressive_when_all_are_available(self):
        '''Verify UltraAggressiveScheduler is chosen when all schedulers are available.'''
        scheduler = Scheduler(self.mock_db_manager)
        self.assertIsNotNone(scheduler.ultra_scheduler)
        # In the current logic, the others might still be instantiated in the constructor
        # The key is that the highest priority one is not None.

    @patch('algorithms.scheduler.ULTRA_AGGRESSIVE_SCHEDULER_AVAILABLE', True)
    @patch('algorithms.scheduler.HybridOptimalScheduler', MagicMock())
    @patch('algorithms.scheduler.SimplePerfectScheduler', MagicMock())
    @patch('algorithms.scheduler.UltimateScheduler', MagicMock())
    @patch('algorithms.scheduler.EnhancedStrictScheduler', MagicMock())
    @patch('algorithms.scheduler.StrictScheduler', MagicMock())
    @patch('algorithms.scheduler.AdvancedScheduler', MagicMock())
    @patch('algorithms.ultra_aggressive_scheduler.UltraAggressiveScheduler.generate_schedule')
    def test_generate_schedule_delegates_to_ultra_aggressive(self, mock_generate):
        '''Test that the main generate_schedule call is delegated to the selected scheduler.'''
        # We need to patch the availability for the scheduler class to instantiate the right one
        with patch('algorithms.scheduler.HYBRID_OPTIMAL_SCHEDULER_AVAILABLE', True), patch('algorithms.scheduler.SIMPLE_PERFECT_SCHEDULER_AVAILABLE', True):


            scheduler = Scheduler(self.mock_db_manager)
            scheduler.generate_schedule()

            # Check that the generate_schedule method of the ultra scheduler was called
            mock_generate.assert_called_once()

if __name__ == '__main__':
    unittest.main()
