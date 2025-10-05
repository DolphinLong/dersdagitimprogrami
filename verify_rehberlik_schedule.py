"""
Script to verify that Rehberlik ve Yönlendirme lessons are properly scheduled
"""

from database import db_manager

def verify_rehberlik_schedule():
    """Verify that Rehberlik ve Yönlendirme lessons are properly scheduled"""
    
    print("VERIFYING REHBERLİK VE YÖNLENDİRME LESSON SCHEDULES")
    print("=" * 60)
    
    # Get all lessons
    lessons = db_manager.get_all_lessons()
    
    # Find the Rehberlik lesson
    rehberlik_lesson = None
    for lesson in lessons:
        if "Rehberlik" in lesson.name and "Yönlendirme" in lesson.name:
            rehberlik_lesson = lesson
            break
    
    if not rehberlik_lesson:
        print("Rehberlik ve Yönlendirme lesson not found in the database.")
        return
    
    print(f"Found lesson: {rehberlik_lesson.name}")
    print(f"Weekly hours: {rehberlik_lesson.weekly_hours}")
    print()
    
    # Get all schedule entries for this lesson
    # We need to get all schedule entries and filter by lesson_id
    all_entries = db_manager.get_schedule_by_school_type()
    
    # Filter for Rehberlik lesson entries
    rehberlik_entries = [entry for entry in all_entries if entry.lesson_id == rehberlik_lesson.lesson_id]
    
    print(f"Total Rehberlik schedule entries: {len(rehberlik_entries)}")
    print()
    
    if rehberlik_entries:
        # Get class and teacher information for each entry
        print("Scheduled Rehberlik Lessons:")
        print("-" * 50)
        
        for entry in rehberlik_entries:
            # Get class information
            class_info = db_manager.get_class_by_id(entry.class_id)
            # Get teacher information
            teacher_info = db_manager.get_teacher_by_id(entry.teacher_id)
            
            # Day mapping
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            day_name = days[entry.day] if 0 <= entry.day < len(days) else f"Day {entry.day}"
            
            print(f"Class: {class_info.name if class_info else 'Unknown'}")
            print(f"  Teacher: {teacher_info.name if teacher_info else 'Unknown'}")
            print(f"  Time: {day_name}, Slot {entry.time_slot}")
            print(f"  Entry ID: {entry.entry_id}")
            print()
    else:
        print("No schedule entries found for Rehberlik ve Yönlendirme lessons.")
    
    # Verify that each class has exactly one Rehberlik lesson scheduled
    print("VERIFICATION BY CLASS:")
    print("-" * 30)
    
    classes = db_manager.get_all_classes()
    for cls in classes:
        # Get all schedule entries for this class
        class_entries = db_manager.get_schedule_for_specific_class(cls.class_id)
        
        # Filter for Rehberlik lesson entries
        class_rehberlik_entries = [entry for entry in class_entries if entry.lesson_id == rehberlik_lesson.lesson_id]
        
        if len(class_rehberlik_entries) == 1:
            entry = class_rehberlik_entries[0]
            teacher_info = db_manager.get_teacher_by_id(entry.teacher_id)
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            day_name = days[entry.day] if 0 <= entry.day < len(days) else f"Day {entry.day}"
            print(f"✓ {cls.name}: 1 Rehberlik lesson scheduled with {teacher_info.name if teacher_info else 'Unknown'} on {day_name}")
        elif len(class_rehberlik_entries) == 0:
            print(f"✗ {cls.name}: No Rehberlik lesson scheduled")
        else:
            print(f"? {cls.name}: {len(class_rehberlik_entries)} Rehberlik lessons scheduled (unexpected)")

if __name__ == "__main__":
    verify_rehberlik_schedule()
    db_manager.close()