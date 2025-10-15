"""
Reports dialog for the Class Scheduling Program - Redesigned for a professional look and feel.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from database import db_manager
from reports.generator import ReportGenerator
from utils.helpers import create_styled_message_box


class ReportsDialog(QDialog):
    """Dialog for generating and exporting reports with a professional table view."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.report_generator = ReportGenerator(db_manager)
        self.setWindowTitle("Raporlar")
        self.setMinimumSize(1000, 700)
        self.setup_ui()
        self.apply_styles()
        self.populate_data()

    def setup_ui(self):
        """Set up the user interface with a two-panel design."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Left Panel (Controls) ---
        left_panel = QFrame()
        left_panel.setObjectName("leftPanel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(15)

        title_label = QLabel("📊 Rapor Merkezi")
        title_label.setObjectName("titleLabel")
        left_layout.addWidget(title_label)

        # Report Type
        type_label = QLabel("Rapor Türü")
        type_label.setObjectName("fieldLabel")
        self.report_type_combo = QComboBox()
        self.report_type_combo.setObjectName("reportTypeCombo")
        self.report_type_combo.addItems(
            ["Sınıf Programı", "Öğretmen Programı", "Derslik Kullanımı"]
        )
        self.report_type_combo.currentIndexChanged.connect(self.on_report_type_changed)
        left_layout.addWidget(type_label)
        left_layout.addWidget(self.report_type_combo)

        # Entity Selection
        self.entity_widget = QWidget()
        entity_layout = QVBoxLayout(self.entity_widget)
        entity_layout.setContentsMargins(0, 0, 0, 0)
        self.entity_label = QLabel("Sınıf")
        self.entity_label.setObjectName("fieldLabel")
        self.entity_combo = QComboBox()
        self.entity_combo.setObjectName("entityCombo")
        entity_layout.addWidget(self.entity_label)
        entity_layout.addWidget(self.entity_combo)
        left_layout.addWidget(self.entity_widget)

        left_layout.addStretch(1)

        # Generate Button
        self.generate_button = QPushButton("Rapor Oluştur")
        self.generate_button.setObjectName("generateButton")
        self.generate_button.clicked.connect(self.generate_report)
        left_layout.addWidget(self.generate_button)

        # --- Right Panel (Display) ---
        right_panel = QFrame()
        right_panel.setObjectName("rightPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(15)

        # Report Table
        self.report_table = QTableWidget()
        self.report_table.setObjectName("reportTable")
        right_layout.addWidget(self.report_table)

        # Export Buttons
        export_layout = QHBoxLayout()
        export_layout.addStretch()
        self.pdf_button = QPushButton("📄 PDF Olarak Aktar")
        self.pdf_button.setObjectName("exportButton")
        self.pdf_button.clicked.connect(self.export_to_pdf)
        self.excel_button = QPushButton("📋 Excel Olarak Aktar")
        self.excel_button.setObjectName("exportButton")
        self.excel_button.clicked.connect(self.export_to_excel)
        export_layout.addWidget(self.pdf_button)
        export_layout.addWidget(self.excel_button)
        right_layout.addLayout(export_layout)

        main_layout.addWidget(left_panel, 2)
        main_layout.addWidget(right_panel, 5)

        self.on_report_type_changed(0)

    def apply_styles(self):
        """Apply a professional and surprising stylesheet."""
        self.setStyleSheet(
            """
            QDialog {
                background-color: #f8f9fa;
            }
            #leftPanel {
                background-color: #2c3e50;
                color: white;
            }
            #rightPanel {
                background-color: #f8f9fa;
            }
            #titleLabel {
                font-size: 24px;
                font-weight: bold;
                color: #ffffff;
                padding-bottom: 10px;
                border-bottom: 1px solid #34495e;
            }
            #fieldLabel {
                font-weight: bold;
                color: #ecf0f1;
                font-size: 14px;
                margin-top: 10px;
            }
            QComboBox {
                padding: 10px;
                border: 2px solid #dcdde1;
                border-radius: 5px;
                background-color: white;
                color: #2c3e50;
                font-size: 14px;
                min-height: 30px;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
            }
            QComboBox::drop-down {
                border: none;
                border-radius: 5px;
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
            #generateButton {
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                color: white;
                background-color: #27ae60;
                border: none;
                border-radius: 5px;
            }
            #generateButton:hover {
                background-color: #2ecc71;
            }
            #reportTable {
                gridline-color: #dcdcdc;
                background-color: #ffffff;
                border: 1px solid #dcdcdc;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QTableWidget::item:alternate {
                background-color: #f2f2f2;
            }
            #exportButton {
                padding: 10px 15px;
                font-size: 12px;
                font-weight: bold;
                color: white;
                border: none;
                border-radius: 5px;
                background-color: #3498db;
            }
            #exportButton:hover {
                background-color: #5dade2;
            }
        """
        )

    def _populate_table(self, headers, data):
        """Populate the QTableWidget with structured data."""
        self.report_table.clear()
        self.report_table.setRowCount(len(data))
        self.report_table.setColumnCount(len(headers))
        self.report_table.setHorizontalHeaderLabels(headers)

        for row_idx, row_data in enumerate(data):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(str(cell_data))
                item.setTextAlignment(Qt.AlignCenter)
                self.report_table.setItem(row_idx, col_idx, item)

        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.report_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.report_table.setAlternatingRowColors(True)

    def _get_data_from_table(self):
        """Extracts headers and data from the report table."""
        headers = [
            self.report_table.horizontalHeaderItem(i).text()
            for i in range(self.report_table.columnCount())
        ]
        data = []
        for row in range(self.report_table.rowCount()):
            row_data = []
            for col in range(self.report_table.columnCount()):
                item = self.report_table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        return headers, data

    def populate_data(self):
        self.populate_classes()

    def populate_classes(self):
        self.entity_combo.clear()
        classes = db_manager.get_all_classes()
        for class_obj in classes:
            self.entity_combo.addItem(class_obj.name, class_obj.class_id)

    def populate_teachers(self):
        self.entity_combo.clear()
        teachers = db_manager.get_all_teachers()
        for teacher in teachers:
            self.entity_combo.addItem(teacher.name, teacher.teacher_id)

    def on_report_type_changed(self, index):
        if index == 0:
            self.entity_label.setText("Sınıf:")
            self.populate_classes()
            self.entity_widget.setVisible(True)
        elif index == 1:
            self.entity_label.setText("Öğretmen:")
            self.populate_teachers()
            self.entity_widget.setVisible(True)
        else:
            self.entity_widget.setVisible(False)

    def generate_report(self):
        """Generate the selected report and display it in the table."""
        report_type_index = self.report_type_combo.currentIndex()

        try:
            headers, data = [], []
            if report_type_index == 0:
                class_id = self.entity_combo.currentData()
                if not class_id:
                    create_styled_message_box(
                        self, "Hata", "Lütfen bir sınıf seçin.", QMessageBox.Warning
                    ).exec_()
                    return
                headers, data = self.report_generator.generate_class_schedule_report(class_id)
            elif report_type_index == 1:
                teacher_id = self.entity_combo.currentData()
                if not teacher_id:
                    create_styled_message_box(
                        self, "Hata", "Lütfen bir öğretmen seçin.", QMessageBox.Warning
                    ).exec_()
                    return
                headers, data = self.report_generator.generate_teacher_schedule_report(teacher_id)
            else:
                headers, data = self.report_generator.generate_classroom_usage_report()

            self._populate_table(headers, data)

        except Exception as e:
            create_styled_message_box(
                self,
                "Hata",
                f"Rapor oluşturulurken bir hata oluştu: {str(e)}",
                QMessageBox.Critical,
            ).exec_()

    def export_to_pdf(self):
        """Export the current table view to a PDF file."""
        if self.report_table.rowCount() == 0:
            create_styled_message_box(
                self,
                "Hata",
                "Dışa aktarılacak bir rapor yok. Lütfen önce bir rapor oluşturun.",
                QMessageBox.Warning,
            ).exec_()
            return

        report_title = self.report_type_combo.currentText()

        filename, _ = QFileDialog.getSaveFileName(
            self, "PDF Olarak Kaydet", f"{report_title}.pdf", "PDF Files (*.pdf)"
        )

        if not filename:
            return

        try:
            headers, data = self._get_data_from_table()
            # The new PDF generator is in the pdf_generator attribute of the report_generator
            result = self.report_generator.pdf_generator.generate_pdf(
                report_title, headers, data, filename
            )
            create_styled_message_box(self, "Başarılı", result).exec_()
        except Exception as e:
            create_styled_message_box(
                self, "Hata", f"PDF oluşturulurken bir hata oluştu: {str(e)}", QMessageBox.Critical
            ).exec_()

    def export_to_excel(self):
        """Export the current table view to an Excel file."""
        if self.report_table.rowCount() == 0:
            create_styled_message_box(
                self,
                "Hata",
                "Dışa aktarılacak bir rapor yok. Lütfen önce bir rapor oluşturun.",
                QMessageBox.Warning,
            ).exec_()
            return

        report_title = self.report_type_combo.currentText()

        filename, _ = QFileDialog.getSaveFileName(
            self, "Excel Olarak Kaydet", f"{report_title}.xlsx", "Excel Files (*.xlsx)"
        )

        if not filename:
            return

        try:
            headers, data = self._get_data_from_table()
            result = self.report_generator.excel_generator.generate_excel(
                report_title, headers, data, filename
            )
            create_styled_message_box(self, "Başarılı", result).exec_()
        except Exception as e:
            create_styled_message_box(
                self,
                "Hata",
                f"Excel oluşturulurken bir hata oluştu: {str(e)}",
                QMessageBox.Critical,
            ).exec_()
