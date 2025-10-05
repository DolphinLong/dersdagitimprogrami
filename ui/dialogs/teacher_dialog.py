"""
Teacher dialog for the Class Scheduling Program
"""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from database import db_manager
from ui.school_type_dialog import SchoolTypeDialog
from ui.dialogs.teacher_availability_dialog import TeacherAvailabilityDialog
from utils.helpers import create_styled_message_box

class TeacherDialog(QDialog):
    """Dialog for adding or editing teachers"""
    
    # Define school types and their subjects
    SCHOOL_SUBJECTS = SchoolTypeDialog.SCHOOL_TYPES
    
    def __init__(self, parent=None, teacher=None):
        super().__init__(parent)
        self.teacher = teacher
        self.setWindowTitle("Öğretmen Ekle/Düzenle")
        self.setFixedSize(450, 320)
        self.setup_ui()
        if self.teacher:
            self.populate_data()
        self.apply_styles()
        self.populate_subjects()
    
    def setup_ui(self):
        """Set up the user interface with modern design"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title with modern styling
        title_label = QLabel("Öğretmen Ekle/Düzenle")
        title_label.setAlignment(Qt.AlignCenter)  # type: ignore
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # Name input with modern styling
        name_layout = QHBoxLayout()
        name_label = QLabel("Ad Soyad:")
        name_label.setObjectName("fieldLabel")
        self.name_input = QLineEdit()
        self.name_input.setObjectName("inputField")
        self.name_input.setPlaceholderText("Öğretmenin tam adını girin")
        name_layout.addWidget(name_label, 1)
        name_layout.addWidget(self.name_input, 3)
        layout.addLayout(name_layout)
        
        # Subject input with modern styling
        subject_layout = QHBoxLayout()
        subject_label = QLabel("Ders:")
        subject_label.setObjectName("fieldLabel")
        self.subject_input = QComboBox()
        self.subject_input.setObjectName("inputField")
        self.subject_input.setEditable(True)
        self.subject_input.setPlaceholderText("Ders seçin veya girin")
        
        # Apply styling directly to the combo box view
        self.subject_input.view().setStyleSheet("""
            background: white;
            color: #212529;
            selection-background-color: #3498db;
            selection-color: white;
        """)
        
        subject_layout.addWidget(subject_label, 1)
        subject_layout.addWidget(self.subject_input, 3)
        layout.addLayout(subject_layout)
        
        # Availability button
        self.availability_button = QPushButton("🕒 Uygunluk Ayarları")
        self.availability_button.setObjectName("availabilityButton")
        self.availability_button.clicked.connect(self.open_availability_dialog)
        layout.addWidget(self.availability_button)
        
        # Buttons with modern styling
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_button = QPushButton("✅ Kaydet")
        self.save_button.setObjectName("saveButton")
        self.save_button.clicked.connect(self.save_teacher)
        
        self.cancel_button = QPushButton("❌ İptal")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Set focus to name input
        self.name_input.setFocus()
    
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
            #title {
                font-size: 18px;
                color: #2c3e50;
                margin-bottom: 10px;
                text-align: center;
            }
            #fieldLabel {
                font-weight: bold;
                color: #3498db;
            }
            QLineEdit, QComboBox {
                padding: 12px;
                border: 2px solid #cccccc;
                border-radius: 8px;
                background: white;
                font-size: 14px;
                min-height: 20px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #3498db;
            }
            QComboBox::drop-down {
                border: none;
                border-radius: 8px;
            }
            QComboBox QAbstractItemView {
                background: white;
                color: #212529;
                selection-background-color: #3498db;
                selection-color: white;
                border: 1px solid #cccccc;
                outline: 0px;
            }
            QComboBox QAbstractItemView::item {
                background: white;
                color: #212529;
                padding: 8px;
            }
            QComboBox QAbstractItemView::item:selected {
                background: #3498db;
                color: white;
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
            #availabilityButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #9b59b6, stop: 1 #8e44ad);
            }
            #availabilityButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #8e44ad, stop: 1 #7d3c98);
            }
        """)
    
    def populate_subjects(self):
        """Populate subject dropdown based on school type"""
        # Clear existing items
        self.subject_input.clear()
        
        # Get school type from database
        school_type = db_manager.get_school_type()
        
        # If no school type is set, default to "Lise"
        if not school_type:
            school_type = "Lise"
        
        # Get subjects for the school type
        subjects = self.SCHOOL_SUBJECTS.get(school_type, self.SCHOOL_SUBJECTS["Lise"])
        
        # Add subjects to combo box
        self.subject_input.addItems(subjects)
    
    def populate_data(self):
        """Populate dialog with existing teacher data"""
        self.name_input.setText(self.teacher.name)
        # Set the subject in the combo box
        subject_text = self.teacher.subject
        index = self.subject_input.findText(subject_text)
        if index >= 0:
            self.subject_input.setCurrentIndex(index)
        else:
            self.subject_input.setEditText(subject_text)
    
    def open_availability_dialog(self):
        """Open teacher availability dialog"""
        # If this is a new teacher, save it first
        if not self.teacher:
            name = self.name_input.text().strip()
            subject = self.subject_input.currentText().strip()
            
            if not name or not subject:
                msg = create_styled_message_box(self, "Hata", "Lütfen önce öğretmen adı ve dersini girin.", QMessageBox.Warning)
                msg.exec_()
                return
            
            # Add new teacher
            teacher_id = db_manager.add_teacher(name, subject)
            if not teacher_id:
                msg = create_styled_message_box(self, "Hata", "Öğretmen eklenirken bir hata oluştu.", QMessageBox.Critical)
                msg.exec_()
                return
            
            # Get the newly created teacher
            self.teacher = db_manager.get_teacher_by_id(teacher_id)
        
        # Open availability dialog
        if self.teacher:
            dialog = TeacherAvailabilityDialog(self, self.teacher)
            dialog.exec_()
    
    def save_teacher(self):
        """Save teacher data"""
        name = self.name_input.text().strip()
        subject = self.subject_input.currentText().strip()
        
        if not name or not subject:
            msg = create_styled_message_box(self, "Hata", "Lütfen tüm alanları doldurun.", QMessageBox.Warning)
            msg.exec_()
            return
        
        try:
            if self.teacher:
                # Update existing teacher
                success = db_manager.update_teacher(self.teacher.teacher_id, name, subject)
                if success:
                    msg = create_styled_message_box(self, "Başarılı", "Öğretmen bilgileri başarıyla güncellendi.")
                    msg.exec_()
                    self.accept()
                else:
                    msg = create_styled_message_box(self, "Hata", "Öğretmen bilgileri güncellenirken bir hata oluştu.", QMessageBox.Critical)
                    msg.exec_()
            else:
                # Add new teacher
                teacher_id = db_manager.add_teacher(name, subject)
                if teacher_id:
                    msg = create_styled_message_box(self, "Başarılı", "Öğretmen başarıyla eklendi.")
                    msg.exec_()
                    self.accept()
                else:
                    msg = create_styled_message_box(self, "Hata", "Öğretmen eklenirken bir hata oluştu.", QMessageBox.Critical)
                    msg.exec_()
        except Exception as e:
            msg = create_styled_message_box(self, "Hata", f"Öğretmen kaydedilirken bir hata oluştu: {str(e)}", QMessageBox.Critical)
            msg.exec_()