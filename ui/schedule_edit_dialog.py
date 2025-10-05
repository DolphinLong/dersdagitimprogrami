"""
Schedule edit dialog for the Class Scheduling Program
"""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from database import db_manager

class ScheduleEditDialog(QDialog):
    """Dialog for editing schedule cells"""
    
    def __init__(self, parent=None, day=None, time_slot=None, current_data=None):
        super().__init__(parent)
        self.day = day
        self.time_slot = time_slot
        self.current_data = current_data or {}
        self.setWindowTitle("Program Hücre Düzenleme")
        self.setFixedSize(500, 400)
        # Fixed the window flags access issue by using the correct approach and adding type ignore
        self.setWindowFlags(self.windowFlags() | Qt.WindowCloseButtonHint)  # type: ignore
        self.setup_ui()
        self.apply_styles()
        self.load_data()
    
    def setup_ui(self):
        """Set up the user interface with modern design"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title with modern styling
        title_label = QLabel("PROGRAM HÜCRESİ DÜZENLEME")
        title_label.setAlignment(Qt.AlignCenter)  # type: ignore
        title_label.setObjectName("dialogTitle")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(title_label)
        
        # Day and time info with modern styling
        if self.day is not None and self.time_slot is not None:
            day_names = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
            time_slots = [
                "08:00-09:00", "09:00-10:00", "10:00-11:00", "11:00-12:00",
                "12:00-13:00", "13:00-14:00", "14:00-15:00", "15:00-16:00"
            ]
            
            info_label = QLabel(f"Gün: {day_names[self.day]}\nSaat: {time_slots[self.time_slot]}")
            info_label.setAlignment(Qt.AlignCenter)  # type: ignore
            info_label.setObjectName("infoLabel")
            layout.addWidget(info_label)
        
        # Lesson selection with modern styling
        lesson_layout = QHBoxLayout()
        lesson_label = QLabel("Ders:")
        lesson_label.setObjectName("fieldLabel")
        self.lesson_combo = QComboBox()
        self.lesson_combo.setObjectName("inputField")
        self.lesson_combo.setEditable(True)
        lesson_layout.addWidget(lesson_label, 1)
        lesson_layout.addWidget(self.lesson_combo, 3)
        layout.addLayout(lesson_layout)
        
        # Teacher selection with modern styling
        teacher_layout = QHBoxLayout()
        teacher_label = QLabel("Öğretmen:")
        teacher_label.setObjectName("fieldLabel")
        self.teacher_combo = QComboBox()
        self.teacher_combo.setObjectName("inputField")
        self.teacher_combo.setEditable(True)
        teacher_layout.addWidget(teacher_label, 1)
        teacher_layout.addWidget(self.teacher_combo, 3)
        layout.addLayout(teacher_layout)
        
        # Class selection with modern styling
        class_layout = QHBoxLayout()
        class_label = QLabel("Sınıf:")
        class_label.setObjectName("fieldLabel")
        self.class_combo = QComboBox()
        self.class_combo.setObjectName("inputField")
        self.class_combo.setEditable(True)
        class_layout.addWidget(class_label, 1)
        class_layout.addWidget(self.class_combo, 3)
        layout.addLayout(class_layout)
        

        
        # Buttons with modern styling
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_button = QPushButton("✅ Kaydet")
        self.save_button.setObjectName("saveButton")
        self.save_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton("❌ İptal")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Pre-populate if we have current data
        if self.current_data:
            if 'lesson' in self.current_data:
                # Find and select the lesson in the combo box
                index = self.lesson_combo.findText(self.current_data['lesson'])
                if index >= 0:
                    self.lesson_combo.setCurrentIndex(index)
                else:
                    self.lesson_combo.setEditText(self.current_data['lesson'])
            
            if 'teacher' in self.current_data:
                # Find and select the teacher in the combo box
                index = self.teacher_combo.findText(self.current_data['teacher'])
                if index >= 0:
                    self.teacher_combo.setCurrentIndex(index)
                else:
                    self.teacher_combo.setEditText(self.current_data['teacher'])
    
    def apply_styles(self):
        """Apply modern styles with improved design"""
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #ffffff, stop: 1 #f8f9fa);
                border-radius: 12px;
            }
            QLabel {
                color: #212529;
                font-weight: bold;
                font-size: 14px;
            }
            #dialogTitle {
                font-size: 18px;
                color: #2c3e50;
                margin-bottom: 10px;
                text-align: center;
            }
            #infoLabel {
                background-color: #e3f2fd;
                border: 1px solid #bbdefb;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
                color: #1976d2;
                text-align: center;
            }
            #fieldLabel {
                font-weight: bold;
                color: #3498db;
            }
            QComboBox {
                padding: 12px;
                border: 2px solid #cccccc;
                border-radius: 8px;
                background: white;
                min-width: 150px;
                font-size: 14px;
                min-height: 20px;
            }
            QComboBox:hover {
                border: 2px solid #3498db;
            }
            QPushButton {
                padding: 12px 20px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                color: white;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #3498db, stop: 1 #2980b9);
                font-size: 14px;
                min-height: 20px;
                min-width: 100px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #2980b9, stop: 1 #2573a7);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #2573a7, stop: 1 #1f618d);
            }
            #saveButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #27ae60, stop: 1 #219653);
            }
            #saveButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #219653, stop: 1 #1e8449);
            }
            #cancelButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #e74c3c, stop: 1 #c0392b);
            }
            #cancelButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #c0392b, stop: 1 #a93226);
            }
        """)
    
    def load_data(self):
        """Load data into combo boxes"""
        # Load lessons
        lessons = db_manager.get_all_lessons()
        for lesson in lessons:
            self.lesson_combo.addItem(lesson.name, lesson.lesson_id)
        
        # Load teachers
        teachers = db_manager.get_all_teachers()
        for teacher in teachers:
            self.teacher_combo.addItem(teacher.name, teacher.teacher_id)
        
        # Load classes
        classes = db_manager.get_all_classes()
        for class_obj in classes:
            self.class_combo.addItem(class_obj.name, class_obj.class_id)
        

    
    def get_data(self):
        """Get the edited data"""
        return {
            'lesson_id': self.lesson_combo.currentData(),
            'lesson_name': self.lesson_combo.currentText(),
            'teacher_id': self.teacher_combo.currentData(),
            'teacher_name': self.teacher_combo.currentText(),
            'class_id': self.class_combo.currentData(),
            'class_name': self.class_combo.currentText(),
            'classroom_id': 1,  # Default classroom ID
            'classroom_name': 'Genel Derslik'
        }