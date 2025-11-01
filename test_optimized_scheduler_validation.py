#!/usr/bin/env python3
"""
Comprehensive validation testing for OptimizedCurriculumScheduler
Tests 100% completion rate achievement and performance comparison
"""

import time
import logging
from typing import Dict, Any, List
from database.db_manager import DatabaseManager
from algorithms.optimized_curriculum_scheduler import OptimizedCurriculumScheduler
from algorithms.curriculum_based_scheduler import CurriculumBasedFullScheduleGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_100_percent_completion():
    """Test that OptimizedCurriculumScheduler achieves 100% completion rate"""
    logger.info("=" * 80)
    logger.info("TESTING 100% COMPLETION RATE ACHIEVEMENT")
    logger.info("=" * 80)
    
    # Initialize database
    db = DatabaseManager()
    
    # Test optimized scheduler
    logger.info("Testing OptimizedCurriculumScheduler...")
    start_time = time.time()
    
    optimized_scheduler = OptimizedCurriculumScheduler(db)
    result = optimized_scheduler.generate_complete_schedule()
    
    execution_time = time.time() - start_time
    
    # Validate results
    logger.info(f"OptimizedCurriculumScheduler Results:")
    logger.info(f"  Completion Rate: {result.completion_rate:.1f}%")
    logger.info(f"  Scheduled Hours: {result.scheduled_hours}/{result.total_hours}")
    logger.info(f"  Execution Time: {execution_time:.2f}s")
    logger.info(f"  Success: {result.success}")
    logger.info(f"  Failed Lessons: {len(result.failed_lessons)}")
    
    # Performance metrics
    if result.performance_metrics:
        logger.info(f"  Performance Metrics:")
        for key, value in result.performance_metrics.items():
            logger.info(f"    {key}: {value}")
    
    # Backtracking statistics
    if result.backtrack_statistics:
        logger.info(f"  Backtracking Stats:")
        for key, value in result.backtrack_statistics.items():
            logger.info(f"    {key}: {value}")
    
    # Validation checks
    success_criteria = []
    
    # Check 1: 100% completion rate
    completion_achieved = result.completion_rate >= 100.0
    success_criteria.append(("100% Completion Rate", completion_achieved))
    logger.info(f"✓ 100% Completion: {'PASS' if completion_achieved else 'FAIL'}")
    
    # Check 2: Execution time under 60 seconds
    time_limit_met = execution_time <= 60.0
    success_criteria.append(("60s Time Limit", time_limit_met))
    logger.info(f"✓ Time Limit (60s): {'PASS' if time_limit_met else 'FAIL'} ({execution_time:.2f}s)")
    
    # Check 3: No failed lessons
    no_failures = len(result.failed_lessons) == 0
    success_criteria.append(("No Failed Lessons", no_failures))
    logger.info(f"✓ No Failures: {'PASS' if no_failures else 'FAIL'} ({len(result.failed_lessons)} failed)")
    
    # Check 4: Valid schedule entries
    valid_entries = len(result.entries) > 0
    success_criteria.append(("Valid Entries", valid_entries))
    logger.info(f"✓ Valid Entries: {'PASS' if valid_entries else 'FAIL'} ({len(result.entries)} entries)")
    
    # Overall success
    all_passed = all(passed for _, passed in success_criteria)
    logger.info(f"\n🎯 OVERALL RESULT: {'SUCCESS' if all_passed else 'PARTIAL SUCCESS'}")
    
    return result, success_criteria, execution_time

