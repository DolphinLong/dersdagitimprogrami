"""Check database schema"""
import sqlite3

db_path = 'schedule.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 50)
print("Database Schema Check")
print("=" * 50)

# Get lessons table schema
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='lessons'")
schema = cursor.fetchone()

if schema:
    print("\nLessons table schema:")
    print(schema[0])
else:
    print("\nLessons table not found!")

# Get indexes
cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='lessons'")
indexes = cursor.fetchall()

if indexes:
    print("\nIndexes on lessons table:")
    for idx in indexes:
        print(f"  - {idx[0]}: {idx[1]}")
else:
    print("\nNo indexes on lessons table")

conn.close()
print("\n" + "=" * 50)
