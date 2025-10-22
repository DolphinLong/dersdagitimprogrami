'''
Repository for all database operations related to Teachers.
'''
import logging
from typing import List, Optional

from database.models import Teacher, ScheduleEntry
from database.repositories.base_repository import BaseRepository

class TeacherRepository(BaseRepository):
    def __init__(self, db_manager):
        """Initializes the repository with the DatabaseManager instance."""
        super().__init__(db_manager)
    """Handles all database operations for the Teacher model."""

    def get_all_teachers(self, school_type: str) -> List[Teacher]:
        """Get all teachers for the given school type."""
        query = "SELECT * FROM teachers WHERE school_type = ? ORDER BY name"
        cursor = self._execute(query, (school_type,))
        rows = cursor.fetchall()
        return [Teacher(row["teacher_id"], row["name"], row["subject"]) for row in rows]

    def get_teacher_by_id(self, teacher_id: int) -> Optional[Teacher]:
        """Get a teacher by its ID."""
        query = "SELECT * FROM teachers WHERE teacher_id = ?"
        cursor = self._execute(query, (teacher_id,))
        row = cursor.fetchone()
        return Teacher(row["teacher_id"], row["name"], row["subject"]) if row else None

    def add_teacher(self, name: str, subject: str, school_type: str) -> Optional[int]:
        """Add a new teacher."""
        query = "INSERT INTO teachers (name, subject, school_type) VALUES (?, ?, ?)"
        try:
            cursor = self._execute(query, (name, subject, school_type))
            self._commit()
            return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"Error adding teacher: {e}")
            return None

    def update_teacher(self, teacher_id: int, name: str, subject: str) -> bool:
        """Update an existing teacher."""
        query = "UPDATE teachers SET name = ?, subject = ? WHERE teacher_id = ?"
        try:
            cursor = self._execute(query, (name, subject, teacher_id))
            self._commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.logger.error(f"Error updating teacher: {e}")
            return False

    def delete_teacher(self, teacher_id: int) -> bool:
        """Delete a teacher and all related records."""
        try:
            # Delete related schedule entries first
            self._execute("DELETE FROM schedule_entries WHERE teacher_id = ?", (teacher_id,))
            # Delete from the main schedule program table
            self._execute("DELETE FROM schedule WHERE teacher_id = ?", (teacher_id,))
            # Delete related teacher availability records
            self._execute("DELETE FROM teacher_availability WHERE teacher_id = ?", (teacher_id,))
            # Finally, delete the teacher
            cursor = self._execute("DELETE FROM teachers WHERE teacher_id = ?", (teacher_id,))
            self._commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.logger.error(f"Error deleting teacher: {e}")
            return False

    def get_teacher_availability(self, teacher_id: int) -> List[dict]:
        """Get teacher availability data."""
        query = "SELECT day, time_slot, is_available FROM teacher_availability WHERE teacher_id = ?"
        cursor = self._execute(query, (teacher_id,))
        rows = cursor.fetchall()
        return [{"day": row["day"], "time_slot": row["time_slot"], "is_available": row["is_available"]} for row in rows]

    def set_teacher_availability(self, teacher_id: int, day: int, time_slot: int, is_available: bool) -> bool:
        """Set teacher availability for a specific day and time slot."""
        try:
            # First try to update existing record
            update_query = "UPDATE teacher_availability SET is_available = ? WHERE teacher_id = ? AND day = ? AND time_slot = ?"
            cursor = self._execute(update_query, (1 if is_available else 0, teacher_id, day, time_slot))

            # If no rows were updated, insert a new record
            if cursor.rowcount == 0:
                insert_query = "INSERT INTO teacher_availability (teacher_id, day, time_slot, is_available) VALUES (?, ?, ?, ?)"
                self._execute(insert_query, (teacher_id, day, time_slot, 1 if is_available else 0))
            
            self._commit()
            return True
        except Exception as e:
            self.logger.error(f"Error setting teacher availability: {e}")
            return False

    def is_teacher_available(self, teacher_id: int, day: int, time_slot: int) -> bool:
        """Check if a teacher is available at a specific day and time slot."""
        query = "SELECT is_available FROM teacher_availability WHERE teacher_id = ? AND day = ? AND time_slot = ?"
        try:
            cursor = self._execute(query, (teacher_id, day, time_slot))
            row = cursor.fetchone()
            # If no record exists, teacher is available by default
            return row["is_available"] == 1 if row else True
        except Exception as e:
            self.logger.error(f"Error checking teacher availability: {e}")
            return True # Default to available on error

    def get_schedule_for_teacher(self, teacher_id: int, school_type: str) -> List[ScheduleEntry]:
        """Get schedule program for a specific teacher."""
        query = "SELECT schedule_id, class_id, teacher_id, lesson_id, classroom_id, day, time_slot FROM schedule WHERE teacher_id = ? AND school_type = ?"
        try:
            cursor = self._execute(query, (teacher_id, school_type))
            rows = cursor.fetchall()
            return [ScheduleEntry(row[0], row[1], row[2], row[3], row[4], row[5], row[6]) for row in rows]
        except Exception as e:
            self.logger.error(f"Error getting schedule for teacher: {e}")
            return []
