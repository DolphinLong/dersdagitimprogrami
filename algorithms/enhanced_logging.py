"""
Enhanced Logging Configuration for Optimized Scheduler
Provides structured logging with performance metrics and diagnostics
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional


class SchedulerFormatter(logging.Formatter):
    """Custom formatter for scheduler logs with enhanced metadata"""
    
    def __init__(self):
        super().__init__()
        
    def format(self, record):
        # Add timestamp and level
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        level = record.levelname.ljust(8)
        
        # Add module and function info
        module = record.module
        func = record.funcName
        
        # Format message
        message = record.getMessage()
        
        # Create formatted log entry
        formatted = f"[{timestamp}] {level} [{module}.{func}] {message}"
        
        # Add exception info if present
        if record.exc_info:
            formatted += "\n" + self.formatException(record.exc_info)
            
        return formatted


class PerformanceFilter(logging.Filter):
    """Filter to add performance context to log records"""
    
    def __init__(self):
        super().__init__()
        self.start_time = datetime.now()
        
    def filter(self, record):
        # Add elapsed time since logger initialization
        elapsed = (datetime.now() - self.start_time).total_seconds()
        record.elapsed_time = f"{elapsed:.3f}s"
        return True


def setup_enhanced_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    console_output: bool = True,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Setup enhanced logging for the optimized scheduler
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
        console_output: Whether to output to console
        max_file_size: Maximum log file size in bytes
        backup_count: Number of backup files to keep
        
    Returns:
        Configured logger instance
    """
    
    # Create logger
    logger = logging.getLogger("OptimizedScheduler")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = SchedulerFormatter()
    
    # Create performance filter
    perf_filter = PerformanceFilter()
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        console_handler.addFilter(perf_filter)
        logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file:
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        file_handler.addFilter(perf_filter)
        logger.addHandler(file_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    logger.info("Enhanced logging initialized")
    logger.info(f"Log level: {log_level}")
    logger.info(f"Console output: {console_output}")
    logger.info(f"Log file: {log_file or 'None'}")
    
    return logger


class SchedulingMetricsLogger:
    """Specialized logger for scheduling metrics and diagnostics"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.metrics_data = {}
        
    def log_phase_start(self, phase_name: str, metadata: Optional[Dict[str, Any]] = None):
        """Log the start of a scheduling phase"""
        self.logger.info(f"🚀 Starting phase: {phase_name}")
        if metadata:
            for key, value in metadata.items():
                self.logger.info(f"   {key}: {value}")
                
    def log_phase_complete(self, phase_name: str, duration: float, success: bool, 
                          results: Optional[Dict[str, Any]] = None):
        """Log the completion of a scheduling phase"""
        status = "✅ SUCCESS" if success else "❌ FAILED"
        self.logger.info(f"{status} Phase completed: {phase_name} ({duration:.3f}s)")
        
        if results:
            for key, value in results.items():
                self.logger.info(f"   {key}: {value}")
                
    def log_backtrack_attempt(self, depth: int, lesson_info: str, reason: str):
        """Log a backtracking attempt"""
        self.logger.debug(f"🔄 Backtrack (depth {depth}): {lesson_info} - {reason}")
        
    def log_constraint_relaxation(self, from_level: str, to_level: str, reason: str):
        """Log constraint relaxation"""
        self.logger.warning(f"⚠️ Constraint relaxation: {from_level} → {to_level} - {reason}")
        
    def log_alternative_block_usage(self, lesson_info: str, original_pattern: str, 
                                  alternative_pattern: str):
        """Log alternative block pattern usage"""
        self.logger.info(f"🔧 Alternative block: {lesson_info} - {original_pattern} → {alternative_pattern}")
        
    def log_placement_failure(self, lesson_info: str, attempts: int, final_reason: str):
        """Log lesson placement failure"""
        self.logger.error(f"❌ Placement failed: {lesson_info} after {attempts} attempts - {final_reason}")
        
    def log_workload_violation(self, teacher_name: str, empty_days: int, severity: str):
        """Log workload distribution violation"""
        self.logger.warning(f"⚖️ Workload violation: {teacher_name} has {empty_days} empty days ({severity})")
        
    def log_performance_milestone(self, milestone: str, elapsed_time: float, 
                                progress_percentage: float):
        """Log performance milestone"""
        self.logger.info(f"📊 {milestone}: {elapsed_time:.2f}s elapsed, {progress_percentage:.1f}% complete")
        
    def log_final_summary(self, completion_rate: float, total_hours: int, 
                         scheduled_hours: int, execution_time: float, 
                         success: bool):
        """Log final scheduling summary"""
        status = "🎉 SUCCESS" if success else "⚠️ PARTIAL"
        self.logger.info("=" * 80)
        self.logger.info(f"{status} FINAL SCHEDULING SUMMARY")
        self.logger.info("=" * 80)
        self.logger.info(f"Completion rate: {completion_rate:.1f}%")
        self.logger.info(f"Scheduled hours: {scheduled_hours}/{total_hours}")
        self.logger.info(f"Execution time: {execution_time:.2f}s")
        self.logger.info(f"Target achieved: {'YES' if success else 'NO'}")
        self.logger.info("=" * 80)


def create_scheduler_logger(
    scheduler_name: str = "OptimizedScheduler",
    log_level: str = "INFO",
    enable_file_logging: bool = True
) -> tuple[logging.Logger, SchedulingMetricsLogger]:
    """
    Create a complete logging setup for the scheduler
    
    Args:
        scheduler_name: Name of the scheduler
        log_level: Logging level
        enable_file_logging: Whether to enable file logging
        
    Returns:
        Tuple of (main_logger, metrics_logger)
    """
    
    # Generate log file path if file logging is enabled
    log_file = None
    if enable_file_logging:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"logs/scheduler_optimization_{timestamp}.log"
    
    # Setup main logger
    main_logger = setup_enhanced_logging(
        log_level=log_level,
        log_file=log_file,
        console_output=True
    )
    
    # Create metrics logger
    metrics_logger = SchedulingMetricsLogger(main_logger)
    
    return main_logger, metrics_logger


# Global logger instances for easy access
_global_logger = None
_global_metrics_logger = None


def get_scheduler_logger() -> logging.Logger:
    """Get the global scheduler logger"""
    global _global_logger
    if _global_logger is None:
        _global_logger, _ = create_scheduler_logger()
    return _global_logger


def get_metrics_logger() -> SchedulingMetricsLogger:
    """Get the global metrics logger"""
    global _global_metrics_logger
    if _global_metrics_logger is None:
        _, _global_metrics_logger = create_scheduler_logger()
    return _global_metrics_logger