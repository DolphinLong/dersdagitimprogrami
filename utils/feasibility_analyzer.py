"""
Schedule Feasibility Analyzer
Identifies structural issues that prevent 100% filling
"""
import sys
import os
from typing import List, Dict, Tuple, Set

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

def analyze_schedule_feasibility(db_manager):
    """
    Deep analysis to identify why 100% filling is not possible
    """
    print("=" * 80)
    print("EĞİTİM PROGRAMI UYGUNLUK ANALİZİ")
    print("=" * 80)
    
    # Get all required data
    classes = db_manager.get_all_classes()
    teachers = db_manager.get_all_teachers()
    lessons = db_manager.get_all_lessons()
    assignments = db_manager.get_schedule_by_school_type()
    
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
    
    print(f"Sınıflar: {len(classes)}")
    print(f"Öğretmenler: {len(teachers)}")
    print(f"Dersler: {len(lessons)}")
    print(f"Atamalar: {len(assignments)}")
    print(f"Okul Türü: {school_type} ({daily_hours} saat/gün)")
    
    # Calculate total theoretical capacity
    total_theoretical_slots = len(classes) * total_days * daily_hours
    print(f"Toplam teorik slot: {total_theoretical_slots}")
    
    # 1. ANALYZE TEACHER CAPACITY
    print("\n" + "=" * 80)
    print("ÖĞRETMEN KAPASİTE ANALİZİ")
    print("=" * 80)
    
    teacher_capacity_issues = []
    for teacher in teachers:
        # Calculate teacher's total available hours per week
        available_hours = 0
        for day in range(total_days):
            for hour in range(daily_hours):
                if db_manager.is_teacher_available(teacher.teacher_id, day, hour):
                    available_hours += 1
        
        # Calculate how many hours this teacher is assigned
        assigned_hours = 0
        for assignment in assignments:
            if assignment.teacher_id == teacher.teacher_id:
                lesson_grade = next((c.grade for c in classes if c.class_id == assignment.class_id), 0)
                weekly_hours = db_manager.get_weekly_hours_for_lesson(assignment.lesson_id, lesson_grade)
                if weekly_hours:
                    assigned_hours += weekly_hours
        
        print(f"{teacher.name} ({teacher.subject}):")
        print(f"   - Uygun saat: {available_hours}")
        print(f"   - Atanmış ders: {assigned_hours}")
        print(f"   - Kullanım oranı: {assigned_hours/available_hours*100:.1f}% " if available_hours > 0 else "   - Uygun saat yok")
        
        if assigned_hours > available_hours:
            teacher_capacity_issues.append({
                'teacher': teacher.name,
                'subject': teacher.subject,
                'available': available_hours,
                'assigned': assigned_hours
            })
    
    if teacher_capacity_issues:
        print("\nUyarı: Öğretmen kapasite sorunları:")
        for issue in teacher_capacity_issues:
            print(f"   - {issue['teacher']} ({issue['subject']}): "
                  f"{issue['available']} saat uygun, {issue['assigned']} saat atanmış")
    else:
        print("\nOgretmen kapasiteleri yeterli")
    
    # 2. ANALYZE CLASS REQUIREMENTS
    print("\n" + "=" * 80)
    print("SINIF GEREKSİNİM ANALİZİ")
    print("=" * 80)
    
    class_requirement_issues = []
    total_required_hours = 0
    
    for cls in classes:
        # Get all lessons assigned to this class
        class_assignments = [a for a in assignments if a.class_id == cls.class_id]
        class_required_hours = 0
        
        for assignment in class_assignments:
            weekly_hours = db_manager.get_weekly_hours_for_lesson(assignment.lesson_id, cls.grade)
            if weekly_hours:
                class_required_hours += weekly_hours
        
        theoretical_capacity = total_days * daily_hours
        print(f"{cls.name}:")
        print(f"   - Gereken ders saati: {class_required_hours}")
        print(f"   - Teorik kapasite: {theoretical_capacity}")
        print(f"   - Fark: {class_required_hours - theoretical_capacity}")
        
        if class_required_hours > theoretical_capacity:
            class_requirement_issues.append({
                'class': cls.name,
                'required': class_required_hours,
                'capacity': theoretical_capacity
            })
        
        total_required_hours += class_required_hours
    
    print(f"\nToplam gereken ders saati: {total_required_hours}")
    print(f"Toplam kullanılabilir kapasite: {total_theoretical_slots}")
    
    if class_requirement_issues:
        print("\nUyarı: Sınıf kapasite sorunları:")
        for issue in class_requirement_issues:
            print(f"   - {issue['class']}: {issue['required']} saat gerekli, "
                  f"{issue['capacity']} saat mevcut")
    else:
        print("\nSinif kapasiteleri yeterli")
    
    # 3. ANALYZE LESSON STRUCTURE
    print("\n" + "=" * 80)
    print("DERS YAPISI ANALİZİ")
    print("=" * 80)
    
    lesson_structure_issues = []
    
    for assignment in assignments:
        cls = next((c for c in classes if c.class_id == assignment.class_id), None)
        lesson = next((l for l in lessons if l.lesson_id == assignment.lesson_id), None)
        teacher = next((t for t in teachers if t.teacher_id == assignment.teacher_id), None)
        
        if cls and lesson and teacher:
            weekly_hours = db_manager.get_weekly_hours_for_lesson(lesson.lesson_id, cls.grade)
            if weekly_hours:
                print(f"{cls.name} - {lesson.name}: {weekly_hours} saat ({teacher.name})")
                
                # Check if this can be scheduled based on teacher availability
                teacher_available_slots = 0
                for day in range(total_days):
                    for hour in range(daily_hours):
                        if db_manager.is_teacher_available(teacher.teacher_id, day, hour):
                            teacher_available_slots += 1
                
                if weekly_hours > teacher_available_slots:
                    lesson_structure_issues.append({
                        'class': cls.name,
                        'lesson': lesson.name,
                        'teacher': teacher.name,
                        'required': weekly_hours,
                        'available': teacher_available_slots
                    })
    
    if lesson_structure_issues:
        print("\nUyarı: Ders yapısı sorunları:")
        for issue in lesson_structure_issues:
            print(f"   - {issue['class']} - {issue['lesson']} ({issue['teacher']}): "
                  f"{issue['required']} saat gerekli, {issue['available']} saat uygun")
    else:
        print("\nDers yapilari uygun")
    
    # 4. ANALYZE BLOCK CONSTRAINTS
    print("\n" + "=" * 80)
    print("BLOK KISITLAMA ANALİZİ")
    print("=" * 80)
    
    # Check for lessons that require block distribution (e.g., 3 hours -> 2+1)
    block_constraint_issues = []
    
    for assignment in assignments:
        cls = next((c for c in classes if c.class_id == assignment.class_id), None)
        lesson = next((l for l in lessons if l.lesson_id == assignment.lesson_id), None)
        
        if cls and lesson:
            weekly_hours = db_manager.get_weekly_hours_for_lesson(lesson.lesson_id, cls.grade)
            if weekly_hours and weekly_hours > 2:
                # This lesson likely needs block distribution
                print(f"{cls.name} - {lesson.name}: {weekly_hours} saat")
                
                # Calculate how many different days at least needed
                # For example: 6 hours might need 3 days (2+2+2), 5 hours might need 3 days (2+2+1)
                min_days_needed = weekly_hours // 2 + (1 if weekly_hours % 2 > 0 else 0)
                
                if min_days_needed > total_days:
                    block_constraint_issues.append({
                        'class': cls.name,
                        'lesson': lesson.name,
                        'hours': weekly_hours,
                        'min_days_needed': min_days_needed,
                        'available_days': total_days
                    })
    
    if block_constraint_issues:
        print("\nUyarı: Blok kısıtlama sorunları:")
        for issue in block_constraint_issues:
            print(f"   - {issue['class']} - {issue['lesson']}: {issue['hours']} saat, "
                  f"minimum {issue['min_days_needed']} gün gerekli ama sadece {issue['available_days']} gün var")
    else:
        print("\nBlok kisitlamalari uygun")
    
    # 5. SUMMARY OF ALL ISSUES
    print("\n" + "=" * 80)
    print("TÜM SORUNLARIN ÖZETİ")
    print("=" * 80)
    
    all_issues = {
        'teacher_capacity': teacher_capacity_issues,
        'class_requirement': class_requirement_issues,
        'lesson_structure': lesson_structure_issues,
        'block_constraint': block_constraint_issues
    }
    
    total_issues = sum(len(issues) for issues in all_issues.values())
    
    if total_issues == 0:
        print("Herhangi bir yapisal sorun bulunamadi. Doluluk orani teorik maximum olmali.")
    else:
        print(f"Toplam {total_issues} yapisal sorun tespit edildi")
        
        if teacher_capacity_issues:
            print(f"   Ogretmen kapasite sorunlari: {len(teacher_capacity_issues)}")
        
        if class_requirement_issues:
            print(f"   Sinif gereksinim sorunlari: {len(class_requirement_issues)}")
        
        if lesson_structure_issues:
            print(f"   Ders yapisi sorunlari: {len(lesson_structure_issues)}")
        
        if block_constraint_issues:
            print(f"   Blok kisitlama sorunlari: {len(block_constraint_issues)}")
    
    # 6. RECOMMENDATIONS
    print("\n" + "=" * 80)
    print("ÖNERİLEN DÜZELTİCİ ÖNLEMLER")
    print("=" * 80)
    
    if teacher_capacity_issues:
        print("Ogretmen uygunluk saatlerini artirin")
        print("Eksik dersler icin daha fazla ogretmen atayin")
        print("Ogretmen yuklerini dengeleyin")
    
    if class_requirement_issues:
        print("Sinif ders saatlerini gozden gecirin")
        print("Gereksiz ders saatlerini azaltin")
        print("Gerektiginde haftalik saat sayisini artirin")
    
    if lesson_structure_issues:
        print("Ogretmen uygunluk saatlerini genisletin")
        print("Ders atamalarini optimize edin")
        print("Ayni dersi birden fazla ogretmene atayin")
    
    if block_constraint_issues:
        print("Blok ders kurallarinda esneklik saglayin")
        print("Daha kucuk blok boyutlarina izin verin")
    
    if total_issues == 0:
        print("Sistem yapisal olarak dolumu artirabilecek yeterliliktetir")
        print("Daha gelismis algoritmalar kullanilabilir")
        print("Ogretmen tercihlerini optimize edin")
    
    return {
        'theoretical_capacity': total_theoretical_slots,
        'required_hours': total_required_hours,
        'issues': all_issues,
        'total_issues': total_issues,
        'recommendations': [
            'Öğretmen uygunluk saatlerini artırın',
            'Ders atamalarını gözden geçirin', 
            'Blok ders kurallarında esneklik sağlayın'
        ] if total_issues > 0 else ['Sistem yapısal olarak dolumu artırabilecek yeterliliktedir']
    }