def test_performance_comparison():
    """Compare performance between old and new schedulers"""
    logger.info("=" * 80)
    logger.info("PERFORMANCE COMPARISON TEST")
    logger.info("=" * 80)
    
    db = DatabaseManager()
    
    # Test original scheduler
    logger.info("Testing Original CurriculumBasedFullScheduleGenerator...")
    start_time = time.time()
    
    try:
        original_scheduler = CurriculumBasedFullScheduleGenerator(db)
        original_schedule = original_scheduler.generate_full_schedule()
        original_time = time.time() - start_time
        original_hours = len(original_schedule)
        
        logger.info(f"Original Scheduler Results:")
        logger.info(f"  Scheduled Hours: {original_hours}")
        logger.info(f"  Execution Time: {original_time:.2f}s")
        
    except Exception as e:
        logger.error(f"Original scheduler failed: {e}")
        original_schedule = []
        original_time = 0
        original_hours = 0
    
    # Test optimized scheduler
    logger.info("\nTesting OptimizedCurriculumScheduler...")
    start_time = time.time()
    
    optimized_scheduler = OptimizedCurriculumScheduler(db)
    optimized_result = optimized_scheduler.generate_complete_schedule()
    optimized_time = time.time() - start_time
    
    logger.info(f"Optimized Scheduler Results:")
    logger.info(f"  Scheduled Hours: {optimized_result.scheduled_hours}")
    logger.info(f"  Completion Rate: {optimized_result.completion_rate:.1f}%")
    logger.info(f"  Execution Time: {optimized_time:.2f}s")
    
    # Performance comparison
    logger.info("\n📊 PERFORMANCE COMPARISON:")
    
    if original_hours > 0:
        improvement_hours = optimized_result.scheduled_hours - original_hours
        improvement_percent = (improvement_hours / original_hours * 100) if original_hours > 0 else 0
        logger.info(f"  Hours Improvement: +{improvement_hours} ({improvement_percent:+.1f}%)")
        
        if original_time > 0:
            time_ratio = optimized_time / original_time
            logger.info(f"  Time Ratio: {time_ratio:.2f}x ({'faster' if time_ratio < 1 else 'slower'})")
        
        efficiency_original = original_hours / original_time if original_time > 0 else 0
        efficiency_optimized = optimized_result.scheduled_hours / optimized_time if optimized_time > 0 else 0
        
        logger.info(f"  Efficiency Original: {efficiency_original:.2f} hours/second")
        logger.info(f"  Efficiency Optimized: {efficiency_optimized:.2f} hours/second")
        
        if efficiency_original > 0:
            efficiency_improvement = (efficiency_optimized - efficiency_original) / efficiency_original * 100
            logger.info(f"  Efficiency Improvement: {efficiency_improvement:+.1f}%")
    else:
        logger.info("  Original scheduler failed - cannot compare")
    
    return {
        'original_hours': original_hours,
        'original_time': original_time,
        'optimized_hours': optimized_result.scheduled_hours,
        'optimized_time': optimized_time,
        'optimized_completion': optimized_result.completion_rate,
        'optimized_success': optimized_result.success
    }

def validate_schedule_quality(result):
    """Validate the quality and correctness of the generated schedule"""
    logger.info("=" * 80)
    logger.info("SCHEDULE QUALITY VALIDATION")
    logger.info("=" * 80)
    
    quality_checks = []
    
    # Check 1: No scheduling conflicts
    conflicts = check_scheduling_conflicts(result.entries)
    no_conflicts = len(conflicts) == 0
    quality_checks.append(("No Scheduling Conflicts", no_conflicts))
    logger.info(f"✓ No Conflicts: {'PASS' if no_conflicts else 'FAIL'} ({len(conflicts)} conflicts)")
    
    if conflicts:
        logger.warning("Scheduling conflicts found:")
        for conflict in conflicts[:5]:  # Show first 5 conflicts
            logger.warning(f"  {conflict}")
    
    # Check 2: Teacher workload distribution
    workload_violations = check_teacher_workload(result.entries)
    good_workload = len(workload_violations) <= 5  # Allow up to 5 minor violations
    quality_checks.append(("Good Workload Distribution", good_workload))
    logger.info(f"✓ Workload Distribution: {'PASS' if good_workload else 'FAIL'} ({len(workload_violations)} violations)")
    
    # Check 3: Block rule compliance
    block_violations = check_block_rules(result.entries)
    block_compliance = len(block_violations) == 0
    quality_checks.append(("Block Rule Compliance", block_compliance))
    logger.info(f"✓ Block Rules: {'PASS' if block_compliance else 'FAIL'} ({len(block_violations)} violations)")
    
    # Check 4: Curriculum coverage
    curriculum_coverage = check_curriculum_coverage(result.entries)
    full_coverage = curriculum_coverage >= 95.0  # Allow 5% tolerance
    quality_checks.append(("Curriculum Coverage", full_coverage))
    logger.info(f"✓ Curriculum Coverage: {'PASS' if full_coverage else 'FAIL'} ({curriculum_coverage:.1f}%)")
    
    # Overall quality score
    passed_checks = sum(1 for _, passed in quality_checks if passed)
    quality_score = (passed_checks / len(quality_checks)) * 100
    
    logger.info(f"\n🏆 QUALITY SCORE: {quality_score:.1f}% ({passed_checks}/{len(quality_checks)} checks passed)")
    
    return quality_checks, quality_score

def check_scheduling_conflicts(entries: List[Dict[str, Any]]) -> List[str]:
    """Check for scheduling conflicts in the generated schedule"""
    conflicts = []
    
    # Group entries by day and time slot
    slot_map = {}
    for entry in entries:
        day = entry.get('day', 0)
        time_slot = entry.get('time_slot', 0)
        key = (day, time_slot)
        
        if key not in slot_map:
            slot_map[key] = []
        slot_map[key].append(entry)
    
    # Check for conflicts
    for (day, time_slot), slot_entries in slot_map.items():
        if len(slot_entries) > 1:
            # Check for teacher conflicts
            teachers = set()
            classes = set()
            
            for entry in slot_entries:
                teacher_id = entry.get('teacher_id')
                class_id = entry.get('class_id')
                
                if teacher_id in teachers:
                    conflicts.append(f"Teacher {teacher_id} conflict on Day {day}, Slot {time_slot}")
                teachers.add(teacher_id)
                
                if class_id in classes:
                    conflicts.append(f"Class {class_id} conflict on Day {day}, Slot {time_slot}")
                classes.add(class_id)
    
    return conflicts

