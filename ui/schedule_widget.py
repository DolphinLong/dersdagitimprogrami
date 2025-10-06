# -*- coding: utf-8 -*-
"""
🚀 MODERN SCHEDULE PLANNER - Çarpıcı Yeni Tasarım
Ultra-modern, animasyonlu, etkileyici arayüz
"""

import sys
import io

if sys.platform.startswith('win'):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QFrame, QGridLayout, QScrollArea, QComboBox, QProgressBar,
                             QMessageBox, QGraphicsDropShadowEffect, QSplitter, QTextEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QTimer, QSize
from PyQt5.QtGui import QFont, QColor, QPalette, QLinearGradient, QPainter, QBrush, QPen, QIcon

from database import db_manager
from algorithms.scheduler import Scheduler
from utils.helpers import generate_color_for_lesson
import logging


class ScheduleGenerationThread(QThread):
    """Background thread for schedule generation"""
    progress = pyqtSignal(int, str)  # percentage, message
    finished = pyqtSignal(list)  # schedule_entries
    error = pyqtSignal(str)  # error message
    
    def __init__(self, scheduler):
        super().__init__()
        self.scheduler = scheduler
        
    def progress_callback(self, message: str, percentage: float):
        """Scheduler'dan gelen progress güncellemelerini UI'ye aktar"""
        self.progress.emit(int(percentage), message)
    
    def run(self):
        try:
            self.progress.emit(10, "🔍 Ders atamaları kontrol ediliyor...")
            assignments = db_manager.get_schedule_by_school_type()

            if not assignments:
                self.error.emit("❌ Ders ataması bulunamadı!\n\nLütfen önce 'Ders Atama' menüsünden dersleri öğretmenlere atayın.")
                return
            
            self.progress.emit(20, "🧹 Mevcut program temizleniyor...")
            db_manager.clear_schedule()
            self.progress.emit(25, "📋 Mevcut ders atamaları yükleniyor...")
            
            self.progress.emit(40, "🎯 Akıllı algoritma çalışıyor...")
            schedule_entries = self.scheduler.generate_schedule()
            self.progress.emit(60, "🔍 Çakışmalar kontrol ediliyor...")
            
            self.progress.emit(70, "💾 Veritabanına kaydediliyor...")
            saved_count = 0

            # Note: Schedule is already cleared and saved in the algorithm
            # Just verify the count
            final_schedule = db_manager.get_schedule_program_by_school_type()
            saved_count = len(final_schedule)
            
            self.progress.emit(90, f"💾 Program temizleniyor...")
            self.progress.emit(100, f"✅ Tamamlandı! {saved_count} ders yerleştirildi")

            # Note: Logging is handled by the main thread, not here
            # Verify the saved schedule
            final_schedule = db_manager.get_schedule_program_by_school_type()
            self.finished.emit(final_schedule)
            
        except Exception as e:
            logging.error(f"Schedule generation error: {e}")
            self.error.emit(f"Hata oluştu: {str(e)}")


class StatCard(QFrame):
    """Modern istatistik kartı"""
    
    def __init__(self, icon, title, value, color, parent=None):
        super().__init__(parent)
        self.setObjectName("statCard")
        self.value_text = value
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(0, 0, 0, 50))
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Icon and value
        top_layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 32))
        top_layout.addWidget(icon_label)
        
        top_layout.addStretch()
        
        self.value_label = QLabel(str(value))
        self.value_label.setFont(QFont("Segoe UI", 36, QFont.Bold))
        self.value_label.setStyleSheet(f"color: {color};")
        top_layout.addWidget(self.value_label)
        
        layout.addLayout(top_layout)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 12))
        title_label.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(title_label)
        
        self.setFixedHeight(120)
        
        # Styling
        self.setStyleSheet("""
            QFrame#statCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border-radius: 15px;
                border: 2px solid #e9ecef;
            }
            QFrame#statCard:hover {
                border: 2px solid """ + color + """;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ffffff, stop:1 #f0f7ff);
            }
        """)
    
    def update_value(self, value):
        """Animate value change"""
        self.value_label.setText(str(value))


