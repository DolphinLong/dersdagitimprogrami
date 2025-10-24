"""
Repository for all database operations related to Teachers.
"""
from typing import List, Optional
from database.models import Teacher, ScheduleEntry
from database.repositories.base_repository import BaseRepository


class TeacherRepository(BaseRepository[Teacher]):
    """Handles all database operations for the Teacher model."""

    def _row_to_entity(self, row: dict) -> Optional[Teacher]:
        """Convert database row to Teacher entity."""
        return Teacher(
            teacher_id=row.get("teacher_id"),
            name=row.get("name"),
            subject=row.get("subject")
        )

    def get_teacher_by_id(self, teacher_id: int) -> Optional[Teacher]:
        """Get a teacher by its ID (compatibility with existing database manager)."""
        return self.get_by_id(teacher_id)

    def get_by_id(self, teacher_id: int) -> Optional[Teacher]:
        """Get a teacher by its ID."""
        query = "SELECT * FROM teachers WHERE teacher_id = ?"
        rows = self._execute_query(query, (teacher_id,))
        return self._row_to_entity(rows[0]) if rows else None

    def get_all(self) -> List[Teacher]:
        """Get all teachers."""
        query = "SELECT * FROM teachers ORDER BY name"
        rows = self._execute_query(query)
        return [self._row_to_entity(row) for row in rows if row]

    def get_all_teachers(self, school_type: str) -> List[Teacher]:
        """Get all teachers for the given school type."""
        query = "SELECT * FROM teachers WHERE school_type = ? ORDER BY name"
        rows = self._execute_query(query, (school_type,))
        return [self._row_to_entity(row) for row in rows if row]

    def add_teacher(self, name: str, subject: str, school_type: str) -> Optional[int]:
        """Add a new teacher."""
        query = "INSERT INTO teachers (name, subject, school_type) VALUES (?, ?, ?)"
        return self._execute_write(query, (name, subject, school_type))

    def update_teacher(self, teacher_id: int, name: str, subject: str) -> bool:
        """Update an existing teacher."""
        query = "UPDATE teachers SET name = ?, subject = ? WHERE teacher_id = ?"
        result = self._execute_write(query, (name, subject, teacher_id))
        return result is not None

    def delete_teacher(self, teacher_id: int) -> bool:
        """Delete a teacher and all related records."""
        try:
            # Delete related schedule entries first
            self._execute_write("DELETE FROM schedule_entries WHERE teacher_id = ?", (teacher_id,))
            # Delete from the main schedule program table
            self._execute_write("DELETE FROM schedule WHERE teacher_id = ?", (teacher_id,))
            # Delete related teacher availability records
            self._execute_write("DELETE FROM teacher_availability WHERE teacher_id = ?", (teacher_id,))
            # Finally, delete the teacher
            result = self._execute_write("DELETE FROM teachers WHERE teacher_id = ?", (teacher_id,))
            return result is not None
        except Exception as e:
            self.logger.error(f"Error deleting teacher: {e}")
            return False

    def get_teacher_availability(self, teacher_id: int) -> List[dict]:
        """Get teacher availability data."""
        query = "SELECT day, time_slot, is_available FROM teacher_availability WHERE teacher_id = ?"
        rows = self._execute_query(query, (teacher_id,))
        return rows

    def set_teacher_availability(self, teacher_id: int, day: int, time_slot: int, is_available: bool) -> bool:
        """Set teacher availability for a specific day and time slot."""
        try:
            # First try to update existing record
            update_query = "UPDATE teacher_availability SET is_available = ? WHERE teacher_id = ? AND day = ? AND time_slot = ?"
            result = self._execute_write(update_query, (1 if is_available else 0, teacher_id, day, time_slot))

            # If no rows were updated, insert a new record
            if result is None:
                insert_query = "INSERT INTO teacher_availability (teacher_id, day, time_slot, is_available) VALUES (?, ?, ?, ?)"
                result = self._execute_write(insert_query, (teacher_id, day, time_slot, 1 if is_available else 0))

            return result is not None
        except Exception as e:
            self.logger.error(f"Error setting teacher availability: {e}")
            return False

    def is_teacher_available(self, teacher_id: int, day: int, time_slot: int) -> bool:
        """Check if a teacher is available at a specific day and time slot."""
        query = "SELECT is_available FROM teacher_availability WHERE teacher_id = ? AND day = ? AND time_slot = ?"
        try:
            rows = self._execute_query(query, (teacher_id, day, time_slot))
            # If no record exists, teacher is available by default
            return rows[0]["is_available"] == 1 if rows else True
        except Exception as e:
            self.logger.error(f"Error checking teacher availability: {e}")
            return True  # Default to available on error

    def get_schedule_for_teacher(self, teacher_id: int, school_type: str) -> List[ScheduleEntry]:
        """Get schedule program for a specific teacher."""
        query = "SELECT schedule_id, class_id, teacher_id, lesson_id, classroom_id, day, time_slot FROM schedule WHERE teacher_id = ? AND school_type = ?"
        try:
            rows = self._execute_query(query, (teacher_id, school_type))
            return [ScheduleEntry(
                row["schedule_id"],
                row["class_id"],
                row["teacher_id"],
                row["lesson_id"],
                row["classroom_id"],
                row["day"],
                row["time_slot"]
            ) for row in rows]
        except Exception as e:
            self.logger.error(f"Error getting schedule for teacher: {e}")
            return []
