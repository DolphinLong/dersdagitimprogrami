"""
Validate schedule requirements for grades 1-8
"""

from utils.schedule_requirements import ScheduleRequirements

def validate_all_grades():
    """Validate requirements for all grades"""
    print("=== Schedule Requirements Validation ===\n")
    
    for grade in range(1, 9):
        print(f"Grade {grade}:")
        mandatory_subjects = ScheduleRequirements.get_mandatory_subjects_for_grade(grade)
        total_mandatory_hours = sum(mandatory_subjects.values())
        max_hours = ScheduleRequirements.get_total_hours_for_grade(grade)
        
        print(f"  Total weekly hours limit: {max_hours}")
        print(f"  Mandatory subjects ({total_mandatory_hours} hours):")
        
        for subject, hours in sorted(mandatory_subjects.items()):
            subject_available = ScheduleRequirements.is_subject_available_for_grade(subject, grade)
            status = "✓" if subject_available else "✗"
            print(f"    {status} {subject}: {hours} hours")
        
        # Check if mandatory hours exceed the limit
        if total_mandatory_hours > max_hours:
            print(f"  ⚠ WARNING: Mandatory hours ({total_mandatory_hours}) exceed limit ({max_hours})")
        else:
            print(f"  ✓ Mandatory hours are within limit ({total_mandatory_hours}/{max_hours})")
        
        # Show available optional subjects
        optional_subjects = ScheduleRequirements.get_available_optional_subjects_for_grade(grade)
        if optional_subjects:
            total_optional_hours = sum(optional_subjects.values())
            print(f"  Available optional subjects ({total_optional_hours} hours):")
            for subject, hours in sorted(optional_subjects.items()):
                print(f"    + {subject}: {hours} hours")
        
        print()

def validate_subject_restrictions():
    """Validate subject restrictions"""
    print("=== Subject Availability by Grade ===\n")
    
    # Subjects to check
    subjects_to_check = [
        "Hayat Bilgisi", "Sosyal Bilgiler", "T.C. İnkılap Tarihi ve Atatürkçülük",
        "Yabancı Dil", "Din Kültürü ve Ahlak Bilgisi", "Trafik Güvenliği",
        "İnsan Hakları, Vatandaşlık ve Demokrasi", "Bilişim Teknolojileri ve Yazılım",
        "Teknoloji ve Tasarım", "Serbest Etkinlikler", "Beden Eğitimi ve Oyun",
        "Beden Eğitimi ve Spor"
    ]
    
    for subject in subjects_to_check:
        print(f"{subject}:")
        available_grades = []
        for grade in range(1, 9):
            if ScheduleRequirements.is_subject_available_for_grade(subject, grade):
                available_grades.append(str(grade))
        
        if available_grades:
            print(f"  Available in grades: {', '.join(available_grades)}")
        else:
            print(f"  Not available in any grade")
        print()

if __name__ == "__main__":
    validate_all_grades()
    validate_subject_restrictions()