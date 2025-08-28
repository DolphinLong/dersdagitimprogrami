import os
import django
from datetime import date

# Django ayarlarını yapılandır
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ders_dagitim.settings')
django.setup()

# Modelleri içe aktar
from scheduling.models import Teacher, Classroom, Course, TimeSlot, Schedule, ScheduleItem, Constraint

def create_sample_constraints():
    # Örnek verileri al
    teacher1 = Teacher.objects.get(email="ahmet.yilmaz@okul.edu.tr")
    classroom1 = Classroom.objects.get(name="A101")
    course1 = Course.objects.get(code="MAT101")
    time_slot1 = TimeSlot.objects.get(day=TimeSlot.MONDAY, start_time__hour=9)
    
    # Zorunlu kısıtlama: Pazartesi sabahları matematik dersi olmasın
    constraint1 = Constraint.objects.create(
        name="Pazartesi Sabahları Matematik Kısıtlaması",
        description="Pazartesi sabahları matematik dersi verilmesin",
        constraint_type=Constraint.HARD,
        priority=5
    )
    constraint1.courses.add(course1)
    constraint1.time_slots.add(time_slot1)
    
    # Tercihli kısıtlama: Ahmet Yılmaz Pazartesi günleri erken gelmek istemiyor
    constraint2 = Constraint.objects.create(
        name="Ahmet Yılmaz Pazartesi Erken Gelme Kısıtlaması",
        description="Ahmet Yılmaz Pazartesi günleri 10:00'dan önce ders vermek istemiyor",
        constraint_type=Constraint.SOFT,
        priority=3
    )
    constraint2.teachers.add(teacher1)
    constraint2.days = [TimeSlot.MONDAY]
    
    # Zorunlu kısıtlama: A101 sınıfında laboratuvar dersi verilemez
    constraint3 = Constraint.objects.create(
        name="A101 Laboratuvar Kısıtlaması",
        description="A101 sınıfında laboratuvar dersi verilemez",
        constraint_type=Constraint.HARD,
        priority=8
    )
    constraint3.classrooms.add(classroom1)
    constraint3.courses.add(Course.objects.get(code="FIZ101"))  # Fizik lab dersi
    
    print("Örnek kısıtlamalar oluşturuldu:")
    print(f"- Toplam kısıtlama: {Constraint.objects.count()}")

if __name__ == "__main__":
    create_sample_constraints()