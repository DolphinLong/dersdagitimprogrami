'''
Repository for all database operations related to Schedule and Schedule Entries.
'''
from typing import List, Optional

from database.models import ScheduleEntry
from database.repositories.base_repository import BaseRepository

class ScheduleRepository(BaseRepository):
    """Handles all database operations for the Schedule and ScheduleEntry models."""

    def __init__(self, db_manager):
        """Initializes the repository with the DatabaseManager instance."""
        super().__init__(db_manager)

    def get_schedule_entries_by_school_type(self, school_type: str) -> List[ScheduleEntry]:
        """Get all schedule entries (assignments) for the given school type."""
        query = "SELECT entry_id, class_id, teacher_id, lesson_id, classroom_id, day, time_slot FROM schedule_entries WHERE school_type = ?"
        cursor = self._execute(query, (school_type,))
        rows = cursor.fetchall()
        return [ScheduleEntry(row[0], row[1], row[2], row[3], row[4], row[5], row[6]) for row in rows]

    def get_schedule_program_by_school_type(self, school_type: str) -> List[ScheduleEntry]:
        """Get all schedule program entries (timetable) for the given school type."""
        query = "SELECT schedule_id, class_id, teacher_id, lesson_id, classroom_id, day, time_slot FROM schedule WHERE school_type = ?"
        cursor = self._execute(query, (school_type,))
        rows = cursor.fetchall()
        return [ScheduleEntry(row[0], row[1], row[2], row[3], row[4], row[5], row[6]) for row in rows]

    def add_schedule_entry(self, class_id: int, teacher_id: int, lesson_id: int, classroom_id: int, day: int, time_slot: int, school_type: str) -> Optional[int]:
        """Add a new schedule entry (assignment)."""
        query = "INSERT INTO schedule_entries (class_id, teacher_id, lesson_id, classroom_id, day, time_slot, school_type) VALUES (?, ?, ?, ?, ?, ?, ?)"
        try:
            cursor = self._execute(query, (class_id, teacher_id, lesson_id, classroom_id, day, time_slot, school_type))
            self._commit()
            return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"Error adding schedule entry: {e}")
            return None

    def add_schedule_program_entry(self, class_id: int, teacher_id: int, lesson_id: int, classroom_id: int, day: int, time_slot: int, school_type: str) -> Optional[int]:
        """Add a new schedule program entry (timetable)."""
        query = "INSERT INTO schedule (class_id, teacher_id, lesson_id, classroom_id, day, time_slot, school_type) VALUES (?, ?, ?, ?, ?, ?, ?)"
        try:
            cursor = self._execute(query, (class_id, teacher_id, lesson_id, classroom_id, day, time_slot, school_type))
            self._commit()
            return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"Error adding schedule program entry: {e}")
            return None

    def get_schedule_for_class(self, class_id: int, school_type: str) -> List[ScheduleEntry]:
        """Get schedule program for a specific class."""
        query = "SELECT schedule_id, class_id, teacher_id, lesson_id, classroom_id, day, time_slot FROM schedule WHERE class_id = ? AND school_type = ?"
        cursor = self._execute(query, (class_id, school_type))
        rows = cursor.fetchall()
        return [ScheduleEntry(row[0], row[1], row[2], row[3], row[4], row[5], row[6]) for row in rows]

    def update_schedule_entry(self, entry_id: int, class_id: int, teacher_id: int, lesson_id: int, classroom_id: int, day: int, time_slot: int) -> bool:
        """Update an existing schedule entry."""
        query = "UPDATE schedule_entries SET class_id = ?, teacher_id = ?, lesson_id = ?, classroom_id = ?, day = ?, time_slot = ? WHERE entry_id = ?"
        try:
            cursor = self._execute(query, (class_id, teacher_id, lesson_id, classroom_id, day, time_slot, entry_id))
            self._commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.logger.error(f"Error updating schedule entry: {e}")
            return False

    def delete_schedule_entry(self, entry_id: int, school_type: str) -> bool:
        """Delete a single schedule entry by entry_id."""
        query = "DELETE FROM schedule_entries WHERE entry_id = ? AND school_type = ?"
        try:
            cursor = self._execute(query, (entry_id, school_type))
            self._commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.logger.error(f"Error deleting schedule entry {entry_id}: {e}")
            return False

    def delete_all_schedule_entries(self, school_type: str) -> int:
        """Delete all schedule entries for the given school type. Returns the number of deleted rows."""
        query = "DELETE FROM schedule_entries WHERE school_type = ?"
        try:
            cursor = self._execute(query, (school_type,))
            deleted_count = cursor.rowcount
            self._commit()
            self.logger.info(f"Deleted {deleted_count} schedule entries for school type: {school_type}")
            return deleted_count
        except Exception as e:
            self.logger.error(f"Error deleting all schedule entries: {e}")
            return -1 # Return -1 to indicate error

    def clear_schedule_program(self, school_type: str) -> int:
        """Clear only the schedule program table (not assignments). Returns the number of deleted rows."""
        query = "DELETE FROM schedule WHERE school_type = ?"
        try:
            cursor = self._execute(query, (school_type,))
            deleted_count = cursor.rowcount
            self._commit()
            self.logger.info(f"Cleared {deleted_count} schedule program entries for school type: {school_type}")
            return deleted_count
        except Exception as e:
            self.logger.error(f"Error clearing schedule program: {e}")
            return -1 # Return -1 to indicate error
