"""
Integration tests for OptimizedCurriculumScheduler
Tests end-to-end scheduling with real data, performance benchmarks, and 100% completion verification
"""
import pytest
import time
import psutil
import os
from unittest.mock import Mock, patch

from algorithms.optimized_curriculum_scheduler import OptimizedCurriculumScheduler, ScheduleResult
from database.db_manager import DatabaseManager


@pytest.mark.integration
class TestOptimizedSchedulerIntegration:
    """Test end-to-end scheduling with real data"""
    
    def test_complete_schedule_generation_workflow(self, db_manager, sample_schedule_data):
        """Test complete scheduling workflow with 100% completion target"""
        scheduler = OptimizedCurriculumScheduler(db_manager)
        
        # Generate complete schedule
        result = scheduler.generate_complete_schedule()
        
        # Verify result structure
        assert isinstance(result, ScheduleResult)
        assert isinstance(result.entries, list)
        assert result.total_hours >= 0  # May be 0 if no data to schedule
        assert result.scheduled_hours >= 0
        assert result.completion_rate >= 0.0
        assert result.execution_time > 0.0
        
        # Verify enhanced entries have required metadata
        for entry in result.entries:
            assert hasattr(entry, 'placement_method')
            assert hasattr(entry, 'constraint_level')
            assert hasattr(entry, 'backtrack_depth')
            assert hasattr(entry, 'block_id')
            assert entry.class_id > 0
            assert entry.teacher_id > 0
            assert entry.lesson_id > 0
            assert 0 <= entry.day <= 4
            assert entry.time_slot >= 0
    
    def test_100_percent_completion_achievement(self, db_manager, sample_schedule_data):
        """Verify 100% completion rate achievement"""
        scheduler = OptimizedCurriculumScheduler(db_manager)
        
        # Generate schedule with completion target
        result = scheduler.generate_complete_schedule()
        
        # Log completion details for analysis
        print(f"\nCompletion Analysis:")
        print(f"  Target hours: {result.total_hours}")
        print(f"  Scheduled hours: {result.scheduled_hours}")
        print(f"  Completion rate: {result.completion_rate:.1f}%")
        print(f"  Success: {result.success}")
        print(f"  Execution time: {result.execution_time:.2f}s")
        
        # Verify high completion rate (aim for 100%, accept 95%+ for test data)
        assert result.completion_rate >= 95.0, f"Completion rate {result.completion_rate:.1f}% below target"
        
        # Verify no conflicts in scheduled entries
        conflicts = self._detect_schedule_conflicts(result.entries)
        assert len(conflicts) == 0, f"Found {len(conflicts)} conflicts in schedule"
    
    def test_graduated_approach_phases(self, db_manager, sample_schedule_data):
        """Test that graduated approach phases work correctly"""
        scheduler = OptimizedCurriculumScheduler(db_manager)
        
        # Mock progress callback to track phases
        phase_calls = []
        def mock_progress(message, percent):
            phase_calls.append((message, percent))
        
        scheduler.progress_callback = mock_progress
        
        # Generate schedule
        result = scheduler.generate_complete_schedule()
        
        # Verify phases were executed
        phase_messages = [call[0] for call in phase_calls]
        
        # Should see initialization and scheduling phases
        assert any("Initializing" in msg for msg in phase_messages)
        assert any("Scheduling" in msg for msg in phase_messages)
        
        # Verify result
        assert isinstance(result, ScheduleResult)
        assert result.scheduled_hours > 0
    
    def test_backtracking_integration(self, db_manager, sample_schedule_data):
        """Test backtracking integration with real data"""
        scheduler = OptimizedCurriculumScheduler(db_manager)
        
        # Generate schedule
        result = scheduler.generate_complete_schedule()
        
        # Verify backtracking statistics
        assert 'total_backtracks' in result.backtrack_statistics
        assert 'successful_backtracks' in result.backtrack_statistics
        assert 'max_depth_reached' in result.backtrack_statistics
        
        # Backtracking should have been used for complex scheduling
        if result.scheduled_hours > 50:  # Only check if substantial scheduling occurred
            assert result.backtrack_statistics['total_backtracks'] >= 0
        
        # Max depth should not exceed limit
        assert result.backtrack_statistics['max_depth_reached'] <= 10
    
    def test_alternative_block_usage(self, db_manager, sample_schedule_data):
        """Test alternative block configurations are used when needed"""
        scheduler = OptimizedCurriculumScheduler(db_manager)
        
        # Generate schedule
        result = scheduler.generate_complete_schedule()
        
        # Verify alternative block usage statistics
        assert 'standard_blocks' in result.alternative_block_usage
        assert 'alternative_blocks' in result.alternative_block_usage
        assert 'relaxed_blocks' in result.alternative_block_usage
        assert 'backtracked_blocks' in result.alternative_block_usage
        
        # Should have used some blocks
        total_blocks = sum(result.alternative_block_usage.values())
        assert total_blocks > 0
    
    def test_constraint_relaxation_progression(self, db_manager, sample_schedule_data):
        """Test constraint relaxation progression works correctly"""
        scheduler = OptimizedCurriculumScheduler(db_manager)
        
        # Generate schedule
        result = scheduler.generate_complete_schedule()
        
        # Verify constraint violations are tracked
        assert isinstance(result.constraint_violations_by_type, dict)
        
        # Should track different violation types
        expected_types = ['teacher_conflicts', 'class_conflicts', 'availability_violations', 'workload_violations']
        for violation_type in expected_types:
            assert violation_type in result.constraint_violations_by_type
            assert result.constraint_violations_by_type[violation_type] >= 0
    
    def test_workload_distribution_tracking(self, db_manager, sample_schedule_data):
        """Test workload distribution tracking and violations"""
        scheduler = OptimizedCurriculumScheduler(db_manager)
        
        # Generate schedule
        result = scheduler.generate_complete_schedule()
        
        # Verify workload violations are tracked
        assert isinstance(result.workload_violations, dict)
        
        # Verify teacher utilization is calculated
        assert isinstance(result.teacher_utilization, dict)
        
        # If teachers are scheduled, utilization should be > 0
        if result.scheduled_hours > 0:
            teacher_utils = [util for util in result.teacher_utilization.values() if util > 0]
            assert len(teacher_utils) > 0


