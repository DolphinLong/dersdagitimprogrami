"""
Initialize grade-specific data for Fen Lisesi (Science High School)
Based on Turkish Ministry of National Education guidelines for grades 9-12
"""

from database import db_manager
from utils.schedule_requirements import ScheduleRequirements

def init_fen_lisesi_data():
    """Initialize data for Fen Lisesi grades (9-12) according to MEB guidelines"""
    
    # Set school type to "Fen Lisesi"
    db_manager.set_school_type("Fen Lisesi")
    print("School type set to: Fen Lisesi (covers grades 9-12)")
    
    # Clear existing data
    print("Clearing existing data...")
    db_manager.clear_all_data()
    
    # Add teachers for all subjects across grades 9-12
    print("Adding teachers for all subjects...")
    
    # Turkish teachers
    turkish_teachers = ["Ali", "Veli", "Ayşe", "Fatma", "Mehmet", "Zeynep", "Ahmet", "Esra"]
    for teacher in turkish_teachers:
        db_manager.add_teacher(teacher, "Türk Dili ve Edebiyatı")
    
    # Math teachers
    math_teachers = ["Yunus", "Tarık", "Elif", "Cumhur", "Osman", "Gamze", "Esen", "Büşra"]
    for teacher in math_teachers:
        db_manager.add_teacher(teacher, "Matematik")
    
    # Physics teachers
    physics_teachers = ["Cumhur", "Aslı", "Cumhur", "Cumhur"]
    for teacher in physics_teachers:
        db_manager.add_teacher(teacher, "Fizik")
    
    # Chemistry teachers
    chemistry_teachers = ["Yeliz", "Leyla", "Nur", "Cumhur"]
    for teacher in chemistry_teachers:
        db_manager.add_teacher(teacher, "Kimya")
    
    # Biology teachers
    biology_teachers = ["Cumhur", "Aslı", "Cumhur", "Cumhur"]
    for teacher in biology_teachers:
        db_manager.add_teacher(teacher, "Biyoloji")
    
    # History teachers
    history_teachers = ["Esra", "Cumhur", "Ali", "Veli"]
    for teacher in history_teachers:
        db_manager.add_teacher(teacher, "Tarih")
    
    # Geography teachers
    geography_teachers = ["Aslı", "Cumhur", "Ayşe", "Fatma"]
    for teacher in geography_teachers:
        db_manager.add_teacher(teacher, "Coğrafya")
    
    # Art teachers
    art_teachers = ["Aslı", "Cumhur", "Ayşe", "Fatma"]
    for teacher in art_teachers:
        db_manager.add_teacher(teacher, "Görsel Sanatlar")
    
    # Music teachers
    music_teachers = ["Gamze", "Cumhur", "Mehmet", "Yunus"]
    for teacher in music_teachers:
        db_manager.add_teacher(teacher, "Müzik")
    
    # Physical Education teachers
    pe_teachers = ["Esen", "Cumhur", "Tarık", "Elif"]
    for teacher in pe_teachers:
        db_manager.add_teacher(teacher, "Beden Eğitimi ve Spor")
    
    # Foreign Language teachers
    foreign_lang_teachers = ["Osman", "Cumhur", "Zeynep", "Ahmet"]
    for teacher in foreign_lang_teachers:
        db_manager.add_teacher(teacher, "Birinci Yabancı Dil")
    
    # Religious Culture teachers
    religious_teachers = ["Cumhur", "Esra", "Ali", "Veli"]
    for teacher in religious_teachers:
        db_manager.add_teacher(teacher, "Din Kültürü ve Ahlak Bilgisi")
    
    # Guidance teachers
    guidance_teachers = ["Erkan", "Cumhur", "Yunus", "Tarık"]
    for teacher in guidance_teachers:
        db_manager.add_teacher(teacher, "Rehberlik ve Yönlendirme")
    
    # Technology teachers
    tech_teachers = ["Büşra", "Cumhur", "Elif", "Leyla"]
    for teacher in tech_teachers:
        db_manager.add_teacher(teacher, "Bilişim Teknolojileri ve Yazılım")
    
    # Philosophy teachers (grade 10)
    philosophy_teachers = ["Cumhur", "Esra"]
    for teacher in philosophy_teachers:
        db_manager.add_teacher(teacher, "Felsefe")
    
    # Turkish Revolution History teachers (grade 12)
    revolution_history_teachers = ["Ali", "Veli"]
    for teacher in revolution_history_teachers:
        db_manager.add_teacher(teacher, "T.C. İnkılap Tarihi ve Atatürkçülük")
    
    # Health and Traffic Culture teachers (grade 9)
    health_traffic_teachers = ["Cumhur", "Esra"]
    for teacher in health_traffic_teachers:
        db_manager.add_teacher(teacher, "Sağlık Bilgisi ve Trafik Kültürü")
    
    # Optional subject teachers
    optional_teachers = ["Cumhur", "Esra", "Ali", "Veli", "Mehmet", "Zeynep"]
    optional_subjects = [
        "Seçmeli Matematik", "Seçmeli Fizik", "Seçmeli Kimya", "Seçmeli Biyoloji",
        "Genetik Bilimine Giriş", "Tıp Bilimine Giriş", "Astronomi ve Uzay Bilimleri",
        "Sosyal Bilim Çalışmaları", "Düşünme Eğitimi", "Kur'an-ı Kerim",
        "Peygamberimizin Hayatı (Fen Lise)", "Temel Dini Bilgiler", "Spor Eğitimi",
        "Sanat Eğitimi", "İslam Kültür ve Medeniyeti", "Osmanlı Türkçesi", "İkinci Yabancı Dil"
    ]
    
    for subject in optional_subjects:
        for teacher in optional_teachers[:2]:  # Add 2 teachers for each optional subject
            db_manager.add_teacher(teacher, subject)
    
    # Add classes for all grades (9-12)
    print("Adding classes for all grades...")
    grades_classes = {
        9: ["9A", "9B", "9C", "9D"],
        10: ["10A", "10B", "10C", "10D"],
        11: ["11A", "11B", "11C", "11D"],
        12: ["12A", "12B", "12C", "12D"]
    }
    
    for grade, class_names in grades_classes.items():
        for class_name in class_names:
            db_manager.add_class(class_name, grade)
    
    # Add classrooms
    print("Adding classrooms...")
    db_manager.add_classroom("Classroom 1", 30)
    db_manager.add_classroom("Classroom 2", 25)
    db_manager.add_classroom("Classroom 3", 30)
    db_manager.add_classroom("Classroom 4", 25)
    db_manager.add_classroom("Science Lab 1", 20)
    db_manager.add_classroom("Science Lab 2", 20)
    db_manager.add_classroom("Science Lab 3", 20)
    db_manager.add_classroom("Computer Lab", 15)
    db_manager.add_classroom("Music Room", 20)
    db_manager.add_classroom("Gym", 30)
    db_manager.add_classroom("Art Studio", 20)
    db_manager.add_classroom("Library", 25)
    
    # Add mandatory lessons for each grade according to MEB guidelines
    print("Adding mandatory lessons for each grade...")
    _add_mandatory_lessons()
    
    # Add optional subjects
    print("Adding optional subjects...")
    fen_lisesi_optional_subjects = [
        "Seçmeli Matematik", "Seçmeli Fizik", "Seçmeli Kimya", "Seçmeli Biyoloji",
        "Genetik Bilimine Giriş", "Tıp Bilimine Giriş", "Astronomi ve Uzay Bilimleri",
        "Sosyal Bilim Çalışmaları", "Düşünme Eğitimi", "Kur'an-ı Kerim",
        "Peygamberimizin Hayatı (Fen Lise)", "Temel Dini Bilgiler", "Spor Eğitimi",
        "Sanat Eğitimi", "İslam Kültür ve Medeniyeti", "Osmanlı Türkçesi", "İkinci Yabancı Dil"
    ]
    
    for subject in fen_lisesi_optional_subjects:
        if subject in ScheduleRequirements.OPTIONAL_SUBJECTS:
            db_manager.add_lesson(subject, ScheduleRequirements.OPTIONAL_SUBJECTS[subject])
    
    print("Fen Lisesi data initialization completed!")

