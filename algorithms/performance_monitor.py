# -*- coding: utf-8 -*-
"""
Performance Monitor - Track and Report Scheduling Performance
Provides timing decorators and performance metrics
"""

import time
import functools
import logging
from typing import Dict, List, Callable, Any
from collections import defaultdict
import json
from datetime import datetime


class PerformanceMonitor:
    """
    Performance monitoring system for schedulers
    
    Features:
    - Method timing with decorators
    - Performance metrics collection
    - Report generation
    - Historical tracking
    """
    
    def __init__(self):
        """Initialize performance monitor"""
        self.logger = logging.getLogger(__name__)
        
        # Metrics storage
        self.metrics: Dict[str, List[float]] = defaultdict(list)
        self.call_counts: Dict[str, int] = defaultdict(int)
        self.total_times: Dict[str, float] = defaultdict(float)
        
        # Current session
        self.session_start = time.time()
        self.session_metrics: List[Dict] = []
    
    def timing_decorator(self, func: Callable) -> Callable:
        """
        Decorator to measure function execution time
        
        Usage:
            @monitor.timing_decorator
            def my_function():
                ...
        
        Args:
            func: Function to decorate
        
        Returns:
            Decorated function
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start
                
                # Record metrics
                func_name = f"{func.__module__}.{func.__name__}"
                self.metrics[func_name].append(elapsed)
                self.call_counts[func_name] += 1
                self.total_times[func_name] += elapsed
                
                # Log if slow
                if elapsed > 1.0:
                    self.logger.warning(
                        f"Slow function: {func_name} took {elapsed:.2f}s"
                    )
                
                return result
            
            except Exception as e:
                elapsed = time.time() - start
                self.logger.error(
                    f"Function {func.__name__} failed after {elapsed:.2f}s: {e}"
                )
                raise
        
        return wrapper
    
    def record_scheduler_run(self, scheduler_name: str, 
                            duration: float, coverage: float,
                            entries: int, conflicts: int):
        """
        Record a scheduler run
        
        Args:
            scheduler_name: Name of scheduler
            duration: Time taken in seconds
            coverage: Coverage percentage
            entries: Number of entries
            conflicts: Number of conflicts
        """
        metric = {
            'timestamp': datetime.now().isoformat(),
            'scheduler': scheduler_name,
            'duration': duration,
            'coverage': coverage,
            'entries': entries,
            'conflicts': conflicts
        }
        
        self.session_metrics.append(metric)
        
        self.logger.info(
            f"Scheduler run: {scheduler_name} - "
            f"{duration:.2f}s, {coverage:.1f}% coverage, "
            f"{entries} entries, {conflicts} conflicts"
        )
    
    def get_function_stats(self, func_name: str) -> Dict:
        """
        Get statistics for a specific function
        
        Args:
            func_name: Function name
        
        Returns:
            Dict with statistics
        """
        if func_name not in self.metrics:
            return {}
        
        times = self.metrics[func_name]
        
        return {
            'function': func_name,
            'call_count': self.call_counts[func_name],
            'total_time': self.total_times[func_name],
            'avg_time': sum(times) / len(times) if times else 0,
            'min_time': min(times) if times else 0,
            'max_time': max(times) if times else 0,
            'last_time': times[-1] if times else 0
        }
    
    def get_all_stats(self) -> List[Dict]:
        """
        Get statistics for all tracked functions
        
        Returns:
            List of stat dicts
        """
        stats = []
        for func_name in self.metrics.keys():
            stats.append(self.get_function_stats(func_name))
        
        # Sort by total time (descending)
        stats.sort(key=lambda x: x['total_time'], reverse=True)
        
        return stats
    
    def get_session_summary(self) -> Dict:
        """
        Get summary of current session
        
        Returns:
            Dict with session summary
        """
        session_duration = time.time() - self.session_start
        
        return {
            'session_duration': session_duration,
            'total_functions_tracked': len(self.metrics),
            'total_function_calls': sum(self.call_counts.values()),
            'total_time_in_functions': sum(self.total_times.values()),
            'scheduler_runs': len(self.session_metrics),
            'session_metrics': self.session_metrics
        }
    
    def generate_report(self, top_n: int = 10) -> str:
        """
        Generate performance report
        
        Args:
            top_n: Number of top functions to include
        
        Returns:
            Formatted report string
        """
        report = []
        report.append("="*80)
        report.append("PERFORMANCE REPORT")
        report.append("="*80)
        
        # Session summary
        summary = self.get_session_summary()
        report.append(f"\nSession Duration: {summary['session_duration']:.2f}s")
        report.append(f"Functions Tracked: {summary['total_functions_tracked']}")
        report.append(f"Total Function Calls: {summary['total_function_calls']}")
        report.append(f"Scheduler Runs: {summary['scheduler_runs']}")
        
        # Top functions by total time
        report.append(f"\n{'='*80}")
        report.append(f"TOP {top_n} FUNCTIONS BY TOTAL TIME")
        report.append(f"{'='*80}")
        
        stats = self.get_all_stats()[:top_n]
        
        for i, stat in enumerate(stats, 1):
            report.append(f"\n{i}. {stat['function']}")
            report.append(f"   Calls: {stat['call_count']}")
            report.append(f"   Total: {stat['total_time']:.2f}s")
            report.append(f"   Avg: {stat['avg_time']:.4f}s")
            report.append(f"   Min: {stat['min_time']:.4f}s")
            report.append(f"   Max: {stat['max_time']:.4f}s")
        
        # Scheduler runs
        if summary['scheduler_runs'] > 0:
            report.append(f"\n{'='*80}")
            report.append(f"SCHEDULER RUNS")
            report.append(f"{'='*80}")
            
            for i, metric in enumerate(summary['session_metrics'], 1):
                report.append(f"\n{i}. {metric['scheduler']}")
                report.append(f"   Time: {metric['timestamp']}")
                report.append(f"   Duration: {metric['duration']:.2f}s")
                report.append(f"   Coverage: {metric['coverage']:.1f}%")
                report.append(f"   Entries: {metric['entries']}")
                report.append(f"   Conflicts: {metric['conflicts']}")
        
        report.append(f"\n{'='*80}")
        
        return "\n".join(report)
    
    def save_report(self, filename: str = "performance_report.txt"):
        """
        Save performance report to file
        
        Args:
            filename: Output filename
        """
        report = self.generate_report()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        self.logger.info(f"Performance report saved to {filename}")
    
    def export_metrics_json(self, filename: str = "performance_metrics.json"):
        """
        Export metrics to JSON file
        
        Args:
            filename: Output filename
        """
        data = {
            'session_summary': self.get_session_summary(),
            'function_stats': self.get_all_stats(),
            'raw_metrics': {
                func: times for func, times in self.metrics.items()
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Metrics exported to {filename}")
    
    def reset(self):
        """Reset all metrics"""
        self.metrics.clear()
        self.call_counts.clear()
        self.total_times.clear()
        self.session_metrics.clear()
        self.session_start = time.time()
        
        self.logger.info("Performance monitor reset")


# Global instance
_global_monitor = PerformanceMonitor()


def get_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    return _global_monitor


def timing(func: Callable) -> Callable:
    """
    Convenience decorator using global monitor
    
    Usage:
        from algorithms.performance_monitor import timing
        
        @timing
        def my_function():
            ...
    """
    return _global_monitor.timing_decorator(func)
