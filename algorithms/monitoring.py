# -*- coding: utf-8 -*-
"""
Advanced metrics and monitoring for scheduler performance
Provides detailed performance analytics and monitoring capabilities
"""
import time
import threading
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
import json
import logging
from dataclasses import dataclass, asdict
from enum import Enum


class MetricType(Enum):
    """Type of metric being tracked"""
    PERFORMANCE = "performance"
    COVERAGE = "coverage"
    CONFLICTS = "conflicts"
    RESOURCE = "resource"
    ALGORITHM = "algorithm"


@dataclass
class Metric:
    """Data class for a single metric"""
    name: str
    value: float
    timestamp: datetime
    type: MetricType
    metadata: Optional[Dict[str, Any]] = None


class MetricsCollector:
    """
    Collects and manages metrics for scheduler performance
    """
    
    def __init__(self, max_metrics: int = 1000):
        self.logger = logging.getLogger(__name__)
        self.max_metrics = max_metrics
        self.metrics: Dict[MetricType, deque] = {
            MetricType.PERFORMANCE: deque(maxlen=max_metrics),
            MetricType.COVERAGE: deque(maxlen=max_metrics),
            MetricType.CONFLICTS: deque(maxlen=max_metrics),
            MetricType.RESOURCE: deque(maxlen=max_metrics),
            MetricType.ALGORITHM: deque(maxlen=max_metrics),
        }
        self.performance_data = defaultdict(list)
        self.lock = threading.Lock()
        
    def record_metric(self, name: str, value: float, metric_type: MetricType, metadata: Optional[Dict[str, Any]] = None):
        """Record a new metric"""
        with self.lock:
            metric = Metric(
                name=name,
                value=value,
                timestamp=datetime.now(),
                type=metric_type,
                metadata=metadata or {}
            )
            
            self.metrics[metric_type].append(metric)
            
            # Store performance data by name for aggregation
            if metric_type == MetricType.PERFORMANCE:
                self.performance_data[name].append({
                    'value': value,
                    'timestamp': metric.timestamp,
                    'metadata': metadata
                })
            
            self.logger.debug(f"Recorded metric: {name} = {value}")
    
    def get_metrics_by_type(self, metric_type: MetricType) -> List[Metric]:
        """Get all metrics of a specific type"""
        with self.lock:
            return list(self.metrics[metric_type])
    
    def get_metrics_by_name(self, name: str) -> List[Metric]:
        """Get all metrics with a specific name"""
        with self.lock:
            all_metrics = []
            for metric_type, metrics_list in self.metrics.items():
                all_metrics.extend([m for m in metrics_list if m.name == name])
            return all_metrics
    
    def get_performance_stats(self, name: str) -> Dict[str, float]:
        """Get performance statistics for a specific metric name"""
        with self.lock:
            values = [item['value'] for item in self.performance_data[name]]
            if not values:
                return {}
                
            return {
                'count': len(values),
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values),
                'last': values[-1]
            }
    
    def get_recent_metrics(self, hours: int = 1) -> List[Metric]:
        """Get metrics from the last specified hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        with self.lock:
            recent = []
            for metrics_list in self.metrics.values():
                recent.extend([m for m in metrics_list if m.timestamp >= cutoff])
            return sorted(recent, key=lambda m: m.timestamp, reverse=True)
    
    def export_metrics(self, filename: str = None) -> str:
        """Export metrics to JSON file"""
        if filename is None:
            filename = f"scheduler_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        with self.lock:
            export_data = {}
            for metric_type, metrics_list in self.metrics.items():
                export_data[metric_type.value] = [
                    {
                        'name': m.name,
                        'value': m.value,
                        'timestamp': m.timestamp.isoformat(),
                        'metadata': m.metadata
                    }
                    for m in metrics_list
                ]
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)
            
        self.logger.info(f"Metrics exported to {filename}")
        return filename
    
    def clear_metrics(self):
        """Clear all metrics"""
        with self.lock:
            for metrics_list in self.metrics.values():
                metrics_list.clear()
            self.performance_data.clear()
            self.logger.info("All metrics cleared")


class PerformanceMonitor:
    """
    Monitors scheduler performance and provides detailed analytics
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.collector = MetricsCollector()
        self.start_times = {}
        
    def start_timer(self, name: str):
        """Start a timer for a specific operation"""
        self.start_times[name] = time.time()
        
    def stop_timer(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> float:
        """Stop a timer and record the duration"""
        if name in self.start_times:
            duration = time.time() - self.start_times[name]
            del self.start_times[name]
            
            self.collector.record_metric(
                name=f"{name}_duration",
                value=duration,
                metric_type=MetricType.PERFORMANCE,
                metadata=metadata
            )
            
            self.logger.debug(f"Timer '{name}' completed in {duration:.3f}s")
            return duration
        else:
            self.logger.warning(f"Timer '{name}' was not started")
            return 0.0
    
    def record_coverage(self, coverage_percentage: float, total_slots: int, scheduled_slots: int):
        """Record schedule coverage metrics"""
        self.collector.record_metric(
            name="coverage_percentage",
            value=coverage_percentage,
            metric_type=MetricType.COVERAGE,
            metadata={
                "total_slots": total_slots,
                "scheduled_slots": scheduled_slots
            }
        )
        
        self.collector.record_metric(
            name="scheduled_slots",
            value=scheduled_slots,
            metric_type=MetricType.COVERAGE,
            metadata={
                "total_slots": total_slots,
                "coverage_percentage": coverage_percentage
            }
        )
        
        self.collector.record_metric(
            name="empty_slots",
            value=total_slots - scheduled_slots,
            metric_type=MetricType.COVERAGE,
            metadata={
                "total_slots": total_slots,
                "coverage_percentage": coverage_percentage
            }
        )
    
    def record_conflicts(self, conflict_count: int, conflict_type: str):
        """Record conflict metrics"""
        self.collector.record_metric(
            name="conflicts_detected",
            value=conflict_count,
            metric_type=MetricType.CONFLICTS,
            metadata={
                "type": conflict_type,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def record_resource_usage(self, memory_mb: float, cpu_percent: float):
        """Record resource usage metrics"""
        self.collector.record_metric(
            name="memory_usage_mb",
            value=memory_mb,
            metric_type=MetricType.RESOURCE,
            metadata={
                "cpu_percent": cpu_percent
            }
        )
        
        self.collector.record_metric(
            name="cpu_usage_percent",
            value=cpu_percent,
            metric_type=MetricType.RESOURCE,
            metadata={
                "memory_mb": memory_mb
            }
        )
    
    def record_algorithm_metrics(self, algorithm_name: str, success: bool, iteration_count: int = 0):
        """Record algorithm-specific metrics"""
        self.collector.record_metric(
            name="algorithm_success",
            value=1 if success else 0,
            metric_type=MetricType.ALGORITHM,
            metadata={
                "algorithm": algorithm_name,
                "iteration_count": iteration_count
            }
        )
        
        if iteration_count > 0:
            self.collector.record_metric(
                name="algorithm_iterations",
                value=iteration_count,
                metric_type=MetricType.ALGORITHM,
                metadata={
                    "algorithm": algorithm_name,
                    "success": success
                }
            )
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate a comprehensive performance report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "performance_stats": {},
            "coverage_stats": {},
            "conflict_stats": {},
            "resource_stats": {},
            "algorithm_stats": {}
        }
        
        # Performance stats
        for name in set([m.name for m in self.collector.get_metrics_by_type(MetricType.PERFORMANCE)]):
            report["performance_stats"][name] = self.collector.get_performance_stats(name)
        
        # Coverage stats
        for name in set([m.name for m in self.collector.get_metrics_by_type(MetricType.COVERAGE)]):
            report["coverage_stats"][name] = self.collector.get_performance_stats(name)
        
        # Conflict stats
        for name in set([m.name for m in self.collector.get_metrics_by_type(MetricType.CONFLICTS)]):
            report["conflict_stats"][name] = self.collector.get_performance_stats(name)
        
        # Resource stats
        for name in set([m.name for m in self.collector.get_metrics_by_type(MetricType.RESOURCE)]):
            report["resource_stats"][name] = self.collector.get_performance_stats(name)
        
        # Algorithm stats
        for name in set([m.name for m in self.collector.get_metrics_by_type(MetricType.ALGORITHM)]):
            report["algorithm_stats"][name] = self.collector.get_performance_stats(name)
        
        return report
    
    def print_detailed_report(self):
        """Print a detailed performance report to console"""
        report = self.get_performance_report()
        
        print("=" * 60)
        print("📊 DETAILED PERFORMANCE REPORT")
        print("=" * 60)
        print(f"Generated at: {report['timestamp']}")
        print()
        
        if report["performance_stats"]:
            print("⏱️  PERFORMANCE METRICS")
            print("-" * 30)
            for name, stats in report["performance_stats"].items():
                if stats:  # Only print if there are stats
                    print(f"{name:20} | Count: {stats.get('count', 0):3} | Min: {stats.get('min', 0):6.3f}s | "
                          f"Max: {stats.get('max', 0):6.3f}s | Avg: {stats.get('avg', 0):6.3f}s")
            print()
        
        if report["coverage_stats"]:
            print("🎯 COVERAGE METRICS")
            print("-" * 30)
            for name, stats in report["coverage_stats"].items():
                if stats:  # Only print if there are stats
                    print(f"{name:20} | Count: {stats.get('count', 0):3} | Min: {stats.get('min', 0):6.2f} | "
                          f"Max: {stats.get('max', 0):6.2f} | Avg: {stats.get('avg', 0):6.2f}")
            print()
        
        if report["conflict_stats"]:
            print("⚠️  CONFLICT METRICS")
            print("-" * 30)
            for name, stats in report["conflict_stats"].items():
                if stats:  # Only print if there are stats
                    print(f"{name:20} | Count: {stats.get('count', 0):3} | Min: {stats.get('min', 0):3} | "
                          f"Max: {stats.get('max', 0):3} | Avg: {stats.get('avg', 0):6.2f}")
            print()
        
        if report["resource_stats"]:
            print("💾 RESOURCE METRICS")
            print("-" * 30)
            for name, stats in report["resource_stats"].items():
                if stats:  # Only print if there are stats
                    print(f"{name:20} | Count: {stats.get('count', 0):3} | Min: {stats.get('min', 0):6.1f} | "
                          f"Max: {stats.get('max', 0):6.1f} | Avg: {stats.get('avg', 0):6.1f}")
            print()
        
        if report["algorithm_stats"]:
            print("⚙️  ALGORITHM METRICS")
            print("-" * 30)
            for name, stats in report["algorithm_stats"].items():
                if stats:  # Only print if there are stats
                    print(f"{name:20} | Count: {stats.get('count', 0):3} | Min: {stats.get('min', 0):3} | "
                          f"Max: {stats.get('max', 0):3} | Avg: {stats.get('avg', 0):6.2f}")
            print()
        
        print("=" * 60)


class MonitoringDecorator:
    """
    Decorator class for monitoring function execution
    """
    
    def __init__(self, monitor: PerformanceMonitor, operation_name: str = None):
        self.monitor = monitor
        self.operation_name = operation_name
    
    def __call__(self, func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            name = self.operation_name or func.__name__
            self.monitor.start_timer(name)
            
            try:
                result = func(*args, **kwargs)
                duration = self.monitor.stop_timer(name)
                self.monitor.record_algorithm_metrics(name, True)
                return result
            except Exception as e:
                self.monitor.stop_timer(name)
                self.monitor.record_algorithm_metrics(name, False)
                raise e
        
        return wrapper


# Global performance monitor instance
_global_monitor = PerformanceMonitor()


def get_global_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance"""
    return _global_monitor


def monitor_function(operation_name: str = None):
    """Decorator to monitor function execution with the global monitor"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            name = operation_name or func.__name__
            _global_monitor.start_timer(name)
            
            try:
                result = func(*args, **kwargs)
                _global_monitor.stop_timer(name)
                _global_monitor.record_algorithm_metrics(name, True)
                return result
            except Exception as e:
                _global_monitor.stop_timer(name)
                _global_monitor.record_algorithm_metrics(name, False)
                raise e
        
        return wrapper
    return decorator