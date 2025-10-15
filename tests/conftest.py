# -*- coding: utf-8 -*-
"""
Pytest configuration and fixtures
"""

import os
import sys

import pytest
from PyQt5.QtWidgets import QApplication

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database.db_manager import DatabaseManager


# Ensure QApplication exists for pytest-qt
@pytest.fixture(scope="session")
def qapp():
    """Provide QApplication instance for all tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def db_manager():
    """Create a test database manager"""
    # Use in-memory database for tests
    db = DatabaseManager(":memory:")
    # Set default school type for tests
    db.set_school_type("Ortaokul")
    return db


@pytest.fixture
def sample_classes(db_manager):
    """Create sample classes for testing"""
    classes = []
    for grade in [5, 6, 7, 8]:
        for section in ["A", "B"]:
            class_id = db_manager.add_class(name=f"{grade}{section}", grade=grade)
            class_obj = db_manager.get_class_by_id(class_id)
            if class_obj:
                classes.append(class_obj)
    return classes


@pytest.fixture
def sample_teachers(db_manager):
    """Create sample teachers for testing"""
    teachers = []
    teacher_names = [
        ("Ahmet Yılmaz", "Matematik"),
        ("Ayşe Kaya", "Türkçe"),
        ("Mehmet Demir", "Fen Bilimleri"),
        ("Fatma Şahin", "İngilizce"),
        ("Ali Çelik", "Sosyal Bilgiler"),
    ]

    for name, subject in teacher_names:
        teacher_id = db_manager.add_teacher(name=name, subject=subject)
        teacher_obj = db_manager.get_teacher_by_id(teacher_id)
        if teacher_obj:
            teachers.append(teacher_obj)

    return teachers


@pytest.fixture
def sample_lessons(db_manager):
    """Create sample lessons for testing"""
    lessons = []
    lesson_names = [
        "Matematik",
        "Türkçe",
        "Fen Bilimleri",
        "İngilizce",
        "Sosyal Bilgiler",
        "Beden Eğitimi",
        "Müzik",
        "Görsel Sanatlar",
    ]

    for lesson_name in lesson_names:
        lesson_id = db_manager.add_lesson(name=lesson_name)
        lesson_obj = db_manager.get_lesson_by_id(lesson_id)
        if lesson_obj:
            lessons.append(lesson_obj)

    return lessons


@pytest.fixture
def sample_schedule_data(db_manager, sample_classes, sample_teachers, sample_lessons):
    """Create complete sample schedule data"""
    # Create a default classroom
    classroom_id = db_manager.add_classroom(name="Test Classroom", capacity=30)

    # Add weekly hours for lessons
    weekly_hours = {
        "Matematik": 5,
        "Türkçe": 5,
        "Fen Bilimleri": 4,
        "İngilizce": 4,
        "Sosyal Bilgiler": 3,
        "Beden Eğitimi": 2,
        "Müzik": 1,
        "Görsel Sanatlar": 1,
    }

    # Get lesson objects properly
    lessons = db_manager.get_all_lessons()
    for lesson in lessons:
        if lesson.name in weekly_hours:
            # Add weekly hours for each grade
            for grade in [5, 6, 7, 8]:
                db_manager.add_lesson_weekly_hours(
                    lesson_id=lesson.lesson_id,
                    grade=grade,
                    school_type="Ortaokul",
                    weekly_hours=weekly_hours[lesson.name],
                )

    # Create lesson assignments
    for class_obj in sample_classes:
        for i, lesson in enumerate(sample_lessons):
            # Assign teachers round-robin
            teacher = sample_teachers[i % len(sample_teachers)]

            db_manager.add_schedule_by_school_type(
                class_id=class_obj.class_id,
                lesson_id=lesson.lesson_id,
                teacher_id=teacher.teacher_id,
                classroom_id=classroom_id,
            )

    return {
        "classes": sample_classes,
        "teachers": sample_teachers,
        "lessons": sample_lessons,
        "classroom_id": classroom_id,
    }
