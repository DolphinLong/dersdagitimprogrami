# -*- coding: utf-8 -*-
"""
End-to-End Tests - Complete user workflows
"""

import pytest

from algorithms.simple_perfect_scheduler import SimplePerfectScheduler
from database.db_manager import DatabaseManager


@pytest.mark.integration
class TestCompleteSchoolSetup:
    """Test complete school setup workflow"""

    def test_new_school_setup_workflow(self, db_manager):
        """Test setting up a new school from scratch"""
        # Step 1: Set school type
        db_manager.set_school_type("Lise")
        assert db_manager.get_school_type() == "Lise"
        
        # Step 2: Add classes
        class_9a = db_manager.add_class("9-A", 9)
        class_9b = db_manager.add_class("9-B", 9)
        class_10a = db_manager.add_class("10-A", 10)
        
        assert class_9a is not None
        assert class_9b is not None
        assert class_10a is not None
        
        # Step 3: Add teachers
        math_teacher = db_manager.add_teacher("Ahmet Yılmaz", "Matematik")
        physics_teacher = db_manager.add_teacher("Ayşe Demir", "Fizik")
        chemistry_teacher = db_manager.add_teacher("Mehmet Kaya", "Kimya")
        
        assert math_teacher is not None
        assert physics_teacher is not None
        assert chemistry_teacher is not None
        
        # Step 4: Add lessons
        math_lesson = db_manager.add_lesson("Matematik", 5)
        physics_lesson = db_manager.add_lesson("Fizik", 4)
        chemistry_lesson = db_manager.add_lesson("Kimya", 3)
        
        assert math_lesson is not None
        assert physics_lesson is not None
        assert chemistry_lesson is not None
        
        # Step 5: Add classrooms
        classroom_a101 = db_manager.add_classroom("A101", 30)
        classroom_a102 = db_manager.add_classroom("A102", 30)
        
        assert classroom_a101 is not None
        assert classroom_a102 is not None
        
        # Step 6: Assign lessons to classes
        db_manager.add_lesson_assignment(class_9a, math_lesson, math_teacher, 5)
        db_manager.add_lesson_assignment(class_9a, physics_lesson, physics_teacher, 4)
        db_manager.add_lesson_assignment(class_9a, chemistry_lesson, chemistry_teacher, 3)
        
        # Step 7: Set teacher availability
        for teacher_id in [math_teacher, physics_teacher, chemistry_teacher]:
            for day in range(1, 6):  # Mon-Fri
                for slot in range(1, 9):  # 8 slots
                    db_manager.set_teacher_availability(teacher_id, day, slot, 1)
        
        # Step 8: Generate schedule
        scheduler = SimplePerfectScheduler(db_manager)
        schedule = scheduler.generate_schedule()
        
        assert isinstance(schedule, list)
        
        # Step 9: Verify schedule was created
        class_schedule = db_manager.get_class_schedule(class_9a)
        assert isinstance(class_schedule, list)


@pytest.mark.integration
class TestScheduleModificationWorkflow:
    """Test schedule modification workflows"""

    def test_update_existing_schedule(self, db_manager, sample_schedule_data):
        """Test updating an existing schedule"""
        # Generate initial schedule
        scheduler = SimplePerfectScheduler(db_manager)
        initial_schedule = scheduler.generate_schedule()
        
        # Modify some data (e.g., change teacher availability)
        teachers = db_manager.get_all_teachers()
        if teachers:
            teacher = teachers[0]
            # Reduce availability
            db_manager.set_teacher_availability(teacher.teacher_id, 1, 1, 0)
        
        # Regenerate schedule
        new_schedule = scheduler.generate_schedule()
        
        assert isinstance(new_schedule, list)

    def test_add_new_class_to_existing_schedule(self, db_manager, sample_schedule_data):
        """Test adding a new class to existing schedule"""
        # Generate initial schedule
        scheduler = SimplePerfectScheduler(db_manager)
        scheduler.generate_schedule()
        
        # Add new class
        new_class_id = db_manager.add_class("11-C", 11)
        assert new_class_id is not None
        
        # Add lesson assignments for new class
        lessons = db_manager.get_all_lessons()
        teachers = db_manager.get_all_teachers()
        
        if lessons and teachers:
            db_manager.add_lesson_assignment(
                new_class_id, lessons[0].lesson_id, teachers[0].teacher_id, 4
            )
        
        # Regenerate schedule
        new_schedule = scheduler.generate_schedule()
        assert isinstance(new_schedule, list)


@pytest.mark.integration
class TestReportGenerationWorkflow:
    """Test report generation workflows"""

    def test_generate_class_report(self, db_manager, sample_schedule_data):
        """Test generating class schedule report"""
        classes = db_manager.get_all_classes()
        
        if classes:
            for class_obj in classes[:3]:  # First 3 classes
                schedule = db_manager.get_class_schedule(class_obj.class_id)
                assert isinstance(schedule, list)

    def test_generate_teacher_report(self, db_manager, sample_schedule_data):
        """Test generating teacher schedule report"""
        teachers = db_manager.get_all_teachers()
        
        if teachers:
            for teacher in teachers[:3]:  # First 3 teachers
                schedule = db_manager.get_teacher_schedule(teacher.teacher_id)
                assert isinstance(schedule, list)

    def test_generate_all_reports(self, db_manager, sample_schedule_data):
        """Test generating all reports"""
        # Class reports
        classes = db_manager.get_all_classes()
        class_reports = []
        for class_obj in classes:
            schedule = db_manager.get_class_schedule(class_obj.class_id)
            class_reports.append(schedule)
        
        # Teacher reports
        teachers = db_manager.get_all_teachers()
        teacher_reports = []
        for teacher in teachers:
            schedule = db_manager.get_teacher_schedule(teacher.teacher_id)
            teacher_reports.append(schedule)
        
        assert len(class_reports) == len(classes)
        assert len(teacher_reports) == len(teachers)


