"""
Data models for the Class Scheduling Program
"""


class User:
    """User model"""

    def __init__(self, user_id, username, password, role):
        self.user_id = user_id
        self.username = username
        self.password = password  # In a real application, this should be hashed
        self.role = role  # admin, teacher, student


class Teacher:
    """Teacher model"""

    def __init__(self, teacher_id, name, subject):
        self.teacher_id = teacher_id
        self.name = name
        self.subject = subject


class Class:
    """Class model"""

    def __init__(self, class_id, name, grade):
        self.class_id = class_id
        self.name = name
        self.grade = grade


class Classroom:
    """Classroom model"""

    def __init__(self, classroom_id, name, capacity):
        self.classroom_id = classroom_id
        self.name = name
        self.capacity = capacity


class Lesson:
    """Lesson model - represents a unique lesson name."""

    def __init__(self, lesson_id, name, weekly_hours=0):
        self.lesson_id = lesson_id
        self.name = name
        self.weekly_hours = weekly_hours


class Curriculum:
    """Curriculum model linking lessons to grades and weekly hours."""

    def __init__(self, curriculum_id, lesson_id, grade, weekly_hours):
        self.curriculum_id = curriculum_id
        self.lesson_id = lesson_id
        self.grade = grade
        self.weekly_hours = weekly_hours


class ScheduleEntry:
    """Schedule entry model"""

    def __init__(self, entry_id, class_id, teacher_id, lesson_id, classroom_id, day, time_slot):
        self.entry_id = entry_id
        self.class_id = class_id
        self.teacher_id = teacher_id
        self.lesson_id = lesson_id
        self.classroom_id = classroom_id
        self.day = day
        self.time_slot = time_slot
