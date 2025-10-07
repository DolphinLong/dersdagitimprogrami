import os
import django
from datetime import date
import unittest

# Django ayarlarını yapılandır
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ders_dagitim.settings')
django.setup()

# Modelleri ve algoritmaları içe aktar
from scheduling.models import Teacher, Classroom, Course, TimeSlot, Schedule, ScheduleItem
from scheduling.algorithms import SchedulingAlgorithm
from scheduling.adaptive_learning import AdaptiveLearningEngine

class SchedulingAlgorithmTest(unittest.TestCase):

    def setUp(self):
        # Temiz bir başlangıç için mevcut verileri sil
        Schedule.objects.all().delete()
        Teacher.objects.all().delete()
        Classroom.objects.all().delete()
        Course.objects.all().delete()
        TimeSlot.objects.all().delete()
        ScheduleItem.objects.all().delete()

        # Test verilerini oluştur
        self.schedule = Schedule.objects.create(name="Test Schedule", start_date=date.today(), end_date=date.today())
        self.teacher1 = Teacher.objects.create(first_name="Ahmet", last_name="Yılmaz", email="ahmet.yilmaz@example.com")
        self.teacher2 = Teacher.objects.create(first_name="Ayşe", last_name="Kaya", email="ayse.kaya@example.com")
        self.classroom1 = Classroom.objects.create(name="A101", capacity=30)
        self.classroom2 = Classroom.objects.create(name="B205", capacity=25)
        self.course1 = Course.objects.create(name="Matematik", code="MAT101")
        self.course2 = Course.objects.create(name="Fizik", code="FIZ101")
        self.time_slot1 = TimeSlot.objects.create(day=TimeSlot.MONDAY, start_time="09:00:00", end_time="10:00:00")
        self.time_slot2 = TimeSlot.objects.create(day=TimeSlot.TUESDAY, start_time="10:00:00", end_time="11:00:00")
        self.algorithm = SchedulingAlgorithm(self.schedule)

    def test_1_create_schedule_item(self):
        """Temel ders planlama"""
        success, schedule_item, errors = self.algorithm.create_schedule_item(
            self.course1, self.teacher1, self.classroom1, self.time_slot1, date(2023, 9, 4)
        )
        self.assertTrue(success)
        self.assertIsNotNone(schedule_item)
        self.assertEqual(len(errors), 0)

    def test_2_teacher_conflict(self):
        """Aynı öğretmenin çakışan dersi"""
        # İlk dersi planla
        self.algorithm.create_schedule_item(
            self.course1, self.teacher1, self.classroom1, self.time_slot1, date(2023, 9, 4)
        )
        # Aynı öğretmen için çakışan bir ders planla
        success, schedule_item, errors = self.algorithm.create_schedule_item(
            self.course2, self.teacher1, self.classroom2, self.time_slot1, date(2023, 9, 4)
        )
        self.assertFalse(success)
        self.assertIsNone(schedule_item)
        self.assertIn('teacher_conflict', [error['type'] for error in errors])

    def test_3_classroom_conflict(self):
        """Aynı sınıfın çakışan dersi"""
        # İlk dersi planla
        self.algorithm.create_schedule_item(
            self.course1, self.teacher1, self.classroom1, self.time_slot1, date(2023, 9, 4)
        )
        # Aynı sınıf için çakışan bir ders planla
        success, schedule_item, errors = self.algorithm.create_schedule_item(
            self.course2, self.teacher2, self.classroom1, self.time_slot1, date(2023, 9, 4)
        )
        self.assertFalse(success)
        self.assertIsNone(schedule_item)
        self.assertIn('classroom_conflict', [error['type'] for error in errors])

    def test_4_find_conflicts(self):
        """Çakışma kontrolü"""
        # Çakışan iki ders planla
        ScheduleItem.objects.create(
            schedule=self.schedule,
            course=self.course1,
            teacher=self.teacher1,
            classroom=self.classroom1,
            time_slot=self.time_slot1,
            date=date(2023, 9, 4)
        )
        ScheduleItem.objects.create(
            schedule=self.schedule,
            course=self.course2,
            teacher=self.teacher2,
            classroom=self.classroom1,
            time_slot=self.time_slot1,
            date=date(2023, 9, 4)
        )
        conflicts = self.algorithm.find_conflicts()
        self.assertGreater(len(conflicts), 0)

    def test_5_create_valid_schedule_item(self):
        """Geçerli bir ders planlama"""
        success, schedule_item, errors = self.algorithm.create_schedule_item(
            self.course2, self.teacher2, self.classroom2, self.time_slot2, date(2023, 9, 5)
        )
        self.assertTrue(success)
        self.assertIsNotNone(schedule_item)
        self.assertEqual(len(errors), 0)

class AdaptiveLearningTest(unittest.TestCase):
    def test_adaptive_learning(self):
        engine = AdaptiveLearningEngine()
        engine.initialize()
        trends = engine.analyze_performance_trends()
        patterns = engine.detect_patterns(trends)
        engine.apply_learning_patterns(patterns)
        engine.generate_improvement_suggestions(trends)
        engine.learn_from_ml_data()
        engine.get_system_health_report()
        engine.auto_improve()

if __name__ == '__main__':
    unittest.main()