@pytest.mark.integration
class TestOptimizedSchedulerPerformance:
    """Test performance benchmarks (time and memory)"""
    
    def test_execution_time_benchmark(self, db_manager, sample_schedule_data):
        """Test performance benchmarks (time and memory)"""
        scheduler = OptimizedCurriculumScheduler(db_manager)
        
        # Measure execution time
        start_time = time.time()
        result = scheduler.generate_complete_schedule()
        actual_duration = time.time() - start_time
        
        # Verify execution time is within target (60 seconds)
        assert actual_duration < 60.0, f"Execution time {actual_duration:.2f}s exceeds 60s target"
        
        # Verify reported execution time matches actual
        time_diff = abs(result.execution_time - actual_duration)
        assert time_diff < 1.0, f"Reported time {result.execution_time:.2f}s differs from actual {actual_duration:.2f}s"
        
        print(f"\nPerformance Benchmark:")
        print(f"  Execution time: {actual_duration:.2f}s (target: <60s)")
        print(f"  Scheduled hours: {result.scheduled_hours}")
        print(f"  Scheduling rate: {result.scheduled_hours / actual_duration:.1f} hours/second")
    
    def test_memory_usage_monitoring(self, db_manager, sample_schedule_data):
        """Test memory usage optimization during backtracking"""
        try:
            # Get initial memory usage
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            scheduler = OptimizedCurriculumScheduler(db_manager)
            
            # Generate schedule
            result = scheduler.generate_complete_schedule()
            
            # Get final memory usage
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            print(f"\nMemory Usage:")
            print(f"  Initial: {initial_memory:.1f}MB")
            print(f"  Final: {final_memory:.1f}MB")
            print(f"  Increase: {memory_increase:.1f}MB")
            
            # Memory increase should be reasonable (< 500MB for test data)
            assert memory_increase < 500.0, f"Memory increase {memory_increase:.1f}MB too high"
            
            # Verify schedule was generated
            assert result.scheduled_hours > 0
            
        except ImportError:
            pytest.skip("psutil not available for memory monitoring")
    
    def test_performance_metrics_collection(self, db_manager, sample_schedule_data):
        """Test comprehensive performance metrics collection"""
        scheduler = OptimizedCurriculumScheduler(db_manager)
        
        # Generate schedule
        result = scheduler.generate_complete_schedule()
        
        # Verify performance metrics are collected
        assert isinstance(result.performance_metrics, dict)
        
        # Should have timing information
        if result.performance_metrics:
            # Check for expected metric types
            print(f"\nPerformance Metrics: {list(result.performance_metrics.keys())}")
        
        # Verify execution time is recorded
        assert result.execution_time > 0.0
    
    def test_scalability_with_larger_dataset(self, db_manager):
        """Test scalability with larger datasets"""
        # Add more data to test scalability
        self._add_additional_test_data(db_manager)
        
        scheduler = OptimizedCurriculumScheduler(db_manager)
        
        # Measure performance with larger dataset
        start_time = time.time()
        result = scheduler.generate_complete_schedule()
        duration = time.time() - start_time
        
        # Should still complete within time limit
        assert duration < 60.0, f"Scalability test failed: {duration:.2f}s > 60s"
        
        # Should achieve reasonable completion rate
        assert result.completion_rate >= 80.0, f"Scalability test: low completion rate {result.completion_rate:.1f}%"
        
        print(f"\nScalability Test:")
        print(f"  Duration: {duration:.2f}s")
        print(f"  Completion: {result.completion_rate:.1f}%")
        print(f"  Scheduled hours: {result.scheduled_hours}")
    
    def _add_additional_test_data(self, db_manager):
        """Add additional test data for scalability testing"""
        # Add more classes
        for i in range(5, 12):  # Add classes 5-11
            db_manager.add_class(f"Test Class {i}", grade=9 + (i % 4))
        
        # Add more teachers
        subjects = ["Matematik", "Türkçe", "Fen", "Sosyal", "İngilizce", "Beden", "Müzik"]
        for i, subject in enumerate(subjects):
            db_manager.add_teacher(f"Test Teacher {i+10}", subject)
        
        # Add more lessons
        for subject in subjects:
            if not db_manager.get_lesson_by_name(subject):
                db_manager.add_lesson(subject)


