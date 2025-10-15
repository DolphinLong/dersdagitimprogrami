"""
Conflict Resolution Dialog for the Class Scheduling Program
"""

import logging

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
)

from database import db_manager
from utils.helpers import create_styled_message_box


class ConflictResolutionDialog(QDialog):
    """Dialog for resolving schedule conflicts"""

    def __init__(self, conflicts, parent=None):
        super().__init__(parent)
        self.conflicts = conflicts
        self.setWindowTitle("Çakışma Çözümleme")
        self.setFixedSize(800, 600)
        self.setup_ui()
        self.populate_conflicts()
        self.apply_styles()

    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QVBoxLayout()
        header_layout.setSpacing(10)

        title_label = QLabel("Çakışma Çözümleme")
        title_label.setAlignment(Qt.AlignCenter)  # type: ignore
        title_label.setObjectName("titleLabel")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))

        desc_label = QLabel(
            f"Toplam {len(self.conflicts)} çakışma bulundu. Çakışmaları inceleyin ve çözümleyin."
        )
        desc_label.setAlignment(Qt.AlignCenter)  # type: ignore
        desc_label.setObjectName("descLabel")
        desc_label.setWordWrap(True)

        header_layout.addWidget(title_label)
        header_layout.addWidget(desc_label)
        header_frame.setLayout(header_layout)
        layout.addWidget(header_frame)

        # Conflict table
        self.conflict_table = QTableWidget()
        self.conflict_table.setColumnCount(5)
        self.conflict_table.setHorizontalHeaderLabels(
            ["Çakışma Türü", "Sınıf", "Öğretmen", "Gün", "Saat Aralığı"]
        )
        self.conflict_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.conflict_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.conflict_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # type: ignore
        self.conflict_table.verticalHeader().setVisible(False)  # type: ignore

        layout.addWidget(self.conflict_table)

        # Conflict details
        details_frame = QFrame()
        details_frame.setObjectName("detailsFrame")
        details_layout = QVBoxLayout()
        details_layout.setSpacing(10)

        details_title = QLabel("Çakışma Detayları:")
        details_title.setObjectName("detailsTitle")
        details_title.setFont(QFont("Segoe UI", 12, QFont.Bold))

        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(100)

        details_layout.addWidget(details_title)
        details_layout.addWidget(self.details_text)
        details_frame.setLayout(details_layout)
        layout.addWidget(details_frame)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.resolve_button = QPushButton("Çakışmayı Çöz")
        self.resolve_button.setObjectName("resolveButton")
        self.resolve_button.clicked.connect(self.resolve_conflict)
        self.resolve_button.setEnabled(False)

        self.auto_resolve_button = QPushButton("Tümünü Otomatik Çöz")
        self.auto_resolve_button.setObjectName("autoResolveButton")
        self.auto_resolve_button.clicked.connect(self.auto_resolve_conflicts)

        self.close_button = QPushButton("Kapat")
        self.close_button.setObjectName("closeButton")
        self.close_button.clicked.connect(self.accept)

        button_layout.addWidget(self.resolve_button)
        button_layout.addWidget(self.auto_resolve_button)
        button_layout.addWidget(self.close_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Connect table selection
        self.conflict_table.itemSelectionChanged.connect(self.on_conflict_selected)

    def apply_styles(self):
        """Apply styles to the dialog"""
        self.setStyleSheet(
            """
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #ffffff, stop: 1 #f8f9fa);
            }
            #headerFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #2c3e50, stop: 1 #4a6491);
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 10px;
            }
            #titleLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
            #descLabel {
                color: rgba(255, 255, 255, 0.9);
                font-size: 14px;
            }
            #detailsFrame {
                background: rgba(255, 255, 255, 0.8);
                border-radius: 8px;
                border: 1px solid #dee2e6;
                padding: 15px;
            }
            #detailsTitle {
                color: #2c3e50;
                font-weight: bold;
                margin-bottom: 5px;
            }
            QLabel {
                color: #212529;
                font-size: 14px;
            }
            QTableWidget {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                gridline-color: #e9ecef;
                background-color: white;
                alternate-background-color: #f8f9fa;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
            QTextEdit {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
                background-color: #f8f9fa;
            }
            QPushButton {
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                color: white;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #3498db, stop: 1 #2980b9);
                font-size: 12px;
                min-width: 120px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #2980b9, stop: 1 #2573a7);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #2573a7, stop: 1 #1f618d);
            }
            #resolveButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #27ae60, stop: 1 #219653);
            }
            #resolveButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #219653, stop: 1 #1e8449);
            }
            #autoResolveButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #f39c12, stop: 1 #e67e22);
            }
            #autoResolveButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #e67e22, stop: 1 #d35400);
            }
            #closeButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #e74c3c, stop: 1 #c0392b);
            }
            #closeButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #c0392b, stop: 1 #a93226);
            }
        """
        )

    def populate_conflicts(self):
        """Populate the conflict table with conflict data"""
        self.conflict_table.setRowCount(len(self.conflicts))

        day_names = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
        time_slot_labels = []

        # Get school type to determine time slots
        school_type = db_manager.get_school_type()
        if not school_type:
            school_type = "Lise"

        time_slots_count = 8  # Default to 8 time slots
        if school_type == "İlkokul":
            time_slots_count = 6
        elif school_type == "Ortaokul":
            time_slots_count = 7

        for i in range(time_slots_count):
            start_hour = 8 + i
            end_hour = 9 + i
            time_slot_labels.append(f"{start_hour:02d}:00-{end_hour:02d}:00")

        for row, conflict in enumerate(self.conflicts):
            # Get conflict details
            conflict_type = conflict["type"]
            entry1 = conflict["entry1"]
            entry2 = conflict["entry2"]

            # Handle both dictionary and ScheduleEntry object formats
            # For entry1
            try:
                if isinstance(entry1, dict):
                    entry1_class_id = entry1.get("class_id")
                    entry1_teacher_id = entry1.get("teacher_id")
                    entry1_day = entry1.get("day")
                    entry1_time_slot = entry1.get("time_slot")
                    entry1_lesson_id = entry1.get("lesson_id")
                else:
                    entry1_class_id = getattr(entry1, "class_id", None)
                    entry1_teacher_id = getattr(entry1, "teacher_id", None)
                    entry1_day = getattr(entry1, "day", None)
                    entry1_time_slot = getattr(entry1, "time_slot", None)
                    entry1_lesson_id = getattr(entry1, "lesson_id", None)
            except Exception as e:
                print(f"Entry1 error: {e}, entry1 type: {type(entry1)}, entry1: {entry1}")
                continue

            # For entry2
            try:
                if isinstance(entry2, dict):
                    entry2_class_id = entry2.get("class_id")
                    entry2_teacher_id = entry2.get("teacher_id")
                    entry2_day = entry2.get("day")
                    entry2_time_slot = entry2.get("time_slot")
                    entry2_lesson_id = entry2.get("lesson_id")
                else:
                    entry2_class_id = getattr(entry2, "class_id", None)
                    entry2_teacher_id = getattr(entry2, "teacher_id", None)
                    entry2_day = getattr(entry2, "day", None)
                    entry2_time_slot = getattr(entry2, "time_slot", None)
                    entry2_lesson_id = getattr(entry2, "lesson_id", None)
            except Exception as e:
                print(f"Entry2 error: {e}, entry2 type: {type(entry2)}, entry2: {entry2}")
                continue

            # Get related data for entry1
            class1 = db_manager.get_class_by_id(entry1_class_id) if entry1_class_id else None
            teacher1 = (
                db_manager.get_teacher_by_id(entry1_teacher_id) if entry1_teacher_id else None
            )

            # Get related data for entry2
            class2 = db_manager.get_class_by_id(entry2_class_id) if entry2_class_id else None
            teacher2 = (
                db_manager.get_teacher_by_id(entry2_teacher_id) if entry2_teacher_id else None
            )

            # Conflict type
            type_text = "Öğretmen Çakışması" if "teacher" in conflict_type else "Sınıf Çakışması"
            type_item = QTableWidgetItem(type_text)
            type_item.setTextAlignment(Qt.AlignCenter)  # type: ignore

            # Class names
            class_text = f"{class1.name if class1 else 'Bilinmiyor'} / {class2.name if class2 else 'Bilinmiyor'}"
            class_item = QTableWidgetItem(class_text)
            class_item.setTextAlignment(Qt.AlignCenter)  # type: ignore

            # Teacher names
            teacher_text = f"{teacher1.name if teacher1 else 'Bilinmiyor'} / {teacher2.name if teacher2 else 'Bilinmiyor'}"
            teacher_item = QTableWidgetItem(teacher_text)
            teacher_item.setTextAlignment(Qt.AlignCenter)  # type: ignore

            # Day
            day_text = (
                day_names[entry1_day]
                if entry1_day is not None and entry1_day < len(day_names)
                else f"Gün {entry1_day}"
            )
            day_item = QTableWidgetItem(day_text)
            day_item.setTextAlignment(Qt.AlignCenter)  # type: ignore

            # Time slot
            time_text = (
                time_slot_labels[entry1_time_slot]
                if entry1_time_slot is not None and entry1_time_slot < len(time_slot_labels)
                else f"Saat {entry1_time_slot}"
            )
            time_item = QTableWidgetItem(time_text)
            time_item.setTextAlignment(Qt.AlignCenter)  # type: ignore

            # Set items in table
            self.conflict_table.setItem(row, 0, type_item)
            self.conflict_table.setItem(row, 1, class_item)
            self.conflict_table.setItem(row, 2, teacher_item)
            self.conflict_table.setItem(row, 3, day_item)
            self.conflict_table.setItem(row, 4, time_item)

    def on_conflict_selected(self):
        """Handle conflict selection"""
        selected_rows = self.conflict_table.selectionModel().selectedRows()  # type: ignore
        if selected_rows:
            self.resolve_button.setEnabled(True)
            row = selected_rows[0].row()
            conflict = self.conflicts[row]
            self.show_conflict_details(conflict)
        else:
            self.resolve_button.setEnabled(False)
            self.details_text.clear()

    def show_conflict_details(self, conflict):
        """Show detailed information about a conflict"""
        entry1 = conflict["entry1"]
        entry2 = conflict["entry2"]

        # Handle both dictionary and ScheduleEntry object formats
        # For entry1
        if isinstance(entry1, dict):
            entry1_class_id = entry1.get("class_id")
            entry1_teacher_id = entry1.get("teacher_id")
            entry1_lesson_id = entry1.get("lesson_id")
            entry1_day = entry1.get("day")
            entry1_time_slot = entry1.get("time_slot")
        else:
            entry1_class_id = getattr(entry1, "class_id", None)
            entry1_teacher_id = getattr(entry1, "teacher_id", None)
            entry1_lesson_id = getattr(entry1, "lesson_id", None)
            entry1_day = getattr(entry1, "day", None)
            entry1_time_slot = getattr(entry1, "time_slot", None)

        # For entry2
        if isinstance(entry2, dict):
            entry2_class_id = entry2.get("class_id")
            entry2_teacher_id = entry2.get("teacher_id")
            entry2_lesson_id = entry2.get("lesson_id")
            entry2_day = entry2.get("day")
            entry2_time_slot = entry2.get("time_slot")
        else:
            entry2_class_id = getattr(entry2, "class_id", None)
            entry2_teacher_id = getattr(entry2, "teacher_id", None)
            entry2_lesson_id = getattr(entry2, "lesson_id", None)
            entry2_day = getattr(entry2, "day", None)
            entry2_time_slot = getattr(entry2, "time_slot", None)

        # Get related data for entry1
        class1 = db_manager.get_class_by_id(entry1_class_id) if entry1_class_id else None
        teacher1 = db_manager.get_teacher_by_id(entry1_teacher_id) if entry1_teacher_id else None
        lesson1 = db_manager.get_lesson_by_id(entry1_lesson_id) if entry1_lesson_id else None

        # Get related data for entry2
        class2 = db_manager.get_class_by_id(entry2_class_id) if entry2_class_id else None
        teacher2 = db_manager.get_teacher_by_id(entry2_teacher_id) if entry2_teacher_id else None
        lesson2 = db_manager.get_lesson_by_id(entry2_lesson_id) if entry2_lesson_id else None

        day_names = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
        day_text = (
            day_names[entry1_day]
            if entry1_day is not None and entry1_day < len(day_names)
            else f"Gün {entry1_day}"
        )

        # Get school type to determine time slots
        school_type = db_manager.get_school_type()
        if not school_type:
            school_type = "Lise"

        time_slots_count = 8  # Default to 8 time slots
        if school_type == "İlkokul":
            time_slots_count = 6
        elif school_type == "Ortaokul":
            time_slots_count = 7

        time_slot_labels = []
        for i in range(time_slots_count):
            start_hour = 8 + i
            end_hour = 9 + i
            time_slot_labels.append(f"{start_hour:02d}:00-{end_hour:02d}:00")

        time_text = (
            time_slot_labels[entry1_time_slot]
            if entry1_time_slot is not None and entry1_time_slot < len(time_slot_labels)
            else f"Saat {entry1_time_slot}"
        )

        details = f"""
Çakışma Türü: {"Öğretmen Çakışması" if "teacher" in conflict['type'] else "Sınıf Çakışması"}

--- İlk Kayıt ---
Sınıf: {class1.name if class1 else 'Bilinmiyor'}
Öğretmen: {teacher1.name if teacher1 else 'Bilinmiyor'}
Ders: {lesson1.name if lesson1 else 'Bilinmiyor'}
Gün: {day_text}
Saat: {time_text}

--- İkinci Kayıt ---
Sınıf: {class2.name if class2 else 'Bilinmiyor'}
Öğretmen: {teacher2.name if teacher2 else 'Bilinmiyor'}
Ders: {lesson2.name if lesson2 else 'Bilinmiyor'}
Gün: {day_text}
Saat: {time_text}
        """

        self.details_text.setPlainText(details.strip())

    def resolve_conflict(self):
        """Resolve the selected conflict"""
        selected_rows = self.conflict_table.selectionModel().selectedRows()  # type: ignore
        if not selected_rows:
            return

        row = selected_rows[0].row()
        conflict = self.conflicts[row]

        # Use the conflict resolver to resolve this conflict
        from algorithms.conflict_resolver import ConflictResolver

        resolver = ConflictResolver(db_manager)

        conflict_type = conflict["type"]
        resolved = False

        if "teacher" in conflict_type:
            resolved = resolver.resolve_teacher_conflict(conflict)
        elif "class" in conflict_type:
            resolved = resolver.resolve_class_conflict(conflict)
        else:
            # For other types of conflicts, try a generic approach
            entry1 = conflict["entry1"]
            resolved = resolver._move_entry_to_available_slot(entry1)

        if resolved:
            msg = create_styled_message_box(
                self, "Başarılı", "Çakışma başarıyla çözüldü. Program yenileniyor."
            )
            msg.exec_()

            # Close the dialog and refresh the schedule
            self.accept()
            # Notify parent to refresh schedule
            parent = self.parent()
            if parent and hasattr(parent, "load_schedule_data"):
                try:
                    getattr(parent, "load_schedule_data")()
                except AttributeError:
                    # Parent doesn't implement the refresh method; nothing to do
                    logging.debug("Parent has no load_schedule_data method to call.")
                except Exception as e:
                    # Log unexpected errors but do not crash the UI
                    logging.warning(f"Error while calling parent.load_schedule_data: {e}")
        else:
            msg = create_styled_message_box(
                self,
                "Uyarı",
                "Çakışma çözülemedi. Manuel müdahale gerekebilir.",
                QMessageBox.Warning,
            )
            msg.exec_()

    def auto_resolve_conflicts(self):
        """Attempt to automatically resolve all conflicts"""
        # Use the conflict resolver to resolve all conflicts
        from algorithms.conflict_resolver import ConflictResolver

        resolver = ConflictResolver(db_manager)

        resolved_count = resolver.auto_resolve_conflicts(self.conflicts)

        msg = create_styled_message_box(
            self,
            "Bilgi",
            f"Otomatik çözümleme tamamlandı. {resolved_count} çakışma çözüldü. {len(self.conflicts) - resolved_count} çakışma hala devam ediyor.",
        )
        msg.exec_()

        # Close the dialog and refresh the schedule
        self.accept()
        # Notify parent to refresh schedule
        parent = self.parent()
        if parent and hasattr(parent, "load_schedule_data"):
            try:
                getattr(parent, "load_schedule_data")()
            except AttributeError:
                logging.debug("Parent has no load_schedule_data method to call.")
            except Exception as e:
                logging.warning(f"Error while calling parent.load_schedule_data: {e}")
