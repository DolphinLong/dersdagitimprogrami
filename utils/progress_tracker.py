"""
Scheduler Progress Tracker
Manages real-time updates and progress reporting for schedulers
"""
import time
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProgressUpdate:
    """Data class for progress updates"""
    percentage: int
    message: str
    timestamp: datetime
    data: Optional[Dict[str, Any]] = None


class SchedulerProgressTracker:
    """
    Tracks scheduler progress and sends updates to UI components
    """
    
    def __init__(self):
        self.callbacks: List[Callable[[ProgressUpdate], None]] = []
        self.start_time = None
        self.last_update_time = None
        self.min_update_interval = 0.1  # Minimum interval between updates (in seconds)
        
    def add_callback(self, callback: Callable[[ProgressUpdate], None]):
        """Add a callback to be called on progress updates"""
        if callback not in self.callbacks:
            self.callbacks.append(callback)
        
    def remove_callback(self, callback: Callable[[ProgressUpdate], None]):
        """Remove a callback from the list"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
        
    def start_tracking(self):
        """Start tracking progress"""
        self.start_time = time.time()
        self.last_update_time = self.start_time
        
    def send_update(self, percentage: int, message: str, data: Optional[Dict[str, Any]] = None):
        """
        Send a progress update to all registered callbacks
        
        Args:
            percentage: Progress percentage (0-100)
            message: Progress message
            data: Optional additional data to pass to callbacks
        """
        current_time = time.time()
        
        # Throttle updates to avoid overwhelming the UI
        if (current_time - self.last_update_time) < self.min_update_interval:
            return
            
        update = ProgressUpdate(
            percentage=min(100, max(0, percentage)),  # Clamp between 0-100
            message=message,
            timestamp=datetime.now(),
            data=data
        )
        
        self.last_update_time = current_time
        
        # Call all registered callbacks
        for callback in self.callbacks:
            try:
                callback(update)
            except Exception as e:
                print(f"Error in progress callback: {e}")
                
    def finish_tracking(self, success: bool = True, final_message: str = ""):
        """Finish tracking and send final update"""
        if success:
            self.send_update(100, final_message or "Schedule generation completed successfully!")
        else:
            self.send_update(100, final_message or "Schedule generation completed with issues.")
            
    def get_elapsed_time(self) -> float:
        """Get the elapsed time since tracking started"""
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time


# Global instance of the progress tracker
_scheduler_progress_tracker = SchedulerProgressTracker()


def get_global_progress_tracker() -> SchedulerProgressTracker:
    """Get the global progress tracker instance"""
    return _scheduler_progress_tracker


def track_scheduler_progress(percentage: int, message: str, data: Optional[Dict[str, Any]] = None):
    """Convenience function to send progress updates to the global tracker"""
    _scheduler_progress_tracker.send_update(percentage, message, data)