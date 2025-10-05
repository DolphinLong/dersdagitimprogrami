"""
Check teacher distribution in the database
"""

from database.db_manager import DatabaseManager

db_manager = DatabaseManager()

def check_teacher_distribution():
    """Check how many teachers we have for each subject"""
    print("=== Teacher Distribution Check ===")
    
    # Get all teachers
    teachers = db_manager.get_all_teachers()
    
    print(f"Total teachers from get_all_teachers: {len(teachers)}")
    
    # Also check directly from database using thread-safe approach
    try:
        # Use the thread-safe connection approach
        if db_manager._ensure_connection():
            conn = db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM teachers")
            total_teachers = cursor.fetchone()[0]
            print(f"Total teachers in database: {total_teachers}")
            
            cursor.execute("SELECT * FROM teachers LIMIT 5")
            rows = cursor.fetchall()
            print("Sample teachers from database:")
            for row in rows:
                print(f"  ID: {row['teacher_id']}, Name: {row['name']}, Subject: {row['subject']}, School Type: {row['school_type']}")
    except Exception as e:
        print(f"Error accessing database directly: {e}")
    
    # Group teachers by subject
    teachers_by_subject = {}
    for teacher in teachers:
        if teacher.subject not in teachers_by_subject:
            teachers_by_subject[teacher.subject] = []
        teachers_by_subject[teacher.subject].append(teacher.name)
    
    print(f"\nTeachers by subject:")
    for subject in sorted(teachers_by_subject.keys()):
        teacher_names = teachers_by_subject[subject]
        print(f"  {subject}: {len(teacher_names)} teacher(s)")
        # Print first few teacher names
        if len(teacher_names) <= 5:
            print(f"    Teachers: {', '.join(teacher_names)}")
        else:
            print(f"    Teachers: {', '.join(teacher_names[:5])}...")

if __name__ == "__main__":
    # Make sure we're using Ortaokul (since that's what we set in the database)
    db_manager.set_school_type("Ortaokul")
    check_teacher_distribution()
    db_manager.close()