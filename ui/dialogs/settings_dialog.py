"""
Settings dialog for the Class Scheduling Program
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from database import db_manager
from ui.school_type_dialog import SchoolTypeDialog
from utils.helpers import create_styled_message_box


class SettingsDialog(QDialog):
    """Dialog for application settings"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ayarlar")
        self.setFixedSize(500, 400)
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        """Set up the user interface with modern design"""
        layout = QVBoxLayout()
        layout.setSpacing(25)
        layout.setContentsMargins(30, 30, 30, 30)

        # Header section
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QVBoxLayout()
        header_layout.setSpacing(10)
        header_layout.setContentsMargins(20, 20, 20, 20)

        # Icon
        icon_label = QLabel("⚙️")
        icon_label.setAlignment(Qt.AlignCenter)  # type: ignore
        icon_label.setStyleSheet("font-size: 32px; margin: 10px;")

        title_label = QLabel("Ayarlar")
        title_label.setAlignment(Qt.AlignCenter)  # type: ignore
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")

        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)

        header_frame.setLayout(header_layout)
        layout.addWidget(header_frame)

        # School type selection
        school_type_layout = QVBoxLayout()
        school_type_label = QLabel("Okul Türü:")
        school_type_label.setObjectName("fieldLabel")
        school_type_label.setFont(QFont("Segoe UI", 14, QFont.Bold))

        self.school_type_combo = QComboBox()
        self.school_type_combo.setObjectName("schoolTypeCombo")
        self.school_type_combo.setFont(QFont("Segoe UI", 12))

        # Add school types to combo box
        for school_type in SchoolTypeDialog.SCHOOL_TYPES.keys():
            self.school_type_combo.addItem(school_type)

        # Apply styling directly to the combo box view
        self.school_type_combo.view().setStyleSheet(
            """
            background: white;
            color: #212529;
            selection-background-color: #3498db;
            selection-color: white;
        """
        )

        # Set current selection
        current_school_type = db_manager.get_school_type()
        if current_school_type:
            index = self.school_type_combo.findText(current_school_type)
            if index >= 0:
                self.school_type_combo.setCurrentIndex(index)

        school_type_layout.addWidget(school_type_label)
        school_type_layout.addWidget(self.school_type_combo)
        layout.addLayout(school_type_layout)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_button = QPushButton("✅ Kaydet")
        self.save_button.setObjectName("saveButton")
        self.save_button.clicked.connect(self.save_settings)
        self.save_button.setFont(QFont("Segoe UI", 12))

        self.cancel_button = QPushButton("❌ İptal")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setFont(QFont("Segoe UI", 12))

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def apply_styles(self):
        """Apply modern styles with improved design"""
        self.setStyleSheet(
            """
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #ffffff, stop: 1 #f8f9fa);
                border-radius: 12px;
            }
            #headerFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #2c3e50, stop: 1 #4a6491);
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            #iconLabel {
                color: white;
                margin: 10px 0;
            }
            #titleLabel {
                color: white;
                font-size: 24px;
                margin: 10px 0 5px 0;
            }
            QLabel {
                color: #212529;
                font-size: 14px;
            }
            #fieldLabel {
                font-weight: bold;
                color: #3498db;
                font-size: 14px;
                margin-bottom: 5px;
            }
            QComboBox {
                padding: 12px;
                border: 2px solid #cccccc;
                border-radius: 8px;
                background: white;
                font-size: 14px;
                min-height: 20px;
            }
            QComboBox:focus {
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
        """
        )

    def save_settings(self):
        """Save settings"""
        selected_school_type = self.school_type_combo.currentText()
        current_school_type = db_manager.get_school_type()

        # Save school type if it's different
        if selected_school_type != current_school_type:
            db_manager.set_school_type(selected_school_type)
            msg = create_styled_message_box(
                self, "Başarılı", f"Okul türü {selected_school_type} olarak güncellendi."
            )
            msg.exec_()

        self.accept()
