# -*- coding: utf-8 -*-
"""
Tests for custom exceptions
"""

import pytest
from exceptions import (
    SchedulerError, ScheduleGenerationError, ConflictError,
    TeacherConflictError, ClassConflictError, AvailabilityError,
    CoverageError, ConfigurationError, DatabaseError, ValidationError
)


def test_scheduler_error():
    """Test base SchedulerError"""
    error = SchedulerError("Test error")
    assert str(error) == "Test error"
    assert isinstance(error, Exception)


def test_schedule_generation_error():
    """Test ScheduleGenerationError"""
    error = ScheduleGenerationError("Generation failed")
    assert isinstance(error, SchedulerError)


def test_conflict_error():
    """Test ConflictError with conflicts"""
    conflicts = [{'day': 0, 'slot': 0}]
    error = ConflictError("Conflict detected", conflicts=conflicts)
    
    assert isinstance(error, SchedulerError)
    assert error.conflicts == conflicts


def test_conflict_error_without_conflicts():
    """Test ConflictError without conflicts"""
    error = ConflictError("Conflict detected")
    assert error.conflicts == []


def test_teacher_conflict_error():
    """Test TeacherConflictError"""
    error = TeacherConflictError("Teacher conflict")
    assert isinstance(error, ConflictError)
    assert isinstance(error, SchedulerError)


def test_class_conflict_error():
    """Test ClassConflictError"""
    error = ClassConflictError("Class conflict")
    assert isinstance(error, ConflictError)
    assert isinstance(error, SchedulerError)


def test_availability_error():
    """Test AvailabilityError"""
    error = AvailabilityError("Teacher not available")
    assert isinstance(error, SchedulerError)


def test_coverage_error():
    """Test CoverageError"""
    error = CoverageError("Coverage too low")
    assert isinstance(error, SchedulerError)


def test_configuration_error():
    """Test ConfigurationError"""
    error = ConfigurationError("Invalid config")
    assert isinstance(error, SchedulerError)


def test_database_error():
    """Test DatabaseError"""
    error = DatabaseError("Database operation failed")
    assert isinstance(error, SchedulerError)


def test_validation_error():
    """Test ValidationError"""
    error = ValidationError("Validation failed")
    assert isinstance(error, SchedulerError)
