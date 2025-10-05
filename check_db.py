import sqlite3

# Connect to the database
conn = sqlite3.connect('schedule.db')
cursor = conn.cursor()

# Get all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in the database:")
for table in tables:
    print(f"  - {table[0]}")

# Check the structure of each table
for table in tables:
    table_name = table[0]
    print(f"\nStructure of {table_name}:")
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    for column in columns:
        print(f"  {column[1]} ({column[2]})")

# Check some sample data
print("\nSchool type:", end=" ")
cursor.execute("SELECT setting_value FROM settings WHERE setting_key = 'school_type';")
school_type = cursor.fetchone()
print(school_type[0] if school_type else "Not set")

print("\nTotal teachers:", end=" ")
cursor.execute("SELECT COUNT(*) FROM teachers;")
print(cursor.fetchone()[0])

print("Total classes:", end=" ")
cursor.execute("SELECT COUNT(*) FROM classes;")
print(cursor.fetchone()[0])

print("Total lessons:", end=" ")
cursor.execute("SELECT COUNT(*) FROM lessons;")
print(cursor.fetchone()[0])

print("\n--- Sample Teachers ---")
cursor.execute("SELECT teacher_id, name, subject FROM teachers LIMIT 5;")
teachers = cursor.fetchall()
for teacher in teachers:
    print(f"ID: {teacher[0]}, Name: {teacher[1]}, Subject: {teacher[2]}")

print("\n--- Sample Classes ---")
cursor.execute("SELECT class_id, name, grade FROM classes LIMIT 5;")
classes = cursor.fetchall()
for class_item in classes:
    print(f"ID: {class_item[0]}, Name: {class_item[1]}, Grade: {class_item[2]}")

print("\n--- Sample Lessons ---")
cursor.execute("SELECT lesson_id, name, weekly_hours FROM lessons LIMIT 5;")
lessons = cursor.fetchall()
for lesson in lessons:
    print(f"ID: {lesson[0]}, Name: {lesson[1]}, Hours: {lesson[2]}")

conn.close()