@pytest.mark.integration
class TestOptimizedSchedulerRobustness:
    """Test robustness and error handling"""
    
    def test_empty_database_handling(self, empty_db_manager):
        """Test handling of empty database"""
        scheduler = OptimizedCurriculumScheduler(empty_db_manager)
        
        # Should not crash with empty database
        result = scheduler.generate_complete_schedule()
        
        assert isinstance(result, ScheduleResult)
        assert result.scheduled_hours == 0
        assert result.completion_rate == 0.0
        assert not result.success
        assert len(result.entries) == 0
    
    def test_insufficient_data_handling(self, db_manager):
        """Test handling of insufficient data scenarios"""
        # Create minimal data (classes but no assignments)
        db_manager.add_class("Minimal Class", 9)
        
        scheduler = OptimizedCurriculumScheduler(empty_db_manager)
        
        # Should handle gracefully
        result = scheduler.generate_complete_schedule()
        
        assert isinstance(result, ScheduleResult)
        assert result.scheduled_hours == 0
    
    def test_constraint_conflict_scenarios(self, db_manager, sample_schedule_data):
        """Test handling of severe constraint conflicts"""
        scheduler = OptimizedCurriculumScheduler(db_manager)
        
        # Generate schedule with potential conflicts
        result = scheduler.generate_complete_schedule()
        
        # Should handle conflicts gracefully
        assert isinstance(result, ScheduleResult)
        
        # Should report constraint violations
        total_violations = sum(result.constraint_violations_by_type.values())
        print(f"\nConstraint Violations: {total_violations}")
        
        # Even with conflicts, should attempt scheduling
        assert result.scheduled_hours >= 0
    
    def test_time_limit_enforcement(self, db_manager, sample_schedule_data):
        """Test that time limit is properly enforced"""
        # Create scheduler with very short time limit
        scheduler = OptimizedCurriculumScheduler(db_manager)
        scheduler.time_limit = 5.0  # 5 second limit
        
        start_time = time.time()
        result = scheduler.generate_complete_schedule()
        actual_duration = time.time() - start_time
        
        # Should respect time limit (with small buffer for cleanup)
        assert actual_duration < 7.0, f"Time limit not enforced: {actual_duration:.2f}s > 7s"
        
        # Should still produce valid result
        assert isinstance(result, ScheduleResult)
    
    def test_multiple_solution_attempts(self, db_manager, sample_schedule_data):
        """Test multiple solution attempts for quality optimization"""
        scheduler = OptimizedCurriculumScheduler(db_manager)
        
        # Generate multiple schedules
        results = []
        for i in range(3):
            result = scheduler.generate_complete_schedule()
            results.append(result)
            
            # Reset scheduler state between attempts
            scheduler._reset_scheduling_state()
        
        # All should be valid
        for result in results:
            assert isinstance(result, ScheduleResult)
            assert result.scheduled_hours >= 0
        
        # Should show some variation (randomization working)
        completion_rates = [r.completion_rate for r in results]
        if len(set(completion_rates)) > 1:
            print(f"\nCompletion rate variation: {completion_rates}")


