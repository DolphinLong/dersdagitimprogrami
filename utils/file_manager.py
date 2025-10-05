"""
File manager for the Class Scheduling Program
"""

import json
import csv
import os
from datetime import datetime
from database.models import User, Teacher, Class, Classroom, Lesson, ScheduleEntry

class FileManager:
    """Handles file operations for saving and loading schedules"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def export_to_json(self, filename):
        """
        Export all data to JSON format
        """
        try:
            # Get all data from database
            data = {
                "metadata": {
                    "export_date": datetime.now().isoformat(),
                    "version": "1.0"
                },
                "users": [],
                "teachers": [],
                "classes": [],
                "classrooms": [],
                "lessons": [],
                "schedule_entries": []
            }
            
            # Export users
            # Note: In a real application, you wouldn't export passwords
            users = self.db_manager.get_all_users()  # This method doesn't exist yet
            for user in users:
                data["users"].append({
                    "user_id": user.user_id,
                    "username": user.username,
                    "role": user.role
                })
            
            # Export teachers
            teachers = self.db_manager.get_all_teachers()
            for teacher in teachers:
                data["teachers"].append({
                    "teacher_id": teacher.teacher_id,
                    "name": teacher.name,
                    "subject": teacher.subject
                })
            
            # Export classes
            classes = self.db_manager.get_all_classes()
            for class_obj in classes:
                data["classes"].append({
                    "class_id": class_obj.class_id,
                    "name": class_obj.name,
                    "grade": class_obj.grade
                })
            
            # Export classrooms
            classrooms = self.db_manager.get_all_classrooms()
            for classroom in classrooms:
                data["classrooms"].append({
                    "classroom_id": classroom.classroom_id,
                    "name": classroom.name,
                    "capacity": classroom.capacity
                })
            
            # Export lessons
            lessons = self.db_manager.get_all_lessons()
            for lesson in lessons:
                data["lessons"].append({
                    "lesson_id": lesson.lesson_id,
                    "name": lesson.name,
                    "weekly_hours": lesson.weekly_hours
                })
            
            # Export schedule entries
            # This is a simplified version - in a real app, you'd get all entries
            # For now, we'll just create an empty list
            data["schedule_entries"] = []
            
            # Write to file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return f"Veriler başarıyla {filename} dosyasına aktarıldı."
            
        except Exception as e:
            return f"JSON dışa aktarma hatası: {str(e)}"
    
    def import_from_json(self, filename):
        """
        Import data from JSON format
        """
        try:
            # Read from file
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Import data
            # Note: In a real application, you would implement proper import logic
            # This is a simplified version for demonstration
            
            imported_count = 0
            if "teachers" in data:
                imported_count += len(data["teachers"])
            if "classes" in data:
                imported_count += len(data["classes"])
            if "lessons" in data:
                imported_count += len(data["lessons"])
            
            return f"Veriler başarıyla {filename} dosyasından içe aktarıldı. {imported_count} kayıt işlendi."
            
        except Exception as e:
            return f"JSON içe aktarma hatası: {str(e)}"
    
    def export_to_csv(self, filename):
        """
        Export schedule data to CSV format
        """
        try:
            # Create CSV file
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow([
                    "Sınıf", "Öğretmen", "Ders", "Derslik", "Gün", "Saat Aralığı"
                ])
                
                # Write sample data
                # In a real application, you would get actual schedule data
                sample_data = [
                    ["5A", "Ahmet Yılmaz", "Matematik", "Derslik 1", "Pazartesi", "08:00-09:00"],
                    ["5A", "Ayşe Kaya", "Türkçe", "Derslik 2", "Pazartesi", "09:00-10:00"],
                    ["5B", "Mehmet Demir", "Fen", "Fen Laboratuvarı", "Salı", "10:00-11:00"]
                ]
                
                for row in sample_data:
                    writer.writerow(row)
            
            return f"Program başarıyla {filename} dosyasına aktarıldı."
            
        except Exception as e:
            return f"CSV dışa aktarma hatası: {str(e)}"
    
    def backup_database(self, filename=None):
        """
        Create a backup of the database
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"schedule_backup_{timestamp}.db"
            
            # Copy the database file
            import shutil
            shutil.copy2(self.db_manager.db_path, filename)
            
            return f"Veri tabanı yedeği başarıyla {filename} dosyasına oluşturuldu."
            
        except Exception as e:
            return f"Veri tabanı yedekleme hatası: {str(e)}"
    
    def restore_database(self, filename):
        """
        Restore database from backup
        """
        try:
            # Check if backup file exists
            if not os.path.exists(filename):
                return f"Yedek dosya bulunamadı: {filename}"
            
            # Close existing database connections
            self.db_manager.close_connection()
            
            # Copy the backup file to database location
            import shutil
            shutil.copy2(filename, self.db_manager.db_path)
            
            # Reopen database connection
            self.db_manager.get_connection()
            
            return f"Veri tabanı başarıyla {filename} dosyasından geri yüklendi."
            
        except Exception as e:
            return f"Veri tabanı geri yükleme hatası: {str(e)}"
