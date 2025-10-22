"""
Database analyzer to check real data inconsistencies
Fully corrected version with proper table names
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
    
    # Check schedule entries table (might be different name)
    schedule_tables = [t[0] for t in tables if 'schedule' in t[0].lower()]
    print(f"Schedule-related tables: {schedule_tables}")
    
    # Check existing schedule entries
    try:
        cursor.execute("SELECT COUNT(*) FROM schedule_entries;")
        schedule_count = cursor.fetchone()[0]
        print(f"Schedule entries: {schedule_count}")
    except sqlite3.Error as e:
        print(f"Error getting schedule entries count: {e}")
    
    # Check curriculum table
    try:
        cursor.execute("SELECT COUNT(*) FROM curriculum;")
        curriculum_count = cursor.fetchone()[0]
        print(f"Curriculum entries: {curriculum_count}")
    except sqlite3.Error as e:
        print(f"Error getting curriculum count: {e}")
    
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
    
    # Check curriculum requirements
    print("\nCURRICULUM REQUIREMENTS ANALYSIS")
    print("-" * 30)
    try:
        cursor.execute("SELECT * FROM curriculum LIMIT 10;")
        curriculum_rows = cursor.fetchall()
        print("Sample curriculum entries:")
        for row in curriculum_rows:
            print(f"  {row}")
            
        # Get total curriculum hours
        cursor.execute("SELECT SUM(weekly_hours) FROM curriculum;")
        total_curriculum_hours = cursor.fetchone()[0] or 0
        print(f"\nTotal curriculum hours required: {total_curriculum_hours}")
    except sqlite3.Error as e:
        print(f"Error getting curriculum sample: {e}")
    
    # Check class details
    print("\nCLASS DETAILS")
    print("-" * 30)
    try:
        cursor.execute("SELECT class_id, name, grade FROM classes;")
        classes = cursor.fetchall()
        print("Classes:")
        for class_id, name, grade in classes:
            print(f"  Class {class_id}: {name} (Grade {grade})")
    except sqlite3.Error as e:
        print(f"Error getting class details: {e}")
    
    # Check teacher details
    print("\nTEACHER DETAILS")
    print("-" * 30)
    try:
        cursor.execute("SELECT teacher_id, name, subject FROM teachers LIMIT 15;")
        teachers = cursor.fetchall()
        print("Teachers:")
        for teacher_id, name, subject in teachers:
            print(f"  Teacher {teacher_id}: {name} ({subject})")
    except sqlite3.Error as e:
        print(f"Error getting teacher details: {e}")
    
    # Check schedule table
    print("\nSCHEDULE ANALYSIS")
    print("-" * 30)
    try:
        cursor.execute("SELECT COUNT(*) FROM schedule;")
        schedule_count = cursor.fetchone()[0]
        print(f"Schedule entries in 'schedule' table: {schedule_count}")
        
        # Check schedule_entries table
        cursor.execute("SELECT COUNT(*) FROM schedule_entries;")
        schedule_entries_count = cursor.fetchone()[0]
        print(f"Schedule entries in 'schedule_entries' table: {schedule_entries_count}")
        
        # Get sample schedule entries
        cursor.execute("SELECT * FROM schedule LIMIT 5;")
        schedule_samples = cursor.fetchall()
        print("Sample schedule entries:")
        for sample in schedule_samples:
            print(f"  {sample}")
    except sqlite3.Error as e:
        print(f"Error getting schedule analysis: {e}")
    
    # Calculate actual fill rate
    print("\nFILL RATE ANALYSIS")
    print("-" * 30)
    try:
        # Total theoretical capacity (16 classes * 5 days * 7 hours = 560 slots)
        total_capacity = 16 * 5 * 7
        print(f"Total theoretical capacity: {total_capacity} slots")
        
        # Actual scheduled slots
        actual_scheduled = schedule_count if schedule_count > 0 else schedule_entries_count
        print(f"Actually scheduled slots: {actual_scheduled}")
        
        if total_capacity > 0:
            fill_rate = (actual_scheduled / total_capacity) * 100
            print(f"Actual fill rate: {fill_rate:.1f}%")
    except sqlite3.Error as e:
        print(f"Error calculating fill rate: {e}")
    
    conn.close()

if __name__ == "__main__":
    analyze_database()