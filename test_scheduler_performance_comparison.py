#!/usr/bin/env python3
"""
Performance comparison test between old and new schedulers
Tests scalability, memory usage, and completion rates
"""

import time
import logging
import psutil
import os
from typing import Dict, Any, List
from database.db_manager import DatabaseManager
from algorithms.optimized_curriculum_scheduler import OptimizedCurriculumScheduler
from algorithms.curriculum_based_scheduler import CurriculumBasedFullScheduleGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_memory_usage():
    """Get current memory usage in MB"""
    try:
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        return memory_info.rss / 1024 / 1024  # Convert to MB
    except:
        return 0

def benchmark_scheduler(scheduler_name: str, scheduler_func, iterations: int = 3) -> Dict[str, Any]:
    """Benchmark a scheduler with multiple iterations"""
    logger.info(f"Benchmarking {scheduler_name} ({iterations} iterations)...")
    
    results = {
        'scheduler_name': scheduler_name,
        'iterations': iterations,
        'execution_times': [],
        'scheduled_hours': [],
        'completion_rates': [],
        'memory_usage_start': [],
        'memory_usage_end': [],
        'memory_peak': [],
        'success_count': 0,
        'failure_count': 0,
        'errors': []
    }
    
    for i in range(iterations):
        logger.info(f"  Iteration {i+1}/{iterations}")
        
        # Record initial memory
        memory_start = get_memory_usage()
        results['memory_usage_start'].append(memory_start)
        
        try:
            start_time = time.time()
            
            # Run scheduler
            schedule_entries = scheduler_func()
            
            execution_time = time.time() - start_time
            
            # Record final memory
            memory_end = get_memory_usage()
            memory_peak = max(memory_start, memory_end)
            
            results['execution_times'].append(execution_time)
            results['scheduled_hours'].append(len(schedule_entries))
            results['memory_usage_end'].append(memory_end)
            results['memory_peak'].append(memory_peak)
            results['success_count'] += 1
            
            # Calculate completion rate (assuming 279 target hours)
            completion_rate = (len(schedule_entries) / 279 * 100) if len(schedule_entries) > 0 else 0
            results['completion_rates'].append(completion_rate)
            
            logger.info(f"    Time: {execution_time:.2f}s, Hours: {len(schedule_entries)}, Completion: {completion_rate:.1f}%")
            
        except Exception as e:
            results['failure_count'] += 1
            results['errors'].append(str(e))
            results['execution_times'].append(0)
            results['scheduled_hours'].append(0)
            results['completion_rates'].append(0)
            results['memory_usage_end'].append(memory_start)
            results['memory_peak'].append(memory_start)
            logger.error(f"    Failed: {e}")
    
    return results