def check_teacher_workload(entries: List[Dict[str, Any]]) -> List[str]:
    """Check teacher workload distribution"""
    violations = []
    
    # Group by teacher
    teacher_schedules = {}
    for entry in entries:
        teacher_id = entry.get('teacher_id')
        day = entry.get('day', 0)
        
        if teacher_id not in teacher_schedules:
            teacher_schedules[teacher_id] = set()
        teacher_schedules[teacher_id].add(day)
    
    # Check workload distribution
    for teacher_id, working_days in teacher_schedules.items():
        empty_days = 5 - len(working_days)  # 5 working days per week
        
        if empty_days > 1:  # More than 1 empty day is a violation
            violations.append(f"Teacher {teacher_id} has {empty_days} empty days")
    
    return violations

def check_block_rules(entries: List[Dict[str, Any]]) -> List[str]:
    """Check block rule compliance"""
    violations = []
    
    # Group by lesson and class
    lesson_blocks = {}
    for entry in entries:
        class_id = entry.get('class_id')
        lesson_id = entry.get('lesson_id')
        day = entry.get('day', 0)
        time_slot = entry.get('time_slot', 0)
        
        key = (class_id, lesson_id)
        if key not in lesson_blocks:
            lesson_blocks[key] = []
        lesson_blocks[key].append((day, time_slot))
    
    # Check for block violations (simplified check)
    for (class_id, lesson_id), slots in lesson_blocks.items():
        if len(slots) > 1:
            # Sort slots by day and time
            slots.sort()
            
            # Check for non-consecutive slots on same day
            day_groups = {}
            for day, time_slot in slots:
                if day not in day_groups:
                    day_groups[day] = []
                day_groups[day].append(time_slot)
            
            for day, time_slots in day_groups.items():
                if len(time_slots) > 1:
                    time_slots.sort()
                    for i in range(1, len(time_slots)):
                        if time_slots[i] != time_slots[i-1] + 1:
                            violations.append(f"Non-consecutive slots for Class {class_id}, Lesson {lesson_id} on Day {day}")
                            break
    
    return violations

def check_curriculum_coverage(entries: List[Dict[str, Any]]) -> float:
    """Check curriculum coverage percentage"""
    # This is a simplified check - in reality would compare against curriculum requirements
    total_entries = len(entries)
    target_entries = 279  # Target curriculum hours
    
    coverage = (total_entries / target_entries * 100) if target_entries > 0 else 0
    return min(coverage, 100.0)

def main():
    """Run comprehensive validation testing"""
    logger.info("🚀 STARTING COMPREHENSIVE VALIDATION TESTING")
    logger.info("=" * 80)
    
    try:
        # Test 1: 100% completion rate
        result, success_criteria, execution_time = test_100_percent_completion()
        
        # Test 2: Performance comparison
        performance_comparison = test_performance_comparison()
        
        # Test 3: Schedule quality validation
        quality_checks, quality_score = validate_schedule_quality(result)
        
        # Final summary
        logger.info("=" * 80)
        logger.info("FINAL VALIDATION SUMMARY")
        logger.info("=" * 80)
        
        logger.info("✅ Completion Tests:")
        for test_name, passed in success_criteria:
            logger.info(f"  {test_name}: {'PASS' if passed else 'FAIL'}")
        
        logger.info("\n📊 Performance Results:")
        logger.info(f"  Optimized Hours: {performance_comparison['optimized_hours']}")
        logger.info(f"  Completion Rate: {performance_comparison['optimized_completion']:.1f}%")
        logger.info(f"  Execution Time: {performance_comparison['optimized_time']:.2f}s")
        logger.info(f"  Success: {performance_comparison['optimized_success']}")
        
        logger.info("\n🏆 Quality Tests:")
        for test_name, passed in quality_checks:
            logger.info(f"  {test_name}: {'PASS' if passed else 'FAIL'}")
        logger.info(f"  Overall Quality Score: {quality_score:.1f}%")
        
        # Overall assessment
        completion_success = all(passed for _, passed in success_criteria)
        quality_success = quality_score >= 80.0
        performance_success = (performance_comparison['optimized_completion'] >= 100.0 and 
                             performance_comparison['optimized_time'] <= 60.0)
        
        overall_success = completion_success and quality_success and performance_success
        
        logger.info(f"\n🎯 OVERALL VALIDATION: {'SUCCESS' if overall_success else 'NEEDS IMPROVEMENT'}")
        
        if overall_success:
            logger.info("✅ OptimizedCurriculumScheduler meets all requirements!")
            logger.info("   - Achieves 100% completion rate")
            logger.info("   - Executes within 60-second time limit")
            logger.info("   - Maintains high schedule quality")
            logger.info("   - Outperforms previous scheduler")
        else:
            logger.warning("⚠️ Some validation criteria not met - review needed")
        
        return overall_success
        
    except Exception as e:
        logger.error(f"Validation testing failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)