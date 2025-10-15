# -*- coding: utf-8 -*-
"""
Database Index Creation and Optimization
Creates indexes for frequently queried columns to improve performance
"""

import logging
import sqlite3
from typing import List, Tuple

logger = logging.getLogger(__name__)


class DatabaseIndexManager:
    """Manages database indexes for performance optimization"""

    def __init__(self, db_path: str = "schedule.db"):
        """
        Initialize index manager
        
        Args:
            db_path: Path to database file
        """
        self.db_path = db_path

    def create_all_indexes(self) -> bool:
        """
        Create all recommended indexes
        
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get list of indexes to create
            indexes = self._get_index_definitions()

            created_count = 0
            for index_name, create_sql in indexes:
                try:
                    # Check if index already exists
                    cursor.execute(
                        "SELECT name FROM sqlite_master WHERE type='index' AND name=?",
                        (index_name,)
                    )
                    if cursor.fetchone():
                        logger.info(f"Index {index_name} already exists, skipping")
                        continue

                    # Create index
                    cursor.execute(create_sql)
                    created_count += 1
                    logger.info(f"Created index: {index_name}")

                except sqlite3.Error as e:
                    logger.error(f"Error creating index {index_name}: {e}")

            conn.commit()
            conn.close()

            logger.info(f"Created {created_count} new indexes")
            return True

        except sqlite3.Error as e:
            logger.error(f"Error creating indexes: {e}")
            return False

    def _get_index_definitions(self) -> List[Tuple[str, str]]:
        """
        Get list of index definitions
        
        Returns:
            List of (index_name, create_sql) tuples
        """
        return [
            # Classes table indexes
            (
                "idx_classes_school_type",
                "CREATE INDEX idx_classes_school_type ON classes(school_type)"
            ),
            (
                "idx_classes_grade",
                "CREATE INDEX idx_classes_grade ON classes(grade)"
            ),
            
            # Teachers table indexes
            (
                "idx_teachers_subject",
                "CREATE INDEX idx_teachers_subject ON teachers(subject)"
            ),
            (
                "idx_teachers_school_type",
                "CREATE INDEX idx_teachers_school_type ON teachers(school_type)"
            ),
            
            # Lessons table indexes
            (
                "idx_lessons_name",
                "CREATE INDEX idx_lessons_name ON lessons(name)"
            ),
            
            # Schedule table indexes (most critical for performance)
            (
                "idx_schedule_class_id",
                "CREATE INDEX idx_schedule_class_id ON schedule(class_id)"
            ),
            (
                "idx_schedule_teacher_id",
                "CREATE INDEX idx_schedule_teacher_id ON schedule(teacher_id)"
            ),
            (
                "idx_schedule_lesson_id",
                "CREATE INDEX idx_schedule_lesson_id ON schedule(lesson_id)"
            ),
            (
                "idx_schedule_day_slot",
                "CREATE INDEX idx_schedule_day_slot ON schedule(day, time_slot)"
            ),
            (
                "idx_schedule_class_day",
                "CREATE INDEX idx_schedule_class_day ON schedule(class_id, day)"
            ),
            (
                "idx_schedule_teacher_day",
                "CREATE INDEX idx_schedule_teacher_day ON schedule(teacher_id, day)"
            ),
            
            # Lesson assignments indexes
            (
                "idx_lesson_assignments_class",
                "CREATE INDEX idx_lesson_assignments_class ON lesson_assignments(class_id)"
            ),
            (
                "idx_lesson_assignments_lesson",
                "CREATE INDEX idx_lesson_assignments_lesson ON lesson_assignments(lesson_id)"
            ),
            (
                "idx_lesson_assignments_teacher",
                "CREATE INDEX idx_lesson_assignments_teacher ON lesson_assignments(teacher_id)"
            ),
            (
                "idx_lesson_assignments_class_lesson",
                "CREATE INDEX idx_lesson_assignments_class_lesson ON lesson_assignments(class_id, lesson_id)"
            ),
            
            # Teacher availability indexes
            (
                "idx_teacher_availability_teacher",
                "CREATE INDEX idx_teacher_availability_teacher ON teacher_availability(teacher_id)"
            ),
            (
                "idx_teacher_availability_day_slot",
                "CREATE INDEX idx_teacher_availability_day_slot ON teacher_availability(day, time_slot)"
            ),
            (
                "idx_teacher_availability_teacher_day",
                "CREATE INDEX idx_teacher_availability_teacher_day ON teacher_availability(teacher_id, day)"
            ),
            
            # Curriculum indexes
            (
                "idx_curriculum_lesson",
                "CREATE INDEX idx_curriculum_lesson ON curriculum(lesson_id)"
            ),
            (
                "idx_curriculum_grade",
                "CREATE INDEX idx_curriculum_grade ON curriculum(grade)"
            ),
            
            # Users table indexes
            (
                "idx_users_username",
                "CREATE INDEX idx_users_username ON users(username)"
            ),
            (
                "idx_users_role",
                "CREATE INDEX idx_users_role ON users(role)"
            ),
        ]

    def drop_all_indexes(self) -> bool:
        """
        Drop all custom indexes (useful for testing)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get all custom indexes
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' 
                AND name LIKE 'idx_%'
            """)
            indexes = cursor.fetchall()

            dropped_count = 0
            for (index_name,) in indexes:
                try:
                    cursor.execute(f"DROP INDEX {index_name}")
                    dropped_count += 1
                    logger.info(f"Dropped index: {index_name}")
                except sqlite3.Error as e:
                    logger.error(f"Error dropping index {index_name}: {e}")

            conn.commit()
            conn.close()

            logger.info(f"Dropped {dropped_count} indexes")
            return True

        except sqlite3.Error as e:
            logger.error(f"Error dropping indexes: {e}")
            return False

    def analyze_database(self) -> dict:
        """
        Analyze database and provide index recommendations
        
        Returns:
            Dictionary with analysis results
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get table sizes
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' 
                AND name NOT LIKE 'sqlite_%'
            """)
            tables = cursor.fetchall()

            analysis = {
                'tables': {},
                'indexes': {},
                'recommendations': []
            }

            for (table_name,) in tables:
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]

                analysis['tables'][table_name] = {
                    'rows': row_count
                }

            # Get existing indexes
            cursor.execute("""
                SELECT name, tbl_name, sql 
                FROM sqlite_master 
                WHERE type='index'
                AND name LIKE 'idx_%'
            """)
            indexes = cursor.fetchall()

            for index_name, table_name, sql in indexes:
                analysis['indexes'][index_name] = {
                    'table': table_name,
                    'sql': sql
                }

            # Generate recommendations
            if analysis['tables'].get('schedule', {}).get('rows', 0) > 100:
                if 'idx_schedule_class_id' not in analysis['indexes']:
                    analysis['recommendations'].append(
                        "Create index on schedule(class_id) for better query performance"
                    )

            conn.close()

            return analysis

        except sqlite3.Error as e:
            logger.error(f"Error analyzing database: {e}")
            return {}

    def rebuild_indexes(self) -> bool:
        """
        Rebuild all indexes (drop and recreate)
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("Rebuilding all indexes...")
        
        # Drop existing indexes
        if not self.drop_all_indexes():
            return False
        
        # Recreate indexes
        if not self.create_all_indexes():
            return False
        
        logger.info("Index rebuild complete")
        return True


def main():
    """Main function for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database Index Management")
    parser.add_argument(
        "--db-path",
        default="schedule.db",
        help="Path to database file"
    )
    parser.add_argument(
        "--action",
        choices=["create", "drop", "rebuild", "analyze"],
        default="create",
        help="Action to perform"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    
    manager = DatabaseIndexManager(args.db_path)
    
    if args.action == "create":
        manager.create_all_indexes()
    elif args.action == "drop":
        manager.drop_all_indexes()
    elif args.action == "rebuild":
        manager.rebuild_indexes()
    elif args.action == "analyze":
        analysis = manager.analyze_database()
        print("\n=== Database Analysis ===")
        print(f"\nTables: {len(analysis.get('tables', {}))}")
        for table, info in analysis.get('tables', {}).items():
            print(f"  {table}: {info['rows']} rows")
        
        print(f"\nIndexes: {len(analysis.get('indexes', {}))}")
        for index in analysis.get('indexes', {}).keys():
            print(f"  {index}")
        
        print(f"\nRecommendations: {len(analysis.get('recommendations', []))}")
        for rec in analysis.get('recommendations', []):
            print(f"  - {rec}")


if __name__ == "__main__":
    main()