class ModernButton(QPushButton):
    """Ultra-modern buton"""
    
    def __init__(self, text, icon, color, parent=None):
        super().__init__(text, parent)
        self.color = color
        self.setMinimumHeight(50)
        self.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.setCursor(Qt.PointingHandCursor)
        
        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)
        
        # Styling
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {color}, stop:1 {self._darken_color(color)});
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 24px;
                text-align: left;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self._lighten_color(color)}, stop:1 {color});
            }}
            QPushButton:pressed {{
                background: {self._darken_color(color)};
            }}
            QPushButton:disabled {{
                background: #bdc3c7;
                color: #7f8c8d;
            }}
        """)
    
    def _darken_color(self, color):
        """Darken a color"""
        colors = {
            '#27ae60': '#229954',
            '#3498db': '#2980b9',
            '#e74c3c': '#c0392b',
            '#f39c12': '#e67e22',
            '#9b59b6': '#8e44ad'
        }
        return colors.get(color, color)
    
    def _lighten_color(self, color):
        """Lighten a color"""
        colors = {
            '#27ae60': '#2ecc71',
            '#3498db': '#5dade2',
            '#e74c3c': '#ec7063',
            '#f39c12': '#f8c471',
            '#9b59b6': '#af7ac5'
        }
        return colors.get(color, color)


class ScheduleWidget(QWidget):
    """🚀 Ultra-modern Schedule Planner (ScheduleWidget for backward compatibility)"""
    
    SCHOOL_TIME_SLOTS = {
        "İlkokul": 6,
        "Ortaokul": 7,
        "Lise": 8,
        "Anadolu Lisesi": 8,
        "Fen Lisesi": 8,
        "Sosyal Bilimler Lisesi": 8
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Scheduler will be created dynamically (to support progress callback)
        self.scheduler = None
        self.schedule_thread = None
        self.setup_ui()
        self.load_statistics()
    
    def setup_ui(self):
        """Setup the stunning UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)
        
        # Hero Section
        hero = self.create_hero_section()
        main_layout.addWidget(hero)
        
        # Statistics Cards
        stats = self.create_statistics_section()
        main_layout.addWidget(stats)
        
        # Action Center
        actions = self.create_action_center()
        main_layout.addWidget(actions)
        
        # Progress Section (hidden by default)
        self.progress_section = self.create_progress_section()
        self.progress_section.setVisible(False)
        main_layout.addWidget(self.progress_section)
        
        # Live Log (collapsible)
        self.log_section = self.create_log_section()
        self.log_section.setMaximumHeight(0)
        main_layout.addWidget(self.log_section)
        
        main_layout.addStretch()
        
        # Apply global styling
        self.apply_global_styles()
    
    def create_hero_section(self):
        """Create hero section with gradient background"""
        hero = QFrame()
        hero.setObjectName("heroSection")
        hero.setMinimumHeight(180)
        
        layout = QVBoxLayout(hero)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(15)
        
        # Title with icon
        title_layout = QHBoxLayout()
        
        icon = QLabel("🎯")
        icon.setFont(QFont("Segoe UI Emoji", 48))
        title_layout.addWidget(icon)
        
        title = QLabel("DERS PROGRAMI OLUŞTURUCU")
        title.setFont(QFont("Segoe UI", 32, QFont.Bold))
        title.setStyleSheet("color: white; letter-spacing: 2px;")
        title_layout.addWidget(title)
        
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Subtitle
        subtitle = QLabel("Yapay zeka destekli akıllı program oluşturma sistemi")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
        layout.addWidget(subtitle)
        
        # Features
        features_layout = QHBoxLayout()
        features = [
            "✨ Akıllı dağılım algoritması",
            "🎯 2+2+1 optimal bloklar",
            "⚡ Çakışma tespiti",
            "🔄 Otomatik düzeltme"
        ]
        for feature in features:
            feature_label = QLabel(feature)
            feature_label.setFont(QFont("Segoe UI", 10))
            feature_label.setStyleSheet("color: rgba(255, 255, 255, 0.85); padding: 5px 15px; background: rgba(255, 255, 255, 0.1); border-radius: 10px;")
            features_layout.addWidget(feature_label)
        features_layout.addStretch()
        layout.addLayout(features_layout)
        
        hero.setStyleSheet("""
            QFrame#heroSection {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:0.5 #764ba2, stop:1 #f093fb);
                border-radius: 20px;
            }
        """)
        
        return hero
    
    def create_statistics_section(self):
        """Create statistics cards"""
        container = QFrame()
        layout = QGridLayout(container)
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Get statistics
        classes = db_manager.get_all_classes()
        teachers = db_manager.get_all_teachers()
        lessons = db_manager.get_all_lessons()
        assignments = db_manager.get_schedule_by_school_type()
        
        # Create cards
        self.classes_card = StatCard("🏫", "SINIFLAR", len(classes), "#3498db", self)
        self.teachers_card = StatCard("👨‍🏫", "ÖĞRETMENLER", len(teachers), "#27ae60", self)
        self.lessons_card = StatCard("📚", "DERSLER", len(lessons), "#f39c12", self)
        self.assignments_card = StatCard("📝", "ATAMALAR", len(assignments), "#9b59b6", self)
        
        layout.addWidget(self.classes_card, 0, 0)
        layout.addWidget(self.teachers_card, 0, 1)
        layout.addWidget(self.lessons_card, 0, 2)
        layout.addWidget(self.assignments_card, 0, 3)
        
        return container
    
    def create_action_center(self):
        """Create action center with modern buttons"""
        container = QFrame()
        container.setObjectName("actionCenter")
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Main action button with card style
        main_card = QFrame()
        main_card.setObjectName("mainCard")
        main_card_layout = QVBoxLayout(main_card)
        main_card_layout.setContentsMargins(20, 20, 20, 20)
        main_card_layout.setSpacing(10)
        
        # Title for main action
        main_title = QLabel("Yeni Program Oluştur")
        main_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        main_title.setStyleSheet("color: #2c3e50;")
        main_card_layout.addWidget(main_title)
        
        # Description
        main_desc = QLabel("Akıllı algoritma ile otomatik ders programı oluştur")
        main_desc.setFont(QFont("Segoe UI", 10))
        main_desc.setStyleSheet("color: #7f8c8d;")
        main_desc.setWordWrap(True)
        main_card_layout.addWidget(main_desc)
        
        # Main buttons (horizontal layout)
        main_buttons_layout = QHBoxLayout()
        main_buttons_layout.setSpacing(10)
        
        self.generate_btn = ModernButton("PROGRAMI OLUŞTUR", "🚀", "#27ae60", self)
        self.generate_btn.setMinimumHeight(60)
        self.generate_btn.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.generate_btn.clicked.connect(self.generate_schedule)
        main_buttons_layout.addWidget(self.generate_btn)
        
        self.fill_gaps_btn = ModernButton("BOŞLUKLARI DOLDUR", "⚡", "#e67e22", self)
        self.fill_gaps_btn.setMinimumHeight(60)
        self.fill_gaps_btn.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.fill_gaps_btn.clicked.connect(self.fill_empty_slots)
        main_buttons_layout.addWidget(self.fill_gaps_btn)
        
        main_card_layout.addLayout(main_buttons_layout)
        
        main_card.setStyleSheet("""
            QFrame#mainCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #e8f5e9, stop:1 #c8e6c9);
                border-radius: 15px;
                border: 2px solid #81c784;
            }
        """)
        
        layout.addWidget(main_card)
        
        # Secondary actions title
        sec_title = QLabel("Diğer İşlemler")
        sec_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        sec_title.setStyleSheet("color: #2c3e50; margin-top: 10px;")
        layout.addWidget(sec_title)
        
        # Secondary buttons grid
        buttons_layout = QGridLayout()
        buttons_layout.setSpacing(12)
        
        self.view_class_btn = ModernButton("Sınıf Programı", "📊", "#3498db", self)
        self.view_class_btn.setMinimumHeight(50)
        self.view_class_btn.clicked.connect(self.view_class_schedule)
        buttons_layout.addWidget(self.view_class_btn, 0, 0)
        
        self.view_teacher_btn = ModernButton("Öğretmen Programı", "👨‍🏫", "#9b59b6", self)
        self.view_teacher_btn.setMinimumHeight(50)
        self.view_teacher_btn.clicked.connect(self.view_teacher_schedule)
        buttons_layout.addWidget(self.view_teacher_btn, 0, 1)
        
        self.clear_btn = ModernButton("Programı Temizle", "🗑️", "#e74c3c", self)
        self.clear_btn.setMinimumHeight(50)
        self.clear_btn.clicked.connect(self.clear_schedule)
        buttons_layout.addWidget(self.clear_btn, 1, 0, 1, 2)
        
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        container.setStyleSheet("""
            QFrame#actionCenter {
                background: white;
                border-radius: 20px;
                border: 2px solid #e9ecef;
            }
        """)
        
        return container
    
    def create_progress_section(self):
        """Create animated progress section"""
        container = QFrame()
        container.setObjectName("progressSection")
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(40)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p% - %v/%m")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 20px;
                background: #ecf0f1;
                text-align: center;
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
            }
            QProgressBar::chunk {
                border-radius: 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:0.5 #764ba2, stop:1 #f093fb);
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Hazır...")
        self.status_label.setFont(QFont("Segoe UI", 12))
        self.status_label.setStyleSheet("color: #7f8c8d;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        container.setStyleSheet("""
            QFrame#progressSection {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ffecd2, stop:1 #fcb69f);
                border-radius: 15px;
                border: 2px solid #ffa07a;
            }
        """)
        
        return container
    
    def create_log_section(self):
        """Create collapsible log section"""
        container = QFrame()
        container.setObjectName("logSection")
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Toggle button
        toggle_layout = QHBoxLayout()
        self.log_toggle_btn = QPushButton("▼ Detaylı Log")
        self.log_toggle_btn.setCheckable(True)
        self.log_toggle_btn.clicked.connect(self.toggle_log)
        self.log_toggle_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #3498db;
                font-weight: bold;
                text-align: left;
                padding: 5px;
            }
            QPushButton:hover {
                color: #2980b9;
            }
        """)
        toggle_layout.addWidget(self.log_toggle_btn)
        toggle_layout.addStretch()
        layout.addLayout(toggle_layout)
        
        # Log text
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setStyleSheet("""
            QTextEdit {
                background: #2c3e50;
                color: #ecf0f1;
                border: none;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.log_text)
        
        container.setStyleSheet("""
            QFrame#logSection {
                background: white;
                border-radius: 10px;
            }
        """)
        
        return container
    
    def apply_global_styles(self):
        """Apply global styling"""
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f5f7fa, stop:1 #e3e8ef);
                font-family: "Segoe UI", Arial, sans-serif;
            }
        """)
    
    def generate_schedule(self):
        """Generate schedule with animation"""
        reply = QMessageBox.question(
            self,
            "Program Oluştur",
            "🚀 Akıllı algoritma ile yeni program oluşturulsun mu?\n\n"
            "• Mevcut program silinecek\n"
            "• 2+2+1 optimal dağılım yapılacak\n"
            "• Çakışmalar otomatik çözülecek",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Check if assignments exist
            assignments = db_manager.get_schedule_by_school_type()
            if not assignments:
                QMessageBox.warning(
                    self,
                    "Ders Ataması Gerekli",
                    "❌ Önce 'Ders Atama' menüsünden dersleri öğretmenlere atayın.\n\n"
                    "Program oluşturmak için en az bir ders ataması yapılmış olmalıdır."
                )
                return

            # Show progress
            self.progress_section.setVisible(True)
            self.progress_bar.setValue(0)
            self.status_label.setText("Başlatılıyor...")
            self.log_text.clear()
            self.add_log("🚀 Program oluşturma başlatıldı...")
            self.add_log(f"📋 {len(assignments)} ders ataması bulundu")
            self.add_log("💪 Ultra Aggressive Scheduler - %100 doluluk hedefi!")

            # Disable button
            self.generate_btn.setEnabled(False)

            # Create scheduler with progress callback support
            self.scheduler = Scheduler(db_manager, progress_callback=None)
            
            # Start thread
            self.schedule_thread = ScheduleGenerationThread(self.scheduler)
            
            # Connect ultra scheduler's callback to thread if available
            if hasattr(self.scheduler, 'ultra_scheduler') and self.scheduler.ultra_scheduler:
                self.scheduler.ultra_scheduler.progress_callback = self.schedule_thread.progress_callback
            
            self.schedule_thread.progress.connect(self.on_progress)
            self.schedule_thread.finished.connect(self.on_finished)
            self.schedule_thread.error.connect(self.on_error)
            self.schedule_thread.start()
    
    def on_progress(self, percentage, message):
        """Handle progress updates"""
        self.progress_bar.setValue(percentage)
        self.status_label.setText(message)
        self.add_log(message)
    
    def on_finished(self, schedule_entries):
        """Handle completion"""
        self.generate_btn.setEnabled(True)
        self.add_log(f"✅ BAŞARILI! {len(schedule_entries)} ders yerleştirildi")

        # Update statistics
        QTimer.singleShot(500, self.load_statistics)

        # Success message
        QMessageBox.information(
            self,
            "🎉 Başarılı!",
            "✅ Program başarıyla oluşturuldu!\n\n"
            f"📊 Toplam: {len(schedule_entries)} ders yerleştirildi\n"
            "✨ 2+2+1 akıllı dağılım uygulandı\n"
            "🎯 Çakışmalar otomatik çözüldü\n"
            "💾 Veritabanına kaydedildi\n\n"
            "📋 'Sınıf Programı' veya 'Öğretmen Programı' menülerinden programı görüntüleyebilirsiniz."
        )

        # Hide progress after delay
        QTimer.singleShot(3000, lambda: self.progress_section.setVisible(False))
    
    def on_error(self, error_msg):
        """Handle errors"""
        self.generate_btn.setEnabled(True)
        self.progress_section.setVisible(False)
        self.add_log(f"❌ HATA: {error_msg}")

        # Show more user-friendly error messages
        if "Ders ataması bulunamadı" in error_msg:
            error_msg += "\n\n💡 Çözüm: 'Ders Atama' menüsünden dersleri öğretmenlere atayın."

        QMessageBox.critical(self, "Hata", error_msg)
    
    def add_log(self, message):
        """Add message to log"""
        self.log_text.append(message)
    
    def toggle_log(self):
        """Toggle log visibility"""
        if self.log_toggle_btn.isChecked():
            self.log_toggle_btn.setText("▲ Detaylı Log")
            self.animate_height(self.log_section, 0, 300)
        else:
            self.log_toggle_btn.setText("▼ Detaylı Log")
            self.animate_height(self.log_section, 300, 0)
    
    def animate_height(self, widget, start, end):
        """Animate widget height"""
        animation = QPropertyAnimation(widget, b"maximumHeight")
        animation.setDuration(300)
        animation.setStartValue(start)
        animation.setEndValue(end)
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        animation.start()
        self.height_animation = animation  # Keep reference
    
    def load_statistics(self):
        """Reload statistics"""
        classes = db_manager.get_all_classes()
        teachers = db_manager.get_all_teachers()
        lessons = db_manager.get_all_lessons()
        assignments = db_manager.get_schedule_by_school_type()
        
        self.classes_card.update_value(len(classes))
        self.teachers_card.update_value(len(teachers))
        self.lessons_card.update_value(len(lessons))
        self.assignments_card.update_value(len(assignments))
    
    def view_class_schedule(self):
        """View class schedule"""
        from ui.dialogs.class_schedule_dialog import ClassScheduleDialog
        dialog = ClassScheduleDialog(self)
        dialog.exec_()
    
    def view_teacher_schedule(self):
        """View teacher schedule"""
        from ui.dialogs.teacher_schedule_dialog import TeacherScheduleDialog
        dialog = TeacherScheduleDialog(self)
        dialog.exec_()

    def fill_empty_slots(self):
        """Fill empty slots with remaining lessons"""
        reply = QMessageBox.question(
            self,
            "Boşlukları Doldur",
            "⚡ Programdaki boş slotlar doldurulmaya çalışılacak.\n\n"
            "Bu işlem:\n"
            "• Henüz tam yerleştirilmemiş dersleri bulur\n"
            "• Boş slotlara uygun dersleri yerleştirir\n"
            "• Öğretmen uygunluğunu ve çakışmaları kontrol eder\n\n"
            "Devam etmek istiyor musunuz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        try:
            self.add_log("⚡ Boş slotlar dolduruluyor...")
            
            # Get all classes
            classes = db_manager.get_all_classes()
            if not classes:
                QMessageBox.warning(self, "Uyarı", "Hiç sınıf bulunamadı!")
                return
            
            # Get school type and time slots
            school_type = db_manager.get_school_type() or "Lise"
            time_slots_map = {
                "İlkokul": 7, "Ortaokul": 7, "Lise": 8,
                "Anadolu Lisesi": 8, "Fen Lisesi": 8, "Sosyal Bilimler Lisesi": 8
            }
            time_slots_count = time_slots_map.get(school_type, 8)
            
            # Get all current schedule
            current_schedule = db_manager.get_schedule_program_by_school_type()
            
            # Get all lesson assignments
            all_assignments = db_manager.get_schedule_by_school_type()
            
            total_filled = 0
            total_attempted = 0
            
            # For each class, find what's missing and try to fill
            for class_obj in classes:
                # Calculate what lessons are needed vs what's scheduled
                needed_hours = {}  # {lesson_id: {teacher_id, hours_needed}}
                scheduled_hours = {}  # {lesson_id: hours_scheduled}
                
                # Get needed hours from assignments
                for assignment in all_assignments:
                    if assignment.class_id == class_obj.class_id:
                        lesson = db_manager.get_lesson_by_id(assignment.lesson_id)
                        if lesson:
                            weekly_hours = db_manager.get_weekly_hours_for_lesson(
                                assignment.lesson_id, class_obj.grade
                            )
                            if weekly_hours:
                                needed_hours[assignment.lesson_id] = {
                                    'teacher_id': assignment.teacher_id,
                                    'hours': weekly_hours
                                }
                                scheduled_hours[assignment.lesson_id] = 0
                
                # Count scheduled hours
                for entry in current_schedule:
                    if entry.class_id == class_obj.class_id:
                        scheduled_hours[entry.lesson_id] = scheduled_hours.get(entry.lesson_id, 0) + 1
                
                # Find empty slots for this class
                occupied_slots = set()
                for entry in current_schedule:
                    if entry.class_id == class_obj.class_id:
                        occupied_slots.add((entry.day, entry.time_slot))
                
                empty_slots = []
                for day in range(5):
                    for slot in range(time_slots_count):
                        if (day, slot) not in occupied_slots:
                            empty_slots.append((day, slot))
                
                # Try to fill missing hours into empty slots
                for lesson_id, info in needed_hours.items():
                    hours_needed = info['hours']
                    hours_scheduled = scheduled_hours.get(lesson_id, 0)
                    hours_missing = hours_needed - hours_scheduled
                    
                    if hours_missing > 0:
                        teacher_id = info['teacher_id']
                        lesson = db_manager.get_lesson_by_id(lesson_id)
                        
                        self.add_log(f"  • {class_obj.name} - {lesson.name}: {hours_missing} saat eksik")
                        
                        # Try to place missing hours
                        for _ in range(hours_missing):
                            total_attempted += 1
                            placed = False
                            
                            for day, slot in empty_slots[:]:
                                # Check if teacher is available
                                if not db_manager.is_teacher_available(teacher_id, day, slot):
                                    continue
                                
                                # Check if teacher has conflict
                                teacher_conflict = False
                                for entry in current_schedule:
                                    if (entry.teacher_id == teacher_id and 
                                        entry.day == day and 
                                        entry.time_slot == slot):
                                        teacher_conflict = True
                                        break
                                
                                if teacher_conflict:
                                    continue
                                
                                # Place the lesson
                                if db_manager.add_schedule_program(
                                    class_obj.class_id, teacher_id, lesson_id, 1, day, slot
                                ):
                                    empty_slots.remove((day, slot))
                                    occupied_slots.add((day, slot))
                                    total_filled += 1
                                    placed = True
                                    self.add_log(f"    ✓ Yerleştirildi: Gün {day+1}, Saat {slot+1}")
                                    break
                            
                            if not placed:
                                self.add_log(f"    ✗ Uygun slot bulunamadı")
                                break
            
            # Reload schedule
            current_schedule = db_manager.get_schedule_program_by_school_type()
            
            # Show result
            result_msg = f"⚡ BOŞLUK DOLDURMA SONUÇLARI\n\n"
            result_msg += f"📊 Denenen: {total_attempted} ders\n"
            result_msg += f"✅ Yerleştirilen: {total_filled} ders\n"
            result_msg += f"❌ Yerleştirilemeyen: {total_attempted - total_filled} ders\n\n"
            
            if total_filled > 0:
                result_msg += "Başarıyla tamamlandı!"
                QMessageBox.information(self, "Başarılı", result_msg)
            else:
                result_msg += "Hiç ders yerleştirilemedi.\n\nMümkün olduğunca program dolu veya uygun slot yok."
                QMessageBox.warning(self, "Uyarı", result_msg)
            
            self.add_log(f"✅ Boşluk doldurma tamamlandı: {total_filled}/{total_attempted}")
            
        except Exception as e:
            logging.error(f"Fill empty slots error: {e}")
            QMessageBox.critical(self, "Hata", f"Bir hata oluştu:\n\n{str(e)}")
    
    def clear_schedule(self):
        """Clear schedule"""
        reply = QMessageBox.question(
            self,
            "Programı Temizle",
            "⚠️ Tüm program silinecek!\n\nEmin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            db_manager.clear_schedule()
            self.add_log("🗑️ Program temizlendi")
            QMessageBox.information(self, "Başarılı", "Program başarıyla temizlendi.")
            self.load_statistics()


# Alias for backward compatibility
ModernSchedulePlanner = ScheduleWidget
