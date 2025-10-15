"""
Teacher list dialog for the Class Scheduling Program
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
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
from ui.dialogs.teacher_dialog import TeacherDialog
from utils.helpers import create_styled_message_box
from utils.notifications import get_notification_manager


class TeacherListDialog(QDialog):
    """Dialog for listing and managing teachers"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Öğretmen Listesi")
        self.setFixedSize(800, 600)
        self.notification_manager = get_notification_manager()
        self.setup_ui()
        self.apply_styles()
        self.load_teachers()

    def setup_ui(self):
        """Set up the user interface with modern design"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title with modern styling
        title_label = QLabel("Öğretmen Listesi")
        title_label.setAlignment(Qt.AlignCenter)  # type: ignore
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)

        # Buttons layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.add_button = QPushButton("➕ Yeni Öğretmen Ekle")
        self.add_button.setObjectName("addButton")
        self.add_button.clicked.connect(self.add_teacher)

        self.edit_button = QPushButton("✏️ Düzenle")
        self.edit_button.setObjectName("editButton")
        self.edit_button.clicked.connect(self.edit_teacher)
        self.edit_button.setEnabled(False)

        self.delete_button = QPushButton("🗑️ Sil")
        self.delete_button.setObjectName("deleteButton")
        self.delete_button.clicked.connect(self.delete_teacher)
        self.delete_button.setEnabled(False)

        self.refresh_button = QPushButton("🔄 Yenile")
        self.refresh_button.setObjectName("refreshButton")
        self.refresh_button.clicked.connect(self.load_teachers)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.refresh_button)
        layout.addLayout(button_layout)

        # Teachers table
        self.teachers_table = QTableWidget()
        self.teachers_table.setColumnCount(3)
        self.teachers_table.setHorizontalHeaderLabels(["Öğretmen ID", "Ad Soyad", "Ders"])
        self.teachers_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.teachers_table.setSelectionMode(QTableWidget.SingleSelection)
        self.teachers_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.teachers_table.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.teachers_table)

        # Close button
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        self.close_button = QPushButton("Kapat")
        self.close_button.setObjectName("closeButton")
        self.close_button.clicked.connect(self.accept)
        close_layout.addWidget(self.close_button)
        layout.addLayout(close_layout)

        self.setLayout(layout)

        # Set up table properties after the table is added to layout
        header = self.teachers_table.horizontalHeader()
        if header:
            header.setStretchLastSection(True)
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        v_header = self.teachers_table.verticalHeader()
        if v_header:
            v_header.setVisible(False)

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
            #title {
                font-size: 20px;
                color: #2c3e50;
                margin-bottom: 10px;
                text-align: center;
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
            QPushButton:disabled {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #bdc3c7, stop: 1 #95a5a6);
            }
            #addButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #27ae60, stop: 1 #219653);
            }
            #addButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #219653, stop: 1 #1e8449);
            }
            #editButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #f39c12, stop: 1 #e67e22);
            }
            #editButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #e67e22, stop: 1 #d35400);
            }
            #deleteButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #e74c3c, stop: 1 #c0392b);
            }
            #deleteButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #c0392b, stop: 1 #a93226);
            }
            #refreshButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #9b59b6, stop: 1 #8e44ad);
            }
            #refreshButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #8e44ad, stop: 1 #7d3c98);
            }
            #closeButton {
                min-width: 100px;
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
                padding: 10px;
                border-bottom: 1px solid #e9ecef;
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
        """
        )

    def load_teachers(self):
        """Load teachers from database into table"""
        teachers = db_manager.get_all_teachers()

        self.teachers_table.setRowCount(len(teachers))
        for row, teacher in enumerate(teachers):
            self.teachers_table.setItem(row, 0, QTableWidgetItem(str(teacher.teacher_id)))
            self.teachers_table.setItem(row, 1, QTableWidgetItem(teacher.name))
            self.teachers_table.setItem(row, 2, QTableWidgetItem(teacher.subject))

        # Resize columns to fit content
        self.teachers_table.resizeColumnsToContents()

    def on_selection_changed(self):
        """Handle table selection change"""
        selection_model = self.teachers_table.selectionModel()
        if selection_model:
            selected_rows = selection_model.selectedRows()
            has_selection = len(selected_rows) > 0
            self.edit_button.setEnabled(has_selection)
            self.delete_button.setEnabled(has_selection)
        else:
            self.edit_button.setEnabled(False)
            self.delete_button.setEnabled(False)

    def add_teacher(self):
        """Add a new teacher"""
        dialog = TeacherDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_teachers()
            self.notification_manager.show_message("Başarılı", "Yeni öğretmen eklendi")

    def edit_teacher(self):
        """Edit selected teacher"""
        selection_model = self.teachers_table.selectionModel()
        if not selection_model:
            return

        selected_rows = selection_model.selectedRows()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        # Check if the item exists before accessing it
        item = self.teachers_table.item(row, 0)
        if not item:
            return

        teacher_id = int(item.text())
        teacher = db_manager.get_teacher_by_id(teacher_id)

        if teacher:
            dialog = TeacherDialog(self, teacher)
            if dialog.exec_() == QDialog.Accepted:
                self.load_teachers()
                self.notification_manager.show_message("Başarılı", "Öğretmen bilgileri güncellendi")

    def delete_teacher(self):
        """Delete selected teacher"""
        selection_model = self.teachers_table.selectionModel()
        if not selection_model:
            return

        selected_rows = selection_model.selectedRows()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        # Check if the items exist before accessing them
        id_item = self.teachers_table.item(row, 0)
        name_item = self.teachers_table.item(row, 1)

        if not id_item or not name_item:
            return

        teacher_id = int(id_item.text())
        teacher_name = name_item.text()

        # Confirm deletion
        msg = create_styled_message_box(
            self,
            "Öğretmen Sil",
            f"'{teacher_name}' öğretmenini silmek istediğinizden emin misiniz?",
            QMessageBox.Warning,
        )
        msg.setInformativeText("Bu işlem geri alınamaz.")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)

        if msg.exec_() == QMessageBox.Yes:
            try:
                success = db_manager.delete_teacher(teacher_id)
                if success:
                    self.load_teachers()
                    self.notification_manager.show_message("Başarılı", "Öğretmen silindi")
                else:
                    msg = create_styled_message_box(
                        self, "Hata", "Öğretmen silinirken bir hata oluştu.", QMessageBox.Critical
                    )
                    msg.exec_()
            except Exception as e:
                msg = create_styled_message_box(
                    self,
                    "Hata",
                    f"Öğretmen silinirken bir hata oluştu: {str(e)}",
                    QMessageBox.Critical,
                )
                msg.exec_()
