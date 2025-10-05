"""
Verify MEB subjects in the database
"""

from database import db_manager

def verify_meb_subjects():
    """Verify the MEB subjects in the database"""
    
    print("Verifying MEB subjects in the database...")
    
    # Get current school type
    school_type = db_manager.get_school_type()
    if not school_type:
        print("No school type set.")
        return
    
    print(f"Current school type: {school_type}")
    
    # Get all lessons
    lessons = db_manager.get_all_lessons()
    
    print(f"\nTotal subjects in database: {len(lessons)}")
    
    # Define elective keywords to identify elective subjects
    elective_keywords = [
        "Seçmeli", "Dijital", "Finansal", "Uygulamaları", "İtalyanca", 
        "Japonca", "Robotik", "Yapay Zeka", "Drama", "Geleneksel",
        "Rehberlik", "İnkılap"
    ]
    
    # Separate mandatory and elective subjects
    mandatory_subjects = []
    elective_subjects = []
    
    for lesson in lessons:
        if any(keyword in lesson.name for keyword in elective_keywords):
            elective_subjects.append(lesson)
        else:
            mandatory_subjects.append(lesson)
    
    # Display mandatory subjects
    print(f"\nMANDATORY SUBJECTS ({len(mandatory_subjects)} subjects):")
    print("=" * 60)
    for lesson in sorted(mandatory_subjects, key=lambda x: x.name):
        print(f"{lesson.name:<45} {lesson.weekly_hours:>2} hours")
    
    # Display elective subjects
    print(f"\nELECTIVE SUBJECTS ({len(elective_subjects)} subjects):")
    print("=" * 60)
    for lesson in sorted(elective_subjects, key=lambda x: x.name):
        print(f"{lesson.name:<45} {lesson.weekly_hours:>2} hours")
    
    print(f"\nSUMMARY:")
    print(f"  Mandatory subjects: {len(mandatory_subjects)}")
    print(f"  Elective subjects:  {len(elective_subjects)}")
    print(f"  Total subjects:     {len(lessons)}")

if __name__ == "__main__":
    verify_meb_subjects()
    db_manager.close()