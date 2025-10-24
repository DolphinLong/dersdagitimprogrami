"""
Repository for all database operations related to Classes and Classrooms.
"""
from typing import List, Optional
from database.models import Class, Classroom
from database.repositories.base_repository import BaseRepository


class ClassRepository(BaseRepository[Class]):
    """Handles all database operations for the Class model."""

    def _row_to_entity(self, row: dict) -> Optional[Class]:
        """Convert database row to Class entity."""
        return Class(
            class_id=row.get("class_id"),
            name=row.get("name"),
            grade=row.get("grade")
        )

    def get_by_id(self, class_id: int) -> Optional[Class]:
        """Get a class by its ID."""
        query = "SELECT * FROM classes WHERE class_id = ?"
        rows = self._execute_query(query, (class_id,))
        return self._row_to_entity(rows[0]) if rows else None
    
    def get_class_by_id(self, class_id: int) -> Optional[Class]:
        """Get a class by its ID (alias for get_by_id)."""
        return self.get_by_id(class_id)

    def get_all(self) -> List[Class]:
        """Get all classes."""
        query = "SELECT * FROM classes ORDER BY name"
        rows = self._execute_query(query)
        return [self._row_to_entity(row) for row in rows if row]

    def get_all_classes(self, school_type: str) -> List[Class]:
        """Get all classes for the given school type."""
        query = "SELECT * FROM classes WHERE school_type = ? ORDER BY name"
        rows = self._execute_query(query, (school_type,))
        return [self._row_to_entity(row) for row in rows if row]

    def add_class(self, name: str, grade: int, school_type: str) -> Optional[int]:
        """Add a new class."""
        query = "INSERT INTO classes (name, grade, school_type) VALUES (?, ?, ?)"
        return self._execute_write(query, (name, grade, school_type))

    def update_class(self, class_id: int, name: str, grade: int) -> bool:
        """Update an existing class."""
        query = "UPDATE classes SET name = ?, grade = ? WHERE class_id = ?"
        result = self._execute_write(query, (name, grade, class_id))
        return result is not None

    def delete_class(self, class_id: int) -> bool:
        """Delete a class and related records."""
        try:
            # Delete related schedule entries first
            self._execute_write("DELETE FROM schedule_entries WHERE class_id = ?", (class_id,))
            # Delete from schedule
            self._execute_write("DELETE FROM schedule WHERE class_id = ?", (class_id,))
            # Finally, delete the class
            result = self._execute_write("DELETE FROM classes WHERE class_id = ?", (class_id,))
            return result is not None
        except Exception as e:
            self.logger.error(f"Error deleting class: {e}")
            return False

    # Classroom operations
    def get_all_classrooms(self, school_type: str) -> List[Classroom]:
        """Get all classrooms for the given school type."""
        query = "SELECT * FROM classrooms WHERE school_type = ? ORDER BY name"
        rows = self._execute_query(query, (school_type,))
        return [Classroom(
            classroom_id=row["classroom_id"],
            name=row["name"],
            capacity=row["capacity"]
        ) for row in rows]

    def get_classroom_by_id(self, classroom_id: int) -> Optional[Classroom]:
        """Get a classroom by its ID."""
        query = "SELECT * FROM classrooms WHERE classroom_id = ?"
        rows = self._execute_query(query, (classroom_id,))
        if rows:
            row = rows[0]
            return Classroom(
                classroom_id=row["classroom_id"],
                name=row["name"],
                capacity=row["capacity"]
            )
        return None

    def add_classroom(self, name: str, capacity: int, school_type: str) -> Optional[int]:
        """Add a new classroom."""
        query = "INSERT INTO classrooms (name, capacity, school_type) VALUES (?, ?, ?)"
        return self._execute_write(query, (name, capacity, school_type))
