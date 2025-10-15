"""
Lesson assignment dialog for the Class Scheduling Program
This dialog allows users to assign lessons to teachers and classes in a more intuitive way.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListView,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from database import db_manager


class LessonAssignmentDialog(QDialog):
    """Dialog for assigning lessons to teachers and classes"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ders Atama")
        self.resize(750, 700)  # Changed from setFixedSize to allow resizing
        self.setMinimumSize(600, 500)  # Set minimum size to prevent window from becoming too small
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
        title_label = QLabel("DERS ATAMA")
        title_label.setAlignment(Qt.AlignCenter)  # type: ignore
        title_label.setObjectName("dialogTitle")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(title_label)

        # Teacher selection group
        teacher_group = QGroupBox("Öğretmen Seçimi")
        teacher_group.setObjectName("teacherGroup")
        teacher_layout = QFormLayout()
        teacher_layout.setSpacing(15)

        self.teacher_combo = QComboBox()
        self.teacher_combo.setObjectName("teacherCombo")
        self.teacher_combo.setEditable(False)
        teacher_layout.addRow(QLabel("Öğretmen:"), self.teacher_combo)

        teacher_group.setLayout(teacher_layout)
        layout.addWidget(teacher_group)

        # Lesson selection group
        lesson_group = QGroupBox("Ders Seçimi")
        lesson_group.setObjectName("lessonGroup")
        lesson_layout = QFormLayout()
        lesson_layout.setSpacing(15)

        self.lesson_combo = QComboBox()
        self.lesson_combo.setObjectName("lessonCombo")
        self.lesson_combo.setEditable(False)
        lesson_layout.addRow(QLabel("Ders:"), self.lesson_combo)

        lesson_group.setLayout(lesson_layout)
        layout.addWidget(lesson_group)

        # Class selection group
        class_group = QGroupBox("Sınıf Seçimi")
        class_group.setObjectName("classGroup")
        class_layout = QVBoxLayout()
        class_layout.setSpacing(10)

        # Bulk selection controls
        bulk_layout = QHBoxLayout()
        self.bulk_select_checkbox = QCheckBox("Tüm sınıfları seç")
        self.bulk_select_checkbox.setObjectName("bulkSelectCheckbox")
        self.bulk_select_checkbox.stateChanged.connect(self.toggle_bulk_selection)

        self.select_by_grade_checkbox = QCheckBox("Sınıfa göre seç")
        self.select_by_grade_checkbox.setObjectName("selectByGradeCheckbox")
        self.select_by_grade_checkbox.stateChanged.connect(self.toggle_grade_selection)

        bulk_layout.addWidget(self.bulk_select_checkbox)
        bulk_layout.addWidget(self.select_by_grade_checkbox)
        bulk_layout.addStretch()
        class_layout.addLayout(bulk_layout)

        # Grade selection combo (initially hidden)
        self.grade_combo = QComboBox()
        self.grade_combo.setObjectName("gradeCombo")
        self.grade_combo.setVisible(False)
        self.grade_combo.currentIndexChanged.connect(self.filter_classes_by_grade)
        class_layout.addWidget(self.grade_combo)

        # Class list
        self.class_list = QListWidget()
        self.class_list.setObjectName("classList")
        self.class_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.class_list.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)  # Smooth scrolling
        self.class_list.setResizeMode(QListView.Adjust)  # Adjust items when resized
        class_layout.addWidget(self.class_list)

        class_group.setLayout(class_layout)
        layout.addWidget(class_group)

        # Buttons with modern styling
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.assign_button = QPushButton("✅ Ders Ata")
        self.assign_button.setObjectName("assignButton")
        self.assign_button.clicked.connect(self.assign_lesson)

        self.clear_button = QPushButton("🗑️ Temizle")
        self.clear_button.setObjectName("clearButton")
        self.clear_button.clicked.connect(self.clear_selections)

        # Add the delete all assignments button
        self.delete_all_button = QPushButton("🧨 Tüm Atamaları Sil")
        self.delete_all_button.setObjectName("deleteAllButton")
        self.delete_all_button.clicked.connect(self.delete_all_assignments)

        self.close_button = QPushButton("❌ Kapat")
        self.close_button.setObjectName("closeButton")
        self.close_button.clicked.connect(self.reject)

        button_layout.addWidget(self.assign_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.delete_all_button)
        button_layout.addWidget(self.close_button)
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
                QLabel {
                    color: #212529;
                    font-weight: bold;
                    font-size: 14px;
                }
                #dialogTitle {
                    font-size: 20px;
                    color: #2c3e50;
                    margin-bottom: 10px;
                    text-align: center;
                }
                QGroupBox {
                    font-weight: bold;
                    font-size: 16px;
                    color: #3498db;
                    border: 2px solid #3498db;
                    border-radius: 10px;
                    margin-top: 15px;
                    padding-top: 20px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    padding: 0 10px;
                    background-color: #3498db;
                    color: white;
                    border-radius: 5px;
                }
                #teacherGroup, #lessonGroup, #classGroup {
                    font-size: 16px;
                }
                QComboBox {
                    padding: 12px;
                    border: 2px solid #cccccc;
                    border-radius: 8px;
                    background: white;
                    min-width: 200px;
                    font-size: 14px;
                    min-height: 20px;
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
                QListWidget {
                    border: 2px solid #cccccc;
                    border-radius: 8px;
                    background: white;
                    font-size: 14px;
                    min-height: 250px;
                    padding: 5px;
                }
                QListWidget::item {
                    padding: 8px;
                }
                QListWidget::item:selected {
                    background-color: #3498db;
                    color: white;
                }
                QCheckBox {
                    font-weight: bold;
                    font-size: 14px;
                    color: #3498db;
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
                #assignButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                              stop: 0 #27ae60, stop: 1 #219653);
                }
                #assignButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                              stop: 0 #219653, stop: 1 #1e8449);
                }
                #clearButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                              stop: 0 #f39c12, stop: 1 #e67e22);
                }
                #clearButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                              stop: 0 #e67e22, stop: 1 #d35400);
                }
                #deleteAllButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                              stop: 0 #e74c3c, stop: 1 #c0392b);
                }
                #deleteAllButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                              stop: 0 #c0392b, stop: 1 #a93226);
                }
                #closeButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                              stop: 0 #95a5a6, stop: 1 #7f8c8d);
                }
                #closeButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                              stop: 0 #7f8c8d, stop: 1 #6c7a7c);
                }
            """
        )

    def load_data(self):
        """Load data into combo boxes and list"""
        # Load teachers with assigned lesson counts
        teachers = db_manager.get_all_teachers()
        self.teacher_combo.clear()
        self.teacher_combo.addItem("Öğretmen seçin...", None)

        # Get all schedule entries to calculate assigned lesson counts
        all_schedule_entries = db_manager.get_schedule_by_school_type()

        # Create a dictionary to sum weekly hours per teacher
        teacher_weekly_hours = {}

        # For each schedule entry, get the weekly hours for that lesson and class grade
        for entry in all_schedule_entries:
            # Get the class to determine the grade
            class_obj = db_manager.get_class_by_id(entry.class_id)
            if class_obj:
                # Get the weekly hours for this lesson and grade from curriculum
                weekly_hours = db_manager.get_weekly_hours_for_lesson(
                    entry.lesson_id, class_obj.grade
                )
                if weekly_hours:
                    # Add to teacher's total weekly hours
                    teacher_weekly_hours[entry.teacher_id] = (
                        teacher_weekly_hours.get(entry.teacher_id, 0) + weekly_hours
                    )

        for teacher in teachers:
            # Get the total weekly hours for this teacher
            total_hours = teacher_weekly_hours.get(teacher.teacher_id, 0)
            self.teacher_combo.addItem(
                f"{teacher.name} ({teacher.subject}) [{total_hours} saat]", teacher.teacher_id
            )

        # Load lessons and categorize them as mandatory or elective
        lessons = db_manager.get_all_lessons()
        mandatory_lessons = []
        elective_lessons = []

        # Define elective keywords to identify elective subjects
        elective_keywords = [
            "Seçmeli",
            "Dijital",
            "Finansal",
            "Uygulamaları",
            "İtalyanca",
            "Japonca",
            "Robotik",
            "Yapay Zeka",
            "Drama",
            "Geleneksel",
            "Rehberlik",
            "İnkılap",
            "Bilişim Teknolojileri",
        ]

        # Separate mandatory and elective lessons
        for lesson in lessons:
            if any(keyword in lesson.name for keyword in elective_keywords):
                elective_lessons.append(lesson)
            else:
                mandatory_lessons.append(lesson)

        # Clear and repopulate lesson combo with categorized lessons
        self.lesson_combo.clear()
        self.lesson_combo.addItem("Ders seçin...", None)

        # Add mandatory lessons
        if mandatory_lessons:
            # Add a separator before mandatory lessons
            if self.lesson_combo.count() > 1:
                self.lesson_combo.insertSeparator(self.lesson_combo.count())
            # Add mandatory lessons with an indicator
            for lesson in sorted(mandatory_lessons, key=lambda x: x.name):
                self.lesson_combo.addItem(f"📘 Zorunlu: {lesson.name}", lesson.lesson_id)

        # Add elective lessons
        if elective_lessons:
            # Add a separator before elective lessons
            self.lesson_combo.insertSeparator(self.lesson_combo.count())
            # Add elective lessons with an indicator
            for lesson in sorted(elective_lessons, key=lambda x: x.name):
                self.lesson_combo.addItem(f"📚 Seçmeli: {lesson.name}", lesson.lesson_id)

        # Load classes with assigned lesson counts
        self.all_classes = db_manager.get_all_classes()
        self.class_list.clear()

        # Create a dictionary to sum weekly hours per class
        class_weekly_hours = {}

        # For each schedule entry, get the weekly hours for that lesson and class grade
        for entry in all_schedule_entries:
            # Get the class to determine the grade
            class_obj = db_manager.get_class_by_id(entry.class_id)
            if class_obj:
                # Get the weekly hours for this lesson and grade from curriculum
                weekly_hours = db_manager.get_weekly_hours_for_lesson(
                    entry.lesson_id, class_obj.grade
                )
                if weekly_hours:
                    # Add to class's total weekly hours
                    class_weekly_hours[class_obj.class_id] = (
                        class_weekly_hours.get(class_obj.class_id, 0) + weekly_hours
                    )

        for class_obj in self.all_classes:
            # Get the total weekly hours for this class
            total_hours = class_weekly_hours.get(class_obj.class_id, 0)
            # Format: "ClassName (Grade. sınıf) [ClassID] [total_hours saat]"
            item_text = f"{class_obj.name} ({class_obj.grade}. sınıf) [{class_obj.class_id}] [{total_hours} saat]"
            item = QListWidgetItem(item_text)
            # Store class ID in item text itself for easier retrieval
            self.class_list.addItem(item)

        # Load grades for grade filter
        grades = sorted(list(set([class_obj.grade for class_obj in self.all_classes])))
        self.grade_combo.addItem("Sınıf seçin...", None)
        for grade in grades:
            self.grade_combo.addItem(f"{grade}. sınıf", grade)

    def toggle_bulk_selection(self, state):
        """Toggle bulk selection of classes"""
        if state == Qt.Checked:  # type: ignore
            # Select all items
            for i in range(self.class_list.count()):
                item = self.class_list.item(i)
                if item:
                    item.setSelected(True)
        else:
            # Deselect all items
            for i in range(self.class_list.count()):
                item = self.class_list.item(i)
                if item:
                    item.setSelected(False)

    def toggle_grade_selection(self, state):
        """Toggle grade selection visibility"""
        self.grade_combo.setVisible(state == Qt.Checked)  # type: ignore
        if state != Qt.Checked:  # type: ignore
            # If grade selection is disabled, show all classes again
            self.filter_classes_by_grade(0)

    def filter_classes_by_grade(self, index):
        """Filter classes by selected grade"""
        if index <= 0:
            # Show all classes
            for i in range(self.class_list.count()):
                item = self.class_list.item(i)
                if item:
                    item.setHidden(False)
        else:
            # Show only classes of selected grade
            selected_grade = self.grade_combo.currentData()
            if selected_grade:
                for i in range(self.class_list.count()):
                    item = self.class_list.item(i)
                    if item:
                        # Extract grade from item text
                        item_text = item.text()
                        start_idx = item_text.find("(")
                        end_idx = item_text.find(". sınıf)")
                        if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                            try:
                                grade = int(item_text[start_idx + 1 : end_idx])
                                item.setHidden(grade != selected_grade)
                            except ValueError:
                                item.setHidden(True)

    def clear_selections(self):
        """Clear all selections"""
        self.teacher_combo.setCurrentIndex(0)
        self.lesson_combo.setCurrentIndex(0)
        self.bulk_select_checkbox.setChecked(False)
        self.select_by_grade_checkbox.setChecked(False)
        self.grade_combo.setCurrentIndex(0)
        self.grade_combo.setVisible(False)
        # Deselect all classes
        for i in range(self.class_list.count()):
            item = self.class_list.item(i)
            if item:
                item.setSelected(False)
                item.setHidden(False)

    def assign_lesson(self):
        """Assign the selected lesson to the selected classes with the selected teacher"""
        teacher_id = self.teacher_combo.currentData()
        lesson_id = self.lesson_combo.currentData()

        # Get selected classes
        selected_classes = []
        for i in range(self.class_list.count()):
            item = self.class_list.item(i)
            if item and item.isSelected() and not item.isHidden():
                # Extract class ID from the item text
                # Format: "ClassName (Grade. sınıf) [ClassID] [assigned_count ders]"
                item_text = item.text()
                # Find the first bracketed section which contains the class ID
                start_idx = item_text.find("[")
                end_idx = item_text.find("]", start_idx)
                if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                    try:
                        class_id = int(item_text[start_idx + 1 : end_idx])
                        selected_classes.append((class_id, item_text))
                    except ValueError:
                        pass  # Skip invalid class IDs

        if not teacher_id or not lesson_id or not selected_classes:
            QMessageBox.warning(self, "Uyarı", "Lütfen öğretmen, ders ve en az bir sınıf seçin.")
            return

        # Get teacher and lesson details for display
        teacher = db_manager.get_teacher_by_id(teacher_id)
        lesson = db_manager.get_lesson_by_id(lesson_id)

        if not teacher or not lesson:
            QMessageBox.critical(self, "Hata", "Seçilen öğretmen veya ders bulunamadı.")
            return

        # Show confirmation dialog
        class_names = [name for _, name in selected_classes]
        class_list_text = "\n".join(class_names)

        reply = QMessageBox.question(
            self,
            "Ders Atama",
            f"{teacher.name} öğretmeni aşağıdaki sınıflara {lesson.name} dersini atamak istediğinizden emin misiniz?\n\nSınıflar:\n{class_list_text}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            # Save the assignments to the database
            success_count = 0
            error_count = 0

            # For lesson assignment, we'll use default values for schedule entry fields
            # since this is not a full schedule but just a lesson assignment
            default_classroom_id = 1  # Default classroom ID
            default_day = 0  # Monday
            default_time_slot = 0  # First time slot

            print(f"📝 Creating lesson assignments for {len(selected_classes)} classes...")

            for class_id, class_name in selected_classes:
                # Add schedule entry to database
                entry_id = db_manager.add_schedule_entry(
                    class_id,
                    teacher_id,
                    lesson_id,
                    default_classroom_id,
                    default_day,
                    default_time_slot,
                )

                if entry_id:
                    print(
                        f"  ✓ Assigned {lesson.name} to Class {class_id} with Teacher {teacher_id}"
                    )
                else:
                    print(f"  ❌ Failed to assign {lesson.name} to Class {class_id}")

                if entry_id:
                    success_count += 1
                else:
                    error_count += 1

            # Show result message
            if error_count == 0:
                QMessageBox.information(
                    self,
                    "Başarılı",
                    f"✅ {teacher.name} öğretmeni {success_count} sınıfa {lesson.name} dersi başarıyla atandı.\n\n"
                    f"📋 Artık 'Ders Programı' menüsünden program oluşturabilirsiniz.",
                )
            else:
                QMessageBox.warning(
                    self,
                    "Kısmen Başarılı",
                    f"⚠️ {teacher.name} öğretmeni {success_count} sınıfa {lesson.name} dersi atandı.\n"
                    f"❌ {error_count} sınıf için atama yapılamadı.",
                )

            # Refresh the data to update the assigned lesson counts
            self.load_data()

            # Clear selections for next assignment
            self.clear_selections()

    def delete_all_assignments(self):
        """Delete all lesson assignments after confirmation"""
        # Show confirmation dialog
        reply = QMessageBox.question(
            self,
            "Tüm Atamaları Sil",
            "Tüm ders atamalarını silmek istediğinizden emin misiniz? Bu işlem geri alınamaz.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            # Delete all schedule entries
            if db_manager.delete_all_schedule_entries():
                QMessageBox.information(self, "Başarılı", "Tüm ders atamaları başarıyla silindi.")
                # Refresh the data to update the assigned lesson counts
                self.load_data()
            else:
                QMessageBox.critical(self, "Hata", "Ders atamaları silinirken bir hata oluştu.")
