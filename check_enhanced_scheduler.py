"""
Quick diagnostic to check database content after enhanced scheduler
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from database.db_manager import DatabaseManager

def check_database_after_enhanced_scheduler():
    """Check database content after running enhanced scheduler"""
    print("DATABASE CONTENT CHECK AFTER ENHANCED SCHEDULER")
    print("=" * 60)
    
    # Initialize database
    db_manager = DatabaseManager(db_path='schedule.db')
    
    try:
        # Check what's actually in the database
        schedule = db_manager.get_schedule_program_by_school_type()
        print(f"Database schedule entries: {len(schedule)}")
        
        if len(schedule) > 0:
            print("Sample entries:")
            for i, entry in enumerate(schedule[:10]):
                print(f"  {i+1}. Class: {entry.class_id}, Lesson: {entry.lesson_id}, "
                      f"Teacher: {entry.teacher_id}, Day: {entry.day}, Slot: {entry.time_slot}")
        else:
            print("No schedule entries found!")
            
        # Calculate required hours
        classes = db_manager.get_all_classes()
        lessons = db_manager.get_all_lessons()
        assignments = db_manager.get_schedule_by_school_type()
        
        total_required_hours = 0
        for assignment in assignments:
            class_obj = next((c for c in classes if c.class_id == assignment.class_id), None)
            if class_obj:
                weekly_hours = db_manager.get_weekly_hours_for_lesson(assignment.lesson_id, class_obj.grade)
                if weekly_hours:
                    total_required_hours += weekly_hours
        
        print(f"\nSchedule Analysis:")
        print(f"  Total required hours: {total_required_hours}")
        print(f"  Actual scheduled hours: {len(schedule)}")
        if total_required_hours > 0:
            fill_rate = len(schedule) / total_required_hours * 100
            print(f"  Fill rate: {fill_rate:.1f}%")
        
        print(f"\n{'='*60}")
        print("DATABASE CHECK COMPLETE")
        print(f"{'='*60}")
        
        return len(schedule)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 0
    finally:
        db_manager.close()

if __name__ == "__main__":
    check_database_after_enhanced_scheduler()