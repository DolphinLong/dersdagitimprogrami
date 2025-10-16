"""
Migration script to fix lessons table schema
Changes UNIQUE constraint from (name) to (name, school_type)
"""
import sqlite3
import os
from datetime import datetime

db_path = 'schedule.db'
backup_path = f'schedule_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'

print("=" * 60)
print("LESSONS TABLE MIGRATION")
print("=" * 60)

# Backup database
print(f"\n1. Creating backup: {backup_path}")
import shutil
shutil.copy2(db_path, backup_path)
print("   ✅ Backup created")

# Connect to database
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

try:
    print("\n2. Reading existing lessons data...")
    cursor.execute("SELECT * FROM lessons")
    lessons_data = cursor.fetchall()
    print(f"   Found {len(lessons_data)} lessons")
    
    print("\n3. Dropping old lessons table...")
    cursor.execute("DROP TABLE IF EXISTS lessons")
    print("   ✅ Old table dropped")
    
    print("\n4. Creating new lessons table with correct schema...")
    cursor.execute("""
        CREATE TABLE lessons (
            lesson_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            weekly_hours INTEGER DEFAULT 0,
            school_type TEXT NOT NULL,
            UNIQUE(name, school_type)
        )
    """)
    print("   ✅ New table created")
    
    print("\n5. Restoring data...")
    for lesson in lessons_data:
        cursor.execute(
            "INSERT INTO lessons (lesson_id, name, weekly_hours, school_type) VALUES (?, ?, ?, ?)",
            (lesson['lesson_id'], lesson['name'], lesson['weekly_hours'], lesson['school_type'])
        )
    print(f"   ✅ Restored {len(lessons_data)} lessons")
    
    print("\n6. Committing changes...")
    conn.commit()
    print("   ✅ Changes committed")
    
    print("\n7. Verifying new schema...")
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='lessons'")
    schema = cursor.fetchone()
    print("   New schema:")
    print("   " + schema[0].replace("\n", "\n   "))
    
    print("\n8. Testing: Adding 'Matematik' for 'Anadolu Lisesi'...")
    cursor.execute(
        "INSERT INTO lessons (name, weekly_hours, school_type) VALUES (?, ?, ?)",
        ("Matematik", 5, "Anadolu Lisesi")
    )
    conn.commit()
    print("   ✅ Test insert successful!")
    
    # Verify
    cursor.execute("SELECT * FROM lessons WHERE name = 'Matematik'")
    matematik_lessons = cursor.fetchall()
    print(f"\n   All 'Matematik' lessons:")
    for lesson in matematik_lessons:
        print(f"   - ID={lesson['lesson_id']}, School={lesson['school_type']}, Hours={lesson['weekly_hours']}")
    
    print("\n" + "=" * 60)
    print("✅ MIGRATION SUCCESSFUL!")
    print("=" * 60)
    print(f"\nBackup saved at: {backup_path}")
    print("You can delete the backup if everything works correctly.")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nRolling back...")
    conn.rollback()
    print(f"Please restore from backup: {backup_path}")
    
finally:
    conn.close()
