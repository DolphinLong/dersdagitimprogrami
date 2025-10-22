"""
Database analyzer to check real data inconsistencies
Corrected version with proper table names
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
    try:
        cursor.execute("SELECT COUNT(*) FROM classes;")
        class_count = cursor.fetchone()[0]
        print(f"Classes: {class_count}")
    except sqlite3.Error as e:
        print(f"Error getting class count: {e}")
    
    # Check teacher count
    try:
        cursor.execute("SELECT COUNT(*) FROM teachers;")
        teacher_count = cursor.fetchone()[0]
        print(f"Teachers: {teacher_count}")
    except sqlite3.Error as e:
        print(f"Error getting teacher count: {e}")
    
    # Check lesson count
    try:
        cursor.execute("SELECT COUNT(*) FROM lessons;")
        lesson_count = cursor.fetchone()[0]
        print(f"Lessons: {lesson_count}")
    except sqlite3.Error as e:
        print(f"Error getting lesson count: {e}")
    
    # Check schedule assignments
    try:
        cursor.execute("SELECT COUNT(*) FROM schedule_assignments;")
        assignment_count = cursor.fetchone()[0]
        print(f"Schedule assignments: {assignment_count}")
    except sqlite3.Error as e:
        print(f"Error getting schedule assignment count: {e}")
    
    # Check existing schedule entries
    try:
        cursor.execute("SELECT COUNT(*) FROM schedule_program;")
        schedule_count = cursor.fetchone()[0]
        print(f"Schedule program entries: {schedule_count}")
    except sqlite3.Error as e:
        print(f"Error getting schedule program count: {e}")
    
    # Check required hours per assignment
    print("\nREQUIRED HOURS ANALYSIS")
    print("-" * 30)
    try:
        cursor.execute("""
            SELECT sa.class_id, sa.lesson_id, c.grade, COUNT(*) as entries
            FROM schedule_assignments sa
            JOIN classes c ON sa.class_id = c.class_id
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
    except sqlite3.Error as e:
        print(f"Error in required hours analysis: {e}")
    
    # Check teacher availability
    print("\nTEACHER AVAILABILITY ANALYSIS")
    print("-" * 30)
    try:
        cursor.execute("SELECT COUNT(*) FROM teacher_availability;")
        availability_count = cursor.fetchone()[0]
        print(f"Teacher availability records: {availability_count}")
    except sqlite3.Error as e:
        print(f"Error getting teacher availability count: {e}")
    
    # Check for teachers with very limited availability
    try:
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
    except sqlite3.Error as e:
        print(f"Error getting teacher availability analysis: {e}")
    
    conn.close()

if __name__ == "__main__":
    analyze_database()