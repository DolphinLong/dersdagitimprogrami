"""
New Lesson Management Dialog with Internet Integration
This dialog allows users to fetch current lessons from the internet and manage weekly hours.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import json
import logging

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
)

from database import db_manager
from utils.helpers import create_styled_message_box


class LessonFetcher(QThread):
    """Thread to fetch lessons from the internet"""

    lessons_fetched = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, school_type):
        super().__init__()
        self.school_type = school_type

    def run(self):
        """Fetch lessons from a mock API (in a real implementation, this would connect to an actual service)"""
        try:
            # In a real implementation, this would connect to an actual API
            # For now, we'll use mock data based on the school type
            lessons_data = self.get_mock_lessons_data()
            self.lessons_fetched.emit(lessons_data)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def get_mock_lessons_data(self):
        """Get mock lessons data based on school type"""
        # This is mock data - in a real implementation, this would come from an API
        mock_data = {
            "İlkokul": [
                {"name": "Türkçe", "grades": [1, 2, 3, 4]},
                {"name": "Matematik", "grades": [1, 2, 3, 4]},
                {"name": "Hayat Bilgisi", "grades": [1, 2, 3]},
                {"name": "Fen Bilimleri", "grades": [4]},
                {"name": "Sosyal Bilgiler", "grades": [4]},
                {"name": "Görsel Sanatlar", "grades": [1, 2, 3, 4]},
                {"name": "Müzik", "grades": [1, 2, 3, 4]},
                {"name": "Beden Eğitimi", "grades": [1, 2, 3, 4]},
                {"name": "Din Kültürü ve Ahlak Bilgisi", "grades": [4]},
                {"name": "Yabancı Dil", "grades": [2, 3, 4]},
                {"name": "Bilişim Teknolojileri", "grades": [4]},
                {"name": "Rehberlik", "grades": [1, 2, 3, 4]},
                {"name": "Oyun ve Fiziki Etkinlikler", "grades": [1, 2, 3, 4]},
                {"name": "Değerler Eğitimi", "grades": [1, 2, 3, 4]},
                {"name": "Yaşam Becerileri", "grades": [1, 2, 3, 4]},
            ],
            "Ortaokul": [
                {"name": "Türkçe", "grades": [5, 6, 7, 8]},
                {"name": "Matematik", "grades": [5, 6, 7, 8]},
                {"name": "Fen Bilimleri", "grades": [5, 6, 7, 8]},
                {"name": "Sosyal Bilgiler", "grades": [5, 6, 7, 8]},
                {"name": "Yabancı Dil", "grades": [5, 6, 7, 8]},
                {"name": "Din Kültürü ve Ahlak Bilgisi", "grades": [5, 6, 7, 8]},
                {"name": "Görsel Sanatlar", "grades": [5, 6, 7, 8]},
                {"name": "Müzik", "grades": [5, 6, 7, 8]},
                {"name": "Beden Eğitimi", "grades": [5, 6, 7, 8]},
                {"name": "Bilişim Teknolojileri", "grades": [5, 6, 7, 8]},
                {"name": "Rehberlik", "grades": [5, 6, 7, 8]},
                {"name": "Teknoloji ve Tasarım", "grades": [7, 8]},
                {"name": "Matematik Uygulamaları", "grades": [5, 6, 7, 8]},
                {"name": "Fen Uygulamaları", "grades": [5, 6, 7, 8]},
                {"name": "Robotik ve Kodlama", "grades": [5, 6, 7, 8]},
                {"name": "Dijital Vatandaşlık", "grades": [5, 6, 7, 8]},
                {"name": "Finansal Okuryazarlık", "grades": [5, 6, 7, 8]},
            ],
            "Lise": [
                {"name": "Türk Dili ve Edebiyatı", "grades": [9, 10, 11, 12]},
                {"name": "Matematik", "grades": [9, 10, 11, 12]},
                {"name": "Fizik", "grades": [9, 10, 11, 12]},
                {"name": "Kimya", "grades": [9, 10, 11, 12]},
                {"name": "Biyoloji", "grades": [9, 10, 11, 12]},
                {"name": "Tarih", "grades": [9, 10, 11, 12]},
                {"name": "Coğrafya", "grades": [9, 10, 11, 12]},
                {"name": "Felsefe", "grades": [9, 10, 11, 12]},
                {"name": "Yabancı Dil", "grades": [9, 10, 11, 12]},
                {"name": "Din Kültürü ve Ahlak Bilgisi", "grades": [9, 10, 11, 12]},
                {"name": "Görsel Sanatlar", "grades": [9, 10, 11, 12]},
                {"name": "Müzik", "grades": [9, 10, 11, 12]},
                {"name": "Beden Eğitimi", "grades": [9, 10, 11, 12]},
                {"name": "Bilişim", "grades": [9, 10, 11, 12]},
                {"name": "Rehberlik", "grades": [9, 10, 11, 12]},
                {"name": "Psikoloji", "grades": [9, 10, 11, 12]},
                {"name": "Sosyoloji", "grades": [9, 10, 11, 12]},
                {"name": "İktisat", "grades": [9, 10, 11, 12]},
                {"name": "Hukuk", "grades": [9, 10, 11, 12]},
                {"name": "İleri Matematik", "grades": [9, 10, 11, 12]},
                {"name": "İleri Fizik", "grades": [9, 10, 11, 12]},
            ],
            "Anadolu Lisesi": [
                {"name": "Türk Dili ve Edebiyatı", "grades": [9, 10, 11, 12]},
                {"name": "Matematik", "grades": [9, 10, 11, 12]},
                {"name": "Fizik", "grades": [9, 10, 11, 12]},
                {"name": "Kimya", "grades": [9, 10, 11, 12]},
                {"name": "Biyoloji", "grades": [9, 10, 11, 12]},
                {"name": "Tarih", "grades": [9, 10, 11, 12]},
                {"name": "Coğrafya", "grades": [9, 10, 11, 12]},
                {"name": "Felsefe", "grades": [9, 10, 11, 12]},
                {"name": "Yabancı Dil", "grades": [9, 10, 11, 12]},
                {"name": "Din Kültürü ve Ahlak Bilgisi", "grades": [9, 10, 11, 12]},
                {"name": "Görsel Sanatlar", "grades": [9, 10, 11, 12]},
                {"name": "Müzik", "grades": [9, 10, 11, 12]},
                {"name": "Beden Eğitimi", "grades": [9, 10, 11, 12]},
                {"name": "Bilişim", "grades": [9, 10, 11, 12]},
                {"name": "Rehberlik", "grades": [9, 10, 11, 12]},
                {"name": "Seçmeli Matematik", "grades": [9, 10, 11, 12]},
                {"name": "Seçmeli Fizik", "grades": [9, 10, 11, 12]},
                {"name": "Seçmeli Kimya", "grades": [9, 10, 11, 12]},
                {"name": "Seçmeli Biyoloji", "grades": [9, 10, 11, 12]},
                {"name": "Seçmeli Edebiyat", "grades": [9, 10, 11, 12]},
                {"name": "Seçmeli Tarih", "grades": [9, 10, 11, 12]},
                {"name": "Seçmeli Coğrafya", "grades": [9, 10, 11, 12]},
            ],
            "Fen Lisesi": [
                {"name": "Türk Dili ve Edebiyatı", "grades": [9, 10, 11, 12]},
                {"name": "Matematik", "grades": [9, 10, 11, 12]},
                {"name": "Fizik", "grades": [9, 10, 11, 12]},
                {"name": "Kimya", "grades": [9, 10, 11, 12]},
                {"name": "Biyoloji", "grades": [9, 10, 11, 12]},
                {"name": "Tarih", "grades": [9, 10, 11, 12]},
                {"name": "Coğrafya", "grades": [9, 10, 11, 12]},
                {"name": "Felsefe", "grades": [9, 10, 11, 12]},
                {"name": "Birinci Yabancı Dil", "grades": [9, 10, 11, 12]},
                {"name": "Din Kültürü ve Ahlak Bilgisi", "grades": [9, 10, 11, 12]},
                {"name": "Beden Eğitimi ve Spor", "grades": [9, 10, 11, 12]},
                {"name": "Görsel Sanatlar", "grades": [9, 10, 11, 12]},
                {"name": "Müzik", "grades": [9, 10, 11, 12]},
                {"name": "Bilişim Teknolojileri ve Yazılım", "grades": [9, 10, 11, 12]},
                {"name": "Rehberlik ve Yönlendirme", "grades": [9, 10, 11, 12]},
                {"name": "Seçmeli Matematik", "grades": [9, 10, 11, 12]},
                {"name": "Seçmeli Fizik", "grades": [9, 10, 11, 12]},
                {"name": "Seçmeli Kimya", "grades": [9, 10, 11, 12]},
                {"name": "Seçmeli Biyoloji", "grades": [9, 10, 11, 12]},
                {"name": "Genetik Bilimine Giriş", "grades": [11, 12]},
                {"name": "Tıp Bilimine Giriş", "grades": [11, 12]},
                {"name": "Astronomi ve Uzay Bilimleri", "grades": [11, 12]},
                {"name": "Sosyal Bilim Çalışmaları", "grades": [9, 10, 11, 12]},
                {"name": "Düşünme Eğitimi", "grades": [9, 10, 11, 12]},
                {"name": "İkinci Yabancı Dil", "grades": [9, 10, 11, 12]},
            ],
            "Sosyal Bilimler Lisesi": [
                {"name": "Türk Dili ve Edebiyatı", "grades": [9, 10, 11, 12]},
                {"name": "Matematik", "grades": [9, 10, 11, 12]},
                {"name": "Tarih", "grades": [9, 10, 11, 12]},
                {"name": "Coğrafya", "grades": [9, 10, 11, 12]},
                {"name": "Felsefe", "grades": [9, 10, 11, 12]},
                {"name": "Psikoloji", "grades": [9, 10, 11, 12]},
                {"name": "Sosyoloji", "grades": [9, 10, 11, 12]},
                {"name": "İktisat", "grades": [9, 10, 11, 12]},
                {"name": "Hukuk", "grades": [9, 10, 11, 12]},
                {"name": "Yabancı Dil", "grades": [9, 10, 11, 12]},
                {"name": "Din Kültürü ve Ahlak Bilgisi", "grades": [9, 10, 11, 12]},
                {"name": "Görsel Sanatlar", "grades": [9, 10, 11, 12]},
                {"name": "Müzik", "grades": [9, 10, 11, 12]},
                {"name": "Beden Eğitimi", "grades": [9, 10, 11, 12]},
                {"name": "Bilişim", "grades": [9, 10, 11, 12]},
                {"name": "Rehberlik", "grades": [9, 10, 11, 12]},
                {"name": "Siyaset Bilimi", "grades": [11, 12]},
                {"name": "Antropoloji", "grades": [11, 12]},
                {"name": "İletişim Bilimleri", "grades": [11, 12]},
                {"name": "Türk Dünyası Edebiyatı", "grades": [11, 12]},
                {"name": "Karşılaştırmalı Edebiyat", "grades": [11, 12]},
                {"name": "Seçmeli Matematik", "grades": [9, 10, 11, 12]},
                {"name": "Seçmeli Tarih", "grades": [9, 10, 11, 12]},
                {"name": "Seçmeli Coğrafya", "grades": [9, 10, 11, 12]},
            ],
        }

        return mock_data.get(self.school_type, [])


class NewLessonDialog(QDialog):
    """Dialog for adding or editing lessons with internet integration and weekly hours management."""

    def __init__(self, parent=None, lesson=None):
        super().__init__(parent)
        self.lesson = lesson
        self.setWindowTitle("Yeni Ders Yönetimi")
        self.resize(900, 700)
        self.setup_ui()
        self.apply_styles()
        self.populate_data()

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel("Ders Yönetimi")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)  # type: ignore
        layout.addWidget(title_label)

        # School type info
        school_type = db_manager.get_school_type()
        if school_type:
            school_info = QLabel(f"Okul Türü: {school_type}")
            school_info.setAlignment(Qt.AlignCenter)  # type: ignore
            school_info.setObjectName("schoolInfo")
            layout.addWidget(school_info)

        # Internet fetch section
        fetch_group = QGroupBox("İnternetten Ders Bilgilerini Al")
        fetch_layout = QVBoxLayout()

        fetch_button_layout = QHBoxLayout()
        self.fetch_button = QPushButton("🌍 İnternetten Dersleri Getir")
        self.fetch_button.setObjectName("fetchButton")
        self.fetch_button.clicked.connect(self.fetch_lessons_from_internet)

        self.refresh_button = QPushButton("🔄 Yenile")
        self.refresh_button.setObjectName("refreshButton")
        self.refresh_button.clicked.connect(self.refresh_lessons)

        fetch_button_layout.addWidget(self.fetch_button)
        fetch_button_layout.addWidget(self.refresh_button)
        fetch_button_layout.addStretch()

        fetch_layout.addLayout(fetch_button_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        fetch_layout.addWidget(self.progress_bar)

        # Status text
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(60)
        self.status_text.setReadOnly(True)
        self.status_text.setVisible(False)
        fetch_layout.addWidget(self.status_text)

        fetch_group.setLayout(fetch_layout)
        layout.addWidget(fetch_group)

        # Lesson name input
        name_layout = QHBoxLayout()
        name_label = QLabel("Ders Adı:")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Dersin adını girin veya listeden seçin")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # Available lessons list
        lessons_label = QLabel("Mevcut Dersler:")
        layout.addWidget(lessons_label)

        self.lessons_list = QTableWidget()
        self.lessons_list.setColumnCount(2)
        self.lessons_list.setHorizontalHeaderLabels(["Ders Adı", "Sınıf Seviyeleri"])
        self.lessons_list.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # type: ignore
        self.lessons_list.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # type: ignore
        self.lessons_list.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.lessons_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.lessons_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.lessons_list.itemSelectionChanged.connect(self.on_lesson_selected)
        layout.addWidget(self.lessons_list)

        # Weekly hours input
        hours_group = QGroupBox("Haftalık Ders Saatleri")
        hours_layout = QVBoxLayout()

        # Grade selection
        grade_layout = QHBoxLayout()
        grade_label = QLabel("Sınıf Seviyesi:")
        self.grade_combo = QComboBox()
        self.grade_combo.currentIndexChanged.connect(self.on_grade_changed)

        hours_label = QLabel("Haftalık Saat:")
        self.hours_spinbox = QSpinBox()
        self.hours_spinbox.setMinimum(0)
        self.hours_spinbox.setMaximum(50)
        self.hours_spinbox.setValue(2)

        grade_layout.addWidget(grade_label)
        grade_layout.addWidget(self.grade_combo)
        grade_layout.addSpacing(20)
        grade_layout.addWidget(hours_label)
        grade_layout.addWidget(self.hours_spinbox)
        grade_layout.addStretch()
        hours_layout.addLayout(grade_layout)

        # Curriculum Table
        curriculum_label = QLabel("Sınıf Seviyesine Göre Haftalık Ders Saatleri:")
        hours_layout.addWidget(curriculum_label)

        self.curriculum_table = QTableWidget()
        self.curriculum_table.setColumnCount(2)
        self.curriculum_table.setHorizontalHeaderLabels(["Sınıf Seviyesi", "Haftalık Saat"])
        self.curriculum_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # type: ignore
        self.curriculum_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # type: ignore
        self.curriculum_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        hours_layout.addWidget(self.curriculum_table)

        hours_group.setLayout(hours_layout)
        layout.addWidget(hours_group)

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

        # Initialize grade combo with school-specific grades
        self.initialize_grades()

    def initialize_grades(self):
        """Initialize grade combo with school-specific grades"""
        school_type = db_manager.get_school_type()
        self.grade_combo.clear()

        if school_type == "İlkokul":
            grades = list(range(1, 5))
        elif school_type == "Ortaokul":
            grades = list(range(5, 9))
        else:  # Lise and others
            grades = list(range(9, 13))

        for grade in grades:
            self.grade_combo.addItem(f"{grade}. Sınıf", grade)

    def apply_styles(self):
        """Apply modern styles."""
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
            #schoolInfo {
                font-size: 16px;
                color: #3498db;
                font-weight: bold;
                margin-bottom: 15px;
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
            QLineEdit, QComboBox, QSpinBox {
                padding: 10px;
                border: 2px solid #ced4da;
                border-radius: 6px;
                font-size: 14px;
                min-height: 20px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border: 2px solid #3498db;
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
            #fetchButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #27ae60, stop: 1 #219653);
            }
            #fetchButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #219653, stop: 1 #1e8449);
            }
            #refreshButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #9b59b6, stop: 1 #8e44ad);
            }
            #refreshButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #8e44ad, stop: 1 #7d3c98);
            }
            QTextEdit {
                border: 2px solid #ced4da;
                border-radius: 6px;
                font-size: 13px;
                padding: 8px;
            }
            QProgressBar {
                border: 2px solid #ced4da;
                border-radius: 6px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                width: 20px;
            }
        """
        )

    def fetch_lessons_from_internet(self):
        """Fetch lessons from the internet"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.status_text.setVisible(True)
        self.status_text.setText("Dersler internetten alınıyor...")
        self.fetch_button.setEnabled(False)

        # Get school type
        school_type = db_manager.get_school_type()
        if not school_type:
            school_type = "Lise"  # Default to Lise if not set

        # Start the fetch thread
        self.fetcher = LessonFetcher(school_type)
        self.fetcher.lessons_fetched.connect(self.on_lessons_fetched)
        self.fetcher.error_occurred.connect(self.on_fetch_error)
        self.fetcher.start()

    def on_lessons_fetched(self, lessons_data):
        """Handle fetched lessons data"""
        self.progress_bar.setVisible(False)
        self.fetch_button.setEnabled(True)

        if lessons_data:
            self.status_text.setText(f"{len(lessons_data)} ders başarıyla alındı.")
            self.populate_lessons_list(lessons_data)
        else:
            self.status_text.setText("İnternetten ders alınamadı.")

    def on_fetch_error(self, error_message):
        """Handle fetch error"""
        self.progress_bar.setVisible(False)
        self.fetch_button.setEnabled(True)
        self.status_text.setVisible(True)
        self.status_text.setText(f"Hata oluştu: {error_message}")
        create_styled_message_box(
            self, "Hata", f"Dersler alınırken hata oluştu: {error_message}", QMessageBox.Critical
        ).exec_()

    def populate_lessons_list(self, lessons_data):
        """Populate the lessons list table"""
        self.lessons_list.setRowCount(len(lessons_data))

        for row, lesson in enumerate(lessons_data):
            # Lesson name
            name_item = QTableWidgetItem(lesson["name"])
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)  # type: ignore
            self.lessons_list.setItem(row, 0, name_item)

            # Grades
            grades_text = ", ".join([f"{grade}. sınıf" for grade in lesson["grades"]])
            grades_item = QTableWidgetItem(grades_text)
            grades_item.setFlags(grades_item.flags() & ~Qt.ItemIsEditable)  # type: ignore
            self.lessons_list.setItem(row, 1, grades_item)

            # Store the lesson data in the first item
            name_item.setData(Qt.UserRole, lesson)  # type: ignore

    def refresh_lessons(self):
        """Refresh lessons from database"""
        self.status_text.setVisible(True)
        self.status_text.setText("Veritabanından dersler yenileniyor...")

        # Get all lessons from database
        all_lessons = db_manager.get_all_lessons()

        # Create mock data structure from database lessons
        lessons_data = []
        for lesson in all_lessons:
            # For existing lessons, we'll create a simple structure
            lessons_data.append(
                {"name": lesson.name, "grades": []}  # We don't have grade info for existing lessons
            )

        self.populate_lessons_list(lessons_data)
        self.status_text.setText(f"{len(lessons_data)} ders veritabanından yüklendi.")

    def on_lesson_selected(self):
        """Handle lesson selection from the list"""
        selected_rows = self.lessons_list.selectionModel().selectedRows()  # type: ignore
        if selected_rows:
            row = selected_rows[0].row()
            lesson_item = self.lessons_list.item(row, 0)
            lesson_data = lesson_item.data(Qt.UserRole)  # type: ignore

            # Set the lesson name in the input field
            self.name_input.setText(lesson_data["name"])

            # Clear the curriculum table
            self.curriculum_table.setRowCount(0)

            # Populate grade combo with available grades for this lesson
            self.grade_combo.clear()
            for grade in lesson_data["grades"]:
                self.grade_combo.addItem(f"{grade}. Sınıf", grade)

    def on_grade_changed(self, index):
        """Handle grade selection change"""
        if index >= 0:
            grade = self.grade_combo.currentData()
            # In a real implementation, we would look up existing hours for this grade
            # For now, we'll just reset to default
            self.hours_spinbox.setValue(2)

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

        # If editing an existing lesson
        if self.lesson:
            self.name_input.setText(self.lesson.name)
            # Get curriculum data for the lesson
            curriculum_data = db_manager.get_curriculum_for_lesson(self.lesson.lesson_id)
            curriculum_map = {item.grade: item.weekly_hours for item in curriculum_data}

            # Populate the curriculum table
            self.curriculum_table.setRowCount(len(curriculum_map))
            row = 0
            for grade, hours in curriculum_map.items():
                grade_item = QTableWidgetItem(f"{grade}. Sınıf")
                grade_item.setFlags(grade_item.flags() & ~Qt.ItemIsEditable)  # type: ignore
                self.curriculum_table.setItem(row, 0, grade_item)

                hours_item = QTableWidgetItem(str(hours))
                hours_item.setFlags(hours_item.flags() & ~Qt.ItemIsEditable)  # type: ignore
                self.curriculum_table.setItem(row, 1, hours_item)
                row += 1

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
            # For this implementation, we'll save the currently selected grade and hours
            grade = self.grade_combo.currentData()
            weekly_hours = self.hours_spinbox.value()

            if grade and weekly_hours > 0:
                db_manager.add_or_update_curriculum(lesson_id, grade, weekly_hours)

            create_styled_message_box(
                self, "Başarılı", "Ders ve müfredat bilgileri başarıyla kaydedildi."
            ).exec_()
            self.accept()

        except Exception as e:
            logging.error(f"Error saving lesson/curriculum: {e}")
            create_styled_message_box(
                self, "Hata", f"Kaydederken bir hata oluştu: {e}", QMessageBox.Critical
            ).exec_()
