import binascii
import hashlib
import json
import logging
import os
import secrets
import sqlite3
import threading
from typing import List, Optional, Union

from database.models import Class, Classroom, Curriculum, Lesson, ScheduleEntry, Teacher, User
from database.repositories.teacher_repository import TeacherRepository
from database.repositories.lesson_repository import LessonRepository
from database.repositories.class_repository import ClassRepository
from database.repositories.schedule_repository import ScheduleRepository

# Import password hasher utility
try:
    from utils.password_hasher import hash_password, verify_password

    USE_PASSWORD_HASHER = True
except ImportError:
    USE_PASSWORD_HASHER = False
    logging.warning("Password hasher utility not available, using legacy hashing")


class DatabaseManager:
    """Manages database operations for the application"""

    def __init__(self, db_path="schedule.db"):
        self.db_path = db_path
        self.local = threading.local()  # Thread-local storage for connections

        # Instantiate repositories with the manager itself for thread-safe connection handling
        self.teachers = TeacherRepository(self)
        self.lessons = LessonRepository(self)
        self.classes = ClassRepository(self)
        self.schedule = ScheduleRepository(self)

        self.create_tables()
        self.school_type = self.get_school_type()

    def __enter__(self):
        """Support use as a context manager: with DatabaseManager(...) as db: ..."""
        return self

    def __exit__(self, exc_type, exc, tb):
        """Ensure connections are closed when exiting context manager."""
        try:
            self.close_connection()
        except Exception:
            pass

    def __del__(self):
        """Destructor to ensure DB connection is closed to avoid ResourceWarning."""
        try:
            # close any open connection for this thread
            self.close_connection()
        except Exception:
            # Avoid raising in destructor
            pass

    def get_connection(self):
        """Get a thread-local database connection"""
        if not hasattr(self.local, "connection") or self.local.connection is None:
            self.local.connection = sqlite3.connect(self.db_path)
            self.local.connection.row_factory = sqlite3.Row
            self.local.connection.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        return self.local.connection

    def close_connection(self):
        """Close the thread-local database connection"""
        if hasattr(self.local, "connection") and self.local.connection is not None:
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
            cursor.execute(
                "INSERT OR REPLACE INTO settings (setting_key, setting_value) VALUES (?, ?)",
                ("school_type", school_type),
            )
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

            cursor.execute(
                "INSERT OR REPLACE INTO settings (setting_key, setting_value) VALUES (?, ?)",
                (key, value_to_store),
            )
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
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL
                )
            """
            )

            # Teachers table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS teachers (
                    teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    school_type TEXT NOT NULL
                )
            """
            )

            # Classes table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS classes (
                    class_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    grade INTEGER NOT NULL,
                    school_type TEXT NOT NULL
                )
            """
            )

            # Classrooms table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS classrooms (
                    classroom_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    capacity INTEGER NOT NULL,
                    school_type TEXT NOT NULL
                )
            """
            )

            # Lessons table (stores unique lesson names)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS lessons (
                    lesson_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    weekly_hours INTEGER DEFAULT 0,
                    school_type TEXT NOT NULL,
                    UNIQUE(name, school_type)
                )
            """
            )

            # Curriculum table (links lessons to grades and hours)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS curriculum (
                    curriculum_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lesson_id INTEGER NOT NULL,
                    grade INTEGER NOT NULL,
                    weekly_hours INTEGER NOT NULL,
                    school_type TEXT NOT NULL,
                    FOREIGN KEY (lesson_id) REFERENCES lessons(lesson_id) ON DELETE CASCADE
                )
            """
            )

            # Schedule entries table (assignments)
            cursor.execute(
                """
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
            """
            )

            # Schedule table (timetable/program)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS schedule (
                    schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            """
            )

            # Teacher availability table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS teacher_availability (
                    availability_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    teacher_id INTEGER NOT NULL,
                    day INTEGER NOT NULL,
                    time_slot INTEGER NOT NULL,
                    is_available INTEGER NOT NULL DEFAULT 1,
                    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE CASCADE
                )
            """
            )

            # Settings table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS settings (
                    setting_key TEXT PRIMARY KEY,
                    setting_value TEXT
                )
            """
            )

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
        if not self._ensure_connection():
            return None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            # Hash the password before storing
            hashed = self._hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, hashed, role),
            )
            if self._safe_commit():
                return cursor.lastrowid
            return None
        except sqlite3.Error as e:
            logging.error(f"Error adding user: {e}")
            return None

    def add_lesson(self, name: str, weekly_hours: int = 0) -> Optional[int]:
        """Add a new unique lesson name for the current school type via repository."""
        school_type = self._get_current_school_type()
        return self.lessons.add_lesson(name, school_type, weekly_hours)

    def get_all_lessons(self) -> List[Lesson]:
        """Get all unique lessons for the current school type via repository."""
        school_type = self._get_current_school_type()
        return self.lessons.get_all_lessons(school_type)

    def update_lesson(self, lesson_id: int, name: str) -> bool:
        """Update a lesson's name via repository."""
        return self.lessons.update_lesson(lesson_id, name)

    def delete_lesson(self, lesson_id: int) -> bool:
        """Delete a lesson and its associated curriculum entries via repository."""
        return self.lessons.delete_lesson(lesson_id)

    def get_curriculum_for_lesson(self, lesson_id: int) -> List[Curriculum]:
        """Get all curriculum entries for a specific lesson via repository."""
        school_type = self._get_current_school_type()
        return self.lessons.get_curriculum_for_lesson(lesson_id, school_type)

    def add_lesson_weekly_hours(self, lesson_id: int, grade: int, school_type: str, weekly_hours: int) -> bool:
        """Add or update weekly hours for a lesson at a specific grade via repository."""
        return self.lessons.add_or_update_curriculum(lesson_id, grade, weekly_hours, school_type)

    def add_or_update_curriculum(self, lesson_id: int, grade: int, weekly_hours: int) -> bool:
        """Add or update a curriculum entry for a lesson at a specific grade via repository."""
        school_type = self._get_current_school_type()
        return self.lessons.add_or_update_curriculum(lesson_id, grade, weekly_hours, school_type)

    def get_weekly_hours_for_lesson(self, lesson_id: int, grade: int) -> Optional[int]:
        """Get the weekly hours for a specific lesson and grade via repository."""
        school_type = self._get_current_school_type()
        return self.lessons.get_weekly_hours_for_lesson(lesson_id, grade, school_type)

    def get_all_teachers(self) -> List[Teacher]:
        """Get all teachers for the current school type via repository."""
        school_type = self._get_current_school_type()
        return self.teachers.get_all_teachers(school_type)

    def get_all_classes(self) -> List[Class]:
        """Get all classes for the current school type via repository."""
        school_type = self._get_current_school_type()
        return self.classes.get_all_classes(school_type)

    def get_schedule_by_school_type(self) -> List[ScheduleEntry]:
        """Get all schedule entries for the current school type (assignments) via repository."""
        school_type = self._get_current_school_type()
        return self.schedule.get_schedule_entries_by_school_type(school_type)

    def get_schedule_program_by_school_type(self) -> List[ScheduleEntry]:
        """Get all schedule program for the current school type (timetable) via repository."""
        school_type = self._get_current_school_type()
        return self.schedule.get_schedule_program_by_school_type(school_type)

    def get_lesson_by_id(self, lesson_id: int) -> Optional[Lesson]:
        """Get a lesson by its ID via repository."""
        return self.lessons.get_lesson_by_id(lesson_id)

    def get_lesson_by_name(self, name: str) -> Optional[Lesson]:
        """Get a lesson by its name for the current school type via repository."""
        school_type = self._get_current_school_type()
        return self.lessons.get_lesson_by_name(name, school_type)

    def get_teacher_by_id(self, teacher_id: int) -> Optional[Teacher]:
        """Get a teacher by its ID via repository."""
        return self.teachers.get_teacher_by_id(teacher_id)

    def get_class_by_id(self, class_id: int) -> Optional[Class]:
        """Get a class by its ID via repository."""
        return self.classes.get_class_by_id(class_id)

    def get_classroom_by_id(self, classroom_id: int) -> Optional[Classroom]:
        """Get a classroom by its ID via repository."""
        return self.classes.get_classroom_by_id(classroom_id)

    def add_schedule_entry(
        self,
        class_id: int,
        teacher_id: int,
        lesson_id: int,
        classroom_id: int,
        day: int,
        time_slot: int,
    ) -> Optional[int]:
        """Add a new schedule entry to schedule_entries table (assignments) via repository."""
        school_type = self._get_current_school_type()
        return self.schedule.add_schedule_entry(class_id, teacher_id, lesson_id, classroom_id, day, time_slot, school_type)

    def add_schedule_by_school_type(
        self,
        class_id: int,
        lesson_id: int,
        teacher_id: int,
        classroom_id: int = 0,
        day: int = -1,
        time_slot: int = -1,
    ) -> Optional[int]:
        """Add a lesson assignment (without schedule details) via repository."""
        return self.add_schedule_entry(class_id, teacher_id, lesson_id, classroom_id, day, time_slot)

    def add_schedule_program(
        self,
        class_id: int,
        teacher_id: int,
        lesson_id: int,
        classroom_id: int,
        day: int,
        time_slot: int,
    ) -> Optional[int]:
        """Add a new schedule program to schedule table (timetable) via repository."""
        school_type = self._get_current_school_type()
        return self.schedule.add_schedule_program_entry(class_id, teacher_id, lesson_id, classroom_id, day, time_slot, school_type)

    def get_schedule_for_specific_class(self, class_id: int) -> List[ScheduleEntry]:
        """Get schedule program for a specific class (from schedule table) via repository."""
        school_type = self._get_current_school_type()
        return self.schedule.get_schedule_for_class(class_id, school_type)

    def get_schedule_for_specific_teacher(self, teacher_id: int) -> List[ScheduleEntry]:
        """Get schedule program for a specific teacher via repository."""
        school_type = self._get_current_school_type()
        return self.teachers.get_schedule_for_teacher(teacher_id, school_type)

    def update_schedule_entry(
        self,
        entry_id: int,
        class_id: int,
        teacher_id: int,
        lesson_id: int,
        classroom_id: int,
        day: int,
        time_slot: int,
    ) -> bool:
        """Update an existing schedule entry via repository."""
        return self.schedule.update_schedule_entry(entry_id, class_id, teacher_id, lesson_id, classroom_id, day, time_slot)

    def delete_teacher(self, teacher_id: int) -> bool:
        """Delete a teacher and all related records via repository."""
        return self.teachers.delete_teacher(teacher_id)

    def delete_schedule_entry(self, entry_id: int) -> bool:
        """Delete a single schedule entry by entry_id via repository."""
        school_type = self._get_current_school_type()
        return self.schedule.delete_schedule_entry(entry_id, school_type)

    def delete_all_schedule_entries(self) -> bool:
        """Delete all schedule entries for the current school type via repository."""
        school_type = self._get_current_school_type()
        deleted_count = self.schedule.delete_all_schedule_entries(school_type)
        return deleted_count >= 0

    def clear_schedule(self) -> bool:
        """Clear only the schedule table (not assignments) via repository."""
        school_type = self._get_current_school_type()
        deleted_count = self.schedule.clear_schedule_program(school_type)
        return deleted_count >= 0

    def delete_class(self, class_id: int) -> bool:
        """Delete a class via repository."""
        return self.classes.delete_class(class_id)

    def add_teacher(self, name: str, subject: str) -> Optional[int]:
        """Add a new teacher via repository."""
        school_type = self._get_current_school_type()
        return self.teachers.add_teacher(name, subject, school_type)

    def update_teacher(self, teacher_id: int, name: str, subject: str) -> bool:
        """Update an existing teacher via repository."""
        return self.teachers.update_teacher(teacher_id, name, subject)

    def add_class(self, name: str, grade: int) -> Optional[int]:
        """Add a new class via repository."""
        school_type = self._get_current_school_type()
        return self.classes.add_class(name, grade, school_type)

    def update_class(self, class_id: int, name: str, grade: int) -> bool:
        """Update an existing class via repository."""
        return self.classes.update_class(class_id, name, grade)

    def get_teacher_availability(self, teacher_id: int) -> List[dict]:
        """Get teacher availability data via repository."""
        return self.teachers.get_teacher_availability(teacher_id)

    def set_teacher_availability(self, teacher_id: int, day: int, time_slot: int, is_available: bool) -> bool:
        """Set teacher availability for a specific day and time slot via repository."""
        return self.teachers.set_teacher_availability(teacher_id, day, time_slot, is_available)

    def is_teacher_available(self, teacher_id: int, day: int, time_slot: int) -> bool:
        """Check if a teacher is available at a specific day and time slot via repository."""
        return self.teachers.is_teacher_available(teacher_id, day, time_slot)

    def get_all_classrooms(self) -> List[Classroom]:
        """Get all classrooms for the current school type via repository."""
        school_type = self._get_current_school_type()
        return self.classes.get_all_classrooms(school_type)

    def get_user(self, username: str, password: str) -> Optional[User]:
        """Get a user by username and password"""
        if not self._ensure_connection():
            return None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            # Fetch stored hash for username and verify
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if not row:
                return None
            stored = row["password"]
            try:
                if self._verify_password(stored, password):
                    return User(row["user_id"], row["username"], row["password"], row["role"])
                else:
                    return None
            except Exception:
                return None
        except sqlite3.Error as e:
            logging.error(f"Error getting user: {e}")
            return None

    # ----------------- Password hashing helpers -----------------
    def _hash_password(self, password: str, *, iterations: int = 100_000) -> str:
        """
        Hash password using best available method (bcrypt or PBKDF2-HMAC-SHA256)

        Args:
            password: Plain text password
            iterations: Number of iterations for PBKDF2 (ignored if bcrypt is used)

        Returns:
            Hashed password string
        """
        if USE_PASSWORD_HASHER:
            return hash_password(password)
        else:
            # Legacy fallback
            salt = secrets.token_bytes(16)
            dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
            return f"pbkdf2_sha256${iterations}${binascii.hexlify(salt).decode()}${binascii.hexlify(dk).decode()}"

    def _verify_password(self, stored: str, provided_password: str) -> bool:
        """
        Verify a provided password against stored hash

        Args:
            stored: Stored password hash
            provided_password: Password to verify

        Returns:
            True if password matches, False otherwise
        """
        if USE_PASSWORD_HASHER:
            return verify_password(stored, provided_password)
        else:
            # Legacy fallback
            try:
                parts = stored.split("$")
                if len(parts) != 4:
                    return False
                algo, iter_str, salt_hex, hash_hex = parts
                if algo != "pbkdf2_sha256":
                    return False
                iterations = int(iter_str)
                salt = binascii.unhexlify(salt_hex)
                expected = binascii.unhexlify(hash_hex)
                dk = hashlib.pbkdf2_hmac("sha256", provided_password.encode("utf-8"), salt, iterations)
                return secrets.compare_digest(dk, expected)
            except Exception:
                return False

    def add_classroom(self, name: str, capacity: int) -> Optional[int]:
        """Add a new classroom via repository."""
        school_type = self._get_current_school_type()
        return self.classes.add_classroom(name, capacity, school_type)

    def get_all_curriculum(self) -> List[Curriculum]:
        """Get all curriculum entries for the current school type via repository."""
        school_type = self._get_current_school_type()
        return self.lessons.get_all_curriculum(school_type)

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
                        missing_lessons.append((curriculum_entry.lesson_id, lesson.name, curriculum_entry.weekly_hours))

            if missing_lessons:
                result[class_obj.class_id] = {
                    "class": class_obj,
                    "missing_lessons": missing_lessons,
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
            return {"success": [], "failed": []}

        result = {"success": [], "failed": []}

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
            class_obj = data["class"]
            missing_lessons = data["missing_lessons"]

            for lesson_id, lesson_name, weekly_hours in missing_lessons:
                # Try to find a suitable teacher
                # Match by subject name (e.g., "Matematik" lesson needs "Matematik" teacher)
                suitable_teachers = [
                    t
                    for t in all_teachers
                    if t.subject.lower() in lesson_name.lower() or lesson_name.lower() in t.subject.lower()
                ]

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
                        -1,  # Not yet scheduled to a specific time slot
                    )

                    if entry_id:
                        # Öğretmen yükünü güncelle (dengeli dağıtım için)
                        teacher_workload[teacher.teacher_id] = (
                            teacher_workload.get(teacher.teacher_id, 0) + weekly_hours
                        )
                        result["success"].append((class_obj.name, lesson_name, teacher.name))
                        logging.info(
                            f"Auto-assigned {lesson_name} to {class_obj.name} with teacher {teacher.name} (yük: {teacher_workload[teacher.teacher_id]} saat)"
                        )
                    else:
                        result["failed"].append((class_obj.name, lesson_name, "Veritabanı hatası"))
                        logging.error(f"Failed to auto-assign {lesson_name} to {class_obj.name}")
                else:
                    # No suitable teacher found
                    result["failed"].append((class_obj.name, lesson_name, "Uygun öğretmen bulunamadı"))
                    logging.warning(f"No suitable teacher found for {lesson_name} in {class_obj.name}")

        return result
