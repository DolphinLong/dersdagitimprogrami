"""
Lesson list dialog for the Class Scheduling Program
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
from ui.dialogs.new_lesson_dialog import NewLessonDialog
from utils.helpers import create_styled_message_box


class LessonListDialog(QDialog):
    """Dialog for listing and managing lessons"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ders Listesi")
        self.setFixedSize(800, 600)
        self.setup_ui()
        self.apply_styles()
        self.load_lessons()

    def setup_ui(self):
        """Set up the user interface with modern design"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title with modern styling
        title_label = QLabel("Ders Listesi")
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

        self.add_button = QPushButton("➕ Yeni Ders Ekle")
        self.add_button.setObjectName("addButton")
        self.add_button.clicked.connect(self.add_lesson)

        self.edit_button = QPushButton("✏️ Düzenle")
        self.edit_button.setObjectName("editButton")
        self.edit_button.clicked.connect(self.edit_lesson)
        self.edit_button.setEnabled(False)

        self.delete_button = QPushButton("🗑️ Sil")
        self.delete_button.setObjectName("deleteButton")
        self.delete_button.clicked.connect(self.delete_lesson)
        self.delete_button.setEnabled(False)

        self.refresh_button = QPushButton("🔄 Yenile")
        self.refresh_button.setObjectName("refreshButton")
        self.refresh_button.clicked.connect(self.load_lessons)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.refresh_button)
        layout.addLayout(button_layout)

        # Lessons table
        self.lessons_table = QTableWidget()
        self.lessons_table.setColumnCount(3)
        self.lessons_table.setHorizontalHeaderLabels(["Ders ID", "Ders Adı", "Haftalık Saat"])
        self.lessons_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.lessons_table.setSelectionMode(QTableWidget.SingleSelection)
        self.lessons_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.lessons_table.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.lessons_table)

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
        header = self.lessons_table.horizontalHeader()
        if header:
            header.setStretchLastSection(True)
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        v_header = self.lessons_table.verticalHeader()
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

    def load_lessons(self):
        """Load lessons from database into table"""
        all_lessons = db_manager.get_all_lessons()

        self.lessons_table.setRowCount(len(all_lessons))
        for row, lesson in enumerate(all_lessons):
            self.lessons_table.setItem(row, 0, QTableWidgetItem(str(lesson.lesson_id)))
            self.lessons_table.setItem(row, 1, QTableWidgetItem(lesson.name))
            # Add weekly hours if available
            weekly_hours = getattr(lesson, "weekly_hours", 0)
            self.lessons_table.setItem(
                row, 2, QTableWidgetItem(str(weekly_hours) if weekly_hours else "0")
            )

        # Resize columns to fit content
        self.lessons_table.resizeColumnsToContents()

    def get_predefined_subjects_for_school_type(self, school_type):
        """Get predefined subjects for a school type"""
        from utils.schedule_requirements import ScheduleRequirements

        subjects = set()

        if school_type == "İlkokul":
            # İlkokul dersleri (1-4. sınıflar)
            for grade in range(1, 5):
                mandatory_subjects = ScheduleRequirements.get_mandatory_subjects_for_grade(grade)
                subjects.update(mandatory_subjects.keys())

            # İlkokul seçmeli dersleri
            optional_subjects = [
                "Oyun ve Fiziki Etkinlikler",
                "Değerler Eğitimi",
                "Yaşam Becerileri",
                "Çevre Eğitimi",
                "Okuma Yazma Hazırlığı",
                "Temel Matematik Becerileri",
            ]
            subjects.update(optional_subjects)

        elif school_type == "Ortaokul":
            # Ortaokul dersleri (5-8. sınıflar)
            for grade in range(5, 9):
                mandatory_subjects = ScheduleRequirements.get_mandatory_subjects_for_grade(grade)
                subjects.update(mandatory_subjects.keys())

            # Ortaokul seçmeli dersleri
            optional_subjects = [
                "Matematik Uygulamaları",
                "Fen Uygulamaları",
                "Robotik ve Kodlama",
                "3D Tasarım ve Modelleme",
                "Bilim Uygulamaları",
                "Proje Tasarımı ve Üretimi",
                "Zeka Oyunları",
                "Satranç",
                "Okuma Becerileri",
                "Yazarlık ve Yazma Becerileri",
                "Medya Okuryazarlığı",
                "Dijital Vatandaşlık",
                "Girişimcilik",
                "Finansal Okuryazarlık",
                "Hukuk ve Adalet",
                "Demokrasi ve İnsan Hakları",
                "Kültürümüzden Esintiler",
                "Peygamberimizin Hayatı",
                "Temel Dini Bilgiler",
                "Kur'an-ı Kerim",
                "Hz. Muhammed'in Hayatı",
                "Spor ve Fiziksel Etkinlikler",
                "Atletizm",
                "Futbol",
                "Basketbol",
                "Voleybol",
                "Halk Oyunları",
                "Modern Dans",
                "Drama",
                "Tiyatro",
                "Müze Eğitimi",
                "Görsel Sanatlar Uygulamaları",
                "Müzik Uygulamaları",
                "Çalgı Eğitimi",
                "Koro",
                "İkinci Yabancı Dil",
                "Almanca",
                "Fransızca",
                "Rusça",
                "Arapça",
                "Çince",
                "İspanyolca",
                "İtalyanca",
                "Japonca",
            ]
            subjects.update(optional_subjects)

        elif school_type in ["Lise", "Anadolu Lisesi"]:
            # Lise dersleri (9-12. sınıflar)
            for grade in range(9, 13):
                mandatory_subjects = ScheduleRequirements.get_mandatory_subjects_for_grade(grade)
                subjects.update(mandatory_subjects.keys())

            # Lise seçmeli dersleri
            optional_subjects = [
                "İleri Matematik",
                "Matematik Uygulamaları",
                "İleri Fizik",
                "Fizik Uygulamaları",
                "İleri Kimya",
                "Kimya Uygulamaları",
                "İleri Biyoloji",
                "Biyoloji Uygulamaları",
                "Astronomi ve Uzay Bilimleri",
                "Çevre Bilimi",
                "Genetik ve Biyoteknoloji",
                "Sağlık Bilgisi ve İlk Yardım",
                "Spor Bilimleri",
                "Beslenme ve Diyetetik",
                "Psikoloji",
                "Sosyoloji",
                "Mantık",
                "Felsefe Tarihi",
                "Karşılaştırmalı Edebiyat",
                "Dil ve Anlatım Uygulamaları",
                "Türk Dili",
                "Türk Edebiyatı",
                "Dünya Edebiyatından Seçmeler",
                "Coğrafya Uygulamaları",
                "Tarih Uygulamaları",
                "Sanat Tarihi",
                "Müze Bilimi",
                "Arkeoloji",
                "Antropoloji",
                "Ekonomi",
                "İşletme",
                "Muhasebe",
                "Hukuk",
                "Uluslararası İlişkiler",
                "Siyaset Bilimi",
                "İstatistik",
                "Bilgisayar Bilimleri",
                "Programlama",
                "Web Tasarımı",
                "Grafik Tasarım",
                "Endüstriyel Tasarım",
                "Mimarlık",
                "Mühendislik Uygulamaları",
                "Yapay Zeka ve Makine Öğrenmesi",
                "Veri Bilimi",
                "Siber Güvenlik",
                "Oyun Geliştirme",
                "Mobil Uygulama Geliştirme",
            ]
            subjects.update(optional_subjects)

        elif school_type == "Fen Lisesi":
            # Fen Lisesi dersleri (9-12. sınıflar)
            for grade in range(9, 13):
                mandatory_subjects = ScheduleRequirements.FEN_LISESI_SUBJECTS.get(grade, {})
                subjects.update(mandatory_subjects.keys())

            # Fen Lisesi özel seçmeli dersleri
            optional_subjects = [
                "İleri Matematik",
                "Matematik Uygulamaları",
                "İleri Fizik",
                "Fizik Uygulamaları",
                "İleri Kimya",
                "Kimya Uygulamaları",
                "İleri Biyoloji",
                "Biyoloji Uygulamaları",
                "Astronomi ve Uzay Bilimleri",
                "Çevre Bilimi",
                "Genetik ve Biyoteknoloji",
                "Bilgisayar Bilimleri",
                "Programlama",
                "Yapay Zeka ve Makine Öğrenmesi",
                "Veri Bilimi",
                "Mühendislik Uygulamaları",
                "İstatistik",
            ]
            subjects.update(optional_subjects)

        elif school_type == "Sosyal Bilimler Lisesi":
            # Sosyal Bilimler Lisesi dersleri (9-12. sınıflar)
            for grade in range(9, 13):
                mandatory_subjects = ScheduleRequirements.SOSYAL_BILIMLER_LISESI_SUBJECTS.get(
                    grade, {}
                )
                subjects.update(mandatory_subjects.keys())

            # Sosyal Bilimler Lisesi özel seçmeli dersleri
            optional_subjects = [
                "Psikoloji",
                "Sosyoloji",
                "Mantık",
                "Felsefe Tarihi",
                "Karşılaştırmalı Edebiyat",
                "Dil ve Anlatım Uygulamaları",
                "Türk Dili",
                "Türk Edebiyatı",
                "Dünya Edebiyatından Seçmeler",
                "Coğrafya Uygulamaları",
                "Tarih Uygulamaları",
                "Sanat Tarihi",
                "Müze Bilimi",
                "Arkeoloji",
                "Antropoloji",
                "Ekonomi",
                "İşletme",
                "Muhasebe",
                "Hukuk",
                "Uluslararası İlişkiler",
                "Siyaset Bilimi",
            ]
            subjects.update(optional_subjects)

        # Ortak dersler (tüm okul türleri için)
        common_subjects = ["Rehberlik", "Seçmeli Ders", "Seçmeli 1", "Seçmeli 2", "Seçmeli 3"]
        subjects.update(common_subjects)

        return subjects

    def is_lesson_in_any_predefined_list(self, lesson_name):
        """Check if a lesson is in any predefined list for any school type"""
        school_types = [
            "İlkokul",
            "Ortaokul",
            "Lise",
            "Anadolu Lisesi",
            "Fen Lisesi",
            "Sosyal Bilimler Lisesi",
        ]

        for school_type in school_types:
            predefined_subjects = self.get_predefined_subjects_for_school_type(school_type)
            if lesson_name in predefined_subjects:
                return True

        return False

    def on_selection_changed(self):
        """Handle table selection change"""
        selection_model = self.lessons_table.selectionModel()
        if selection_model:
            selected_rows = selection_model.selectedRows()
            has_selection = len(selected_rows) > 0
            self.edit_button.setEnabled(has_selection)
            self.delete_button.setEnabled(has_selection)
        else:
            self.edit_button.setEnabled(False)
            self.delete_button.setEnabled(False)

    def add_lesson(self):
        """Add a new lesson"""
        dialog = NewLessonDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_lessons()

    def edit_lesson(self):
        """Edit selected lesson"""
        selection_model = self.lessons_table.selectionModel()
        if not selection_model:
            return

        selected_rows = selection_model.selectedRows()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        # Check if the item exists before accessing it
        item = self.lessons_table.item(row, 0)
        if not item:
            return

        lesson_id = int(item.text())
        lesson = db_manager.get_lesson_by_id(lesson_id)

        if lesson:
            dialog = NewLessonDialog(self, lesson)
            if dialog.exec_() == QDialog.Accepted:
                self.load_lessons()

    def delete_lesson(self):
        """Delete selected lesson"""
        selection_model = self.lessons_table.selectionModel()
        if not selection_model:
            return

        selected_rows = selection_model.selectedRows()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        # Check if the items exist before accessing them
        id_item = self.lessons_table.item(row, 0)
        name_item = self.lessons_table.item(row, 1)

        if not id_item or not name_item:
            return

        lesson_id = int(id_item.text())
        lesson_name = name_item.text()

        # Confirm deletion
        msg = create_styled_message_box(
            self,
            "Ders Sil",
            f"'{lesson_name}' dersini silmek istediğinizden emin misiniz?",
            QMessageBox.Warning,
        )
        msg.setInformativeText("Bu işlem geri alınamaz.")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)

        if msg.exec_() == QMessageBox.Yes:
            try:
                success = db_manager.delete_lesson(lesson_id)
                if success:
                    self.load_lessons()
                    # Show message in a dialog since we don't have access to main window status bar
                    info_msg = create_styled_message_box(
                        self, "Başarılı", "Ders silindi", QMessageBox.Information
                    )
                    info_msg.exec_()
                else:
                    msg = create_styled_message_box(
                        self, "Hata", "Ders silinirken bir hata oluştu.", QMessageBox.Critical
                    )
                    msg.exec_()
            except Exception as e:
                msg = create_styled_message_box(
                    self, "Hata", f"Ders silinirken bir hata oluştu: {str(e)}", QMessageBox.Critical
                )
                msg.exec_()
