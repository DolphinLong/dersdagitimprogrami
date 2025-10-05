"""
Main window for the Class Scheduling Program
"""

from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget, QLabel, QMessageBox, QDialog, QFileDialog, QStatusBar, QScrollArea, QFrame, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QIcon
from reports.generator import ReportGenerator
from database import db_manager
from utils.notifications import get_notification_manager
from utils.file_manager import FileManager
# Add imports for the new dialogs
from ui.dialogs.teacher_dialog import TeacherDialog
from ui.dialogs.class_dialog import ClassDialog
from ui.dialogs.class_list_dialog import ClassListDialog
from ui.dialogs.teacher_list_dialog import TeacherListDialog
from ui.dialogs.lesson_dialog import LessonDialog
from ui.dialogs.lesson_list_dialog import LessonListDialog
from ui.school_type_dialog import SchoolTypeDialog
from init_curriculum import initialize_curriculum_for_school_type, create_sample_classes
from ui.dialogs.backup_restore_dialog import BackupRestoreDialog

class MainWindow(QMainWindow):
    """Main application window with modern dashboard design"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ders Programı")
        self.setGeometry(100, 100, 1200, 800)
        self.report_generator = ReportGenerator(db_manager)
        self.file_manager = FileManager(db_manager)
        self.notification_manager = get_notification_manager(self)
        self.setup_ui()
        self.apply_styles()
        # Show school type selection
        self.show_school_type_selection()
    
    def setup_ui(self):
        """Set up the user interface with modern dashboard design"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        central_widget.setLayout(main_layout)
        
        # Create header
        header_layout = QHBoxLayout()
        
        header_label = QLabel("EĞİTİM KURUMLARI İÇİN DERS PROGRAMI YÖNETİM SİSTEMİ")
        header_label.setAlignment(Qt.AlignLeft)  # type: ignore
        header_label.setObjectName("header")
        header_layout.addWidget(header_label)
        
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
        # Create dashboard grid layout
        self.dashboard_layout = QGridLayout()
        self.dashboard_layout.setSpacing(20)
        self.dashboard_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create dashboard cards
        self.create_dashboard_cards()
        
        # Add dashboard to scroll area for better responsiveness
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # type: ignore
        scroll_area.setObjectName("dashboardScroll")
        
        dashboard_widget = QWidget()
        dashboard_widget.setLayout(self.dashboard_layout)
        scroll_area.setWidget(dashboard_widget)
        
        main_layout.addWidget(scroll_area)
        
        # Create status bar
        status_bar = self.statusBar()
        if status_bar:
            status_bar.showMessage("Sistem hazır")
    
    def create_dashboard_cards(self):
        """Create dashboard cards for main functions"""
        # Schedule card
        schedule_card = self.create_dashboard_card(
            "📅", 
            "Ders Programı", 
            "Program oluştur, düzenle ve görüntüle", 
            self.open_schedule_tab
        )
        self.dashboard_layout.addWidget(schedule_card, 0, 0)
        
        # Teachers card
        teachers_card = self.create_dashboard_card(
            "👨‍🏫", 
            "Öğretmenler", 
            "Öğretmen ekle, düzenle ve yönet", 
            self.open_teachers_tab
        )
        self.dashboard_layout.addWidget(teachers_card, 0, 1)
        
        # Classes card
        classes_card = self.create_dashboard_card(
            "📚", 
            "Sınıflar", 
            "Sınıf ekle, düzenle ve yönet", 
            self.open_classes_tab
        )
        self.dashboard_layout.addWidget(classes_card, 0, 2)
        
        # Lessons card
        lessons_card = self.create_dashboard_card(
            "📖", 
            "Dersler", 
            "Ders ekle, düzenle ve yönet", 
            self.open_lessons_tab
        )
        self.dashboard_layout.addWidget(lessons_card, 1, 0)
        
        # Lesson Assignment card
        lesson_assignment_card = self.create_dashboard_card(
            "📝", 
            "Ders Atama", 
            "Öğretmenlere ders atama", 
            self.open_lesson_assignment
        )
        self.dashboard_layout.addWidget(lesson_assignment_card, 1, 1)
        
        # Reports card
        reports_card = self.create_dashboard_card(
            "📊", 
            "Raporlar", 
            "Program raporlarını oluştur ve dışa aktar", 
            self.open_reports_tab
        )
        self.dashboard_layout.addWidget(reports_card, 1, 2)
        

        
        # Backup/Restore card
        backup_restore_card = self.create_dashboard_card(
            "💾", 
            "Yedekle/Geri Yükle", 
            "Veri tabanı yedekleme ve geri yükleme", 
            self.open_backup_restore
        )
        self.dashboard_layout.addWidget(backup_restore_card, 2, 0)
        
        # Settings card
        settings_card = self.create_dashboard_card(
            "⚙️", 
            "Ayarlar", 
            "Uygulama ayarlarını yönet", 
            self.open_settings
        )
        self.dashboard_layout.addWidget(settings_card, 2, 1)
    
    def create_dashboard_card(self, icon, title, description, callback):
        """Create a dashboard card widget"""
        card = QFrame()
        card.setObjectName("dashboardCard")
        card.setFrameStyle(QFrame.StyledPanel)
        card.setLineWidth(2)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Icon label
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)  # type: ignore
        icon_label.setObjectName("cardIcon")
        icon_label.setFont(QFont("Segoe UI", 24))
        layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)  # type: ignore
        title_label.setObjectName("cardTitle")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignCenter)  # type: ignore
        desc_label.setObjectName("cardDescription")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Action button
        action_button = QPushButton("Aç")
        action_button.setObjectName("cardButton")
        action_button.clicked.connect(callback)
        layout.addWidget(action_button)
        
        card.setLayout(layout)
        return card
    
    def apply_styles(self):
        """Apply modern styles with gradient background"""
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                      stop: 0 #2c3e50, stop: 1 #4a6491);
            }
            #header {
                color: white;
                font-size: 24px;
                font-weight: bold;
                padding: 15px;
                background: rgba(0, 0, 0, 0.3);
                border-radius: 12px;
                margin-bottom: 10px;
            }
            #dashboardScroll {
                border: none;
                background: transparent;
            }
            #dashboardCard {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #ffffff, stop: 1 #f8f9fa);
                border-radius: 15px;
                border: 1px solid #dee2e6;
                padding: 15px;
            }
            #dashboardCard:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #f8f9fa, stop: 1 #e9ecef);
                border: 1px solid #3498db;
            }
            #cardIcon {
                color: #3498db;
                font-size: 32px;
                margin: 10px 0;
            }
            #cardTitle {
                color: #2c3e50;
                font-size: 18px;
                font-weight: bold;
                margin: 5px 0;
            }
            #cardDescription {
                color: #6c757d;
                font-size: 13px;
                margin: 5px 0;
            }
            #cardButton {
                padding: 12px 20px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                color: white;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #3498db, stop: 1 #2980b9);
                font-size: 14px;
                min-height: 40px;
            }
            #cardButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #2980b9, stop: 1 #2573a7);
            }
            QWidget {
                background: transparent;
                font-family: "Segoe UI", sans-serif;
            }
            QLabel {
                color: #212529;
                font-size: 14px;
            }
            QPushButton {
                padding: 10px 15px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                color: white;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #3498db, stop: 1 #2980b9);
                font-size: 13px;
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
            QStatusBar {
                background: rgba(0, 0, 0, 0.3);
                color: white;
                font-weight: bold;
                border-radius: 0 0 12px 12px;
                font-size: 12px;
                padding: 5px;
            }
        """)
    
    def open_schedule_tab(self):
        """Open schedule tab"""
        from ui.schedule_widget import ScheduleWidget
        
        # Create schedule widget dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Ders Programı Yönetimi")
        dialog.setGeometry(100, 100, 1200, 800)
        
        # Create layout
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        
        # Add schedule widget
        schedule_widget = ScheduleWidget(dialog)
        layout.addWidget(schedule_widget)
        
        # Add close button
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_button = QPushButton("Kapat")
        close_button.clicked.connect(dialog.accept)
        close_layout.addWidget(close_button)
        layout.addLayout(close_layout)
        
        # Apply styles
        dialog.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #ffffff, stop: 1 #f8f9fa);
            }
            QPushButton {
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                color: white;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #3498db, stop: 1 #2980b9);
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                          stop: 0 #2980b9, stop: 1 #2573a7);
            }
        """)
        
        # Show dialog
        dialog.exec_()
    
    def open_teachers_tab(self):
        """Open teachers tab"""
        dialog = TeacherListDialog(self)
        dialog.exec_()
    
    def open_classes_tab(self):
        """Open classes tab"""
        dialog = ClassListDialog(self)
        dialog.exec_()
    
    def open_lessons_tab(self):
        """Open lessons tab"""
        dialog = LessonListDialog(self)
        dialog.exec_()
    
    def open_reports_tab(self):
        """Open reports tab"""
        # For now, just show a message
        # msg = QMessageBox(self)
        # msg.setWindowTitle("Raporlar")
        # msg.setText("Raporlama işlevi henüz tam olarak uygulanmadı.")
        # msg.setIcon(QMessageBox.Information)
        # msg.exec_()
        
        # Use the reports dialog instead
        from ui.dialogs.reports_dialog import ReportsDialog
        dialog = ReportsDialog(self)
        dialog.exec_()
    

    
    def open_settings(self):
        """Open settings"""
        from ui.dialogs.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self)
        dialog.exec_()
    
    def open_lesson_assignment(self):
        """Open lesson assignment dialog"""
        from ui.dialogs.easy_assignment_dialog import EasyAssignmentDialog
        dialog = EasyAssignmentDialog(self)
        dialog.exec_()
    
    def open_backup_restore(self):
        """Open backup/restore dialog"""
        from ui.dialogs.backup_restore_dialog import BackupRestoreDialog
        dialog = BackupRestoreDialog(self)
        result = dialog.exec_()
        # If restore was successful, restart the application
        if result == 1:
            self.restart_application()
    
    def restart_application(self):
        """Restart the application after database restore"""
        from PyQt5.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, 
            'Yeniden Başlat', 
            'Uygulama yeniden başlatılacak. Devam etmek istiyor musunuz?',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            import sys
            import os
            import subprocess
            # Get the current Python executable and script
            python = sys.executable
            script = os.path.abspath(sys.argv[0])
            # Restart the application
            subprocess.Popen([python, script])
            # Close the current instance
            sys.exit(0)
    
    def show_school_type_selection(self):
        """Show the school type selection dialog"""
        # Check if school type is already set
        if db_manager.get_school_type():
            return  # Skip if already set
        
        # Show school type selection dialog
        school_dialog = SchoolTypeDialog(self)
        if school_dialog.exec_() == QDialog.Accepted:
            selected_type = school_dialog.get_selected_school_type()
            if selected_type:
                db_manager.set_school_type(selected_type)
                
                # Only initialize curriculum if no lessons exist yet
                existing_lessons = db_manager.get_all_lessons()
                if not existing_lessons:
                    # Initialize curriculum based on selected school type
                    initialize_curriculum_for_school_type(db_manager, selected_type)
                    
                    # Create sample classes
                    create_sample_classes(db_manager, selected_type)
                
                self.notification_manager.show_message(
                    "Okul Türü Seçildi", 
                    f"{selected_type} olarak ayarlandı."
                )
        else:
            # If user cancels, we can either close the application or set a default
            if not db_manager.get_school_type():
                db_manager.set_school_type("Lise")  # Set default
    