def _add_mandatory_lessons():
    """Add mandatory lessons for all grades without duplicates"""
    # Keep track of lessons we've already added
    added_lessons = set()
    
    # Add lessons for all grades (9-12)
    for grade in range(9, 13):
        mandatory_subjects = ScheduleRequirements.get_mandatory_subjects_for_grade(grade)
        for subject_name, hours in mandatory_subjects.items():
            # Create a unique key for this subject
            lesson_key = f"{subject_name}_{hours}"
            if lesson_key not in added_lessons:
                db_manager.add_lesson(subject_name, hours)
                added_lessons.add(lesson_key)
                print(f"  Added lesson: {subject_name} ({hours} hours)")

def validate_fen_lisesi_schedule():
    """Validate the Fen Lisesi schedule configuration"""
    print("\n=== Fen Lisesi Schedule Validation ===")
    
    # Check school type
    school_type = db_manager.get_school_type()
    print(f"School type: {school_type}")
    
    # Check classes
    classes = db_manager.get_all_classes()
    print(f"Total classes: {len(classes)}")
    
    # Group classes by grade
    classes_by_grade = {}
    for class_obj in classes:
        if class_obj.grade not in classes_by_grade:
            classes_by_grade[class_obj.grade] = []
        classes_by_grade[class_obj.grade].append(class_obj.name)
    
    print("Classes by grade:")
    for grade in sorted(classes_by_grade.keys()):
        print(f"  Grade {grade}: {', '.join(classes_by_grade[grade])}")
    
    # Check lessons
    lessons = db_manager.get_all_lessons()
    print(f"\nTotal lessons: {len(lessons)}")
    
    # Group lessons by subject
    lessons_by_subject = {}
    for lesson in lessons:
        if lesson.name not in lessons_by_subject:
            lessons_by_subject[lesson.name] = []
        lessons_by_subject[lesson.name].append(lesson.weekly_hours)
    
    print("Lessons by subject:")
    for subject in sorted(lessons_by_subject.keys()):
        hours_list = lessons_by_subject[subject]
        if len(hours_list) == 1:
            print(f"  {subject}: {hours_list[0]} hours")
        else:
            print(f"  {subject}: {hours_list} hours (multiple entries)")
    
    # Check teachers
    teachers = db_manager.get_all_teachers()
    print(f"\nTotal teachers: {len(teachers)}")
    
    # Group teachers by subject
    teachers_by_subject = {}
    for teacher in teachers:
        if teacher.subject not in teachers_by_subject:
            teachers_by_subject[teacher.subject] = []
        teachers_by_subject[teacher.subject].append(teacher.name)
    
    print("Teachers by subject:")
    for subject in sorted(teachers_by_subject.keys()):
        teacher_names = teachers_by_subject[subject]
        print(f"  {subject}: {len(teacher_names)} teacher(s) ({', '.join(teacher_names[:3])}{'' if len(teacher_names) <= 3 else ', ...'})")
    
    print("\nValidation completed!")

if __name__ == "__main__":
    init_fen_lisesi_data()
    validate_fen_lisesi_schedule()
    db_manager.close()