"""
Teacher availability dialog for the Class Scheduling Program
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from database import db_manager
from utils.helpers import create_styled_message_box


class TeacherAvailabilityDialog(QDialog):
    """Dialog for setting teacher availability"""

    # Define time slots for each school type
    SCHOOL_TIME_SLOTS = {
        "İlkokul": 6,
        "Ortaokul": 7,
        "Lise": 8,
        "Anadolu Lisesi": 8,
        "Fen Lisesi": 8,
        "Sosyal Bilimler Lisesi": 8,
    }

    def __init__(self, parent=None, teacher=None):
        super().__init__(parent)
        self.teacher = teacher
        self.availability_data = {}  # Store availability data locally
        self.setWindowTitle(
            f"Öğretmen Uygunluk Ayarları - {teacher.name if teacher else 'Yeni Öğretmen'}"
        )
        self.setFixedSize(900, 600)
        self.setup_ui()
        self.load_availability_data()
        self.apply_styles()

    def setup_ui(self):
        """Set up the user interface with modern design"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title with modern styling
        title_label = QLabel(
            f"Öğretmen Uygunluk Ayarları - {self.teacher.name if self.teacher else 'Yeni Öğretmen'}"
        )
        title_label.setAlignment(Qt.AlignCenter)  # type: ignore
        title_label.setObjectName("titleLabel")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(title_label)

        # Instruction label
        instruction_label = QLabel(
            "Aşağıdaki tabloda öğretmenin uygun olduğu saatleri işaretleyin. Yeşil: Uygun, Kırmızı: Uygun Değil"
        )
        instruction_label.setWordWrap(True)
        instruction_label.setAlignment(Qt.AlignCenter)  # type: ignore
        instruction_label.setObjectName("instructionLabel")
        layout.addWidget(instruction_label)

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

        # Availability table
        self.availability_table = QTableWidget()
        self.availability_table.setColumnCount(time_slots_count)  # Time slots based on school type
        self.availability_table.setRowCount(5)  # Days (Monday-Friday)
        self.availability_table.setHorizontalHeaderLabels(time_slot_labels)
        self.availability_table.setVerticalHeaderLabels(
            ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
        )

        # Set table properties
        self.availability_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.availability_table.setSelectionMode(QTableWidget.SingleSelection)
        self.availability_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.availability_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Connect cell click event
        self.availability_table.cellClicked.connect(self.toggle_availability)

        layout.addWidget(self.availability_table)

        # Buttons layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_button = QPushButton("✅ Kaydet")
        self.save_button.setObjectName("saveButton")
        self.save_button.clicked.connect(self.save_availability)

        self.cancel_button = QPushButton("❌ İptal")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.reject)

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
            #titleLabel {
                font-size: 18px;
                color: #2c3e50;
                margin-bottom: 10px;
                text-align: center;
            }
            #instructionLabel {
                font-size: 14px;
                color: #495057;
                margin-bottom: 10px;
                text-align: center;
            }
            QTableWidget {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                gridline-color: #e9ecef;
                background-color: white;
                alternate-background-color: #f8f9fa;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #e9ecef;
                selection-background-color: transparent;
                selection-color: black;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
                border-right: 1px solid #2980b9;
            }
            QHeaderView::section:last {
                border-right: none;
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

    def load_availability_data(self):
        """Load availability data from database"""
        if not self.teacher:
            return

        # Get availability data from database
        availability_list = db_manager.get_teacher_availability(self.teacher.teacher_id)

        # Store in local dictionary for easy access
        self.availability_data = {}
        for item in availability_list:
            key = (item["day"], item["time_slot"])
            self.availability_data[key] = item["is_available"]

        # Update table display
        self.update_table_display()

    def update_table_display(self):
        """Update table display based on availability data"""
        # Get school type and time slots
        school_type = db_manager.get_school_type()
        if not school_type:
            school_type = "Lise"

        time_slots_count = self.SCHOOL_TIME_SLOTS.get(school_type, 8)

        # Clear the table first
        for day in range(5):
            for time_slot in range(time_slots_count):
                item = QTableWidgetItem("")
                item.setTextAlignment(Qt.AlignCenter)  # type: ignore
                item.setBackground(QColor(165, 214, 167))  # Light green (default available)
                self.availability_table.setItem(day, time_slot, item)

        # Update with actual availability data
        for day in range(5):  # 5 days
            for time_slot in range(time_slots_count):  # Time slots based on school type
                key = (day, time_slot)
                is_available = self.availability_data.get(key, True)  # Default to available

                item = self.availability_table.item(day, time_slot)
                if not item:
                    item = QTableWidgetItem("")
                    item.setTextAlignment(Qt.AlignCenter)  # type: ignore
                    self.availability_table.setItem(day, time_slot, item)

                # Set color based on availability
                if is_available:
                    item.setBackground(QColor(165, 214, 167))  # Light green
                    item.setText("Uygun")  # Add text to make it clearer
                else:
                    item.setBackground(QColor(239, 154, 154))  # Light red
                    item.setText("Uygun Değil")  # Add text to make it clearer

    def toggle_availability(self, row, column):
        """Toggle availability for a specific day and time slot"""
        key = (row, column)
        current_state = self.availability_data.get(key, True)  # Default to available
        new_state = not current_state
        self.availability_data[key] = new_state

        # Update display
        item = self.availability_table.item(row, column)
        if not item:
            item = QTableWidgetItem("")
            item.setTextAlignment(Qt.AlignCenter)  # type: ignore
            self.availability_table.setItem(row, column, item)

        if new_state:
            item.setBackground(QColor(165, 214, 167))  # Light green
            item.setText("Uygun")
        else:
            item.setBackground(QColor(239, 154, 154))  # Light red
            item.setText("Uygun Değil")

    def save_availability(self):
        """Save availability data to database"""
        if not self.teacher:
            msg = create_styled_message_box(
                self, "Hata", "Öğretmen bilgisi bulunamadı.", QMessageBox.Warning
            )
            msg.exec_()
            return

        try:
            # Save each availability entry
            success_count = 0
            for (day, time_slot), is_available in self.availability_data.items():
                if db_manager.set_teacher_availability(
                    self.teacher.teacher_id, day, time_slot, is_available
                ):
                    success_count += 1

            msg = create_styled_message_box(
                self,
                "Başarılı",
                f"Öğretmen uygunluk bilgileri başarıyla kaydedildi. {success_count} kayıt güncellendi.",
            )
            msg.exec_()
            self.accept()
        except Exception as e:
            msg = create_styled_message_box(
                self,
                "Hata",
                f"Uygunluk bilgileri kaydedilirken bir hata oluştu: {str(e)}",
                QMessageBox.Critical,
            )
            msg.exec_()
