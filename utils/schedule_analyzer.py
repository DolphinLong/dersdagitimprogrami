"""
Schedule Analysis Tool
Analyzes why the schedule is not fully filled and provides insights
"""
import sys
from typing import List, Dict, Tuple
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

def analyze_schedule_filling(db_manager):
    """
    Analyze schedule filling issues and provide insights
    """
    print("=" * 80)
    print("DERS PROGRAMI DOLUM ANALIZI")
    print("=" * 80)
    
    # Get all required data
    classes = db_manager.get_all_classes()
    teachers = db_manager.get_all_teachers()
    lessons = db_manager.get_all_lessons()
    assignments = db_manager.get_schedule_by_school_type()
    
    print(f"Sınıflar: {len(classes)}")
    print(f"Öğretmenler: {len(teachers)}")
    print(f"Dersler: {len(lessons)}")
    print(f"Atamalar: {len(assignments)}")
    
    # Get school config
    school_type = db_manager.get_school_type() or "Lise"
    school_hours = {
        "İlkokul": 7,
        "Ortaokul": 7,
        "Lise": 8,
        "Anadolu Lisesi": 8,
        "Fen Lisesi": 8,
        "Sosyal Bilimler Lisesi": 8,
    }
    daily_hours = school_hours.get(school_type, 8)
    total_days = 5
    
    print(f"Okul Türü: {school_type} ({daily_hours} saat/gün)")
    
    # Calculate theoretical capacity
    total_theoretical_slots = len(classes) * total_days * daily_hours
    print(f"Toplam teorik slot: {total_theoretical_slots}")
    
    # Get current schedule
    current_schedule = db_manager.get_schedule_program_by_school_type()
    current_filled = len(current_schedule)
    print(f"Yerleştirilen ders: {current_filled}")
    print(f"Kullanım oranı: {current_filled/total_theoretical_slots*100:.1f}%")
    print(f"Boş slot: {total_theoretical_slots - current_filled}")
    
    print("\n" + "=" * 80)
    print("SINIFLARA GORE ANALIZ")
    print("=" * 80)
    
    for cls in classes:
        cls_schedule = [entry for entry in current_schedule if entry.class_id == cls.class_id]
        cls_theoretical = total_days * daily_hours
        cls_filled = len(cls_schedule)
        cls_percentage = (cls_filled / cls_theoretical * 100) if cls_theoretical > 0 else 0
        
        print(f"{cls.name}: {cls_filled}/{cls_theoretical} ({cls_percentage:.1f}%) - "
              f"{cls_theoretical - cls_filled} slot boş")
        
        # Get class assignments
        cls_assignments = [a for a in assignments if a.class_id == cls.class_id]
        total_required_hours = 0
        for assignment in cls_assignments:
            weekly_hours = db_manager.get_weekly_hours_for_lesson(assignment.lesson_id, cls.grade)
            if weekly_hours:
                total_required_hours += weekly_hours
                
        print(f"   Gereken toplam ders saati: {total_required_hours}, Yerleşen: {cls_filled}")
        
    print("\n" + "=" * 80)
    print("OGRETMENLERE GORE ANALIZ")
    print("=" * 80)
    
    for teacher in teachers[:10]:  # First 10 teachers
        teacher_schedule = [entry for entry in current_schedule if entry.teacher_id == teacher.teacher_id]
        print(f"{teacher.name} ({teacher.subject}): {len(teacher_schedule)} saat")
        
        # Check teacher availability
        availability_count = 0
        for day in range(5):
            for hour in range(daily_hours):
                if db_manager.is_teacher_available(teacher.teacher_id, day, hour):
                    availability_count += 1
        print(f"   Toplam uygunluk: {availability_count} saat")
    
    print("\n" + "=" * 80)
    print("DERSLERE GORE ANALIZ")
    print("=" * 80)
    
    # Check for lessons that couldn't be placed
    for assignment in assignments[:20]:  # First 20 assignments
        cls = next((c for c in classes if c.class_id == assignment.class_id), None)
        lesson = next((l for l in lessons if l.lesson_id == assignment.lesson_id), None)
        teacher = next((t for t in teachers if t.teacher_id == assignment.teacher_id), None)
        
        if cls and lesson and teacher:
            weekly_hours = db_manager.get_weekly_hours_for_lesson(lesson.lesson_id, cls.grade)
            placed_hours = len([e for e in current_schedule 
                              if e.class_id == cls.class_id and e.lesson_id == lesson.lesson_id])
            
            print(f"{cls.name} - {lesson.name}: {placed_hours}/{weekly_hours} saat "
                  f"({teacher.name}) - {'Eksik' if placed_hours < weekly_hours else 'Tam'}")
    
    print("\n" + "=" * 80)
    print("OLASI SORUNLAR VE COZUMLER")
    print("=" * 80)
    
    # Identify common filling issues
    issues = []
    
    # Issue 1: Teacher availability
    insufficient_teachers = []
    for assignment in assignments:
        cls = next((c for c in classes if c.class_id == assignment.class_id), None)
        if cls:
            weekly_hours = db_manager.get_weekly_hours_for_lesson(assignment.lesson_id, cls.grade)
            teacher = next((t for t in teachers if t.teacher_id == assignment.teacher_id), None)
            if teacher and weekly_hours:
                # Calculate teacher's total availability
                available_slots = 0
                for day in range(5):
                    for hour in range(daily_hours):
                        if db_manager.is_teacher_available(teacher.teacher_id, day, hour):
                            available_slots += 1
                if available_slots < weekly_hours:
                    insufficient_teachers.append((teacher.name, available_slots, weekly_hours, cls.name, lesson.name if 'lesson' in locals() else 'Unknown'))
    
    if insufficient_teachers:
        print("Ogretmen Uygunluk Sorunu:")
        for teacher_name, available, required, class_name, lesson_name in insufficient_teachers[:10]:
            print(f"   {teacher_name} ({class_name} - {lesson_name}): "
                  f"{available} saat uygun, {required} saat gerekli")
            issues.append(f"Ogretmen uygunlugu yetersiz: {teacher_name}")
    
    # Issue 2: Too many constraints
    print(f"\nToplam sinif kapasitesi: {total_theoretical_slots} saat")
    print(f"Gereken toplam ders saati: {sum(db_manager.get_weekly_hours_for_lesson(a.lesson_id, next((c for c in classes if c.class_id == a.class_id), type('', (), {'grade': 0})()).grade) or 0 for a in assignments)}")
    
    print(f"\nEtki edebilecek faktorler:")
    print("   • Ogretmen uygunluk saatleri")
    print("   • Blok ders kurallari (2+2+2, 2+2+1 vs.)")
    print("   • Ayni dersin farkli gunlerde yer alma zorunlulugu")
    print("   • Ardisik saat zorunluklari")
    print("   • Ogretmen cakisimalari")
    
    return {
        'total_slots': total_theoretical_slots,
        'filled_slots': current_filled,
        'fill_percentage': current_filled/total_theoretical_slots*100,
        'issues': issues,
        'classes_analysis': [{'name': c.name, 'filled': len([e for e in current_schedule if e.class_id == c.class_id]), 
                             'theoretical': total_days * daily_hours} for c in classes]
    }

if __name__ == "__main__":
    # This would normally run with a database manager
    print("Bu modül doğrudan çalıştırıldığında bir DB bağlantısı gerektirir.")
    print("Kullanım: analyze_schedule_filling(db_manager) fonksiyonunu çağırın.")