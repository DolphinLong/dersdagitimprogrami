"""Test lesson adding fix"""
from database.db_manager import DatabaseManager

# Test the fix
db = DatabaseManager('schedule.db')

print("=" * 50)
print("Testing Lesson Adding Fix")
print("=" * 50)

# Get current school type
school_type = db.get_school_type()
print(f"\nCurrent school type: {school_type}")

# Try to add a lesson
print("\n1. Adding 'Matematik' lesson...")
lesson_id = db.add_lesson('Matematik', 5)
print(f"   Result: lesson_id = {lesson_id}")

if lesson_id:
    print("   ✅ SUCCESS: Lesson added or existing lesson found")
else:
    print("   ❌ FAILED: Lesson could not be added")

# Try again (should return existing ID)
print("\n2. Adding 'Matematik' again (should return existing ID)...")
lesson_id2 = db.add_lesson('Matematik', 5)
print(f"   Result: lesson_id = {lesson_id2}")

if lesson_id2:
    print("   ✅ SUCCESS: Existing lesson found")
    if lesson_id == lesson_id2:
        print("   ✅ Same ID returned (correct behavior)")
else:
    print("   ❌ FAILED: Should have returned existing ID")

# Check all lessons
print("\n3. All lessons in database:")
lessons = db.get_all_lessons()
for lesson in lessons:
    print(f"   - {lesson.name} (ID: {lesson.lesson_id}, Hours: {lesson.weekly_hours})")

print("\n" + "=" * 50)
print("Test completed!")
print("=" * 50)