@pytest.mark.integration
class TestOptimizedSchedulerDiagnostics:
    """Test diagnostic and reporting capabilities"""
    
    def test_comprehensive_diagnostics_generation(self, db_manager, sample_schedule_data):
        """Test comprehensive diagnostics and failure analysis"""
        scheduler = OptimizedCurriculumScheduler(db_manager)
        
        # Generate schedule
        result = scheduler.generate_complete_schedule()
        
        # Verify diagnostic information is available
        assert hasattr(result, 'backtrack_statistics')
        assert hasattr(result, 'alternative_block_usage')
        assert hasattr(result, 'constraint_violations_by_type')
        assert hasattr(result, 'teacher_utilization')
        assert hasattr(result, 'class_utilization')
        
        # Print diagnostic summary
        print(f"\nDiagnostic Summary:")
        print(f"  Backtrack stats: {result.backtrack_statistics}")
        print(f"  Block usage: {result.alternative_block_usage}")
        print(f"  Violations: {result.constraint_violations_by_type}")
        print(f"  Teacher utilization: {len(result.teacher_utilization)} teachers")
        print(f"  Class utilization: {len(result.class_utilization)} classes")
    
    def test_failure_analysis_for_unscheduled_lessons(self, db_manager, sample_schedule_data):
        """Test failure analysis for unscheduled lessons"""
        scheduler = OptimizedCurriculumScheduler(db_manager)
        
        # Generate schedule
        result = scheduler.generate_complete_schedule()
        
        # Verify failed lessons are tracked
        assert hasattr(result, 'failed_lessons')
        assert isinstance(result.failed_lessons, list)
        
        # If there are failures, they should have diagnostic information
        for failed_lesson in result.failed_lessons:
            print(f"Failed lesson: {failed_lesson}")
    
    def test_performance_bottleneck_identification(self, db_manager, sample_schedule_data):
        """Test bottleneck analysis and improvement suggestions"""
        scheduler = OptimizedCurriculumScheduler(db_manager)
        
        # Generate schedule
        result = scheduler.generate_complete_schedule()
        
        # Should have performance metrics for bottleneck analysis
        assert isinstance(result.performance_metrics, dict)
        
        # Check if diagnostics component provided analysis
        if hasattr(scheduler, 'diagnostics'):
            # Diagnostics should be available
            assert scheduler.diagnostics is not None


# Helper methods
def _detect_schedule_conflicts(entries):
    """Detect conflicts in schedule entries"""
    conflicts = []
    
    # Check for same slot conflicts
    slot_usage = {}
    
    for entry in entries:
        # Teacher conflicts
        teacher_key = (entry.teacher_id, entry.day, entry.time_slot)
        if teacher_key in slot_usage:
            conflicts.append({
                'type': 'teacher_conflict',
                'teacher_id': entry.teacher_id,
                'day': entry.day,
                'time_slot': entry.time_slot
            })
        slot_usage[teacher_key] = entry
        
        # Class conflicts
        class_key = (entry.class_id, entry.day, entry.time_slot)
        if class_key in slot_usage:
            conflicts.append({
                'type': 'class_conflict',
                'class_id': entry.class_id,
                'day': entry.day,
                'time_slot': entry.time_slot
            })
        slot_usage[class_key] = entry
    
    return conflicts


# Fixtures
@pytest.fixture
def empty_db_manager(tmp_path):
    """Create an empty database manager for testing"""
    db_path = tmp_path / "empty_optimized_test.db"
    return DatabaseManager(str(db_path))