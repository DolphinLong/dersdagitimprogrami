from database import db_manager
import sqlite3

def check_schema():
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    # Check teachers table schema
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='teachers'")
    result = cursor.fetchone()
    if result:
        print("Teachers table schema:")
        print(result[0])
        print()
    
    # Check schedule_entries table schema
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='schedule_entries'")
    result = cursor.fetchone()
    if result:
        print("Schedule entries table schema:")
        print(result[0])
        print()
    
    # Check teacher_availability table schema
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='teacher_availability'")
    result = cursor.fetchone()
    if result:
        print("Teacher availability table schema:")
        print(result[0])
        print()
    
    # Check guidance_counselor_assignments table schema
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='guidance_counselor_assignments'")
    result = cursor.fetchone()
    if result:
        print("Guidance counselor assignments table schema:")
        print(result[0])
        print()

if __name__ == "__main__":
    check_schema()