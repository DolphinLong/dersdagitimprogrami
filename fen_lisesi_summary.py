"""
Summary of Fen Lisesi (Science High School) Implementation
Based on Turkish Ministry of National Education guidelines
"""

from utils.schedule_requirements import ScheduleRequirements

def print_fen_lisesi_summary():
    """Print a comprehensive summary of the Fen Lisesi implementation"""
    print("=" * 60)
    print("FEN LİSESİ (SCIENCE HIGH SCHOOL) IMPLEMENTATION SUMMARY")
    print("=" * 60)
    print("Based on Turkish Ministry of National Education Guidelines")
    print()
    
    # General Rules
    print("GENERAL RULES:")
    print("- Covers grades 9, 10, 11, and 12")
    print("- Total weekly hours: 40 for all grades")
    print("- Mandatory 1 hour 'Rehberlik ve Yönlendirme' for all grades")
    print("- Subjects divided into Mandatory and Elective groups")
    print()
    
    # Grade-specific information
    print("GRADE-SPECIFIC REQUIREMENTS:")
    print()
    
    fen_lisesi_grades = {
        9: {
            "Türk Dili ve Edebiyatı": 5,
            "Matematik": 6,
            "Fizik": 2,
            "Kimya": 2,
            "Biyoloji": 2,
            "Tarih": 2,
            "Coğrafya": 2,
            "Din Kültürü ve Ahlak Bilgisi": 2,
            "Birinci Yabancı Dil": 4,
            "Beden Eğitimi ve Spor": 2,
            "Görsel Sanatlar": 1,
            "Müzik": 1,
            "Sağlık Bilgisi ve Trafik Kültürü": 1,
            "Bilişim Teknolojileri ve Yazılım": 2,
            "Rehberlik ve Yönlendirme": 1
        },
        10: {
            "Türk Dili ve Edebiyatı": 5,
            "Matematik": 6,
            "Fizik": 2,
            "Kimya": 2,
            "Biyoloji": 2,
            "Tarih": 2,
            "Coğrafya": 2,
            "Din Kültürü ve Ahlak Bilgisi": 2,
            "Birinci Yabancı Dil": 4,
            "Felsefe": 2,
            "Beden Eğitimi ve Spor": 2,
            "Görsel Sanatlar": 1,
            "Müzik": 1,
            "Bilişim Teknolojileri ve Yazılım": 2,
            "Rehberlik ve Yönlendirme": 1
        },
        11: {
            "Türk Dili ve Edebiyatı": 5,
            "Matematik": 6,
            "Fizik": 4,
            "Kimya": 4,
            "Biyoloji": 4,
            "Tarih": 2,
            "Din Kültürü ve Ahlak Bilgisi": 2,
            "Birinci Yabancı Dil": 4,
            "Beden Eğitimi ve Spor": 2,
            "Rehberlik ve Yönlendirme": 1
        },
        12: {
            "Türk Dili ve Edebiyatı": 5,
            "Matematik": 6,
            "Fizik": 4,
            "Kimya": 4,
            "Biyoloji": 4,
            "T.C. İnkılap Tarihi ve Atatürkçülük": 2,
            "Din Kültürü ve Ahlak Bilgisi": 2,
            "Birinci Yabancı Dil": 4,
            "Beden Eğitimi ve Spor": 2,
            "Rehberlik ve Yönlendirme": 1
        }
    }
    
    for grade, subjects in fen_lisesi_grades.items():
        total_mandatory_hours = sum(subjects.values())
        optional_hours_limit = ScheduleRequirements.get_optional_hours_limit_for_grade(grade)
        total_hours = ScheduleRequirements.get_total_hours_for_grade(grade)
        
        print(f"Grade {grade}:")
        print(f"  Mandatory Subjects ({len(subjects)} subjects, {total_mandatory_hours} hours):")
        for subject, hours in subjects.items():
            print(f"    - {subject}: {hours} hours")
        print(f"  Optional Subject Limit: {optional_hours_limit} hours")
        print(f"  Total Weekly Hours: {total_hours}")
        print()
    
    # Elective Subjects
    print("ELECTIVE SUBJECTS BY CATEGORY:")
    print()
    
    elective_categories = {
        "Akademik Çalışmalar": [
            "Seçmeli Matematik", "Seçmeli Fizik", "Seçmeli Kimya", "Seçmeli Biyoloji",
            "Genetik Bilimine Giriş", "Tıp Bilimine Giriş"
        ],
        "İnsan, Toplum ve Bilim": [
            "Astronomi ve Uzay Bilimleri", "Sosyal Bilim Çalışmaları", "Düşünme Eğitimi"
        ],
        "Din, Ahlak ve Değer": [
            "Kur'an-ı Kerim", "Peygamberimizin Hayatı (Fen Lise)", "Temel Dini Bilgiler"
        ],
        "Kültür, Sanat ve Spor": [
            "Spor Eğitimi", "Sanat Eğitimi", "İslam Kültür ve Medeniyeti"
        ],
        "Dil Alanı": [
            "Osmanlı Türkçesi", "İkinci Yabancı Dil"
        ]
    }
    
    for category, subjects in elective_categories.items():
        print(f"{category}:")
        for subject in subjects:
            if subject in ScheduleRequirements.OPTIONAL_SUBJECTS:
                hours = ScheduleRequirements.OPTIONAL_SUBJECTS[subject]
                print(f"  - {subject}: {hours} hours")
        print()
    
    # Validation
    print("IMPLEMENTATION VALIDATION:")
    print()
    
    # Test each grade
    all_valid = True
    for grade in range(9, 13):
        mandatory_subjects = ScheduleRequirements.get_mandatory_subjects_for_grade(grade)
        is_valid, message = ScheduleRequirements.validate_schedule(grade, mandatory_subjects)
        status = "✓ PASS" if is_valid else "✗ FAIL"
        print(f"  Grade {grade} Mandatory Subjects: {status}")
        if not is_valid:
            print(f"    Error: {message}")
            all_valid = False
    
    # Test optional limits
    optional_limits_correct = True
    expected_limits = {9: 5, 10: 4, 11: 4, 12: 8}
    for grade, expected in expected_limits.items():
        actual = ScheduleRequirements.get_optional_hours_limit_for_grade(grade)
        if actual != expected:
            print(f"  Grade {grade} Optional Limit: ✗ FAIL (Expected {expected}, got {actual})")
            optional_limits_correct = False
        else:
            print(f"  Grade {grade} Optional Limit: ✓ PASS ({actual} hours)")
    
    print()
    if all_valid and optional_limits_correct:
        print("✓ ALL TESTS PASSED - Fen Lisesi implementation is correct!")
    else:
        print("✗ SOME TESTS FAILED - Please check the implementation")
    
    print()
    print("=" * 60)
    print("END OF SUMMARY")
    print("=" * 60)

if __name__ == "__main__":
    print_fen_lisesi_summary()