# -*- coding: utf-8 -*-
"""
Custom Exception Classes for Scheduler
"""


class SchedulerError(Exception):
    """Base exception for all scheduler errors"""

    pass


class ScheduleGenerationError(SchedulerError):
    """Raised when schedule generation fails"""

    pass


class ConflictError(SchedulerError):
    """Raised when a scheduling conflict is detected"""

    def __init__(self, message, conflicts=None):
        super().__init__(message)
        self.conflicts = conflicts or []


class TeacherConflictError(ConflictError):
    """Raised when a teacher has conflicting assignments"""

    pass


class ClassConflictError(ConflictError):
    """Raised when a class has conflicting lessons"""

    pass


class AvailabilityError(SchedulerError):
    """Raised when teacher availability constraints are violated"""

    pass


class CoverageError(SchedulerError):
    """Raised when coverage requirements cannot be met"""

    pass


class ConfigurationError(SchedulerError):
    """Raised when configuration is invalid"""

    pass


class DatabaseError(SchedulerError):
    """Raised when database operations fail"""

    pass


class ValidationError(SchedulerError):
    """Raised when validation fails"""

    pass
