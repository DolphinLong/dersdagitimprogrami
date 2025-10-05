"""
School type selection dialog for the Class Scheduling Program
"""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class SchoolTypeDialog(QDialog):
    """Dialog for selecting school type with modern design"""
    
    # Define school types and their subjects
    SCHOOL_TYPES = {
        "İlkokul": [
            "Türkçe", "Matematik", "Hayat Bilgisi", "Görsel Sanatlar", 
            "Müzik", "Beden Eğitimi ve Oyun", "Yabancı Dil", "Din Kültürü ve Ahlak Bilgisi",
            "Rehberlik ve Yönlendirme", "Serbest Etkinlikler", "Trafik Güvenliği",
            "İnsan Hakları, Vatandaşlık ve Demokrasi", "Matematik ve Bilim Uygulamaları",
            "Robotik Kodlama", "Yapay Zeka Uygulamaları", "Drama", "Geleneksel Sanatlar"
        ],
        "Ortaokul": [
            "Türkçe", "Matematik", "Fen Bilimleri", "Sosyal Bilgiler", 
            "Görsel Sanatlar", "Müzik", "Beden Eğitimi ve Spor", "Yabancı Dil", 
            "Din Kültürü ve Ahlak Bilgisi", "Teknoloji ve Tasarım", "T.C. İnkılap Tarihi ve Atatürkçülük",
            "Bilişim Teknolojileri ve Yazılım", "Rehberlik ve Yönlendirme",
            "Matematik ve Bilim Uygulamaları", "Robotik Kodlama", "Yapay Zeka Uygulamaları",
            "Drama", "Geleneksel Sanatlar"
        ],
        "Lise": [
            "Türk Dili ve Edebiyatı", "Matematik", "Fizik", "Kimya", "Biyoloji",
            "Tarih", "Coğrafya", "Felsefe", "Yabancı Dil", "Din Kültürü ve Ahlak Bilgisi",
            "Görsel Sanatlar", "Müzik", "Beden Eğitimi", "Bilişim",
            "Seçmeli 1", "Seçmeli 2", "Seçmeli 3", "Rehberlik"
        ],
        "Anadolu Lisesi": [
            "Türk Dili ve Edebiyatı", "Matematik", "Fizik", "Kimya", "Biyoloji",
            "Tarih", "Coğrafya", "Felsefe", "Yabancı Dil", "Din Kültürü ve Ahlak Bilgisi",
            "Görsel Sanatlar", "Müzik", "Beden Eğitimi", "Bilişim",
            "Seçmeli 1", "Seçmeli 2", "Seçmeli 3", "Rehberlik"
        ],
        "Fen Lisesi": [
            "Türk Dili ve Edebiyatı", "Matematik", "Fizik", "Kimya", "Biyoloji",
            "Tarih", "Coğrafya", "Felsefe", "Birinci Yabancı Dil", "Din Kültürü ve Ahlak Bilgisi",
            "Beden Eğitimi ve Spor", "Görsel Sanatlar", "Müzik", "Sağlık Bilgisi ve Trafik Kültürü",
            "Bilişim Teknolojileri ve Yazılım", "Rehberlik ve Yönlendirme",
            "Seçmeli Matematik", "Seçmeli Fizik", "Seçmeli Kimya", "Seçmeli Biyoloji",
            "Genetik Bilimine Giriş", "Tıp Bilimine Giriş", "Astronomi ve Uzay Bilimleri",
            "Sosyal Bilim Çalışmaları", "Düşünme Eğitimi", "Kur'an-ı Kerim",
            "Peygamberimizin Hayatı (Fen Lise)", "Temel Dini Bilgiler", "Spor Eğitimi",
            "Sanat Eğitimi", "İslam Kültür ve Medeniyeti", "Osmanlı Türkçesi", "İkinci Yabancı Dil"
        ],
        "Sosyal Bilimler Lisesi": [
            "Türk Dili ve Edebiyatı", "Matematik", "Tarih", "Coğrafya", "Felsefe",
            "Psikoloji", "Sosyoloji", "İktisat", "Hukuk", "Yabancı Dil", 
            "Din Kültürü ve Ahlak Bilgisi", "Görsel Sanatlar", "Müzik", "Beden Eğitimi",
            "Bilişim", "Seçmeli 1", "Seçmeli 2", "Seçmeli 3", "Rehberlik"
        ]
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_school_type = None
        self.setWindowTitle("Okul Türü Seçimi")
        self.setFixedSize(550, 450)
        self.setup_ui()
        self.apply_styles()
    
    def setup_ui(self):
        """Set up the user interface with modern design"""
        layout = QVBoxLayout()
        layout.setSpacing(25)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header section
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QVBoxLayout()
        header_layout.setSpacing(10)
        header_layout.setContentsMargins(20, 20, 20, 20)
        
        # Icon
        icon_label = QLabel("🏫")
        icon_label.setAlignment(Qt.AlignCenter)  # type: ignore
        icon_label.setObjectName("iconLabel")
        icon_label.setFont(QFont("Segoe UI", 36))
        header_layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel("OKUL TÜRÜNÜ SEÇİN")
        title_label.setAlignment(Qt.AlignCenter)  # type: ignore
        title_label.setObjectName("titleLabel")
        title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        header_layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel("Lütfen okul türünü seçin. Bu seçim, öğretmen branş listesini otomatik olarak dolduracaktır.")
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)  # type: ignore
        desc_label.setObjectName("descLabel")
        desc_label.setFont(QFont("Segoe UI", 12))
        header_layout.addWidget(desc_label)
        
        header_frame.setLayout(header_layout)
        layout.addWidget(header_frame)
        
        # School type list
        self.school_list = QListWidget()
        self.school_list.setObjectName("schoolList")
        self.school_list.setFont(QFont("Segoe UI", 13))
        for school_type in self.SCHOOL_TYPES.keys():
            item = QListWidgetItem(school_type)
            item.setFont(QFont("Segoe UI", 13))
            self.school_list.addItem(item)
        self.school_list.currentItemChanged.connect(self.on_selection_changed)
        self.school_list.itemDoubleClicked.connect(self.accept)
        layout.addWidget(self.school_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.continue_button = QPushButton("Devam Et")
        self.continue_button.setObjectName("continueButton")
        self.continue_button.clicked.connect(self.accept)
        self.continue_button.setEnabled(False)  # Disabled until selection is made
        self.continue_button.setFont(QFont("Segoe UI", 12))
        
        self.cancel_button = QPushButton("İptal")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setFont(QFont("Segoe UI", 12))
        
        button_layout.addWidget(self.continue_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Select first item by default
        if self.school_list.count() > 0:
            self.school_list.setCurrentRow(0)
    
    def apply_styles(self):
        """Apply modern styles with improved design"""
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #2c3e50, stop: 1 #4a6491);
                border-radius: 15px;
            }
            #headerFrame {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            #iconLabel {
                color: white;
                margin: 10px 0;
            }
            #titleLabel {
                color: white;
                font-size: 24px;
                margin: 10px 0 5px 0;
            }
            #descLabel {
                color: #aed6f1;
                font-weight: normal;
                margin-bottom: 10px;
            }
            QListWidget {
                border: 2px solid #cccccc;
                border-radius: 10px;
                background: white;
                font-size: 14px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 15px;
                border-bottom: 1px solid #eeeeee;
            }
            QListWidget::item:selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #3498db, stop: 1 #2980b9);
                color: white;
                border-radius: 8px;
            }
            QPushButton {
                padding: 14px 25px;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                color: white;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #3498db, stop: 1 #2980b9);
                font-size: 14px;
                min-height: 25px;
                min-width: 130px;
            }
            QPushButton:disabled {
                background: #7f8c8d;
                color: #bdc3c7;
            }
            QPushButton:hover:!disabled {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #2980b9, stop: 1 #2573a7);
            }
            QPushButton:pressed:!disabled {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #2573a7, stop: 1 #1f618d);
            }
            #continueButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #27ae60, stop: 1 #219653);
            }
            #continueButton:hover:!disabled {
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
        """)
    
    def on_selection_changed(self, current, previous):
        """Handle selection change"""
        if current:
            self.selected_school_type = current.text()
            self.continue_button.setEnabled(True)
        else:
            self.selected_school_type = None
            self.continue_button.setEnabled(False)
    
    def get_selected_school_type(self):
        """Get the selected school type"""
        return self.selected_school_type
    
    def get_subjects_for_school_type(self, school_type):
        """Get subjects for the selected school type"""
        return self.SCHOOL_TYPES.get(school_type, [])
    
    def initialize_lessons_for_school_type(self, db_manager, school_type):
        """
        Initialize lessons based on the curriculum rules for the selected school type.
        This function creates mandatory lessons according to the official curriculum.
        """
        # For all school types, use the predefined subject list
        subjects = self.get_subjects_for_school_type(school_type)
        for subject in subjects:
            # Check if lesson already exists
            existing_lesson = db_manager.get_lesson_by_name(subject)
            if not existing_lesson:
                # Create a basic lesson with 2 weekly hours (can be adjusted later)
                db_manager.add_lesson(subject, 2)