"""
Conflict checker for the Class Scheduling Program
"""

class ConflictChecker:
    """Handles conflict detection in schedules"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def check_teacher_conflict(self, teacher_id, day, time_slot, exclude_entry_id=None):
        """
        Check if a teacher has a conflict at a specific time
        Returns (has_conflict, conflicting_entry)
        """
        try:
            # Get all schedule entries for the current school type
            schedule_entries = self.db_manager.get_schedule_by_school_type()
            
            # Check for conflicts
            for entry in schedule_entries:
                # Skip the entry we're checking against (if specified)
                if exclude_entry_id and entry.entry_id == exclude_entry_id:
                    continue
                
                # Check if same teacher at same time
                if (entry.teacher_id == teacher_id and 
                    entry.day == day and 
                    entry.time_slot == time_slot):
                    return (True, entry)
            
            return (False, None)
        except Exception:
            # In case of any error, return no conflict
            return (False, None)
    
    def check_class_conflict(self, class_id, day, time_slot, exclude_entry_id=None):
        """
        Check if a class has a conflict at a specific time
        Returns (has_conflict, conflicting_entry)
        """
        try:
            # Get all schedule entries for the current school type
            schedule_entries = self.db_manager.get_schedule_by_school_type()
            
            # Check for conflicts
            for entry in schedule_entries:
                # Skip the entry we're checking against (if specified)
                if exclude_entry_id and entry.entry_id == exclude_entry_id:
                    continue
                
                # Check if same class at same time
                if (entry.class_id == class_id and 
                    entry.day == day and 
                    entry.time_slot == time_slot):
                    return (True, entry)
            
            return (False, None)
        except Exception:
            # In case of any error, return no conflict
            return (False, None)
    
    def check_classroom_conflict(self, classroom_id, day, time_slot, exclude_entry_id=None):
        """
        Check if a classroom has a conflict at a specific time
        Returns (has_conflict, conflicting_entry)
        """
        try:
            # Get all schedule entries for the current school type
            schedule_entries = self.db_manager.get_schedule_by_school_type()
            
            # Check for conflicts
            for entry in schedule_entries:
                # Skip the entry we're checking against (if specified)
                if exclude_entry_id and entry.entry_id == exclude_entry_id:
                    continue
                
                # Check if same classroom at same time
                if (entry.classroom_id == classroom_id and 
                    entry.day == day and 
                    entry.time_slot == time_slot):
                    return (True, entry)
            
            return (False, None)
        except Exception:
            # In case of any error, return no conflict
            return (False, None)
    
    def check_all_conflicts(self, schedule_entry):
        """
        Check all types of conflicts for a schedule entry
        Returns list of conflicts
        """
        conflicts = []
        
        # Check teacher conflict
        teacher_conflict, conflicting_entry = self.check_teacher_conflict(
            schedule_entry.teacher_id, 
            schedule_entry.day, 
            schedule_entry.time_slot,
            schedule_entry.entry_id if hasattr(schedule_entry, 'entry_id') else None
        )
        
        if teacher_conflict:
            conflicts.append({
                'type': 'teacher',
                'entry1': schedule_entry,
                'entry2': conflicting_entry,
                'message': f"Öğretmen çakışması: {schedule_entry.teacher_id}"
            })
        
        # Check class conflict
        class_conflict, conflicting_entry = self.check_class_conflict(
            schedule_entry.class_id, 
            schedule_entry.day, 
            schedule_entry.time_slot,
            schedule_entry.entry_id if hasattr(schedule_entry, 'entry_id') else None
        )
        
        if class_conflict:
            conflicts.append({
                'type': 'class',
                'entry1': schedule_entry,
                'entry2': conflicting_entry,
                'message': f"Sınıf çakışması: {schedule_entry.class_id}"
            })
        
        # Check classroom conflict
        classroom_conflict, conflicting_entry = self.check_classroom_conflict(
            schedule_entry.classroom_id, 
            schedule_entry.day, 
            schedule_entry.time_slot,
            schedule_entry.entry_id if hasattr(schedule_entry, 'entry_id') else None
        )
        
        if classroom_conflict:
            conflicts.append({
                'type': 'classroom',
                'entry1': schedule_entry,
                'entry2': conflicting_entry,
                'message': f"Derslik çakışması: {schedule_entry.classroom_id}"
            })
        
        return conflicts
    
    def validate_schedule_entry(self, schedule_entry):
        """
        Validate a schedule entry for all conflicts
        Returns (is_valid, conflicts)
        """
        conflicts = self.check_all_conflicts(schedule_entry)
        return (len(conflicts) == 0, conflicts)