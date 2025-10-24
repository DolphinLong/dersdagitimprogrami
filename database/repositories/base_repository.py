"""
Base Repository - Common database operations for all repositories.
Provides a base class with common CRUD operations and database connection handling.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, TypeVar, Generic
from abc import ABC, abstractmethod

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """
    Base repository class providing common database operations.

    This class provides:
    - Connection management through DBManager
    - Common CRUD operations
    - Error handling and logging
    - Connection cleanup

    All repository classes should inherit from this class.
    """

    def __init__(self, db_manager: 'DBManager'):
        """
        Initialize repository with database manager.

        Args:
            db_manager: DatabaseManager instance for connection handling
        """
        self.db_manager = db_manager
        self.logger = logging.getLogger(self.__class__.__name__)

    def _get_connection(self):
        """
        Get database connection from the manager.

        Returns:
            SQLite connection object
        """
        return self.db_manager.get_connection()

    def _safe_commit(self) -> bool:
        """
        Safely commit database changes.

        Returns:
            True if commit successful, False otherwise
        """
        return self.db_manager._safe_commit()

    def _execute_query(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results as list of dictionaries.

        Args:
            query: SQL query string
            params: Query parameters tuple

        Returns:
            List of dictionaries representing rows
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.error(f"Error executing query '{query}': {e}")
            return []

    def _execute_write(self, query: str, params: Tuple = ()) -> Optional[int]:
        """
        Execute an INSERT/UPDATE/DELETE query.

        Args:
            query: SQL query string
            params: Query parameters tuple

        Returns:
            Last row ID for INSERT operations, None for others
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            if not self._safe_commit():
                return None
            return cursor.lastrowid if cursor.lastrowid else None
        except Exception as e:
            self.logger.error(f"Error executing write query '{query}': {e}")
            return None

    @abstractmethod
    def _row_to_entity(self, row: Dict[str, Any]) -> Optional[T]:
        """
        Convert a database row dictionary to an entity object.

        Args:
            row: Database row as dictionary

        Returns:
            Entity object or None if conversion fails
        """
        pass

    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[T]:
        """
        Get entity by ID.

        Args:
            entity_id: Entity ID

        Returns:
            Entity object or None if not found
        """
        pass

    @abstractmethod
    def get_all(self) -> List[T]:
        """
        Get all entities.

        Returns:
            List of entity objects
        """
        pass
