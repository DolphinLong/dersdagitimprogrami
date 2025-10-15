"""
Class schedule dialog - FINAL FIX
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QFont
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from database import db_manager
from utils.helpers import generate_color_for_lesson


class ClassScheduleDialog(QDialog):

    SCHOOL_TIME_SLOTS = {
        "İlkokul": 6,
        "Ortaokul": 7,
        "Lise": 8,
        "Anadolu Lisesi": 8,
        "Fen Lisesi": 8,
        "Sosyal Bilimler Lisesi": 8,
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        # Force Fusion style
        from PyQt5.QtWidgets import QApplication

        app = QApplication.instance()
        app.setStyle("Fusion")
        print(f"✅ Style set to: {app.style().objectName()}")

        self.setWindowTitle("Sınıf Programı Görüntüle")
        self.setFixedSize(1000, 600)
        self.setup_ui()
        self.populate_classes()
        self.apply_styles()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title_label = QLabel("SINIF PROGRAMI")
        title_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(title_label)

        # Class selection
        class_layout = QHBoxLayout()
        class_label = QLabel("Sınıf:")
        self.class_combo = QComboBox()
        self.class_combo.currentIndexChanged.connect(self.load_class_schedule)

        class_layout.addWidget(class_label)
        class_layout.addWidget(self.class_combo, 1)
        layout.addLayout(class_layout)

        # Get school type
        school_type = db_manager.get_school_type()
        if not school_type:
            school_type = "Lise"

        time_slots_count = self.SCHOOL_TIME_SLOTS.get(school_type, 8)

        # Time slot labels
        time_slot_labels = []
        for i in range(time_slots_count):
            start_hour = 8 + i
            end_hour = 9 + i
            time_slot_labels.append(f"{start_hour:02d}:00-{end_hour:02d}:00")

        # Schedule table
        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(time_slots_count)
        self.schedule_table.setRowCount(5)
        self.schedule_table.setHorizontalHeaderLabels(time_slot_labels)
        self.schedule_table.setVerticalHeaderLabels(
            ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
        )

        # Table properties
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
        """Apply styles WITHOUT item background override"""
        self.setStyleSheet(
            """
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
            }
            QComboBox:hover {
                border: 2px solid #3498db;
            }
            QComboBox::drop-down {
                border: none;
                border-radius: 8px;
                padding-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #2c3e50;
                selection-background-color: #3498db;
                selection-color: white;
                border: 1px solid #dcdde1;
                outline: 0px;
                padding: 5px;
            }
            QComboBox QAbstractItemView::item {
                background-color: white;
                color: #2c3e50;
                padding: 8px;
                min-height: 30px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #ecf0f1;
                color: #2c3e50;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #3498db;
                color: white;
            }
            QTableWidget {
                border: 2px solid #dee2e6;
                border-radius: 12px;
                gridline-color: #e9ecef;
                background-color: white;
            }
            /* NO ITEM BACKGROUND STYLES - Let setBackground() work */
            QHeaderView::section {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #3498db, stop: 1 #2980b9);
                color: white;
                padding: 15px;
                font-weight: bold;
                border-right: 1px solid #2980b9;
            }
            QPushButton {
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                color: white;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #e74c3c, stop: 1 #c0392b);
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #c0392b, stop: 1 #a93226);
            }
        """
        )

    def populate_classes(self):
        self.class_combo.clear()
        classes = db_manager.get_all_classes()
        for class_obj in classes:
            self.class_combo.addItem(class_obj.name, class_obj.class_id)

    def load_class_schedule(self):
        class_id = self.class_combo.currentData()
        if not class_id:
            return

        # Get schedule entries
        class_entries = db_manager.get_schedule_for_specific_class(class_id)

        # Clear table
        for row in range(self.schedule_table.rowCount()):
            for col in range(self.schedule_table.columnCount()):
                self.schedule_table.setItem(row, col, QTableWidgetItem(""))

        # Populate table
        for entry in class_entries:
            lesson = db_manager.get_lesson_by_id(entry.lesson_id)
            teacher = db_manager.get_teacher_by_id(entry.teacher_id)
            classroom = db_manager.get_classroom_by_id(entry.classroom_id)

            if lesson and teacher and classroom:
                display_text = f"📚 {lesson.name}\n👨‍🏫 {teacher.name}\n🏫 {classroom.name}"

                item = QTableWidgetItem(display_text)
                item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)

                # Generate and apply color
                color = generate_color_for_lesson(lesson.name)
                item.setBackground(QBrush(color))
                item.setForeground(QBrush(QColor(255, 255, 255)))

                # Bold font
                font = QFont("Segoe UI", 10, QFont.Bold)
                item.setFont(font)

                self.schedule_table.setItem(entry.day, entry.time_slot, item)

                print(
                    f"✓ Set color for {lesson.name}: RGB({color.red()}, {color.green()}, {color.blue()})"
                )
