import os
import django
from datetime import time, date

# Django ayarlarını yapılandır
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ders_dagitim.settings')
django.setup()

# Modelleri içe aktar
from scheduling.models import Teacher, Classroom, Course, TimeSlot, Schedule

def create_sample_data():
    # Öğretmenler
    teacher1 = Teacher.objects.create(
        first_name="Ahmet",
        last_name="Yılmaz",
        email="ahmet.yilmaz@okul.edu.tr",
        max_daily_hours=8,
        max_weekly_hours=40
    )
    
    teacher2 = Teacher.objects.create(
        first_name="Ayşe",
        last_name="Kaya",
        email="ayse.kaya@okul.edu.tr",
        max_daily_hours=6,
        max_weekly_hours=30
    )
    
    # Sınıflar
    classroom1 = Classroom.objects.create(
        name="A101",
        capacity=30,
        location="A Blok 1. Kat",
        has_projector=True,
        has_computer=False
    )
    
    classroom2 = Classroom.objects.create(
        name="B205",
        capacity=50,
        location="B Blok 2. Kat",
        has_projector=True,
        has_computer=True,
        is_lab=True
    )
    
    # Dersler
    course1 = Course.objects.create(
        code="MAT101",
        name="Matematik I",
        duration_hours=2,
        requires_projector=False
    )
    
    course2 = Course.objects.create(
        code="FIZ101",
        name="Fizik I",
        duration_hours=3,
        requires_projector=True,
        is_lab_course=True
    )
    
    # Zaman dilimleri
    time_slot1 = TimeSlot.objects.create(
        day=TimeSlot.MONDAY,
        start_time=time(9, 0),
        end_time=time(11, 0)
    )
    
    time_slot2 = TimeSlot.objects.create(
        day=TimeSlot.TUESDAY,
        start_time=time(10, 0),
        end_time=time(12, 0)
    )
    
    time_slot3 = TimeSlot.objects.create(
        day=TimeSlot.WEDNESDAY,
        start_time=time(13, 0),
        end_time=time(15, 0)
    )
    
    # Ders çizelgesi
    schedule = Schedule.objects.create(
        name="2023-2024 Güz Dönemi",
        start_date=date(2023, 9, 1),
        end_date=date(2024, 1, 31)
    )
    
    # İlişkileri kur
    course1.eligible_teachers.add(teacher1)
    course2.eligible_teachers.add(teacher2)
    
    print("Örnek veriler oluşturuldu:")
    print(f"- Öğretmenler: {Teacher.objects.count()}")
    print(f"- Sınıflar: {Classroom.objects.count()}")
    print(f"- Dersler: {Course.objects.count()}")
    print(f"- Zaman Dilimleri: {TimeSlot.objects.count()}")
    print(f"- Çizelgeler: {Schedule.objects.count()}")

if __name__ == "__main__":
    create_sample_data()