#!/usr/bin/env python3
"""
Simple test for OptimizedCurriculumScheduler basic functionality
"""

import time
import logging
from database.db_manager import DatabaseManager
from algorithms.optimized_curriculum_scheduler import OptimizedCurriculumScheduler

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_basic_functionality():
    """Test basic OptimizedCurriculumScheduler functionality"""
    logger.info("Testing OptimizedCurriculumScheduler basic functionality...")
    
    # Initialize database
    db = DatabaseManager()
    
    # Test optimized scheduler
    start_time = time.time()
    
    try:
        optimized_scheduler = OptimizedCurriculumScheduler(db)
        schedule_entries = optimized_scheduler.generate_schedule()
        
        execution_time = time.time() - start_time
        
        logger.info(f"Basic test results:")
        logger.info(f"  Schedule entries: {len(schedule_entries)}")
        logger.info(f"  Execution time: {execution_time:.2f}s")
        logger.info(f"  Success: {len(schedule_entries) > 0}")
        
        # Show first few entries
        if schedule_entries:
            logger.info("First few schedule entries:")
            for i, entry in enumerate(schedule_entries[:5]):
                logger.info(f"  {i+1}: Class {entry.get('class_id')}, Lesson {entry.get('lesson_id')}, Day {entry.get('day')}, Slot {entry.get('time_slot')}")
        
        return len(schedule_entries) > 0
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_basic_functionality()
    logger.info(f"Test result: {'SUCCESS' if success else 'FAILED'}")
    exit(0 if success else 1)