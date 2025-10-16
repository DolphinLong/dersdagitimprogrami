"""Test direct insert"""
import sqlite3
import logging

logging.basicConfig(level=logging.DEBUG)

db_path = 'schedule.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

school_type = "Anadolu Lisesi"
name = "Matematik"
weekly_hours = 5

print("=" * 50)
print("Testing Direct INSERT")
print("=" * 50)

try:
    print(f"\n1. Attempting to INSERT '{name}' for '{school_type}'...")
    cursor.execute(
        "INSERT INTO lessons (name, weekly_hours, school_type) VALUES (?, ?, ?)",
        (name, weekly_hours, school_type)
    )
    conn.commit()
    print("   ✅ INSERT successful!")
    
    # Get the inserted lesson
    cursor.execute(
        "SELECT lesson_id FROM lessons WHERE name = ? AND school_type = ?",
        (name, school_type)
    )
    row = cursor.fetchone()
    if row:
        print(f"   Lesson ID: {row['lesson_id']}")
    
except sqlite3.IntegrityError as e:
    print(f"   ❌ IntegrityError: {e}")
    conn.rollback()
    
    # Try to find existing
    print(f"\n2. Looking for existing lesson...")
    cursor.execute(
        "SELECT lesson_id FROM lessons WHERE name = ? AND school_type = ?",
        (name, school_type)
    )
    row = cursor.fetchone()
    if row:
        print(f"   Found existing: lesson_id={row['lesson_id']}")
    else:
        print("   No existing lesson found!")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    conn.rollback()

conn.close()
print("\n" + "=" * 50)
