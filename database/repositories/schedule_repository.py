"""
Repository for all database operations related to Schedule Entries.
"""
from typing import List, Optional
from database.models import ScheduleEntry
from database.repositories.base_repository import BaseRepository


class ScheduleRepository(BaseRepository[ScheduleEntry]):
    """Handles all database operations for schedule entries and programs."""

    def _row_to_entity(self, row: dict) -> Optional[ScheduleEntry]:
        """Convert database row to ScheduleEntry entity."""
        return ScheduleEntry(
            entry_id=row.get("schedule_id") or row.get("entry_id"),
            class_id=row.get("class_id"),
            teacher_id=row.get("teacher_id"),
            lesson_id=row.get("lesson_id"),
            classroom_id=row.get("classroom_id"),
            day=row.get("day"),
            time_slot=row.get("time_slot")
        )

    def get_by_id(self, entry_id: int) -> Optional[ScheduleEntry]:
        """Get a schedule entry by its ID."""
        query = "SELECT * FROM schedule WHERE schedule_id = ?"
        rows = self._execute_query(query, (entry_id,))
        return self._row_to_entity(rows[0]) if rows else None

    def get_all(self) -> List[ScheduleEntry]:
        """Get all schedule entries."""
        query = "SELECT * FROM schedule ORDER BY day, time_slot"
        rows = self._execute_query(query)
        return [self._row_to_entity(row) for row in rows if row]

    def get_schedule_entries_by_school_type(self, school_type: str) -> List[ScheduleEntry]:
        """Get all schedule entries (assignments) for school type."""
        # DÜZELTME: Ders atamaları schedule_entries tablosunda!
        query = "SELECT * FROM schedule_entries WHERE school_type = ?"
        rows = self._execute_query(query, (school_type,))
        return [ScheduleEntry(
            entry_id=row.get("entry_id"),
            class_id=row["class_id"],
            teacher_id=row["teacher_id"],
            lesson_id=row["lesson_id"],
            classroom_id=row["classroom_id"],
            day=row["day"],
            time_slot=row["time_slot"]
        ) for row in rows]

    def get_schedule_program_by_school_type(self, school_type: str) -> List[ScheduleEntry]:
        """Get all schedule program entries for school type."""
        query = "SELECT * FROM schedule WHERE school_type = ? ORDER BY day, time_slot"
        rows = self._execute_query(query, (school_type,))
        return [self._row_to_entity(row) for row in rows if row]

    def add_schedule_entry(self, class_id: int, teacher_id: int, lesson_id: int,
                          classroom_id: int, day: int, time_slot: int, school_type: str) -> Optional[int]:
        """Add a new schedule entry (assignment)."""
        query = """INSERT INTO schedule_entries
                   (class_id, teacher_id, lesson_id, classroom_id, day, time_slot, school_type)
                   VALUES (?, ?, ?, ?, ?, ?, ?)"""
        return self._execute_write(query, (class_id, teacher_id, lesson_id, classroom_id, day, time_slot, school_type))

    def add_schedule_program_entry(self, class_id: int, teacher_id: int, lesson_id: int,
                                 classroom_id: int, day: int, time_slot: int, school_type: str) -> Optional[int]:
        """Add a new schedule program entry (timetable)."""
        query = """INSERT INTO schedule
                   (class_id, teacher_id, lesson_id, classroom_id, day, time_slot, school_type)
                   VALUES (?, ?, ?, ?, ?, ?, ?)"""
        return self._execute_write(query, (class_id, teacher_id, lesson_id, classroom_id, day, time_slot, school_type))

    def update_schedule_entry(self, entry_id: int, class_id: int, teacher_id: int, lesson_id: int,
                             classroom_id: int, day: int, time_slot: int) -> bool:
        """Update an existing schedule entry."""
        query = """UPDATE schedule_entries SET
                   class_id = ?, teacher_id = ?, lesson_id = ?, classroom_id = ?,
                   day = ?, time_slot = ? WHERE entry_id = ?"""
        result = self._execute_write(query, (class_id, teacher_id, lesson_id, classroom_id, day, time_slot, entry_id))
        return result is not None

    def delete_schedule_entry(self, entry_id: int, school_type: str) -> bool:
        """Delete a schedule entry by ID."""
        # Delete from schedule_entries table (school_type kontrolü olmadan)
        query = "DELETE FROM schedule_entries WHERE entry_id = ?"
        result = self._execute_write(query, (entry_id,))
        return result is not None and result > 0

    def delete_all_schedule_entries(self, school_type: str) -> int:
        """Delete all schedule entries for school type."""
        query = "DELETE FROM schedule_entries WHERE school_type = ?"
        result = self._execute_write(query, (school_type,))
        return result or 0

    def clear_schedule_program(self, school_type: str) -> int:
        """Clear all schedule program entries for school type."""
        query = "DELETE FROM schedule WHERE school_type = ?"
        result = self._execute_write(query, (school_type,))
        return result or 0

    def get_schedule_for_class(self, class_id: int, school_type: str) -> List[ScheduleEntry]:
        """Get schedule program for a specific class."""
        query = "SELECT * FROM schedule WHERE class_id = ? AND school_type = ? ORDER BY day, time_slot"
        rows = self._execute_query(query, (class_id, school_type))
        return [self._row_to_entity(row) for row in rows if row]
