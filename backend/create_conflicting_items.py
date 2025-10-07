import os
import django
from datetime import date

# Django ayarlarını yapılandır
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ders_dagitim.settings')
django.setup()

# Modelleri içe aktar
from scheduling.models import Schedule, Teacher, Classroom, Course, TimeSlot, ScheduleItem

def create_conflicting_schedule_items():
    # Verileri al
    schedule = Schedule.objects.first()
    teacher1 = Teacher.objects.first()
    teacher2 = Teacher.objects.last()
    classroom = Classroom.objects.first()
    course1 = Course.objects.first()
    course2 = Course.objects.last()
    time_slot = TimeSlot.objects.first()
    
    if not all([schedule, teacher1, teacher2, classroom, course1, course2, time_slot]):
        print("Gerekli veriler bulunamadı")
        return
    
    # Farklı öğretmenler için çakışan iki ders oluştur (aynı sınıf ve zaman dilimi)
    try:
        # İlk ders
        item1 = ScheduleItem.objects.create(
            schedule=schedule,
            teacher=teacher1,
            classroom=classroom,
            course=course1,
            time_slot=time_slot,
            date=date(2023, 9, 4)
        )
        print(f"İlk ders oluşturuldu: {item1}")
        
        # İkinci ders (sınıf çakışması)
        item2 = ScheduleItem.objects.create(
            schedule=schedule,
            teacher=teacher2,
            classroom=classroom,
            course=course2,
            time_slot=time_slot,
            date=date(2023, 9, 4)
        )
        print(f"İkinci ders oluşturuldu: {item2}")
        
        print("Çakışan dersler başarıyla oluşturuldu")
    except Exception as e:
        print(f"Çakışan dersler oluşturulurken hata: {e}")

if __name__ == "__main__":
    create_conflicting_schedule_items()