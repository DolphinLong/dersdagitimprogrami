"""
Class list dialog for the Class Scheduling Program
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
from ui.dialogs.class_dialog import ClassDialog
from utils.helpers import create_styled_message_box
from utils.notifications import get_notification_manager


class ClassListDialog(QDialog):
    """Dialog for listing and managing classes"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sınıf Listesi")
        self.setFixedSize(800, 600)
        self.notification_manager = get_notification_manager()
        self.setup_ui()
        self.apply_styles()
        self.load_classes()

    def setup_ui(self):
        """Set up the user interface with modern design"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title with modern styling
        title_label = QLabel("Sınıf Listesi")
        title_label.setAlignment(Qt.AlignCenter)  # type: ignore
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)

        # Get current school type and display it
        school_type = db_manager.get_school_type()
        if school_type:
            school_type_label = QLabel(f"Okul Türü: {school_type}")
            school_type_label.setAlignment(Qt.AlignCenter)  # type: ignore
            school_type_label.setStyleSheet(
                "font-size: 14px; color: #3498db; font-weight: bold; margin: 5px;"
            )
            layout.addWidget(school_type_label)

        # Buttons layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.add_button = QPushButton("➕ Yeni Sınıf Ekle")
        self.add_button.setObjectName("addButton")
        self.add_button.clicked.connect(self.add_class)

        self.edit_button = QPushButton("✏️ Düzenle")
        self.edit_button.setObjectName("editButton")
        self.edit_button.clicked.connect(self.edit_class)
        self.edit_button.setEnabled(False)

        self.delete_button = QPushButton("🗑️ Sil")
        self.delete_button.setObjectName("deleteButton")
        self.delete_button.clicked.connect(self.delete_class)
        self.delete_button.setEnabled(False)

        self.refresh_button = QPushButton("🔄 Yenile")
        self.refresh_button.setObjectName("refreshButton")
        self.refresh_button.clicked.connect(self.load_classes)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.refresh_button)
        layout.addLayout(button_layout)

        # Classes table
        self.classes_table = QTableWidget()
        self.classes_table.setColumnCount(3)
        self.classes_table.setHorizontalHeaderLabels(["Sınıf ID", "Sınıf Adı", "Seviye"])
        self.classes_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.classes_table.setSelectionMode(QTableWidget.SingleSelection)
        self.classes_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.classes_table.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.classes_table)

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
        header = self.classes_table.horizontalHeader()
        if header:
            header.setStretchLastSection(True)
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        v_header = self.classes_table.verticalHeader()
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

    def load_classes(self):
        """Load classes from database into table"""
        classes = db_manager.get_all_classes()

        self.classes_table.setRowCount(len(classes))
        for row, class_obj in enumerate(classes):
            self.classes_table.setItem(row, 0, QTableWidgetItem(str(class_obj.class_id)))
            self.classes_table.setItem(row, 1, QTableWidgetItem(class_obj.name))
            self.classes_table.setItem(row, 2, QTableWidgetItem(str(class_obj.grade)))

        # Resize columns to fit content
        self.classes_table.resizeColumnsToContents()

    def on_selection_changed(self):
        """Handle table selection change"""
        selection_model = self.classes_table.selectionModel()
        if selection_model:
            selected_rows = selection_model.selectedRows()
            has_selection = len(selected_rows) > 0
            self.edit_button.setEnabled(has_selection)
            self.delete_button.setEnabled(has_selection)
        else:
            self.edit_button.setEnabled(False)
            self.delete_button.setEnabled(False)

    def add_class(self):
        """Add a new class"""
        dialog = ClassDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_classes()
            self.notification_manager.show_message("Başarılı", "Yeni sınıf eklendi")

    def edit_class(self):
        """Edit selected class"""
        selection_model = self.classes_table.selectionModel()
        if not selection_model:
            return

        selected_rows = selection_model.selectedRows()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        # Check if the item exists before accessing it
        item = self.classes_table.item(row, 0)
        if not item:
            return

        class_id = int(item.text())
        class_obj = db_manager.get_class_by_id(class_id)

        if class_obj:
            dialog = ClassDialog(self, class_obj)
            if dialog.exec_() == QDialog.Accepted:
                self.load_classes()
                self.notification_manager.show_message("Başarılı", "Sınıf bilgileri güncellendi")

    def delete_class(self):
        """Delete selected class"""
        selection_model = self.classes_table.selectionModel()
        if not selection_model:
            return

        selected_rows = selection_model.selectedRows()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        # Check if the items exist before accessing them
        id_item = self.classes_table.item(row, 0)
        name_item = self.classes_table.item(row, 1)

        if not id_item or not name_item:
            return

        class_id = int(id_item.text())
        class_name = name_item.text()

        # Confirm deletion
        msg = create_styled_message_box(
            self,
            "Sınıf Sil",
            f"'{class_name}' sınıfını silmek istediğinizden emin misiniz?",
            QMessageBox.Warning,
        )
        msg.setInformativeText("Bu işlem geri alınamaz.")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)

        if msg.exec_() == QMessageBox.Yes:
            try:
                success = db_manager.delete_class(class_id)
                if success:
                    self.load_classes()
                    self.notification_manager.show_message("Başarılı", "Sınıf silindi")
                else:
                    msg = create_styled_message_box(
                        self, "Hata", "Sınıf silinirken bir hata oluştu.", QMessageBox.Critical
                    )
                    msg.exec_()
            except Exception as e:
                msg = create_styled_message_box(
                    self,
                    "Hata",
                    f"Sınıf silinirken bir hata oluştu: {str(e)}",
                    QMessageBox.Critical,
                )
                msg.exec_()
