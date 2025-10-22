'''
Repository for all database operations related to Lessons and Curriculum.
'''
from typing import List, Optional

from database.models import Lesson, Curriculum
from database.repositories.base_repository import BaseRepository

class LessonRepository(BaseRepository):
    def __init__(self, db_manager):
        """Initializes the repository with the DatabaseManager instance."""
        super().__init__(db_manager)
    """Handles all database operations for the Lesson and Curriculum models."""

    def add_lesson(self, name: str, school_type: str, weekly_hours: int = 0) -> Optional[int]:
        """Add a new unique lesson name for the given school type."""
        # Check if lesson already exists
        find_query = "SELECT lesson_id FROM lessons WHERE name = ? AND school_type = ?"
        cursor = self._execute(find_query, (name, school_type))
        existing = cursor.fetchone()
        if existing:
            self.logger.info(f"Lesson '{name}' already exists for school type '{school_type}'")
            return existing["lesson_id"]

        # Insert new lesson
        insert_query = "INSERT INTO lessons (name, weekly_hours, school_type) VALUES (?, ?, ?)"
        try:
            cursor = self._execute(insert_query, (name, weekly_hours, school_type))
            self._commit()
            return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"Error adding lesson '{name}': {e}")
            return None

    def get_all_lessons(self, school_type: str) -> List[Lesson]:
        """Get all unique lessons for the given school type."""
        query = "SELECT * FROM lessons WHERE school_type = ? ORDER BY name"
        cursor = self._execute(query, (school_type,))
        rows = cursor.fetchall()
        return [Lesson(row["lesson_id"], row["name"], row["weekly_hours"]) for row in rows]

    def update_lesson(self, lesson_id: int, name: str) -> bool:
        """Update a lesson's name."""
        query = "UPDATE lessons SET name = ? WHERE lesson_id = ?"
        try:
            cursor = self._execute(query, (name, lesson_id))
            self._commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.logger.error(f"Error updating lesson {lesson_id}: {e}")
            return False

    def delete_lesson(self, lesson_id: int) -> bool:
        """Delete a lesson and its associated curriculum entries."""
        try:
            self._execute("DELETE FROM schedule WHERE lesson_id = ?", (lesson_id,))
            self._execute("DELETE FROM schedule_entries WHERE lesson_id = ?", (lesson_id,))
            self._execute("DELETE FROM curriculum WHERE lesson_id = ?", (lesson_id,))
            cursor = self._execute("DELETE FROM lessons WHERE lesson_id = ?", (lesson_id,))
            self._commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.logger.error(f"Error deleting lesson {lesson_id}: {e}")
            return False

    def get_lesson_by_id(self, lesson_id: int) -> Optional[Lesson]:
        """Get a lesson by its ID."""
        query = "SELECT * FROM lessons WHERE lesson_id = ?"
        cursor = self._execute(query, (lesson_id,))
        row = cursor.fetchone()
        return Lesson(row["lesson_id"], row["name"], row["weekly_hours"]) if row else None

    def get_lesson_by_name(self, name: str, school_type: str) -> Optional[Lesson]:
        """Get a lesson by its name for the given school type."""
        query = "SELECT * FROM lessons WHERE name = ? AND school_type = ?"
        cursor = self._execute(query, (name, school_type))
        row = cursor.fetchone()
        return Lesson(row["lesson_id"], row["name"], row["weekly_hours"]) if row else None

    def get_all_curriculum(self, school_type: str) -> List[Curriculum]:
        """Get all curriculum entries for the given school type."""
        query = "SELECT * FROM curriculum WHERE school_type = ?"
        cursor = self._execute(query, (school_type,))
        rows = cursor.fetchall()
        return [Curriculum(row["curriculum_id"], row["lesson_id"], row["grade"], row["weekly_hours"]) for row in rows]

    def get_curriculum_for_lesson(self, lesson_id: int, school_type: str) -> List[Curriculum]:
        """Get all curriculum entries for a specific lesson."""
        query = "SELECT * FROM curriculum WHERE lesson_id = ? AND school_type = ?"
        cursor = self._execute(query, (lesson_id, school_type))
        rows = cursor.fetchall()
        return [Curriculum(row["curriculum_id"], row["lesson_id"], row["grade"], row["weekly_hours"]) for row in rows]

    def add_or_update_curriculum(self, lesson_id: int, grade: int, weekly_hours: int, school_type: str) -> bool:
        """Add or update a curriculum entry for a lesson at a specific grade."""
        find_query = "SELECT curriculum_id FROM curriculum WHERE lesson_id = ? AND grade = ? AND school_type = ?"
        try:
            cursor = self._execute(find_query, (lesson_id, grade, school_type))
            row = cursor.fetchone()
            if row:
                update_query = "UPDATE curriculum SET weekly_hours = ? WHERE curriculum_id = ?"
                self._execute(update_query, (weekly_hours, row["curriculum_id"]))
            else:
                insert_query = "INSERT INTO curriculum (lesson_id, grade, weekly_hours, school_type) VALUES (?, ?, ?, ?)"
                self._execute(insert_query, (lesson_id, grade, weekly_hours, school_type))
            self._commit()
            return True
        except Exception as e:
            self.logger.error(f"Error adding/updating curriculum: {e}")
            return False

    def get_weekly_hours_for_lesson(self, lesson_id: int, grade: int, school_type: str) -> Optional[int]:
        """Get the weekly hours for a specific lesson and grade."""
        query = "SELECT weekly_hours FROM curriculum WHERE lesson_id = ? AND grade = ? AND school_type = ?"
        cursor = self._execute(query, (lesson_id, grade, school_type))
        row = cursor.fetchone()
        return row["weekly_hours"] if row else None
