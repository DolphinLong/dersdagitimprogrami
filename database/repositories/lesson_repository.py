"""
Repository for all database operations related to Lessons.
"""
from typing import List, Optional
from database.models import Lesson, Curriculum
from database.repositories.base_repository import BaseRepository


class LessonRepository(BaseRepository[Lesson]):
    """Handles all database operations for the Lesson model."""

    def _row_to_entity(self, row: dict) -> Optional[Lesson]:
        """Convert database row to Lesson entity."""
        return Lesson(
            lesson_id=row.get("lesson_id"),
            name=row.get("name"),
            weekly_hours=row.get("weekly_hours", 0)
        )

    def get_lesson_by_id(self, lesson_id: int) -> Optional[Lesson]:
        """Get a lesson by its ID (compatibility with existing database manager)."""
        return self.get_by_id(lesson_id)

    def get_by_id(self, lesson_id: int) -> Optional[Lesson]:
        """Get a lesson by its ID."""
        query = "SELECT * FROM lessons WHERE lesson_id = ?"
        rows = self._execute_query(query, (lesson_id,))
        return self._row_to_entity(rows[0]) if rows else None

    def get_all(self) -> List[Lesson]:
        """Get all lessons."""
        query = "SELECT * FROM lessons ORDER BY name"
        rows = self._execute_query(query)
        return [self._row_to_entity(row) for row in rows if row]

    def get_all_lessons(self, school_type: str) -> List[Lesson]:
        """Get all lessons for the given school type."""
        query = "SELECT * FROM lessons WHERE school_type = ? ORDER BY name"
        rows = self._execute_query(query, (school_type,))
        return [self._row_to_entity(row) for row in rows if row]

    def add_lesson(self, name: str, school_type: str, weekly_hours: int = 0) -> Optional[int]:
        """Add a new lesson."""
        query = "INSERT INTO lessons (name, school_type, weekly_hours) VALUES (?, ?, ?)"
        return self._execute_write(query, (name, school_type, weekly_hours))

    def update_lesson(self, lesson_id: int, name: str) -> bool:
        """Update an existing lesson."""
        query = "UPDATE lessons SET name = ? WHERE lesson_id = ?"
        result = self._execute_write(query, (name, lesson_id))
        return result is not None

    def delete_lesson(self, lesson_id: int) -> bool:
        """Delete a lesson and its curriculum entries."""
        try:
            # Delete curriculum entries first
            self._execute_write("DELETE FROM curriculum WHERE lesson_id = ?", (lesson_id,))
            # Delete from schedule entries
            self._execute_write("DELETE FROM schedule_entries WHERE lesson_id = ?", (lesson_id,))
            # Delete from schedule
            self._execute_write("DELETE FROM schedule WHERE lesson_id = ?", (lesson_id,))
            # Finally, delete the lesson
            result = self._execute_write("DELETE FROM lessons WHERE lesson_id = ?", (lesson_id,))
            return result is not None
        except Exception as e:
            self.logger.error(f"Error deleting lesson: {e}")
            return False

    def get_curriculum_for_lesson(self, lesson_id: int, school_type: str) -> List[Curriculum]:
        """Get all curriculum entries for a specific lesson."""
        query = "SELECT * FROM curriculum WHERE lesson_id = ? AND school_type = ?"
        rows = self._execute_query(query, (lesson_id, school_type))
        return [Curriculum(
            curriculum_id=row["curriculum_id"],
            lesson_id=row["lesson_id"],
            grade=row["grade"],
            weekly_hours=row["weekly_hours"]
        ) for row in rows]
    
    def get_all_curriculum(self, school_type: str) -> List[Curriculum]:
        """Get all curriculum entries for the given school type."""
        query = "SELECT * FROM curriculum WHERE school_type = ? ORDER BY grade, lesson_id"
        rows = self._execute_query(query, (school_type,))
        return [Curriculum(
            curriculum_id=row["curriculum_id"],
            lesson_id=row["lesson_id"],
            grade=row["grade"],
            weekly_hours=row["weekly_hours"]
        ) for row in rows]

    def get_weekly_hours_for_lesson(self, lesson_id: int, grade: int, school_type: str) -> Optional[int]:
        """Get the weekly hours for a specific lesson and grade."""
        query = "SELECT weekly_hours FROM curriculum WHERE lesson_id = ? AND grade = ? AND school_type = ?"
        rows = self._execute_query(query, (lesson_id, grade, school_type))
        return rows[0]["weekly_hours"] if rows else None

    def add_or_update_curriculum(self, lesson_id: int, grade: int, weekly_hours: int, school_type: str) -> bool:
        """Add or update a curriculum entry for a lesson at a specific grade."""
        try:
            # Try to update first
            update_query = "UPDATE curriculum SET weekly_hours = ? WHERE lesson_id = ? AND grade = ? AND school_type = ?"
            result = self._execute_write(update_query, (weekly_hours, lesson_id, grade, school_type))

            # If no rows were updated, insert a new record
            if result is None:
                insert_query = "INSERT INTO curriculum (lesson_id, grade, weekly_hours, school_type) VALUES (?, ?, ?, ?)"
                result = self._execute_write(insert_query, (lesson_id, grade, weekly_hours, school_type))

            return result is not None
        except Exception as e:
            self.logger.error(f"Error adding/updating curriculum: {e}")
            return False
