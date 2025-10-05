"""
Simple verification script for schedule dialogs
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from ui.dialogs.class_schedule_dialog import ClassScheduleDialog
from ui.dialogs.teacher_schedule_dialog import TeacherScheduleDialog

def main():
    app = QApplication(sys.argv)
    
    # Test class schedule dialog creation
    print("Creating class schedule dialog...")
    class_dialog = ClassScheduleDialog()
    print("Class schedule dialog created successfully!")
    
    # Test teacher schedule dialog creation
    print("Creating teacher schedule dialog...")
    teacher_dialog = TeacherScheduleDialog()
    print("Teacher schedule dialog created successfully!")
    
    print("All dialogs verified successfully!")

if __name__ == "__main__":
    main()