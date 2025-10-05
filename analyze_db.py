import sqlite3

# Connect to the database
conn = sqlite3.connect('schedule.db')
cursor = conn.cursor()

# Check for duplicate entries
print("=== Duplicate Lessons Analysis ===")
cursor.execute("""
    SELECT name, COUNT(*) as count 
    FROM lessons 
    GROUP BY name 
    HAVING COUNT(*) > 1
    ORDER BY count DESC;
""")
duplicates = cursor.fetchall()
if duplicates:
    for dup in duplicates:
        print(f"  {dup[0]}: {dup[1]} entries")
else:
    print("  No duplicate lessons found")

print("\n=== Lessons by School Type ===")
cursor.execute("""
    SELECT school_type, COUNT(*) as count 
    FROM lessons 
    GROUP BY school_type;
""")
school_types = cursor.fetchall()
for st in school_types:
    print(f"  {st[0]}: {st[1]} lessons")

print("\n=== All Lessons ===")
cursor.execute("""
    SELECT lesson_id, name, weekly_hours, school_type 
    FROM lessons 
    ORDER BY name, school_type;
""")
lessons = cursor.fetchall()
for lesson in lessons:
    print(f"  ID: {lesson[0]}, Name: {lesson[1]}, Hours: {lesson[2]}, School: {lesson[3]}")

print("\n=== Classes by Grade ===")
cursor.execute("""
    SELECT grade, COUNT(*) as count 
    FROM classes 
    GROUP BY grade 
    ORDER BY grade;
""")
grades = cursor.fetchall()
for grade in grades:
    print(f"  Grade {grade[0]}: {grade[1]} classes")

print("\n=== Schedule Entries ===")
cursor.execute("""
    SELECT COUNT(*) as count 
    FROM schedule_entries;
""")
schedule_count = cursor.fetchone()
print(f"  Total schedule entries: {schedule_count[0]}")

# Show sample schedule entries
print("\n--- Sample Schedule Entries ---")
cursor.execute("""
    SELECT se.entry_id, c.name as class_name, t.name as teacher_name, l.name as lesson_name, 
           cl.name as classroom_name, se.day, se.time_slot
    FROM schedule_entries se
    JOIN classes c ON se.class_id = c.class_id
    JOIN teachers t ON se.teacher_id = t.teacher_id
    JOIN lessons l ON se.lesson_id = l.lesson_id
    JOIN classrooms cl ON se.classroom_id = cl.classroom_id
    ORDER BY c.name, se.day, se.time_slot
    LIMIT 10;
""")
entries = cursor.fetchall()
for entry in entries:
    day_names = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
    day_name = day_names[entry['day']] if entry['day'] < len(day_names) else f"Gün {entry['day']}"
    print(f"  ID: {entry['entry_id']}, Class: {entry['class_name']}, Teacher: {entry['teacher_name']}, "
          f"Lesson: {entry['lesson_name']}, Classroom: {entry['classroom_name']}, "
          f"Day: {day_name}, Time: {entry['time_slot']}")

conn.close()