def analyze_results(results: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze benchmark results and calculate statistics"""
    if not results['execution_times'] or results['success_count'] == 0:
        return {
            'avg_execution_time': 0,
            'min_execution_time': 0,
            'max_execution_time': 0,
            'avg_scheduled_hours': 0,
            'avg_completion_rate': 0,
            'avg_memory_usage': 0,
            'success_rate': 0,
            'reliability_score': 0
        }
    
    # Filter successful runs
    successful_times = [t for t in results['execution_times'] if t > 0]
    successful_hours = [h for h in results['scheduled_hours'] if h > 0]
    successful_rates = [r for r in results['completion_rates'] if r > 0]
    
    analysis = {
        'avg_execution_time': sum(successful_times) / len(successful_times) if successful_times else 0,
        'min_execution_time': min(successful_times) if successful_times else 0,
        'max_execution_time': max(successful_times) if successful_times else 0,
        'avg_scheduled_hours': sum(successful_hours) / len(successful_hours) if successful_hours else 0,
        'avg_completion_rate': sum(successful_rates) / len(successful_rates) if successful_rates else 0,
        'avg_memory_usage': sum(results['memory_peak']) / len(results['memory_peak']) if results['memory_peak'] else 0,
        'success_rate': (results['success_count'] / results['iterations'] * 100) if results['iterations'] > 0 else 0,
        'reliability_score': results['success_count'] / results['iterations'] if results['iterations'] > 0 else 0
    }
    
    return analysis

def compare_schedulers():
    """Compare performance between old and new schedulers"""
    logger.info("=" * 80)
    logger.info("SCHEDULER PERFORMANCE COMPARISON")
    logger.info("=" * 80)
    
    db = DatabaseManager()
    
    # Test configurations
    iterations = 3
    
    # Benchmark original scheduler
    def run_original_scheduler():
        scheduler = CurriculumBasedFullScheduleGenerator(db)
        return scheduler.generate_full_schedule()
    
    original_results = benchmark_scheduler("CurriculumBasedFullScheduleGenerator", run_original_scheduler, iterations)
    original_analysis = analyze_results(original_results)
    
    # Benchmark optimized scheduler
    def run_optimized_scheduler():
        scheduler = OptimizedCurriculumScheduler(db)
        return scheduler.generate_schedule()
    
    optimized_results = benchmark_scheduler("OptimizedCurriculumScheduler", run_optimized_scheduler, iterations)
    optimized_analysis = analyze_results(optimized_results)
    
    # Performance comparison
    logger.info("\n" + "=" * 80)
    logger.info("PERFORMANCE COMPARISON RESULTS")
    logger.info("=" * 80)
    
    logger.info(f"\n📊 EXECUTION TIME:")
    logger.info(f"  Original Scheduler:")
    logger.info(f"    Average: {original_analysis['avg_execution_time']:.2f}s")
    logger.info(f"    Min: {original_analysis['min_execution_time']:.2f}s")
    logger.info(f"    Max: {original_analysis['max_execution_time']:.2f}s")
    
    logger.info(f"  Optimized Scheduler:")
    logger.info(f"    Average: {optimized_analysis['avg_execution_time']:.2f}s")
    logger.info(f"    Min: {optimized_analysis['min_execution_time']:.2f}s")
    logger.info(f"    Max: {optimized_analysis['max_execution_time']:.2f}s")
    
    # Time improvement
    if original_analysis['avg_execution_time'] > 0:
        time_improvement = ((original_analysis['avg_execution_time'] - optimized_analysis['avg_execution_time']) / 
                           original_analysis['avg_execution_time'] * 100)
        logger.info(f"  Time Improvement: {time_improvement:+.1f}%")
    
    logger.info(f"\n📈 COMPLETION RATE:")
    logger.info(f"  Original Scheduler: {original_analysis['avg_completion_rate']:.1f}%")
    logger.info(f"  Optimized Scheduler: {optimized_analysis['avg_completion_rate']:.1f}%")
    
    # Completion improvement
    completion_improvement = optimized_analysis['avg_completion_rate'] - original_analysis['avg_completion_rate']
    logger.info(f"  Completion Improvement: {completion_improvement:+.1f} percentage points")
    
    logger.info(f"\n📋 SCHEDULED HOURS:")
    logger.info(f"  Original Scheduler: {original_analysis['avg_scheduled_hours']:.0f} hours")
    logger.info(f"  Optimized Scheduler: {optimized_analysis['avg_scheduled_hours']:.0f} hours")
    
    # Hours improvement
    hours_improvement = optimized_analysis['avg_scheduled_hours'] - original_analysis['avg_scheduled_hours']
    logger.info(f"  Hours Improvement: {hours_improvement:+.0f} hours")
    
    logger.info(f"\n💾 MEMORY USAGE:")
    logger.info(f"  Original Scheduler: {original_analysis['avg_memory_usage']:.1f} MB")
    logger.info(f"  Optimized Scheduler: {optimized_analysis['avg_memory_usage']:.1f} MB")
    
    # Memory improvement
    if original_analysis['avg_memory_usage'] > 0:
        memory_improvement = ((original_analysis['avg_memory_usage'] - optimized_analysis['avg_memory_usage']) / 
                             original_analysis['avg_memory_usage'] * 100)
        logger.info(f"  Memory Improvement: {memory_improvement:+.1f}%")
    
    logger.info(f"\n🎯 RELIABILITY:")
    logger.info(f"  Original Scheduler: {original_analysis['success_rate']:.1f}% success rate")
    logger.info(f"  Optimized Scheduler: {optimized_analysis['success_rate']:.1f}% success rate")
    
    # Overall assessment
    logger.info(f"\n🏆 OVERALL ASSESSMENT:")
    
    improvements = []
    if optimized_analysis['avg_completion_rate'] > original_analysis['avg_completion_rate']:
        improvements.append("Higher completion rate")
    if optimized_analysis['avg_execution_time'] < original_analysis['avg_execution_time'] and original_analysis['avg_execution_time'] > 0:
        improvements.append("Faster execution")
    if optimized_analysis['avg_memory_usage'] < original_analysis['avg_memory_usage'] and original_analysis['avg_memory_usage'] > 0:
        improvements.append("Lower memory usage")
    if optimized_analysis['success_rate'] >= original_analysis['success_rate']:
        improvements.append("Equal or better reliability")
    
    if improvements:
        logger.info(f"  ✅ Optimized scheduler shows improvements in: {', '.join(improvements)}")
    else:
        logger.info(f"  ⚠️ Optimized scheduler needs further optimization")
    
    # Performance score calculation
    completion_score = min(optimized_analysis['avg_completion_rate'] / 100, 1.0) * 40  # 40% weight
    speed_score = min(60 / max(optimized_analysis['avg_execution_time'], 1), 1.0) * 30  # 30% weight (60s target)
    reliability_score = optimized_analysis['reliability_score'] * 30  # 30% weight
    
    total_score = completion_score + speed_score + reliability_score
    
    logger.info(f"  📊 Performance Score: {total_score:.1f}/100")
    logger.info(f"    - Completion: {completion_score:.1f}/40")
    logger.info(f"    - Speed: {speed_score:.1f}/30")
    logger.info(f"    - Reliability: {reliability_score:.1f}/30")
    
    return {
        'original_results': original_results,
        'original_analysis': original_analysis,
        'optimized_results': optimized_results,
        'optimized_analysis': optimized_analysis,
        'improvements': improvements,
        'performance_score': total_score
    }

def test_scalability():
    """Test scheduler scalability with different dataset sizes"""
    logger.info("\n" + "=" * 80)
    logger.info("SCALABILITY TESTING")
    logger.info("=" * 80)
    
    db = DatabaseManager()
    
    # Test with current dataset
    logger.info("Testing with current dataset...")
    
    start_time = time.time()
    memory_start = get_memory_usage()
    
    scheduler = OptimizedCurriculumScheduler(db)
    schedule_entries = scheduler.generate_schedule()
    
    execution_time = time.time() - start_time
    memory_end = get_memory_usage()
    memory_used = memory_end - memory_start
    
    logger.info(f"Current Dataset Results:")
    logger.info(f"  Execution Time: {execution_time:.2f}s")
    logger.info(f"  Scheduled Hours: {len(schedule_entries)}")
    logger.info(f"  Memory Used: {memory_used:.1f} MB")
    logger.info(f"  Memory Efficiency: {len(schedule_entries)/memory_used:.1f} hours/MB" if memory_used > 0 else "  Memory Efficiency: N/A")
    
    # Scalability metrics
    classes_count = len(db.get_all_classes())
    teachers_count = len(db.get_all_teachers())
    lessons_count = len(db.get_all_lessons())
    
    logger.info(f"\nDataset Characteristics:")
    logger.info(f"  Classes: {classes_count}")
    logger.info(f"  Teachers: {teachers_count}")
    logger.info(f"  Lessons: {lessons_count}")
    logger.info(f"  Target Hours: 279")
    
    # Performance per unit calculations
    time_per_hour = execution_time / len(schedule_entries) if len(schedule_entries) > 0 else 0
    time_per_class = execution_time / classes_count if classes_count > 0 else 0
    
    logger.info(f"\nScalability Metrics:")
    logger.info(f"  Time per scheduled hour: {time_per_hour:.4f}s")
    logger.info(f"  Time per class: {time_per_class:.4f}s")
    logger.info(f"  Throughput: {len(schedule_entries)/execution_time:.1f} hours/second" if execution_time > 0 else "  Throughput: N/A")
    
    # Scalability assessment
    logger.info(f"\n📈 SCALABILITY ASSESSMENT:")
    
    if execution_time < 10:
        logger.info("  ✅ Excellent scalability - completes quickly")
    elif execution_time < 30:
        logger.info("  ✅ Good scalability - reasonable execution time")
    elif execution_time < 60:
        logger.info("  ⚠️ Moderate scalability - approaching time limit")
    else:
        logger.info("  ❌ Poor scalability - exceeds time limit")
    
    if memory_used < 100:
        logger.info("  ✅ Excellent memory efficiency")
    elif memory_used < 500:
        logger.info("  ✅ Good memory efficiency")
    elif memory_used < 1000:
        logger.info("  ⚠️ Moderate memory usage")
    else:
        logger.info("  ❌ High memory usage")
    
    return {
        'execution_time': execution_time,
        'scheduled_hours': len(schedule_entries),
        'memory_used': memory_used,
        'time_per_hour': time_per_hour,
        'throughput': len(schedule_entries)/execution_time if execution_time > 0 else 0,
        'classes_count': classes_count,
        'teachers_count': teachers_count,
        'lessons_count': lessons_count
    }

def main():
    """Run comprehensive performance comparison and scalability tests"""
    logger.info("🚀 STARTING PERFORMANCE COMPARISON AND SCALABILITY TESTING")
    
    try:
        # Performance comparison
        comparison_results = compare_schedulers()
        
        # Scalability testing
        scalability_results = test_scalability()
        
        # Final summary
        logger.info("\n" + "=" * 80)
        logger.info("FINAL SUMMARY")
        logger.info("=" * 80)
        
        logger.info("✅ Performance Comparison:")
        logger.info(f"  Optimized scheduler performance score: {comparison_results['performance_score']:.1f}/100")
        logger.info(f"  Key improvements: {', '.join(comparison_results['improvements']) if comparison_results['improvements'] else 'None identified'}")
        
        logger.info("\n✅ Scalability Assessment:")
        logger.info(f"  Execution time: {scalability_results['execution_time']:.2f}s")
        logger.info(f"  Throughput: {scalability_results['throughput']:.1f} hours/second")
        logger.info(f"  Memory efficiency: {scalability_results['scheduled_hours']/scalability_results['memory_used']:.1f} hours/MB" if scalability_results['memory_used'] > 0 else "  Memory efficiency: N/A")
        
        # Overall success criteria
        success_criteria = [
            comparison_results['optimized_analysis']['avg_completion_rate'] >= 95.0,  # 95%+ completion
            comparison_results['optimized_analysis']['avg_execution_time'] <= 60.0,   # Under 60s
            comparison_results['optimized_analysis']['success_rate'] >= 90.0,         # 90%+ reliability
            comparison_results['performance_score'] >= 70.0                           # 70+ performance score
        ]
        
        passed_criteria = sum(success_criteria)
        
        logger.info(f"\n🎯 SUCCESS CRITERIA: {passed_criteria}/4 passed")
        
        if passed_criteria >= 3:
            logger.info("🎉 OVERALL RESULT: SUCCESS - Optimized scheduler meets performance requirements!")
        else:
            logger.info("⚠️ OVERALL RESULT: NEEDS IMPROVEMENT - Some performance criteria not met")
        
        return passed_criteria >= 3
        
    except Exception as e:
        logger.error(f"Performance testing failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)