def suggest_data_improvements(db_manager):
    """
    Suggest specific data improvements to increase filling rate
    """
    print("\n" + "=" * 80)
    print("VERİ İYİLEŞTİRME ÖNERİLERİ")
    print("=" * 80)
    
    classes = db_manager.get_all_classes()
    assignments = db_manager.get_schedule_by_school_type()
    
    # Find classes with lowest filling rates
    class_filling_rates = []
    for cls in classes:
        cls_assignments = [a for a in assignments if a.class_id == cls.class_id]
        total_required = 0
        for assignment in cls_assignments:
            weekly_hours = db_manager.get_weekly_hours_for_lesson(assignment.lesson_id, cls.grade)
            if weekly_hours:
                total_required += weekly_hours
        
        # Get current schedule for this class
        current_schedule = db_manager.get_schedule_program_by_school_type()
        cls_schedule = [entry for entry in current_schedule if entry.class_id == cls.class_id]
        
        filling_rate = len(cls_schedule) / (5 * 7) * 100 if (5 * 7) > 0 else 0  # 5 days * 7 hours
        class_filling_rates.append((cls.name, filling_rate, len(cls_schedule), total_required))
    
    # Sort by filling rate
    class_filling_rates.sort(key=lambda x: x[1])
    
    print("En düşük dolum oranına sahip sınıflar:")
    for name, rate, filled, required in class_filling_rates[:5]:  # Top 5 lowest
        print(f"  - {name}: {rate:.1f}% ({filled}/{5*7}, gereken: {required})")
    
    print("\nVeri iyileştirme önerileri:")
    print("1. Öğretmen uygunluk saatlerini artırın")
    print("2. Eksik atamaları tamamlayın")
    print("3. Çakışan ders saatlerini düzenleyin")
    print("4. Blok ders kurallarında esneklik sağlayın")
    print("5. Öğretmen yüklerini dengeleyin")

if __name__ == "__main__":
    print("Bu modül doğrudan çalıştırıldığında bir DB bağlantısı gerektirir.")
    print("Kullanım: analyze_schedule_feasibility(db_manager) fonksiyonunu çağırın.")