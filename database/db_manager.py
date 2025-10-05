import sqlite3
import os
import logging
from database.models import User, Teacher, Class, Classroom, Lesson, ScheduleEntry, Curriculum
from typing import Optional, List, Union
import threading
import json

class DatabaseManager:
    """Manages database operations for the application"""

    def __init__(self, db_path="schedule.db"):
        self.db_path = db_path
        self.local = threading.local()  # Thread-local storage for connections
        self.create_tables()
        self.school_type = self.get_school_type()

    def get_connection(self):
        """Get a thread-local database connection"""
        if not hasattr(self.local, 'connection') or self.local.connection is None:
            self.local.connection = sqlite3.connect(self.db_path)
            self.local.connection.row_factory = sqlite3.Row
            self.local.connection.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        return self.local.connection

    def close_connection(self):
        """Close the thread-local database connection"""
        if hasattr(self.local, 'connection') and self.local.connection is not None:
            self.local.connection.close()
            self.local.connection = None

    def _ensure_connection(self) -> bool:
        """Ensure database connection is active for the current thread"""
        try:
            conn = self.get_connection()
            return conn is not None
        except sqlite3.Error as e:
            logging.error(f"Error ensuring database connection: {e}")
            return False

    def _safe_commit(self) -> bool:
        """Safely commit database changes"""
        if self._ensure_connection():
            try:
                conn = self.get_connection()
                conn.commit()
                return True
            except sqlite3.Error as e:
                logging.error(f"Error committing transaction: {e}")
                return False
        return False

    def get_school_type(self) -> Optional[str]:
        """Get the school type from settings."""
        if not self._ensure_connection():
            return None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT setting_value FROM settings WHERE setting_key = ?", ("school_type",))
            row = cursor.fetchone()
            return row[0] if row else None
        except sqlite3.Error as e:
            logging.error(f"Error getting school type: {e}")
            return None

    def set_school_type(self, school_type: str) -> bool:
        """Set the school type in settings."""
        if not self._ensure_connection():
            return False
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO settings (setting_key, setting_value) VALUES (?, ?)", 
                          ("school_type", school_type))
            return self._safe_commit()
        except sqlite3.Error as e:
            logging.error(f"Error setting school type: {e}")
            return False

    def get_setting(self, key: str) -> Optional[Union[str, dict, list]]:
        """Get a setting value from the database."""
        if not self._ensure_connection():
            return None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT setting_value FROM settings WHERE setting_key = ?", (key,))
            row = cursor.fetchone()
            if row:
                value = row[0]
                try:
                    # Try to decode as JSON
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    # Return as plain string if not JSON
                    return value
            return None
        except sqlite3.Error as e:
            logging.error(f"Error getting setting '{key}': {e}")
            return None

    def set_setting(self, key: str, value: Union[str, dict, list]) -> bool:
        """Set a setting value in the database."""
        if not self._ensure_connection():
            return False
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Serialize to JSON if it's a dict or list
            if isinstance(value, (dict, list)):
                value_to_store = json.dumps(value)
            else:
                value_to_store = str(value)
                
            cursor.execute("INSERT OR REPLACE INTO settings (setting_key, setting_value) VALUES (?, ?)", 
                          (key, value_to_store))
            return self._safe_commit()
        except sqlite3.Error as e:
            logging.error(f"Error setting setting '{key}': {e}")
            return False

    def _get_current_school_type(self, default="Lise") -> str:
        """Get the current school type from settings, returning a default if not set."""
        school_type = self.get_school_type()
        return school_type if school_type else default

    def create_tables(self) -> bool:
        """Create database tables if they don't exist"""
        if not self._ensure_connection():
            return False
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL
                )
            """)
            
            # Teachers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS teachers (
                    teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    school_type TEXT NOT NULL
                )
            """)
            
            # Classes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS classes (
                    class_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    grade INTEGER NOT NULL,
                    school_type TEXT NOT NULL
                )
            """)
            
            # Classrooms table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS classrooms (
                    classroom_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    capacity INTEGER NOT NULL,
                    school_type TEXT NOT NULL
                )
            """)
            
            # Lessons table (stores unique lesson names)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lessons (
                    lesson_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    weekly_hours INTEGER DEFAULT 0,
                    school_type TEXT NOT NULL
                )
            """)

            # Curriculum table (links lessons to grades and hours)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS curriculum (
                    curriculum_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lesson_id INTEGER NOT NULL,
                    grade INTEGER NOT NULL,
                    weekly_hours INTEGER NOT NULL,
                    school_type TEXT NOT NULL,
                    FOREIGN KEY (lesson_id) REFERENCES lessons(lesson_id) ON DELETE CASCADE
                )
            """)
            
            # Schedule entries table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schedule_entries (
                    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    class_id INTEGER NOT NULL,
                    teacher_id INTEGER NOT NULL,
                    lesson_id INTEGER NOT NULL,
                    classroom_id INTEGER NOT NULL,
                    day INTEGER NOT NULL,
                    time_slot INTEGER NOT NULL,
                    school_type TEXT NOT NULL,
                    FOREIGN KEY (class_id) REFERENCES classes(class_id),
                    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id),
                    FOREIGN KEY (lesson_id) REFERENCES lessons(lesson_id),
                    FOREIGN KEY (classroom_id) REFERENCES classrooms(classroom_id)
                )
            """)
            
            # Teacher availability table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS teacher_availability (
                    availability_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    teacher_id INTEGER NOT NULL,
                    day INTEGER NOT NULL,
                    time_slot INTEGER NOT NULL,
                    is_available INTEGER NOT NULL DEFAULT 1,
                    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE CASCADE
                )
            """)
            
            # Settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    setting_key TEXT PRIMARY KEY,
                    setting_value TEXT
                )
            """)
            

            
            conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Error creating tables: {e}")
            return False

    def migrate_existing_data(self):
        """Handle schema migrations. Currently a placeholder."""
        # TODO: Implement a proper data migration strategy.
        pass

    def close(self):
        """Close the database connection"""
        self.close_connection()

    def add_user(self, username: str, password: str, role: str) -> Optional[int]:
        if not self._ensure_connection(): return None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
            if self._safe_commit(): return cursor.lastrowid
            return None
        except sqlite3.Error as e:
            logging.error(f"Error adding user: {e}")
            return None

    def add_lesson(self, name: str, weekly_hours: int = 0) -> Optional[int]:
        """Add a new unique lesson name."""
        if not self._ensure_connection(): return None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            school_type = self._get_current_school_type()
            cursor.execute("INSERT INTO lessons (name, weekly_hours, school_type) VALUES (?, ?, ?)", (name, weekly_hours, school_type))
            lesson_id = None
            if self._safe_commit(): 
                cursor.execute("SELECT lesson_id FROM lessons WHERE name = ?", (name,))
                row = cursor.fetchone()
                lesson_id = row['lesson_id'] if row else None
            return lesson_id
        except sqlite3.Error as e:
            logging.error(f"Error adding lesson: {e}")
            return None

    def get_all_lessons(self) -> List[Lesson]:
        """Get all unique lessons."""
        if not self._ensure_connection(): return []
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM lessons ORDER BY name")
            rows = cursor.fetchall()
            return [Lesson(row['lesson_id'], row['name'], row['weekly_hours']) for row in rows]
        except sqlite3.Error as e:
            logging.error(f"Error getting all lessons: {e}")
            return []

    def update_lesson(self, lesson_id: int, name: str) -> bool:
        """Update a lesson's name."""
        if not self._ensure_connection(): return False
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE lessons SET name = ? WHERE lesson_id = ?", (name, lesson_id))
            result = cursor.rowcount > 0
            return self._safe_commit() and result
        except sqlite3.Error as e:
            logging.error(f"Error updating lesson: {e}")
            return False

    def delete_lesson(self, lesson_id: int) -> bool:
        """Delete a lesson and its associated curriculum entries."""
        if not self._ensure_connection(): return False
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Delete in proper order to avoid foreign key constraint errors
            # 1. Delete from schedule_program (generated schedules)
            cursor.execute("DELETE FROM schedule_program WHERE lesson_id = ?", (lesson_id,))
            
            # 2. Delete from schedule (lesson assignments)
            cursor.execute("DELETE FROM schedule WHERE lesson_id = ?", (lesson_id,))
            
            # 3. Delete from curriculum (lesson curriculum data)
            cursor.execute("DELETE FROM curriculum WHERE lesson_id = ?", (lesson_id,))
            
            # 4. Finally delete the lesson itself
            cursor.execute("DELETE FROM lessons WHERE lesson_id = ?", (lesson_id,))
            
            result = cursor.rowcount > 0
            return self._safe_commit() and result
        except sqlite3.Error as e:
            logging.error(f"Error deleting lesson: {e}")
            return False

    def get_curriculum_for_lesson(self, lesson_id: int) -> List[Curriculum]:
        """Get all curriculum entries for a specific lesson."""
        if not self._ensure_connection(): return []
        school_type = self._get_current_school_type()
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM curriculum WHERE lesson_id = ? AND school_type = ?", (lesson_id, school_type))
            rows = cursor.fetchall()
            return [Curriculum(row['curriculum_id'], row['lesson_id'], row['grade'], row['weekly_hours']) for row in rows]
        except sqlite3.Error as e:
            logging.error(f"Error getting curriculum for lesson {lesson_id}: {e}")
            return []

    def add_or_update_curriculum(self, lesson_id: int, grade: int, weekly_hours: int) -> bool:
        """Add or update a curriculum entry for a lesson at a specific grade."""
        if not self._ensure_connection(): return False
        school_type = self._get_current_school_type()
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT curriculum_id FROM curriculum WHERE lesson_id = ? AND grade = ? AND school_type = ?", (lesson_id, grade, school_type))
            row = cursor.fetchone()
            if row:
                cursor.execute("UPDATE curriculum SET weekly_hours = ? WHERE curriculum_id = ?", (weekly_hours, row['curriculum_id']))
            else:
                cursor.execute("INSERT INTO curriculum (lesson_id, grade, weekly_hours, school_type) VALUES (?, ?, ?, ?)", (lesson_id, grade, weekly_hours, school_type))
            return self._safe_commit()
        except sqlite3.Error as e:
            logging.error(f"Error adding/updating curriculum: {e}")
            return False

    def get_weekly_hours_for_lesson(self, lesson_id: int, grade: int) -> Optional[int]:
        """Get the weekly hours for a specific lesson and grade."""
        if not self._ensure_connection(): return None
        school_type = self._get_current_school_type()
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT weekly_hours FROM curriculum WHERE lesson_id = ? AND grade = ? AND school_type = ?", (lesson_id, grade, school_type))
            row = cursor.fetchone()
            return row['weekly_hours'] if row else None
        except sqlite3.Error as e:
            logging.error(f"Error getting weekly hours: {e}")
            return None

    def get_all_teachers(self) -> List[Teacher]:
        """Get all teachers for the current school type"""
        if not self._ensure_connection():
            return []
        school_type = self._get_current_school_type()
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM teachers WHERE school_type = ?", (school_type,))
            rows = cursor.fetchall()
            return [Teacher(row['teacher_id'], row['name'], row['subject']) for row in rows]
        except sqlite3.Error as e:
            logging.error(f"Error getting all teachers: {e}")
            return []

    def get_all_classes(self) -> List[Class]:
        """Get all classes for the current school type"""
        if not self._ensure_connection():
            return []
        school_type = self._get_current_school_type()
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM classes WHERE school_type = ?", (school_type,))
            rows = cursor.fetchall()
            return [Class(row['class_id'], row['name'], row['grade']) for row in rows]
        except sqlite3.Error as e:
            logging.error(f"Error getting all classes: {e}")
            return []

    def get_schedule_by_school_type(self) -> List[ScheduleEntry]:
        """Get all schedule entries for the current school type (assignments)"""
        if not self._ensure_connection():
            return []
        school_type = self._get_current_school_type()
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT entry_id, class_id, teacher_id, lesson_id, classroom_id, day, time_slot FROM schedule_entries WHERE school_type = ?", (school_type,))
            rows = cursor.fetchall()
            entries = [ScheduleEntry(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
                      for row in rows]
            logging.debug(f"Retrieved {len(entries)} schedule entries for school type: {school_type}")
            return entries
        except sqlite3.Error as e:
            logging.error(f"Error getting schedule entries: {e}")
            return []

    def get_schedule_program_by_school_type(self) -> List[ScheduleEntry]:
        """Get all schedule program for the current school type (timetable)"""
        if not self._ensure_connection():
            return []
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            school_type = self._get_current_school_type()
            cursor.execute("""
                SELECT schedule_id, class_id, teacher_id, lesson_id, classroom_id, day, time_slot
                FROM schedule
                WHERE school_type = ?
            """, (school_type,))
            rows = cursor.fetchall()
            return [ScheduleEntry(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
                   for row in rows]
        except sqlite3.Error as e:
            logging.error(f"Error getting schedule program: {e}")
            return []

    def get_lesson_by_id(self, lesson_id: int) -> Optional[Lesson]:
        """Get a lesson by its ID"""
        if not self._ensure_connection():
            return None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM lessons WHERE lesson_id = ?", (lesson_id,))
            row = cursor.fetchone()
            return Lesson(row['lesson_id'], row['name'], row['weekly_hours']) if row else None
        except sqlite3.Error as e:
            logging.error(f"Error getting lesson by ID: {e}")
            return None
    
    def get_lesson_by_name(self, name: str) -> Optional[Lesson]:
        """Get a lesson by its name"""
        if not self._ensure_connection():
            return None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM lessons WHERE name = ?", (name,))
            row = cursor.fetchone()
            return Lesson(row['lesson_id'], row['name'], row['weekly_hours']) if row else None
        except sqlite3.Error as e:
            logging.error(f"Error getting lesson by name: {e}")
            return None

    def get_teacher_by_id(self, teacher_id: int) -> Optional[Teacher]:
        """Get a teacher by its ID"""
        if not self._ensure_connection():
            return None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM teachers WHERE teacher_id = ?", (teacher_id,))
            row = cursor.fetchone()
            return Teacher(row['teacher_id'], row['name'], row['subject']) if row else None
        except sqlite3.Error as e:
            logging.error(f"Error getting teacher by ID: {e}")
            return None

    def get_class_by_id(self, class_id: int) -> Optional[Class]:
        """Get a class by its ID"""
        if not self._ensure_connection():
            return None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM classes WHERE class_id = ?", (class_id,))
            row = cursor.fetchone()
            return Class(row['class_id'], row['name'], row['grade']) if row else None
        except sqlite3.Error as e:
            logging.error(f"Error getting class by ID: {e}")
            return None

    def get_classroom_by_id(self, classroom_id: int) -> Optional[Classroom]:
        """Get a classroom by its ID"""
        if not self._ensure_connection():
            return None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM classrooms WHERE classroom_id = ?", (classroom_id,))
            row = cursor.fetchone()
            return Classroom(row['classroom_id'], row['name'], row['capacity']) if row else None
        except sqlite3.Error as e:
            logging.error(f"Error getting classroom by ID: {e}")
            return None

    def add_schedule_entry(self, class_id: int, teacher_id: int, lesson_id: int,
                          classroom_id: int, day: int, time_slot: int) -> Optional[int]:
        """Add a new schedule entry to schedule_entries table (assignments)"""
        if not self._ensure_connection():
            return None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            school_type = self._get_current_school_type()
            cursor.execute("""
                INSERT INTO schedule_entries
                (class_id, teacher_id, lesson_id, classroom_id, day, time_slot, school_type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (class_id, teacher_id, lesson_id, classroom_id, day, time_slot, school_type))
            if self._safe_commit():
                logging.debug(f"Added schedule entry: Class {class_id}, Teacher {teacher_id}, Lesson {lesson_id}")
                return cursor.lastrowid
            return None
        except sqlite3.Error as e:
            logging.error(f"Error adding schedule entry: {e}")
            return None

    def add_schedule_program(self, class_id: int, teacher_id: int, lesson_id: int,
                           classroom_id: int, day: int, time_slot: int) -> Optional[int]:
        """Add a new schedule program to schedule table (timetable)"""
        if not self._ensure_connection():
            return None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            school_type = self._get_current_school_type()
            cursor.execute("""
                INSERT INTO schedule
                (class_id, teacher_id, lesson_id, classroom_id, day, time_slot, school_type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (class_id, teacher_id, lesson_id, classroom_id, day, time_slot, school_type))
            if self._safe_commit():
                logging.debug(f"Added schedule program: Class {class_id}, Teacher {teacher_id}, Lesson {lesson_id}, Day {day}, Slot {time_slot}, Classroom {classroom_id}")
                return cursor.lastrowid
            return None
        except sqlite3.Error as e:
            logging.error(f"Error adding schedule program: {e}")
            return None

    def get_schedule_for_specific_class(self, class_id: int) -> List[ScheduleEntry]:
        """Get schedule program for a specific class (from schedule table)"""
        if not self._ensure_connection():
            return []
        school_type = self._get_current_school_type()
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT schedule_id, class_id, teacher_id, lesson_id, classroom_id, day, time_slot
                FROM schedule
                WHERE class_id = ? AND school_type = ?
            """, (class_id, school_type))
            rows = cursor.fetchall()
            return [ScheduleEntry(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
                   for row in rows]
        except sqlite3.Error as e:
            logging.error(f"Error getting schedule program for class: {e}")
            return []

    def get_schedule_for_specific_teacher(self, teacher_id: int) -> List[ScheduleEntry]:
        """Get schedule program for a specific teacher (from schedule table)"""
        if not self._ensure_connection():
            return []
        school_type = self._get_current_school_type()
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT schedule_id, class_id, teacher_id, lesson_id, classroom_id, day, time_slot
                FROM schedule
                WHERE teacher_id = ? AND school_type = ?
            """, (teacher_id, school_type))
            rows = cursor.fetchall()
            return [ScheduleEntry(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
                   for row in rows]
        except sqlite3.Error as e:
            logging.error(f"Error getting schedule program for teacher: {e}")
            return []

    def update_schedule_entry(self, entry_id: int, class_id: int, teacher_id: int, 
                             lesson_id: int, classroom_id: int, day: int, time_slot: int) -> bool:
        """Update an existing schedule entry"""
        if not self._ensure_connection():
            return False
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE schedule_entries 
                SET class_id = ?, teacher_id = ?, lesson_id = ?, classroom_id = ?, day = ?, time_slot = ?
                WHERE entry_id = ?
            """, (class_id, teacher_id, lesson_id, classroom_id, day, time_slot, entry_id))
            result = cursor.rowcount > 0
            return self._safe_commit() and result
        except sqlite3.Error as e:
            logging.error(f"Error updating schedule entry: {e}")
            return False

    def delete_teacher(self, teacher_id: int) -> bool:
        """Delete a teacher and all related records"""
        if not self._ensure_connection():
            return False
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Delete related schedule entries first
            cursor.execute("DELETE FROM schedule_entries WHERE teacher_id = ?", (teacher_id,))
            
            # Delete related teacher availability records
            cursor.execute("DELETE FROM teacher_availability WHERE teacher_id = ?", (teacher_id,))
            

            
            # Finally, delete the teacher
            cursor.execute("DELETE FROM teachers WHERE teacher_id = ?", (teacher_id,))
            result = cursor.rowcount > 0
            
            return self._safe_commit() and result
        except sqlite3.Error as e:
            logging.error(f"Error deleting teacher: {e}")
            return False

    def delete_schedule_entry(self, entry_id: int) -> bool:
        """Delete a single schedule entry by entry_id"""
        if not self._ensure_connection():
            return False
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            school_type = self._get_current_school_type()

            # Delete the specific schedule entry for the current school type
            cursor.execute(
                "DELETE FROM schedule_entries WHERE entry_id = ? AND school_type = ?", 
                (entry_id, school_type)
            )
            deleted_count = cursor.rowcount

            if self._safe_commit() and deleted_count > 0:
                logging.info(f"Deleted schedule entry {entry_id} for school type: {school_type}")
                return True
            return False
        except sqlite3.Error as e:
            logging.error(f"Error deleting schedule entry {entry_id}: {e}")
            return False

    def delete_all_schedule_entries(self) -> bool:
        """Delete all schedule entries for the current school type"""
        if not self._ensure_connection():
            return False
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            school_type = self._get_current_school_type()

            # Delete all schedule entries for the current school type
            cursor.execute("DELETE FROM schedule_entries WHERE school_type = ?", (school_type,))
            deleted_count = cursor.rowcount
            result = cursor.rowcount >= 0  # Allow 0 rows to be deleted

            if self._safe_commit() and result:
                logging.info(f"Deleted {deleted_count} schedule entries for school type: {school_type}")
                return True
            return result
        except sqlite3.Error as e:
            logging.error(f"Error deleting all schedule entries: {e}")
            return False

    def clear_schedule(self) -> bool:
        """Clear only the schedule table (not assignments)"""
        if not self._ensure_connection():
            return False
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            school_type = self._get_current_school_type()

            # Delete only from schedule table (keep assignments in schedule_entries)
            cursor.execute("DELETE FROM schedule WHERE school_type = ?", (school_type,))
            deleted_count = cursor.rowcount
            result = cursor.rowcount >= 0  # Allow 0 rows to be deleted

            if self._safe_commit() and result:
                logging.info(f"Cleared {deleted_count} schedule entries for school type: {school_type}")
                return True
            return result
        except sqlite3.Error as e:
            logging.error(f"Error clearing schedule: {e}")
            return False

    def delete_class(self, class_id: int) -> bool:
        """Delete a class"""
        if not self._ensure_connection():
            return False
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM classes WHERE class_id = ?", (class_id,))
            result = cursor.rowcount > 0
            return self._safe_commit() and result
        except sqlite3.Error as e:
            logging.error(f"Error deleting class: {e}")
            return False

    def add_teacher(self, name: str, subject: str) -> Optional[int]:
        """Add a new teacher"""
        if not self._ensure_connection():
            return None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            school_type = self._get_current_school_type()
            cursor.execute("INSERT INTO teachers (name, subject, school_type) VALUES (?, ?, ?)", 
                          (name, subject, school_type))
            if self._safe_commit():
                return cursor.lastrowid
            return None
        except sqlite3.Error as e:
            logging.error(f"Error adding teacher: {e}")
            return None

    def update_teacher(self, teacher_id: int, name: str, subject: str) -> bool:
        """Update an existing teacher"""
        if not self._ensure_connection():
            return False
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE teachers SET name = ?, subject = ? WHERE teacher_id = ?", 
                          (name, subject, teacher_id))
            result = cursor.rowcount > 0
            return self._safe_commit() and result
        except sqlite3.Error as e:
            logging.error(f"Error updating teacher: {e}")
            return False

    def add_class(self, name: str, grade: int) -> Optional[int]:
        """Add a new class"""
        if not self._ensure_connection():
            return None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            school_type = self._get_current_school_type()
            cursor.execute("INSERT INTO classes (name, grade, school_type) VALUES (?, ?, ?)", 
                          (name, grade, school_type))
            if self._safe_commit():
                return cursor.lastrowid
            return None
        except sqlite3.Error as e:
            logging.error(f"Error adding class: {e}")
            return None

    def update_class(self, class_id: int, name: str, grade: int) -> bool:
        """Update an existing class"""
        if not self._ensure_connection():
            return False
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE classes SET name = ?, grade = ? WHERE class_id = ?", 
                          (name, grade, class_id))
            result = cursor.rowcount > 0
            return self._safe_commit() and result
        except sqlite3.Error as e:
            logging.error(f"Error updating class: {e}")
            return False

    def get_teacher_availability(self, teacher_id: int) -> List[dict]:
        """Get teacher availability data"""
        if not self._ensure_connection():
            return []
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT day, time_slot, is_available 
                FROM teacher_availability 
                WHERE teacher_id = ?
            """, (teacher_id,))
            rows = cursor.fetchall()
            return [{'day': row['day'], 'time_slot': row['time_slot'], 'is_available': row['is_available']} 
                   for row in rows]
        except sqlite3.Error as e:
            logging.error(f"Error getting teacher availability: {e}")
            return []

    def set_teacher_availability(self, teacher_id: int, day: int, time_slot: int, is_available: bool) -> bool:
        """Set teacher availability for a specific day and time slot"""
        if not self._ensure_connection():
            return False
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            # First try to update existing record
            cursor.execute("""
                UPDATE teacher_availability 
                SET is_available = ? 
                WHERE teacher_id = ? AND day = ? AND time_slot = ?
            """, (1 if is_available else 0, teacher_id, day, time_slot))
            
            # If no rows were updated, insert a new record
            if cursor.rowcount == 0:
                cursor.execute("""
                    INSERT INTO teacher_availability (teacher_id, day, time_slot, is_available)
                    VALUES (?, ?, ?, ?)
                """, (teacher_id, day, time_slot, 1 if is_available else 0))
            
            return self._safe_commit()
        except sqlite3.Error as e:
            logging.error(f"Error setting teacher availability: {e}")
            return False

    def is_teacher_available(self, teacher_id: int, day: int, time_slot: int) -> bool:
        """Check if a teacher is available at a specific day and time slot"""
        if not self._ensure_connection():
            return True  # Default to available if there's a connection issue
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT is_available 
                FROM teacher_availability 
                WHERE teacher_id = ? AND day = ? AND time_slot = ?
            """, (teacher_id, day, time_slot))
            row = cursor.fetchone()
            # If no record exists, teacher is available by default
            return row['is_available'] == 1 if row else True
        except sqlite3.Error as e:
            logging.error(f"Error checking teacher availability: {e}")
            return True  # Default to available if there's an error

    def get_all_classrooms(self) -> List[Classroom]:
        """Get all classrooms for the current school type"""
        if not self._ensure_connection():
            return []
        school_type = self._get_current_school_type()
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM classrooms WHERE school_type = ?", (school_type,))
            rows = cursor.fetchall()
            classrooms = [Classroom(row['classroom_id'], row['name'], row['capacity']) for row in rows]
            logging.debug(f"Retrieved {len(classrooms)} classrooms for school type: {school_type}")
            return classrooms
        except sqlite3.Error as e:
            logging.error(f"Error getting all classrooms: {e}")
            return []

    def get_user(self, username: str, password: str) -> Optional[User]:
        """Get a user by username and password"""
        if not self._ensure_connection():
            return None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            row = cursor.fetchone()
            return User(row['user_id'], row['username'], row['password'], row['role']) if row else None
        except sqlite3.Error as e:
            logging.error(f"Error getting user: {e}")
            return None

    def add_classroom(self, name: str, capacity: int) -> Optional[int]:
        """Add a new classroom"""
        if not self._ensure_connection():
            return None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            school_type = self._get_current_school_type()
            cursor.execute("INSERT INTO classrooms (name, capacity, school_type) VALUES (?, ?, ?)", 
                          (name, capacity, school_type))
            if self._safe_commit():
                return cursor.lastrowid
            return None
        except sqlite3.Error as e:
            logging.error(f"Error adding classroom: {e}")
            return None

    def get_all_curriculum(self) -> List[Curriculum]:
        """Get all curriculum entries for the current school type."""
        if not self._ensure_connection():
            return []
        school_type = self._get_current_school_type()
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM curriculum WHERE school_type = ?", (school_type,))
            rows = cursor.fetchall()
            return [Curriculum(row['curriculum_id'], row['lesson_id'], row['grade'], row['weekly_hours']) for row in rows]
        except sqlite3.Error as e:
            logging.error(f"Error getting all curriculum: {e}")
            return []

    def find_missing_assignments(self) -> dict:
        """
        Find missing lesson assignments for all classes.
        Returns a dictionary with structure:
        {
            class_id: {
                'class': Class object,
                'missing_lessons': [(lesson_id, lesson_name, weekly_hours), ...]
            }
        }
        """
        if not self._ensure_connection():
            return {}
        
        result = {}
        
        # Get all classes
        all_classes = self.get_all_classes()
        
        # Get all curriculum entries
        all_curriculum = self.get_all_curriculum()
        
        # Get all current assignments
        all_assignments = self.get_schedule_by_school_type()
        
        # Create a set of (class_id, lesson_id) for quick lookup
        assigned_combinations = set()
        for assignment in all_assignments:
            assigned_combinations.add((assignment.class_id, assignment.lesson_id))
        
        # For each class, find missing lessons
        for class_obj in all_classes:
            missing_lessons = []
            
            # Get curriculum for this grade
            grade_curriculum = [c for c in all_curriculum if c.grade == class_obj.grade]
            
            for curriculum_entry in grade_curriculum:
                # Check if this lesson is assigned to this class
                if (class_obj.class_id, curriculum_entry.lesson_id) not in assigned_combinations:
                    # This lesson is missing
                    lesson = self.get_lesson_by_id(curriculum_entry.lesson_id)
                    if lesson:
                        missing_lessons.append((
                            curriculum_entry.lesson_id,
                            lesson.name,
                            curriculum_entry.weekly_hours
                        ))
            
            if missing_lessons:
                result[class_obj.class_id] = {
                    'class': class_obj,
                    'missing_lessons': missing_lessons
                }
        
        return result

    def auto_fill_assignments(self) -> dict:
        """
        Automatically fill missing lesson assignments.
        Tries to match teachers by subject.
        Returns a dictionary with assignment results:
        {
            'success': [(class_name, lesson_name, teacher_name), ...],
            'failed': [(class_name, lesson_name, reason), ...]
        }
        """
        if not self._ensure_connection():
            return {'success': [], 'failed': []}
        
        result = {'success': [], 'failed': []}
        
        # Find missing assignments
        missing_data = self.find_missing_assignments()
        
        if not missing_data:
            return result
        
        # Get all teachers
        all_teachers = self.get_all_teachers()
        
        # Get all current assignments to calculate teacher workload
        all_assignments = self.get_schedule_by_school_type()
        
        # Calculate workload for each teacher (total weekly hours)
        teacher_workload = {}
        for teacher in all_teachers:
            total_hours = 0
            for assignment in all_assignments:
                if assignment.teacher_id == teacher.teacher_id:
                    # Get the class to determine grade
                    class_obj = self.get_class_by_id(assignment.class_id)
                    if class_obj:
                        # Get weekly hours for this lesson
                        weekly_hours = self.get_weekly_hours_for_lesson(assignment.lesson_id, class_obj.grade)
                        if weekly_hours:
                            total_hours += weekly_hours
            teacher_workload[teacher.teacher_id] = total_hours
        
        # Default classroom (assuming ID 1 exists)
        default_classroom_id = 1
        
        # For each class with missing lessons
        for class_id, data in missing_data.items():
            class_obj = data['class']
            missing_lessons = data['missing_lessons']
            
            for lesson_id, lesson_name, weekly_hours in missing_lessons:
                # Try to find a suitable teacher
                # Match by subject name (e.g., "Matematik" lesson needs "Matematik" teacher)
                suitable_teachers = [t for t in all_teachers if t.subject.lower() in lesson_name.lower() or lesson_name.lower() in t.subject.lower()]
                
                if not suitable_teachers:
                    # No exact match, try more flexible matching
                    # For example, "Fen Bilimleri" could match "Fen" or "Fizik" teachers
                    for teacher in all_teachers:
                        # Check if any word from lesson name is in teacher's subject
                        lesson_words = lesson_name.lower().split()
                        subject_words = teacher.subject.lower().split()
                        if any(word in subject_words for word in lesson_words if len(word) > 3):
                            suitable_teachers.append(teacher)
                            break
                
                if suitable_teachers:
                    # DENGELI DAĞITIM: En az yüklü öğretmeni seç
                    # Öğretmenleri yüke göre sırala (en az yüklü önce)
                    suitable_teachers.sort(key=lambda t: teacher_workload.get(t.teacher_id, 0))
                    teacher = suitable_teachers[0]
                    
                    # Create assignment (day=-1, time_slot=-1 means not yet scheduled)
                    entry_id = self.add_schedule_entry(
                        class_id,
                        teacher.teacher_id,
                        lesson_id,
                        default_classroom_id,
                        -1,  # Not yet scheduled to a specific day
                        -1   # Not yet scheduled to a specific time slot
                    )
                    
                    if entry_id:
                        # Öğretmen yükünü güncelle (dengeli dağıtım için)
                        teacher_workload[teacher.teacher_id] = teacher_workload.get(teacher.teacher_id, 0) + weekly_hours
                        result['success'].append((class_obj.name, lesson_name, teacher.name))
                        logging.info(f"Auto-assigned {lesson_name} to {class_obj.name} with teacher {teacher.name} (yük: {teacher_workload[teacher.teacher_id]} saat)")
                    else:
                        result['failed'].append((class_obj.name, lesson_name, "Veritabanı hatası"))
                        logging.error(f"Failed to auto-assign {lesson_name} to {class_obj.name}")
                else:
                    # No suitable teacher found
                    result['failed'].append((class_obj.name, lesson_name, "Uygun öğretmen bulunamadı"))
                    logging.warning(f"No suitable teacher found for {lesson_name} in {class_obj.name}")
        
        return result


