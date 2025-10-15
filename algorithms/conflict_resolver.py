"""
Conflict resolver for the Class Scheduling Program
"""

import logging


class ConflictResolver:
    """Handles conflict resolution in schedules"""

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)

    def resolve_teacher_conflict(self, conflict):
        """
        Attempt to resolve a teacher conflict by moving one of the conflicting entries
        Returns True if conflict was resolved, False otherwise
        """
        try:
            entry1 = conflict["entry1"]
            entry2 = conflict["entry2"]

            # Try to move entry2 to a different time slot
            self.logger.info(f"Attempting to resolve teacher conflict by moving entry: {entry2}")
            moved = self._move_entry_to_available_slot(entry2)
            if moved:
                self.logger.info(f"Successfully resolved teacher conflict by moving entry: {entry2}")
                return True

            # If that didn't work, try to move entry1
            self.logger.info(f"Attempting to resolve teacher conflict by moving entry: {entry1}")
            moved = self._move_entry_to_available_slot(entry1)
            if moved:
                self.logger.info(f"Successfully resolved teacher conflict by moving entry: {entry1}")
            return moved
        except Exception as e:
            self.logger.error(f"Error resolving teacher conflict: {e}", exc_info=True)
            return False

    def resolve_class_conflict(self, conflict):
        """
        Attempt to resolve a class conflict by moving one of the conflicting entries
        Returns True if conflict was resolved, False otherwise
        """
        try:
            entry1 = conflict["entry1"]
            entry2 = conflict["entry2"]

            # Try to move entry2 to a different time slot
            self.logger.info(f"Attempting to resolve class conflict by moving entry: {entry2}")
            moved = self._move_entry_to_available_slot(entry2)
            if moved:
                self.logger.info(f"Successfully resolved class conflict by moving entry: {entry2}")
                return True

            # If that didn't work, try to move entry1
            self.logger.info(f"Attempting to resolve class conflict by moving entry: {entry1}")
            moved = self._move_entry_to_available_slot(entry1)
            if moved:
                self.logger.info(f"Successfully resolved class conflict by moving entry: {entry1}")
            return moved
        except Exception as e:
            self.logger.error(f"Error resolving class conflict: {e}", exc_info=True)
            return False

    def _move_entry_to_available_slot(self, entry):
        """
        Try to move an entry to an available time slot
        Returns True if moved successfully, False otherwise
        """
        # Get the class and teacher for this entry
        class_obj = self.db_manager.get_class_by_id(entry.class_id)
        teacher = self.db_manager.get_teacher_by_id(entry.teacher_id)

        if not class_obj or not teacher:
            return False

        # Try to find an available slot for this class and teacher
        for day in range(5):  # Monday to Friday
            # Get school type to determine time slots
            school_type = self.db_manager.get_school_type()
            if not school_type:
                school_type = "Lise"

            time_slots_count = 8  # Default to 8 time slots
            if school_type == "İlkokul":
                time_slots_count = 6
            elif school_type == "Ortaokul":
                time_slots_count = 7

            for time_slot in range(time_slots_count):
                # Skip the current slot
                if day == entry.day and time_slot == entry.time_slot:
                    continue

                # Check if class is available at this time
                class_conflict = self._check_class_conflict_at_time(class_obj.class_id, day, time_slot, entry.entry_id)
                if class_conflict:
                    continue

                # Check if teacher is available at this time
                teacher_conflict = self._check_teacher_conflict_at_time(
                    teacher.teacher_id, day, time_slot, entry.entry_id
                )
                if teacher_conflict:
                    continue

                # If we get here, this slot is available
                # Update the entry
                success = self.db_manager.update_schedule_entry(
                    entry.entry_id,
                    entry.class_id,
                    entry.teacher_id,
                    entry.lesson_id,
                    entry.classroom_id,
                    day,
                    time_slot,
                )

                return success

        # No available slot found
        return False

    def _check_class_conflict_at_time(self, class_id, day, time_slot, exclude_entry_id=None):
        """Check if a class has a conflict at a specific time"""
        schedule_entries = self.db_manager.get_schedule_by_school_type()

        for entry in schedule_entries:
            # Skip the entry we're checking against (if specified)
            if exclude_entry_id and entry.entry_id == exclude_entry_id:
                continue

            # Check if same class at same time
            if entry.class_id == class_id and entry.day == day and entry.time_slot == time_slot:
                return True

        return False

    def _check_teacher_conflict_at_time(self, teacher_id, day, time_slot, exclude_entry_id=None):
        """Check if a teacher has a conflict at a specific time"""
        schedule_entries = self.db_manager.get_schedule_by_school_type()

        for entry in schedule_entries:
            # Skip the entry we're checking against (if specified)
            if exclude_entry_id and entry.entry_id == exclude_entry_id:
                continue

            # Check if same teacher at same time
            if entry.teacher_id == teacher_id and entry.day == day and entry.time_slot == time_slot:
                return True

        return False

    def auto_resolve_conflicts(self, conflicts):
        """
        Attempt to automatically resolve all conflicts
        Returns the number of conflicts resolved
        """
        resolved_count = 0
        self.logger.info(f"Starting auto-resolution for {len(conflicts)} conflicts.")

        try:
            # Try to resolve each conflict
            for conflict in conflicts:
                conflict_type = conflict["type"]

                if "teacher" in conflict_type:
                    resolved = self.resolve_teacher_conflict(conflict)
                elif "class" in conflict_type:
                    resolved = self.resolve_class_conflict(conflict)
                else:
                    # For other types of conflicts, try a generic approach
                    entry1 = conflict["entry1"]
                    self.logger.info(f"Attempting to resolve generic conflict by moving entry: {entry1}")
                    resolved = self._move_entry_to_available_slot(entry1)

                if resolved:
                    resolved_count += 1

            self.logger.info(f"Auto-resolution finished. Resolved {resolved_count} conflicts.")
            return resolved_count
        except Exception as e:
            self.logger.error(f"An error occurred during auto-resolution: {e}", exc_info=True)
            return resolved_count
