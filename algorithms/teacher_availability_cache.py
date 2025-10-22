'''
This module provides a cache for teacher availability to reduce database queries
during the scheduling process.
'''
import logging
from collections import defaultdict

class TeacherAvailabilityCache:
    """
    Caches teacher availability data to minimize database lookups.

    This class loads all teacher non-available time slots into an in-memory
    dictionary for quick access, significantly speeding up the scheduling algorithms.
    """

    def __init__(self, db_manager):
        """
        Initializes the cache by loading all availability data from the database.

        Args:
            db_manager: An instance of the DatabaseManager to fetch data.
        """
        self.logger = logging.getLogger(__name__)
        self._db_manager = db_manager
        # The cache will store a set of (day, slot) tuples for each teacher_id
        # representing the times they are NOT available.
        self._cache = defaultdict(set)
        self._load_all_availability()

    def _load_all_availability(self):
        """
        Loads all teacher availability records from the database.
        This method is called once upon initialization.
        """
        self.logger.info("Initializing TeacherAvailabilityCache: Loading all teacher availability data...")
        try:
            all_teachers = self._db_manager.get_all_teachers()
            count = 0
            for teacher in all_teachers:
                # The get_teacher_availability now comes from the repository via db_manager
                availability_records = self._db_manager.get_teacher_availability(teacher.teacher_id)
                for record in availability_records:
                    if not record["is_available"]:
                        self._cache[teacher.teacher_id].add((record["day"], record["time_slot"]))
                        count += 1
            self.logger.info(f"Cache initialized successfully. Loaded {count} non-available slots.")
        except Exception as e:
            self.logger.error(f"Failed to load teacher availability cache: {e}", exc_info=True)

    def is_available(self, teacher_id: int, day: int, time_slot: int) -> bool:
        """
        Checks if a teacher is available at a specific day and time slot using the cache.

        Args:
            teacher_id: The ID of the teacher.
            day: The day of the week (e.g., 0 for Monday).
            time_slot: The time slot of the day.

        Returns:
            bool: True if the teacher is available, False otherwise.
        """
        # A teacher is considered available if their (day, time_slot) is NOT in the set
        # of non-available slots for them.
        return (day, time_slot) not in self._cache[teacher_id]

    def prefetch_for_teacher(self, teacher_id: int):
        """
        Manually pre-fetches or updates the availability for a single teacher.
        Useful if availability is changed dynamically.
        """
        self.logger.debug(f"Prefetching availability for teacher_id: {teacher_id}")
        # Clear existing cache for the teacher
        self._cache[teacher_id].clear()
        try:
            availability_records = self._db_manager.get_teacher_availability(teacher_id)
            for record in availability_records:
                if not record["is_available"]:
                    self._cache[teacher_id].add((record["day"], record["time_slot"]))
        except Exception as e:
            self.logger.error(f"Failed to prefetch availability for teacher {teacher_id}: {e}", exc_info=True)