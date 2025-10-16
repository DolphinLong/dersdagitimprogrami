"""Debug lesson adding"""
import sqlite3
import logging

logging.basicConfig(level=logging.DEBUG)

db_path = 'schedule.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

school_type = "Anadolu Lisesi"
name = "Matematik"

print("=" * 50)
print("Direct Database Test")
print("=" * 50)

# Check existing
print(f"\n1. Checking if '{name}' exists for '{school_type}'...")
cursor.execute(
    "SELECT lesson_id, name, school_type FROM lessons WHERE name = ? AND school_type = ?",
    (name, school_type)
)
existing = cursor.fetchone()

if existing:
    print(f"   Found: lesson_id={existing['lesson_id']}, name={existing['name']}, school_type={existing['school_type']}")
else:
    print("   Not found")

# Show all lessons
print(f"\n2. All lessons in database:")
cursor.execute("SELECT lesson_id, name, school_type FROM lessons")
all_lessons = cursor.fetchall()
for lesson in all_lessons:
    print(f"   - ID={lesson['lesson_id']}, Name={lesson['name']}, School={lesson['school_type']}")

conn.close()
print("\n" + "=" * 50)
