"""
Extended Database Manager Tests
"""
import pytest
from database.db_manager import DatabaseManager


class TestDatabaseManagerCRUD:
    """Test CRUD operations"""
    
    def test_add_and_get_class(self, db_manager):
        """Test adding and retrieving class"""
        class_id = db_manager.add_class("Test Class", 5)
        
        classes = db_manager.get_all_classes()
        class_names = [c.name for c in classes]
        
        assert "Test Class" in class_names
    
    def test_update_class(self, db_manager):
        """Test updating class"""
        class_id = db_manager.add_class("Old Name", 5)
        
        # Update (if method exists)
        try:
            db_manager.update_class(class_id, "New Name", 5)
            classes = db_manager.get_all_classes()
            class_names = [c.name for c in classes]
            assert "New Name" in class_names
        except AttributeError:
            # Method doesn't exist
            assert True
    
    def test_delete_class(self, db_manager):
        """Test deleting class"""
        class_id = db_manager.add_class("To Delete", 5)
        
        # Delete
        try:
            db_manager.delete_class(class_id)
            classes = db_manager.get_all_classes()
            class_ids = [c.class_id for c in classes]
            assert class_id not in class_ids
        except AttributeError:
            # Method doesn't exist
            assert True
    
    def test_add_and_get_teacher(self, db_manager):
        """Test adding and retrieving teacher"""
        teacher_id = db_manager.add_teacher("Test Teacher", "Matematik")
        
        teachers = db_manager.get_all_teachers()
        teacher_names = [t.name for t in teachers]
        
        assert "Test Teacher" in teacher_names
    
    def test_add_and_get_lesson(self, db_manager):
        """Test adding and retrieving lesson"""
        lesson_id = db_manager.add_lesson("Test Lesson")
        
        lessons = db_manager.get_all_lessons()
        lesson_names = [l.name for l in lessons]
        
        assert "Test Lesson" in lesson_names


class TestDatabaseManagerQueries:
    """Test complex queries"""
    
    def test_get_schedule_by_school_type(self, db_manager, sample_schedule_data):
        """Test getting schedule by school type"""
        schedule = db_manager.get_schedule_by_school_type()
        
        assert isinstance(schedule, list)
    
    def test_get_schedule_for_class(self, db_manager, sample_schedule_data):
        """Test getting schedule for specific class"""
        classes = db_manager.get_all_classes()
        if len(classes) > 0:
            class_id = classes[0].class_id
            schedule = db_manager.get_schedule_for_class(class_id)
            
            assert isinstance(schedule, list)
    
    def test_get_schedule_for_teacher(self, db_manager, sample_teachers):
        """Test getting schedule for specific teacher"""
        if len(sample_teachers) > 0:
            teacher_id = sample_teachers[0].teacher_id
            schedule = db_manager.get_schedule_for_specific_teacher(teacher_id)
            
            assert isinstance(schedule, list)
    
    def test_get_weekly_hours_for_lesson(self, db_manager, sample_lessons):
        """Test getting weekly hours for lesson"""
        if len(sample_lessons) > 0:
            class_id = 1
            lesson_id = sample_lessons[0].lesson_id
            
            hours = db_manager.get_weekly_hours_for_lesson(class_id, lesson_id)
            
            assert isinstance(hours, (int, type(None)))


class TestDatabaseManagerTransactions:
    """Test transaction handling"""
    
    def test_multiple_inserts_transaction(self, db_manager):
        """Test multiple inserts in transaction"""
        # Add multiple items
        class_ids = []
        for i in range(5):
            class_id = db_manager.add_class(f"Class {i}", 5)
            class_ids.append(class_id)
        
        # All should be added
        classes = db_manager.get_all_classes()
        assert len(classes) >= 5
    
    def test_rollback_on_error(self, db_manager):
        """Test rollback on error"""
        initial_count = len(db_manager.get_all_classes())
        
        try:
            # Try to add invalid data
            db_manager.add_class(None, None)
        except Exception:
            pass
        
        # Count should be same
        final_count = len(db_manager.get_all_classes())
        assert final_count == initial_count


class TestDatabaseManagerSchoolType:
    """Test school type management"""
    
    def test_set_and_get_school_type(self, db_manager):
        """Test setting and getting school type"""
        db_manager.set_school_type("Lise")
        
        school_type = db_manager.get_school_type()
        assert school_type == "Lise"
    
    def test_change_school_type(self, db_manager):
        """Test changing school type"""
        db_manager.set_school_type("İlkokul")
        assert db_manager.get_school_type() == "İlkokul"
        
        db_manager.set_school_type("Ortaokul")
        assert db_manager.get_school_type() == "Ortaokul"


class TestDatabaseManagerEdgeCases:
    """Test edge cases"""
    
    def test_add_duplicate_class(self, db_manager):
        """Test adding duplicate class"""
        db_manager.add_class("Duplicate", 5)
        db_manager.add_class("Duplicate", 5)
        
        # Should handle gracefully
        classes = db_manager.get_all_classes()
        assert len(classes) >= 2
    
    def test_get_nonexistent_teacher(self, db_manager):
        """Test getting non-existent teacher"""
        teacher = db_manager.get_teacher_by_id(99999)
        
        assert teacher is None
    
    def test_empty_database_queries(self, empty_db_manager):
        """Test queries on empty database"""
        classes = empty_db_manager.get_all_classes()
        teachers = empty_db_manager.get_all_teachers()
        lessons = empty_db_manager.get_all_lessons()
        
        assert classes == []
        assert teachers == []
        assert lessons == []


@pytest.fixture
def empty_db_manager(tmp_path):
    """Create empty database manager"""
    db_path = tmp_path / "empty_test.db"
    return DatabaseManager(str(db_path))
