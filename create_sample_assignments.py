#!/usr/bin/env python3
"""
Create sample lesson assignments for testing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_manager

def create_sample_assignments():
    """Create sample lesson assignments for testing"""
    print("🚀 Creating Sample Lesson Assignments")
    print("=" * 50)
    
    # Get current data
    classes = db_manager.get_all_classes()
    teachers = db_manager.get_all_teachers()
    lessons = db_manager.get_all_lessons()
    
    print(f"📊 Available Data:")
    print(f"   • Classes: {len(classes)}")
    print(f"   • Teachers: {len(teachers)}")
    print(f"   • Lessons: {len(lessons)}")
    
    if not classes or not teachers or not lessons:
        print("❌ Insufficient data. Please run init_data.py first.")
        return
    
    # Clear existing assignments
    print("\n🧹 Clearing existing assignments...")
    # db_manager.clear_schedule()  # Don't clear, just add new assignments
    
    # Create teacher-subject mapping
    teacher_map = {}
    for teacher in teachers:
        if teacher.subject not in teacher_map:
            teacher_map[teacher.subject] = []
        teacher_map[teacher.subject].append(teacher)
    
    print(f"\n👨‍🏫 Teacher subjects available:")
    for subject, teacher_list in teacher_map.items():
        teacher_names = [t.name for t in teacher_list]
        print(f"   • {subject}: {', '.join(teacher_names)}")
    
    # Create lesson assignments for each class
    assignment_count = 0
    
    for class_obj in classes:
        print(f"\n📚 Creating assignments for {class_obj.name} (Grade {class_obj.grade}):")
        
        for lesson in lessons:
            # Get weekly hours for this lesson and grade
            weekly_hours = db_manager.get_weekly_hours_for_lesson(lesson.lesson_id, class_obj.grade)
            
            if not weekly_hours or weekly_hours <= 0:
                continue
            
            # Find a teacher for this lesson
            assigned_teacher = None
            
            # First try exact subject match
            if lesson.name in teacher_map:
                assigned_teacher = teacher_map[lesson.name][0]  # Take first available
            
            # Special cases for subject matching
            elif lesson.name == "T.C. İnkılap Tarihi ve Atatürkçülük" and "Sosyal Bilgiler" in teacher_map:
                assigned_teacher = teacher_map["Sosyal Bilgiler"][0]
            elif lesson.name == "Rehberlik ve Yönlendirme":
                # Assign any available teacher for guidance
                for subject, teacher_list in teacher_map.items():
                    if teacher_list:
                        assigned_teacher = teacher_list[0]
                        break
            elif "Bilişim" in lesson.name and "Bilişim Teknolojileri ve Yazılım" in teacher_map:
                assigned_teacher = teacher_map["Bilişim Teknolojileri ve Yazılım"][0]
            elif "Teknoloji" in lesson.name and "Teknoloji ve Tasarım" in teacher_map:
                assigned_teacher = teacher_map["Teknoloji ve Tasarım"][0]
            
            if assigned_teacher:
                # Create assignment entry
                print(f"   🔧 Attempting to assign {lesson.name} (ID: {lesson.lesson_id}) to {assigned_teacher.name} (ID: {assigned_teacher.teacher_id}) for class {class_obj.name} (ID: {class_obj.class_id})")
                entry_id = db_manager.add_schedule_entry(
                    class_obj.class_id,
                    assigned_teacher.teacher_id,
                    lesson.lesson_id,
                    1,  # Default classroom
                    0,  # Default day
                    0   # Default time slot
                )
                
                if entry_id:
                    assignment_count += 1
                    print(f"   ✅ {lesson.name} -> {assigned_teacher.name} ({weekly_hours} hours) [Entry ID: {entry_id}]")
                else:
                    print(f"   ❌ Failed to assign {lesson.name}")
            else:
                print(f"   ⚠️  No teacher found for {lesson.name}")
    
    print(f"\n✅ Created {assignment_count} lesson assignments!")
    print("\nNow you can run the scheduler to generate the timetable.")

if __name__ == "__main__":
    create_sample_assignments()
    db_manager.close()