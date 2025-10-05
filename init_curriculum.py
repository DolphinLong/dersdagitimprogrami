"""
Initialize complete curriculum for all grades based on school type
"""

from init_grade_data import get_school_rules
from database.models import Lesson

def initialize_curriculum_for_school_type(db_manager, school_type):
    """
    Initialize the complete curriculum for all grades based on the selected school type.
    
    Args:
        db_manager: Database manager instance
        school_type (str): Selected school type
    """
    # Check if lessons already exist for this school type
    existing_lessons = db_manager.get_all_lessons()
    
    # If lessons already exist, don't initialize again to prevent duplicates
    if existing_lessons:
        # Check if these lessons are from the curriculum initialization
        # (Simple check: if there are many lessons, assume they're from curriculum)
        if len(existing_lessons) > 10:
            return  # Don't re-initialize if we already have a full curriculum
    
    # Get curriculum rules for the selected school type
    if school_type in ["Anadolu Lisesi", "Sosyal Bilimler Lisesi"]:
        if school_type == "Anadolu Lisesi":
            rules = get_school_rules("anatolian")
        else:
            rules = get_school_rules("social_sciences")
        
        # Initialize mandatory courses for all grades
        initialize_mandatory_courses(db_manager, school_type, rules)
        
        # Initialize elective courses information (as a reference)
        initialize_elective_courses_info(db_manager, school_type, rules)
    else:
        # For other school types, initialize basic subjects
        initialize_basic_subjects(db_manager, school_type)

def clear_lessons_for_school_type(db_manager, school_type):
    """
    Clear all existing lessons for the specified school type.
    
    Args:
        db_manager: Database manager instance
        school_type (str): School type to clear lessons for
    """
    # This is a simplified approach - in a real implementation, you might want to
    # handle this more carefully to avoid deleting data that might be in use
    pass

def initialize_mandatory_courses(db_manager, school_type, rules):
    """
    Initialize mandatory courses for all grades according to curriculum rules.
    
    Args:
        db_manager: Database manager instance
        school_type (str): Selected school type
        rules (dict): Curriculum rules for the school type
    """
    # Process mandatory courses for each grade
    for grade in rules["grades"]:
        mandatory_courses = rules["mandatory_courses"][grade]
        
        for course_name, weekly_hours in mandatory_courses.items():
            if weekly_hours > 0:  # Only create lessons for courses with allocated hours
                # Create lesson with grade information in the name to distinguish between grades
                lesson_name = f"{course_name} ({grade}. Sınıf)"
                db_manager.add_lesson(lesson_name, weekly_hours)

def initialize_elective_courses_info(db_manager, school_type, rules):
    """
    Initialize information about elective courses as reference lessons.
    
    Args:
        db_manager: Database manager instance
        school_type (str): Selected school type
        rules (dict): Curriculum rules for the school type
    """
    # Create a special "Elective Courses Information" lesson to store elective course details
    # This is just for reference and won't be scheduled directly
    elective_info = f"Seçmeli Dersler ({school_type}):\n"
    
    # Add available hours information
    elective_info += "Müfredat Saatleri:\n"
    for grade, hours in rules["elective_courses"]["available_hours"].items():
        elective_info += f"  {grade}. Sınıf: {hours} saat\n"
    
    # Add elective course groups
    elective_info += "\nSeçmeli Ders Grupları:\n"
    for group_name, courses in rules["elective_courses"]["groups"].items():
        elective_info += f"  {group_name}:\n"
        for course in courses:
            elective_info += f"    - {course}\n"
    
    # Add this information as a special lesson with 0 weekly hours
    db_manager.add_lesson(elective_info, 0)

def initialize_basic_subjects(db_manager, school_type):
    """
    Initialize basic subjects for school types without detailed curriculum rules.
    
    Args:
        db_manager: Database manager instance
        school_type (str): Selected school type
    """
    from ui.school_type_dialog import SchoolTypeDialog
    
    dialog = SchoolTypeDialog()
    subjects = dialog.get_subjects_for_school_type(school_type)
    
    for subject in subjects:
        # Create a basic lesson with 2 weekly hours (can be adjusted later)
        db_manager.add_lesson(subject, 2)

def create_sample_classes(db_manager, school_type):
    """
    Create sample classes for the selected school type.
    
    Args:
        db_manager: Database manager instance
        school_type (str): Selected school type
    """
    # Check if classes already exist for this school type
    existing_classes = db_manager.get_all_classes()
    
    # If classes already exist, don't create sample classes again
    if existing_classes:
        return
    
    if school_type in ["Anadolu Lisesi", "Sosyal Bilimler Lisesi"]:
        # Create sample classes for high school (9-12 grades)
        for grade in range(9, 13):
            for section in ["A", "B", "C"]:  # Three sections per grade
                class_name = f"{grade}/{section}"
                db_manager.add_class(class_name, grade)
    else:
        # For other school types, create simpler class structure
        # This is just an example - you can adjust based on your needs
        grades = []
        if school_type == "İlkokul":
            grades = list(range(1, 5))  # 1-4 grades
        elif school_type == "Ortaokul":
            grades = list(range(5, 9))  # 5-8 grades
        elif school_type == "Lise":
            grades = list(range(9, 13))  # 9-12 grades
        elif school_type == "Fen Lisesi":
            grades = list(range(9, 13))  # 9-12 grades
        
        for grade in grades:
            for section in ["A", "B"]:  # Two sections per grade
                class_name = f"{grade}/{section}"
                db_manager.add_class(class_name, grade)

# Example usage
if __name__ == "__main__":
    print("This module provides functions to initialize curriculum based on school type.")
    print("Use initialize_curriculum_for_school_type(db_manager, school_type) to initialize.")