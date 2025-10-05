"""
Teacher schedule dialog for the Class Scheduling Program - FIXED
"""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QBrush
from database import db_manager
from utils.helpers import generate_color_for_lesson

class TeacherScheduleDialog(QDialog):
    """Dialog for viewing a specific teacher schedule"""
    
    SCHOOL_TIME_SLOTS = {
        "İlkokul": 6,
        "Ortaokul": 7,
        "Lise": 8,
        "Anadolu Lisesi": 8,
        "Fen Lisesi": 8,
        "Sosyal Bilimler Lisesi": 8
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)

        # 🎯 Force Fusion style
        from PyQt5.QtWidgets import QApplication
        QApplication.setStyle('Fusion')

        self.setWindowTitle("Öğretmen Programı Görüntüle")
        self.setFixedSize(1000, 600)
        self.setup_ui()
        self.populate_teachers()
        self.apply_styles()  # SADECE BİR KEZ!
    
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel("ÖĞRETMEN PROGRAMI")
        title_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(title_label)
        
        # Teacher selection
        teacher_layout = QHBoxLayout()
        teacher_label = QLabel("Öğretmen:")
        self.teacher_combo = QComboBox()
        self.teacher_combo.currentIndexChanged.connect(self.load_teacher_schedule)
        
        teacher_layout.addWidget(teacher_label)
        teacher_layout.addWidget(self.teacher_combo, 1)
        layout.addLayout(teacher_layout)
        
        # Get school type and time slots
        school_type = db_manager.get_school_type()
        if not school_type:
            school_type = "Lise"
        
        time_slots_count = self.SCHOOL_TIME_SLOTS.get(school_type, 8)
        
        # Create time slot labels
        time_slot_labels = []
        for i in range(time_slots_count):
            start_hour = 8 + i
            end_hour = 9 + i
            time_slot_labels.append(f"{start_hour:02d}:00-{end_hour:02d}:00")
        
        # Schedule table
        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(time_slots_count)
        self.schedule_table.setRowCount(5)  # Days
        self.schedule_table.setHorizontalHeaderLabels(time_slot_labels)
        self.schedule_table.setVerticalHeaderLabels([
            "Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"
        ])
        
        # Set table properties
        self.schedule_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.schedule_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.schedule_table.setSelectionMode(QTableWidget.NoSelection)
        
        layout.addWidget(self.schedule_table)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.close_button = QPushButton("Kapat")
        self.close_button.clicked.connect(self.accept)
        
        button_layout.addWidget(self.close_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

    def apply_styles(self):
        """Apply CORRECT styles - NO item background override!"""
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #ffffff, stop: 1 #f8f9fa);
            }
            QLabel {
                color: #2c3e50;
                font-size: 14px;
                font-weight: bold;
            }
            QComboBox {
                padding: 10px;
                border: 2px solid #cccccc;
                border-radius: 8px;
                background: white;
                font-size: 14px;
                min-height: 20px;
            }
            QComboBox:hover {
                border: 2px solid #3498db;
            }
            QTableWidget {
                border: 2px solid #dee2e6;
                border-radius: 12px;
                gridline-color: #e9ecef;
                background-color: white;
            }
            /* ❌ REMOVED: QTableWidget::item background overrides */
            /* Sadece hover efekti */
            QTableWidget::item:hover {
                border: 2px solid #3498db;
            }
            QHeaderView::section {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #27ae60, stop: 1 #229954);
                color: white;
                padding: 15px;
                font-weight: bold;
                border: none;
                border-right: 1px solid #229954;
                font-size: 12px;
            }
            QPushButton {
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                color: white;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #3498db, stop: 1 #2980b9);
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #2980b9, stop: 1 #2573a7);
            }
        """)
    
    def populate_teachers(self):
        """Populate the teacher combo box"""
        self.teacher_combo.clear()
        teachers = db_manager.get_all_teachers()
        for teacher in teachers:
            self.teacher_combo.addItem(teacher.name, teacher.teacher_id)
    
    def load_teacher_schedule(self):
        """Load schedule for the selected teacher"""
        teacher_id = self.teacher_combo.currentData()
        if not teacher_id:
            return
        
        # Get schedule entries
        teacher_entries = db_manager.get_schedule_for_specific_teacher(teacher_id)
        
        # Clear table
        for row in range(self.schedule_table.rowCount()):
            for col in range(self.schedule_table.columnCount()):
                self.schedule_table.setItem(row, col, QTableWidgetItem(""))
        
        # Populate table
        for entry in teacher_entries:
            lesson = db_manager.get_lesson_by_id(entry.lesson_id)
            class_obj = db_manager.get_class_by_id(entry.class_id)
            classroom = db_manager.get_classroom_by_id(entry.classroom_id)
            
            if lesson and class_obj and classroom:
                display_text = f"📚 {lesson.name}\n🎓 {class_obj.name}\n🏢 {classroom.name}"
                
                item = QTableWidgetItem(display_text)
                item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                
                # Generate color
                color = generate_color_for_lesson(lesson.name)
                
                # Apply color - SIMPLE METHOD
                item.setBackground(QBrush(color))
                item.setForeground(QBrush(QColor(255, 255, 255)))
                
                # Font
                font = QFont("Segoe UI", 10, QFont.Bold)
                item.setFont(font)
                
                self.schedule_table.setItem(entry.day, entry.time_slot, item)
        
        # ❌ REMOVED: No stylesheet override here!
        print("✅ Öğretmen programı yüklendi - Renkler uygulandı")
