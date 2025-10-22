"""
Database analyzer to check real data inconsistencies
"""
import sqlite3
import os

def analyze_database():
    """Analyze the database for inconsistencies"""
    db_path = 'schedule.db'
    
    if not os.path.exists(db_path):
        print("Database file not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("DATABASE ANALYSIS")
    print("=" * 50)
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables: {[t[0] for t in tables]}")
    
    # Check class count
    cursor.execute("SELECT COUNT(*) FROM class;")
    class_count = cursor.fetchone()[0]
    print(f"Classes: {class_count}")
    
    # Check teacher count
    cursor.execute("SELECT COUNT(*) FROM teacher;")
    teacher_count = cursor.fetchone()[0]
    print(f"Teachers: {teacher_count}")
    
    # Check lesson count
    cursor.execute("SELECT COUNT(*) FROM lesson;")
    lesson_count = cursor.fetchone()[0]
    print(f"Lessons: {lesson_count}")
    
    # Check schedule assignments
    cursor.execute("SELECT COUNT(*) FROM schedule_assignment;")
    assignment_count = cursor.fetchone()[0]
    print(f"Schedule assignments: {assignment_count}")
    
    # Check existing schedule entries
    cursor.execute("SELECT COUNT(*) FROM schedule_program;")
    schedule_count = cursor.fetchone()[0]
    print(f"Schedule program entries: {schedule_count}")
    
    # Check required hours per assignment
    print("\nREQUIRED HOURS ANALYSIS")
    print("-" * 30)
    cursor.execute("""
        SELECT sa.class_id, sa.lesson_id, c.grade, COUNT(*) as entries
        FROM schedule_assignment sa
        JOIN class c ON sa.class_id = c.class_id
        GROUP BY sa.class_id, sa.lesson_id, c.grade
        ORDER BY sa.class_id, sa.lesson_id;
    """)
    
    assignments = cursor.fetchall()
    total_required_hours = 0
    
    for class_id, lesson_id, grade, count in assignments:
        # Get weekly hours for this lesson and grade
        cursor.execute("""
            SELECT weekly_hours FROM lesson_curriculum 
            WHERE lesson_id = ? AND grade = ?;
        """, (lesson_id, grade))
        
        result = cursor.fetchone()
        weekly_hours = result[0] if result else 0
        
        print(f"Class {class_id} - Lesson {lesson_id} (Grade {grade}): {weekly_hours} hours")
        total_required_hours += weekly_hours
    
    print(f"\nTotal required hours: {total_required_hours}")
    print(f"Current schedule entries: {schedule_count}")
    if total_required_hours > 0:
        fill_rate = (schedule_count / total_required_hours) * 100
        print(f"Fill rate: {fill_rate:.1f}%")
    
    # Check teacher availability
    print("\nTEACHER AVAILABILITY ANALYSIS")
    print("-" * 30)
    cursor.execute("SELECT teacher_id, day, time_slot FROM teacher_availability;")
    availabilities = cursor.fetchall()
    print(f"Teacher availability records: {len(availabilities)}")
    
    # Check for teachers with very limited availability
    cursor.execute("""
        SELECT teacher_id, COUNT(*) as available_slots
        FROM teacher_availability
        GROUP BY teacher_id
        ORDER BY available_slots ASC;
    """)
    
    teacher_slots = cursor.fetchall()
    print("Teachers by available slots (ascending):")
    for teacher_id, slots in teacher_slots[:10]:  # Top 10 with least availability
        print(f"  Teacher {teacher_id}: {slots} slots")
    
    # Check for classes with missing assignments
    print("\nCLASS ASSIGNMENT ANALYSIS")
    print("-" * 30)
    cursor.execute("SELECT DISTINCT class_id FROM schedule_assignment;")
    assigned_classes = {row[0] for row in cursor.fetchall()}
    
    cursor.execute("SELECT class_id FROM class;")
    all_classes = {row[0] for row in cursor.fetchall()}
    
    unassigned_classes = all_classes - assigned_classes
    print(f"Classes with assignments: {len(assigned_classes)}")
    print(f"Total classes: {len(all_classes)}")
    if unassigned_classes:
        print(f"Unassigned classes: {unassigned_classes}")
    
    # Check for lessons with missing assignments
    cursor.execute("SELECT DISTINCT lesson_id FROM schedule_assignment;")
    assigned_lessons = {row[0] for row in cursor.fetchall()}
    
    cursor.execute("SELECT lesson_id FROM lesson;")
    all_lessons = {row[0] for row in cursor.fetchall()}
    
    unassigned_lessons = all_lessons - assigned_lessons
    print(f"Lessons with assignments: {len(assigned_lessons)}")
    print(f"Total lessons: {len(all_lessons)}")
    if unassigned_lessons:
        print(f"Unassigned lessons: {unassigned_lessons}")
    
    conn.close()

if __name__ == "__main__":
    analyze_database()