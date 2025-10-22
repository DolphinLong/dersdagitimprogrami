'''
Repository for all database operations related to Classes and Classrooms.
'''
from typing import List, Optional

from database.models import Class, Classroom
from database.repositories.base_repository import BaseRepository

class ClassRepository(BaseRepository):
    """Handles all database operations for the Class and Classroom models."""

    def __init__(self, db_manager):
        """Initializes the repository with the DatabaseManager instance."""
        super().__init__(db_manager)

    def get_all_classes(self, school_type: str) -> List[Class]:
        """Get all classes for the given school type."""
        query = "SELECT * FROM classes WHERE school_type = ? ORDER BY name"
        cursor = self._execute(query, (school_type,))
        rows = cursor.fetchall()
        return [Class(row["class_id"], row["name"], row["grade"]) for row in rows]

    def get_class_by_id(self, class_id: int) -> Optional[Class]:
        """Get a class by its ID."""
        query = "SELECT * FROM classes WHERE class_id = ?"
        cursor = self._execute(query, (class_id,))
        row = cursor.fetchone()
        return Class(row["class_id"], row["name"], row["grade"]) if row else None

    def add_class(self, name: str, grade: int, school_type: str) -> Optional[int]:
        """Add a new class."""
        query = "INSERT INTO classes (name, grade, school_type) VALUES (?, ?, ?)"
        try:
            cursor = self._execute(query, (name, grade, school_type))
            self._commit()
            return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"Error adding class: {e}")
            return None

    def update_class(self, class_id: int, name: str, grade: int) -> bool:
        """Update an existing class."""
        query = "UPDATE classes SET name = ?, grade = ? WHERE class_id = ?"
        try:
            cursor = self._execute(query, (name, grade, class_id))
            self._commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.logger.error(f"Error updating class: {e}")
            return False

    def delete_class(self, class_id: int) -> bool:
        """Delete a class."""
        query = "DELETE FROM classes WHERE class_id = ?"
        try:
            # Also delete related schedule entries
            self._execute("DELETE FROM schedule WHERE class_id = ?", (class_id,))
            self._execute("DELETE FROM schedule_entries WHERE class_id = ?", (class_id,))
            cursor = self._execute(query, (class_id,))
            self._commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.logger.error(f"Error deleting class: {e}")
            return False

    # --- Classroom Methods ---

    def get_all_classrooms(self, school_type: str) -> List[Classroom]:
        """Get all classrooms for the given school type."""
        query = "SELECT * FROM classrooms WHERE school_type = ? ORDER BY name"
        cursor = self._execute(query, (school_type,))
        rows = cursor.fetchall()
        return [Classroom(row["classroom_id"], row["name"], row["capacity"]) for row in rows]

    def get_classroom_by_id(self, classroom_id: int) -> Optional[Classroom]:
        """Get a classroom by its ID."""
        query = "SELECT * FROM classrooms WHERE classroom_id = ?"
        cursor = self._execute(query, (classroom_id,))
        row = cursor.fetchone()
        return Classroom(row["classroom_id"], row["name"], row["capacity"]) if row else None

    def add_classroom(self, name: str, capacity: int, school_type: str) -> Optional[int]:
        """Add a new classroom."""
        query = "INSERT INTO classrooms (name, capacity, school_type) VALUES (?, ?, ?)"
        try:
            cursor = self._execute(query, (name, capacity, school_type))
            self._commit()
            return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"Error adding classroom: {e}")
            return None