@pytest.mark.integration
class TestDataImportExportWorkflow:
    """Test data import/export workflows"""

    def test_export_school_data(self, db_manager, sample_schedule_data):
        """Test exporting school data"""
        # Get all data
        classes = db_manager.get_all_classes()
        teachers = db_manager.get_all_teachers()
        lessons = db_manager.get_all_lessons()
        classrooms = db_manager.get_all_classrooms()
        
        # Verify data exists
        assert len(classes) > 0
        assert len(teachers) > 0
        assert len(lessons) > 0

    def test_bulk_import_workflow(self, db_manager):
        """Test bulk importing data"""
        # Simulate bulk import
        classes_data = [
            ("9-A", 9), ("9-B", 9), ("10-A", 10), ("10-B", 10)
        ]
        
        class_ids = []
        for name, grade in classes_data:
            class_id = db_manager.add_class(name, grade)
            class_ids.append(class_id)
        
        # Verify all imported
        assert len(class_ids) == len(classes_data)
        assert all(cid is not None for cid in class_ids)


@pytest.mark.integration
class TestUserJourneys:
    """Test complete user journeys"""

    def test_admin_user_journey(self, db_manager):
        """Test complete admin user journey"""
        # 1. Admin logs in
        admin_id = db_manager.add_user("admin", "admin_password", "admin")
        admin = db_manager.get_user("admin", "admin_password")
        assert admin is not None
        assert admin.role == "admin"
        
        # 2. Admin sets up school
        db_manager.set_school_type("Lise")
        
        # 3. Admin adds teachers
        teacher_id = db_manager.add_teacher("New Teacher", "Math")
        assert teacher_id is not None
        
        # 4. Admin adds classes
        class_id = db_manager.add_class("9-A", 9)
        assert class_id is not None
        
        # 5. Admin generates schedule
        scheduler = SimplePerfectScheduler(db_manager)
        schedule = scheduler.generate_schedule()
        assert isinstance(schedule, list)

    def test_teacher_user_journey(self, db_manager, sample_schedule_data):
        """Test complete teacher user journey"""
        # 1. Teacher logs in
        teacher_user_id = db_manager.add_user("teacher1", "teacher_pass", "teacher")
        teacher_user = db_manager.get_user("teacher1", "teacher_pass")
        assert teacher_user is not None
        
        # 2. Teacher views their schedule
        teachers = db_manager.get_all_teachers()
        if teachers:
            schedule = db_manager.get_teacher_schedule(teachers[0].teacher_id)
            assert isinstance(schedule, list)
        
        # 3. Teacher sets availability
        if teachers:
            db_manager.set_teacher_availability(teachers[0].teacher_id, 1, 1, 1)
            availability = db_manager.get_teacher_availability(teachers[0].teacher_id)
            assert len(availability) > 0


@pytest.mark.integration
class TestErrorScenarios:
    """Test error handling in complete workflows"""

    def test_incomplete_setup_workflow(self, db_manager):
        """Test workflow with incomplete setup"""
        # Set school type but don't add any data
        db_manager.set_school_type("Lise")
        
        # Try to generate schedule
        scheduler = SimplePerfectScheduler(db_manager)
        schedule = scheduler.generate_schedule()
        
        # Should handle gracefully
        assert isinstance(schedule, list)

    def test_conflicting_data_workflow(self, db_manager):
        """Test workflow with conflicting data"""
        db_manager.set_school_type("Lise")
        
        # Add class and teacher
        class_id = db_manager.add_class("9-A", 9)
        teacher_id = db_manager.add_teacher("Teacher", "Math")
        lesson_id = db_manager.add_lesson("Math", 4)
        
        # Add assignment
        db_manager.add_lesson_assignment(class_id, lesson_id, teacher_id, 4)
        
        # Set very limited availability (conflict scenario)
        db_manager.set_teacher_availability(teacher_id, 1, 1, 1)
        
        # Try to schedule
        scheduler = SimplePerfectScheduler(db_manager)
        schedule = scheduler.generate_schedule()
        
        # Should handle conflict gracefully
        assert isinstance(schedule, list)


@pytest.mark.integration
class TestMultiSchoolScenarios:
    """Test scenarios with multiple schools/databases"""

    def test_independent_databases(self, tmp_path):
        """Test multiple independent school databases"""
        # Create two separate databases
        db1_path = tmp_path / "school1.db"
        db2_path = tmp_path / "school2.db"
        
        db1 = DatabaseManager(str(db1_path))
        db2 = DatabaseManager(str(db2_path))
        
        # Setup school 1
        db1.set_school_type("İlkokul")
        class1 = db1.add_class("1-A", 1)
        
        # Setup school 2
        db2.set_school_type("Lise")
        class2 = db2.add_class("9-A", 9)
        
        # Verify independence
        assert db1.get_school_type() == "İlkokul"
        assert db2.get_school_type() == "Lise"
        
        db1.close_connection()
        db2.close_connection()
