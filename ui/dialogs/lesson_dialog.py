import logging

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from database import db_manager
from utils.helpers import create_styled_message_box


class LessonDialog(QDialog):
    """Dialog for adding or editing lessons and their curriculum."""

    def __init__(self, parent=None, lesson=None):
        super().__init__(parent)
        self.lesson = lesson
        self.setWindowTitle("Ders ve Müfredat Yönetimi")
        self.setMinimumSize(500, 600)
        self.setup_ui()
        self.populate_data()
        self.apply_styles()

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel("Ders ve Müfredat Yönetimi")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Name input
        name_layout = QHBoxLayout()
        name_label = QLabel("Ders Adı:")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Dersin adını girin")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # Curriculum Table
        curriculum_label = QLabel("Sınıf Seviyesine Göre Haftalık Ders Saatleri:")
        layout.addWidget(curriculum_label)

        self.curriculum_table = QTableWidget()
        self.curriculum_table.setColumnCount(2)
        self.curriculum_table.setHorizontalHeaderLabels(["Sınıf Seviyesi", "Haftalık Saat"])
        self.curriculum_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.curriculum_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        layout.addWidget(self.curriculum_table)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.save_button = QPushButton("✅ Kaydet")
        self.save_button.clicked.connect(self.save_lesson_and_curriculum)
        self.cancel_button = QPushButton("❌ İptal")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def populate_data(self):
        """Populate dialog with existing lesson and curriculum data."""
        # Define grades based on school type
        school_type = db_manager.get_school_type()
        if school_type == "İlkokul":
            grades = list(range(1, 5))
        elif school_type == "Ortaokul":
            grades = list(range(5, 9))
        else:  # Lise and others
            grades = list(range(9, 13))

        self.curriculum_table.setRowCount(len(grades))

        # Store grades in the first column (as non-editable items)
        for i, grade in enumerate(grades):
            grade_item = QTableWidgetItem(f"{grade}. Sınıf")
            grade_item.setData(Qt.UserRole, grade)
            grade_item.setFlags(grade_item.flags() & ~Qt.ItemIsEditable)
            self.curriculum_table.setItem(i, 0, grade_item)

            # Add an empty item for weekly hours
            self.curriculum_table.setItem(i, 1, QTableWidgetItem(""))

        if self.lesson:
            self.name_input.setText(self.lesson.name)
            # Get curriculum data for the lesson
            curriculum_data = db_manager.get_curriculum_for_lesson(self.lesson.lesson_id)
            curriculum_map = {item.grade: item.weekly_hours for item in curriculum_data}

            # Populate the table with existing hours
            for i in range(self.curriculum_table.rowCount()):
                grade_item = self.curriculum_table.item(i, 0)
                grade = grade_item.data(Qt.UserRole)
                if grade in curriculum_map:
                    self.curriculum_table.item(i, 1).setText(str(curriculum_map[grade]))

    def save_lesson_and_curriculum(self):
        """Save lesson name and its curriculum data."""
        lesson_name = self.name_input.text().strip()
        if not lesson_name:
            create_styled_message_box(
                self, "Hata", "Ders adı boş bırakılamaz.", QMessageBox.Warning
            ).exec_()
            return

        try:
            # Step 1: Save the lesson name (add or update)
            if self.lesson:
                # Update existing lesson name if it has changed
                if self.lesson.name != lesson_name:
                    db_manager.update_lesson(self.lesson.lesson_id, lesson_name)
                lesson_id = self.lesson.lesson_id
            else:
                # Add new lesson
                lesson_id = db_manager.add_lesson(lesson_name)
                if not lesson_id:
                    # This could happen if the lesson name is not unique
                    create_styled_message_box(
                        self,
                        "Hata",
                        f"'{lesson_name}' adında bir ders zaten mevcut veya eklenemedi.",
                        QMessageBox.Critical,
                    ).exec_()
                    return

            # Step 2: Save the curriculum data from the table
            for i in range(self.curriculum_table.rowCount()):
                grade = self.curriculum_table.item(i, 0).data(Qt.UserRole)
                hours_text = self.curriculum_table.item(i, 1).text().strip()

                if hours_text:
                    try:
                        weekly_hours = int(hours_text)
                        db_manager.add_or_update_curriculum(lesson_id, grade, weekly_hours)
                    except ValueError:
                        create_styled_message_box(
                            self,
                            "Hata",
                            f"{grade}. sınıf için girilen saat geçersiz bir sayı.",
                            QMessageBox.Warning,
                        ).exec_()
                        return  # Stop saving on first error
                else:
                    # Optional: handle empty hours - maybe delete the curriculum entry if it exists
                    pass

            create_styled_message_box(
                self, "Başarılı", "Ders ve müfredat bilgileri başarıyla kaydedildi."
            ).exec_()
            self.accept()

        except Exception as e:
            logging.error(f"Error saving lesson/curriculum: {e}")
            create_styled_message_box(
                self, "Hata", f"Kaydederken bir hata oluştu: {e}", QMessageBox.Critical
            ).exec_()

    def apply_styles(self):
        """Apply modern styles."""
        self.setStyleSheet(
            """
            QDialog {
                background-color: #f8f9fa;
            }
            QLabel, QLineEdit, QPushButton {
                font-size: 14px;
            }
            #title {
                font-size: 18px;
                font-weight: bold;
                color: #343a40;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ced4da;
                border-radius: 4px;
            }
            QTableWidget {
                border: 1px solid #dee2e6;
            }
            QPushButton {
                padding: 10px 15px;
                border: none;
                border-radius: 4px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
        """
        )
