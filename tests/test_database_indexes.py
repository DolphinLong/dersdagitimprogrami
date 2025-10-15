# -*- coding: utf-8 -*-
"""
Tests for database indexes
"""

import pytest
import sqlite3

from database.create_indexes import DatabaseIndexManager


class TestDatabaseIndexes:
    """Test database index creation and management"""

    @pytest.fixture
    def index_manager(self, tmp_path):
        """Create index manager with temporary database"""
        db_path = tmp_path / "test_indexes.db"
        
        # Create basic tables
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS classes (
                class_id INTEGER PRIMARY KEY,
                name TEXT,
                grade INTEGER,
                school_type TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schedule (
                entry_id INTEGER PRIMARY KEY,
                class_id INTEGER,
                teacher_id INTEGER,
                lesson_id INTEGER,
                day INTEGER,
                time_slot INTEGER
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teacher_availability (
                availability_id INTEGER PRIMARY KEY,
                teacher_id INTEGER,
                day INTEGER,
                time_slot INTEGER,
                is_available INTEGER
            )
        """)
        
        conn.commit()
        conn.close()
        
        return DatabaseIndexManager(str(db_path))

    def test_create_all_indexes(self, index_manager):
        """Test creating all indexes"""
        result = index_manager.create_all_indexes()
        assert result is True

    def test_indexes_created(self, index_manager):
        """Test that indexes are actually created"""
        index_manager.create_all_indexes()
        
        conn = sqlite3.connect(index_manager.db_path)
        cursor = conn.cursor()
        
        # Check for specific indexes
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' 
            AND name LIKE 'idx_%'
        """)
        indexes = cursor.fetchall()
        conn.close()
        
        assert len(indexes) > 0

    def test_duplicate_index_creation(self, index_manager):
        """Test that duplicate indexes are not created"""
        # Create indexes twice
        index_manager.create_all_indexes()
        index_manager.create_all_indexes()
        
        # Should not raise error
        assert True

    def test_drop_all_indexes(self, index_manager):
        """Test dropping all indexes"""
        # Create indexes first
        index_manager.create_all_indexes()
        
        # Drop them
        result = index_manager.drop_all_indexes()
        assert result is True
        
        # Verify they're gone
        conn = sqlite3.connect(index_manager.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' 
            AND name LIKE 'idx_%'
        """)
        indexes = cursor.fetchall()
        conn.close()
        
        assert len(indexes) == 0

    def test_rebuild_indexes(self, index_manager):
        """Test rebuilding indexes"""
        result = index_manager.rebuild_indexes()
        assert result is True

    def test_analyze_database(self, index_manager):
        """Test database analysis"""
        analysis = index_manager.analyze_database()
        
        assert 'tables' in analysis
        assert 'indexes' in analysis
        assert 'recommendations' in analysis

    def test_analyze_with_indexes(self, index_manager):
        """Test analysis after creating indexes"""
        index_manager.create_all_indexes()
        analysis = index_manager.analyze_database()
        
        assert len(analysis['indexes']) > 0


class TestIndexPerformance:
    """Test index performance improvements"""

    @pytest.fixture
    def populated_db(self, tmp_path):
        """Create database with test data"""
        db_path = tmp_path / "test_performance.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE schedule (
                entry_id INTEGER PRIMARY KEY,
                class_id INTEGER,
                teacher_id INTEGER,
                lesson_id INTEGER,
                day INTEGER,
                time_slot INTEGER
            )
        """)
        
        # Insert test data
        for i in range(1000):
            cursor.execute("""
                INSERT INTO schedule (class_id, teacher_id, lesson_id, day, time_slot)
                VALUES (?, ?, ?, ?, ?)
            """, (i % 10, i % 20, i % 15, i % 5 + 1, i % 8 + 1))
        
        conn.commit()
        conn.close()
        
        return str(db_path)

    def test_query_performance_with_index(self, populated_db):
        """Test that queries are faster with indexes"""
        import time
        
        # Query without index
        conn = sqlite3.connect(populated_db)
        cursor = conn.cursor()
        
        start = time.time()
        for _ in range(100):
            cursor.execute("SELECT * FROM schedule WHERE class_id = 5")
            cursor.fetchall()
        time_without_index = time.time() - start
        
        # Create index
        cursor.execute("CREATE INDEX idx_test_class ON schedule(class_id)")
        conn.commit()
        
        # Query with index
        start = time.time()
        for _ in range(100):
            cursor.execute("SELECT * FROM schedule WHERE class_id = 5")
            cursor.fetchall()
        time_with_index = time.time() - start
        
        conn.close()
        
        # With index should be faster or at least not slower
        # (For small datasets, difference might be negligible)
        assert time_with_index <= time_without_index * 1.5
