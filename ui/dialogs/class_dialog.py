"""
Class dialog for the Class Scheduling Program
"""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from database import db_manager
from utils.helpers import create_styled_message_box

class ClassDialog(QDialog):
    """Dialog for adding or editing classes"""
    
    def __init__(self, parent=None, class_obj=None):
        super().__init__(parent)
        self.class_obj = class_obj
        self.setWindowTitle("Sınıf Ekle/Düzenle")
        self.setFixedSize(450, 350)
        self.setup_ui()
        if self.class_obj:
            self.populate_data()
        self.apply_styles()
    
    def setup_ui(self):
        """Set up the user interface with modern design"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title with modern styling
        title_label = QLabel("Sınıf Ekle/Düzenle")
        title_label.setAlignment(Qt.AlignCenter)  # type: ignore
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # Grade level input with modern styling
        grade_layout = QHBoxLayout()
        grade_label = QLabel("Sınıf Seviyesi:")
        grade_label.setObjectName("fieldLabel")
        self.grade_input = QComboBox()
        self.grade_input.setObjectName("inputField")
        self.grade_input.addItems([str(i) for i in range(1, 13)])  # 1-12 grade levels
        self.grade_input.setPlaceholderText("Sınıf seviyesini seçin")
        grade_layout.addWidget(grade_label, 1)
        grade_layout.addWidget(self.grade_input, 3)
        layout.addLayout(grade_layout)
        
        # Section input with modern styling
        section_layout = QHBoxLayout()
        section_label = QLabel("Şube:")
        section_label.setObjectName("fieldLabel")
        self.section_input = QComboBox()
        self.section_input.setObjectName("inputField")
        self.section_input.addItems([chr(i) for i in range(ord('A'), ord('Z')+1)])  # A-Z sections
        self.section_input.setPlaceholderText("Şube seçin")
        section_layout.addWidget(section_label, 1)
        section_layout.addWidget(self.section_input, 3)
        layout.addLayout(section_layout)
        
        # Buttons with modern styling
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_button = QPushButton("✅ Kaydet")
        self.save_button.setObjectName("saveButton")
        self.save_button.clicked.connect(self.save_class)
        
        self.cancel_button = QPushButton("❌ İptal")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Set focus to grade input
        self.grade_input.setFocus()
    
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
        """)
    
    def populate_data(self):
        """Populate dialog with existing class data"""
        if self.class_obj:
            # Extract grade and section from class name
            class_name = self.class_obj.name
            if len(class_name) >= 2:
                grade_part = class_name[:-1]  # Everything except last character
                section_part = class_name[-1]  # Last character
                
                # Set grade
                grade_index = self.grade_input.findText(grade_part)
                if grade_index >= 0:
                    self.grade_input.setCurrentIndex(grade_index)
                
                # Set section
                section_index = self.section_input.findText(section_part)
                if section_index >= 0:
                    self.section_input.setCurrentIndex(section_index)
    
    def save_class(self):
        """Save class data"""
        grade_text = self.grade_input.currentText().strip()
        section_text = self.section_input.currentText().strip()
        
        if not grade_text or not section_text:
            msg = create_styled_message_box(self, "Hata", "Lütfen tüm alanları doldurun.", QMessageBox.Warning)
            msg.exec_()
            return
        
        # Create class name from grade and section
        class_name = f"{grade_text}{section_text}"
        
        try:
            grade = int(grade_text)
        except ValueError:
            msg = create_styled_message_box(self, "Hata", "Lütfen geçerli bir seviye numarası girin.", QMessageBox.Warning)
            msg.exec_()
            return
        
        try:
            if self.class_obj:
                # Update existing class
                success = db_manager.update_class(self.class_obj.class_id, class_name, grade)
                if success:
                    msg = create_styled_message_box(self, "Başarılı", "Sınıf bilgileri başarıyla güncellendi.")
                    msg.exec_()
                    self.accept()
                else:
                    msg = create_styled_message_box(self, "Hata", "Sınıf bilgileri güncellenirken bir hata oluştu.", QMessageBox.Critical)
                    msg.exec_()
            else:
                # Add new class
                class_id = db_manager.add_class(class_name, grade)
                if class_id:
                    msg = create_styled_message_box(self, "Başarılı", "Sınıf başarıyla eklendi.")
                    msg.exec_()
                    self.accept()
        except Exception as e:
            msg = create_styled_message_box(self, "Hata", f"Sınıf kaydedilirken bir hata oluştu: {str(e)}", QMessageBox.Critical)
            msg.exec_()