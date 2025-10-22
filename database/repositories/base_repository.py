
'''
Base Repository class providing common database functionalities.
'''
import logging
import sqlite3

class BaseRepository:
    """
    A base class for repositories that provides a shared database connection
    and basic execution helpers.
    """
    def __init__(self, db_manager):
        """
        Initializes the repository with the DatabaseManager instance.
        Args:
            db_manager: An instance of the DatabaseManager.
        """
        self._db_manager = db_manager
        self.logger = logging.getLogger(self.__class__.__name__)

    def _execute(self, sql: str, params: tuple = None) -> sqlite3.Cursor:
        """
        Executes a given SQL query using the thread-safe connection from the db_manager.

        Args:
            sql (str): The SQL query to execute.
            params (tuple, optional): Parameters to substitute into the query. Defaults to None.

        Returns:
            sqlite3.Cursor: The cursor object after execution.
        """
        try:
            # Get the thread-local connection for every execution
            conn = self._db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute(sql, params or ())
            return cursor
        except sqlite3.Error as e:
            self.logger.error(f"Database error in _execute: {e}\nQuery: {sql}\nParams: {params}", exc_info=True)
            raise

    def _commit(self):
        """Commits the current transaction via the db_manager."""
        self._db_manager._safe_commit()
